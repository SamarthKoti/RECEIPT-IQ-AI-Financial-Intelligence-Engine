import csv
import hashlib
import io
import time
import uuid
from collections import defaultdict, deque
from decimal import Decimal
from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from .config import settings
from .db import get_db
from .models import User, Session, Receipt, Item, Decision
from .schemas import Register, Login, Profile, ReceiptEdit, AlertAction, MatchInput
from .security import current_user, create_session, password_hasher, DUMMY_HASH, digest, csrf_matches, issue_csrf
from .engines.ocr import prepare_file, extract
from .engines.parser import parse_receipt
from .engines.categorizer import categorize
from .engines.prices import normalize, unit_price
from .service import serialize, investigation
from .analytics import detailed_analytics

app = FastAPI(title='Receipt IQ', version='1.0.0')
storage = Path(settings.storage_dir).resolve()
storage.mkdir(parents=True, exist_ok=True)
attempts = defaultdict(deque)
attempt_lock = Lock()

@app.middleware('http')
async def safeguards(request, call_next):
    if request.method in ('POST', 'PATCH', 'DELETE'):
        origin = request.headers.get('origin')
        if origin and origin not in settings.allowed_origins:
            return JSONResponse({'detail': 'Request origin is not allowed.', 'code': 'origin_invalid'}, status_code=403)
        if request.headers.get('x-receipt-iq') != '1' or not csrf_matches(request):
            return JSONResponse({'detail': 'CSRF token is missing or invalid. Refresh the page and try again.', 'code': 'csrf_invalid'}, status_code=403)
        if request.headers.get('content-length', '').isdigit() and int(request.headers['content-length']) > 13 * 1024 * 1024:
            return JSONResponse({'detail': 'Maximum upload size is 12 MB.'}, status_code=413)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'same-origin'
    return response

# Wrap the request guard so allowed-origin clients can read validation errors too.
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True,
                   allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
                   allow_headers=['Content-Type', 'X-Receipt-IQ', 'X-CSRF-Token'])

def throttle(request):
    key = request.client.host if request.client else 'local'
    with attempt_lock:
        queue = attempts[key]
        now = time.monotonic()
        while queue and queue[0] < now - 300:
            queue.popleft()
        if len(queue) >= 20:
            raise HTTPException(429, 'Too many sign-in attempts. Try again in five minutes.')
        queue.append(now)

def user_json(user):
    return {'id': user.id, 'name': user.name, 'email': user.email, 'currency': user.currency}

def owned(db, user, receipt_id):
    receipt = db.scalar(select(Receipt).where(Receipt.id == receipt_id, Receipt.user_id == user.id))
    if not receipt:
        raise HTTPException(404, 'Receipt not found.')
    return receipt

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/auth/csrf')
def csrf(request: Request, response: Response):
    origin = request.headers.get('origin')
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(403, 'Request origin is not allowed.')
    return issue_csrf(request, response)

@app.post('/api/auth/register', status_code=201)
def register(payload: Register, request: Request, response: Response, db: DBSession = Depends(get_db)):
    throttle(request)
    user = User(name=payload.name.strip(), email=str(payload.email).lower(), password_hash=password_hasher.hash(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'An account with this email already exists.')
    create_session(db, user, response)
    return user_json(user)

@app.post('/api/auth/login')
def login(payload: Login, request: Request, response: Response, db: DBSession = Depends(get_db)):
    throttle(request)
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    valid = password_hasher.verify(payload.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, 'Email or password is incorrect.')
    old_token = request.cookies.get('receipt_session')
    if old_token:
        db.execute(delete(Session).where(Session.token_hash == digest(old_token)))
    create_session(db, user, response)
    return user_json(user)

@app.get('/api/auth/me')
def me(user: User = Depends(current_user)):
    return user_json(user)

@app.post('/api/auth/logout')
def logout(request: Request, response: Response, db: DBSession = Depends(get_db)):
    db.execute(delete(Session).where(Session.token_hash == digest(request.cookies.get('receipt_session', ''))))
    db.commit()
    response.delete_cookie('receipt_session', path='/')
    return {'ok': True}

@app.patch('/api/auth/me')
def profile(payload: Profile, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    user.name = payload.name.strip()
    user.currency = payload.currency
    db.commit()
    return user_json(user)

@app.post('/api/receipts/upload', status_code=201)
def upload(file: UploadFile = File(...), user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    content = file.file.read(12 * 1024 * 1024 + 1)
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(413, 'Maximum upload size is 12 MB.')
    if not content:
        raise HTTPException(400, 'The uploaded file is empty.')
    name = f'{uuid.uuid4().hex}.png'
    path = storage / name
    try:
        prepare_file(content, path)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(422, str(exc) if isinstance(exc, ValueError) else 'Unable to decode this file. Use a valid image or single-page PDF.')
    try:
        ocr = extract(path)
        parsed = parse_receipt(ocr['text'])
        items = parsed.pop('items')
        category = categorize(ocr['text'])
        warnings = ocr['warnings']
        if parsed['total'] is None or parsed['purchase_date'] is None:
            warnings = warnings + ['The date or total could not be extracted. Enter the missing details before confirming.']
        receipt = Receipt(user_id=user.id, **parsed, category=category['category'], currency=user.currency, file_hash=hashlib.sha256(content).hexdigest(), file_name=name, original_name=(file.filename or 'receipt')[:255], raw_text=ocr['text'], ocr_lines=ocr['lines'], confidence=ocr['confidence'], warnings=warnings, items=[Item(**i) for i in items])
        db.add(receipt)
        db.commit()
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return serialize(receipt)

@app.get('/api/receipts')
def receipts(user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    records = db.scalars(select(Receipt).where(Receipt.user_id == user.id).order_by(Receipt.created_at.desc())).all()
    hashes = defaultdict(int)
    for receipt in records:
        hashes[receipt.file_hash] += 1
    return [{**serialize(receipt), 'possible_duplicate': hashes[receipt.file_hash] > 1} for receipt in records]

@app.get('/api/receipts/{receipt_id}')
def detail(receipt_id: int, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    return serialize(owned(db, user, receipt_id))

@app.get('/api/receipts/{receipt_id}/image')
def image(receipt_id: int, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    return FileResponse(storage / receipt.file_name, media_type='image/png')

@app.patch('/api/receipts/{receipt_id}')
def edit(receipt_id: int, payload: ReceiptEdit, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    values = payload.model_dump(exclude={'items'})
    for key, value in values.items():
        setattr(receipt, key, value)
    if any(item.line_index is not None and item.line_index >= len(receipt.ocr_lines) for item in payload.items):
        raise HTTPException(422, 'An evidence line is outside the receipt image.')
    receipt.items = [Item(**item.model_dump()) for item in payload.items]
    receipt.decisions = []
    receipt.status = 'review'
    db.commit()
    return serialize(receipt)

@app.post('/api/receipts/{receipt_id}/confirm')
def confirm(receipt_id: int, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    if receipt.total is None or receipt.purchase_date is None or not receipt.items:
        raise HTTPException(422, 'Add a date, total, and at least one line item before confirming.')
    receipt.status = 'confirmed'
    db.commit()
    return serialize(receipt)

@app.get('/api/receipts/{receipt_id}/investigation')
def investigate(receipt_id: int, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    if receipt.status != 'confirmed':
        raise HTTPException(409, 'Review and confirm this receipt first.')
    return investigation(db, receipt)

@app.patch('/api/receipts/{receipt_id}/alerts/{alert_key}')
def decide(receipt_id: int, alert_key: str, payload: AlertAction, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    if receipt.status != 'confirmed' or alert_key not in {a['key'] for a in investigation(db, receipt)['alerts']}:
        raise HTTPException(404, 'Alert not found.')
    decision = next((d for d in receipt.decisions if d.alert_key == alert_key), None)
    if decision:
        decision.action = payload.action
    else:
        receipt.decisions.append(Decision(alert_key=alert_key, action=payload.action))
    db.commit()
    return {'ok': True}

@app.post('/api/receipts/{receipt_id}/matches')
def match_product(receipt_id: int, payload: MatchInput, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    receipt = owned(db, user, receipt_id)
    item = next((i for i in receipt.items if i.id == payload.item_id), None)
    previous = db.scalar(select(Item).join(Receipt).where(Item.id == payload.historical_item_id, Receipt.user_id == user.id, Receipt.status == 'confirmed', Receipt.id != receipt.id, Receipt.currency == receipt.currency))
    if not item or not previous or unit_price(item)[1] != unit_price(previous)[1]:
        raise HTTPException(422, 'Choose a comparable product from your confirmed receipts.')
    item.product_key = previous.product_key or normalize(previous.name)
    previous.product_key = item.product_key
    receipt.decisions = [d for d in receipt.decisions if d.alert_key != f'price-{item.id}']
    db.commit()
    return {'ok': True}

def confirmed(db, user):
    return db.scalars(select(Receipt).where(Receipt.user_id == user.id, Receipt.status == 'confirmed', Receipt.currency == user.currency)).all()

@app.get('/api/analytics/overview')
def overview(user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    records = confirmed(db, user)
    total_count = len(db.scalars(select(Receipt.id).where(Receipt.user_id == user.id)).all())
    alerts = sum(sum(a['state'] == 'open' and a['kind'] != 'ocr' for a in investigation(db, r)['alerts']) for r in records)
    return {'total': str(sum((r.total for r in records), Decimal(0))), 'count': total_count, 'confirmed': len(records), 'alerts': alerts, 'currency': user.currency, 'recent': [serialize(r) for r in sorted(records, key=lambda r: r.created_at, reverse=True)[:5]], 'scope': 'Confirmed receipts in your selected currency. No currency conversion is applied.'}

@app.get('/api/analytics/categories')
def categories(user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    values = defaultdict(Decimal)
    for receipt in confirmed(db, user):
        values[receipt.category] += receipt.total
    return [{'name': k, 'value': str(v)} for k, v in sorted(values.items())]

@app.get('/api/analytics/details')
def analytics_details(days: int | None = Query(default=None, ge=1, le=365), user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    records = confirmed(db, user)
    if days:
        end = date.today()
        start = end - timedelta(days=days-1)
        records = [r for r in records if start <= r.purchase_date <= end]
    return {**detailed_analytics(records), 'currency': user.currency}

@app.get('/api/analytics/trends')
def trends(user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    values = defaultdict(Decimal)
    for receipt in confirmed(db, user):
        values[receipt.purchase_date.strftime('%Y-%m')] += receipt.total
    return [{'month': k, 'total': str(v)} for k, v in sorted(values.items())]

@app.get('/api/reports/export')
def export(receipt_id: int | None = None, user: User = Depends(current_user), db: DBSession = Depends(get_db)):
    records = [owned(db, user, receipt_id)] if receipt_id is not None else confirmed(db, user)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Receipt', 'Merchant', 'Date', 'Category', 'Currency', 'Total', 'Status', 'Alert', 'Evidence', 'Decision'])
    def safe(value):
        value = '' if value is None else str(value)
        return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else value
    for receipt in records:
        findings = investigation(db, receipt)['alerts'] if receipt.status == 'confirmed' else []
        for finding in findings or [{}]:
            writer.writerow([safe(x) for x in [receipt.id, receipt.merchant, receipt.purchase_date, receipt.category, receipt.currency, receipt.total, receipt.status, finding.get('title'), finding.get('evidence'), finding.get('state')]])
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="receipt-iq-report.csv"'})
