import hashlib
import secrets
import re
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, Response
from pwdlib import PasswordHash
from sqlalchemy.orm import Session as DBSession
from .db import get_db
from .models import Session, User
from .config import settings

password_hasher = PasswordHash.recommended()
DUMMY_HASH = password_hasher.hash(secrets.token_urlsafe(24))
CSRF_COOKIE = 'receipt_csrf'
CSRF_HEADER = 'x-csrf-token'

def valid_csrf_token(token):
    return bool(token and re.fullmatch(r'[A-Za-z0-9_-]{43}', token))

def csrf_matches(request):
    cookie = request.cookies.get(CSRF_COOKIE, '')
    header = request.headers.get(CSRF_HEADER, '')
    return valid_csrf_token(cookie) and valid_csrf_token(header) and secrets.compare_digest(cookie, header)

def issue_csrf(request, response):
    # Host-only HttpOnly cookie: JS receives the token through this allowed-origin
    # endpoint, not document.cookie. Reuse it so concurrent tabs remain valid.
    token = request.cookies.get(CSRF_COOKIE, '')
    if not valid_csrf_token(token):
        token = secrets.token_urlsafe(32)
    response.set_cookie(CSRF_COOKIE, token, httponly=True, secure=settings.cookie_secure,
                        samesite='lax', max_age=settings.session_hours*3600, path='/')
    return {'csrf_token': token}

def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(db, user, response):
    token = secrets.token_urlsafe(32)
    db.add(Session(token_hash=digest(token), user_id=user.id, expires=datetime.now(timezone.utc) + timedelta(hours=settings.session_hours)))
    db.commit()
    response.set_cookie('receipt_session', token, httponly=True, secure=settings.cookie_secure, samesite='lax', max_age=settings.session_hours*3600, path='/')

def current_user(request: Request, db: DBSession = Depends(get_db)):
    token = request.cookies.get('receipt_session', '')
    session = db.get(Session, digest(token)) if token else None
    if not session or session.expires.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(401, 'Please sign in to continue.')
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, 'Session is no longer valid.')
    return user
