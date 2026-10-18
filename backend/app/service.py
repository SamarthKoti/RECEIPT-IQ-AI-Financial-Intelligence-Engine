from sqlalchemy import select
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from .models import Receipt
from .engines.billing import investigate_billing, alert
from .engines.prices import price_memory
from .engines.anomalies import detect_anomalies

def investigation(db, receipt):
    history = db.scalars(select(Receipt).where(Receipt.user_id == receipt.user_id, Receipt.status == 'confirmed', Receipt.id != receipt.id)).all()
    billing = investigate_billing(receipt)
    prices, trends, candidates = price_memory(receipt, history)
    anomalies, message = detect_anomalies(receipt, history)
    uncertainty = [alert('ocr', 'ocr', 'Review extraction confidence', ' '.join(receipt.warnings))] if receipt.warnings else []
    decisions = {d.alert_key: d.action for d in receipt.decisions}
    findings = uncertainty + billing + prices + anomalies
    for finding in findings:
        finding['state'] = decisions.get(finding['key'], 'open')
    return {'alerts': findings, 'price_trends': trends, 'match_candidates': candidates, 'history_message': message, 'billing_message': 'Calculations reconcile within 0.02.' if not billing and receipt.items else 'Review extracted line items and recorded totals.', 'price_message': f'{len(trends)} products with comparable history.' if trends else 'No matching historical products yet. Price memory grows with confirmed receipts.'}

def serialize(receipt):
    result = {**{field: getattr(receipt, field) for field in ['id', 'merchant', 'purchase_date', 'category', 'currency', 'subtotal', 'tax', 'discount', 'fees', 'rounding', 'total', 'status', 'original_name', 'raw_text', 'ocr_lines', 'warnings', 'confidence', 'created_at']}, 'items': [{field: getattr(item, field) for field in ['id', 'name', 'quantity', 'unit', 'amount', 'line_index']} for item in receipt.items], 'image_url': f'/api/receipts/{receipt.id}/image'}
    return jsonable_encoder(result, custom_encoder={Decimal: str})
