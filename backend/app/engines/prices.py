import re
from decimal import Decimal
from rapidfuzz.fuzz import ratio
from .billing import alert

def normalize(name):
    return re.sub(r'[^a-z0-9]+', ' ', name.casefold()).strip()

def unit_price(item):
    scale, unit = {'kg': (1000, 'g'), 'l': (1000, 'ml')}.get(item.unit, (1, item.unit))
    return item.amount / (item.quantity * Decimal(scale)), unit

def price_memory(receipt, history):
    findings, trends, candidates = [], [], []
    for item in receipt.items:
        current, unit = unit_price(item)
        matches = []
        for old in history:
            if old.currency != receipt.currency or (old.purchase_date, old.id) >= (receipt.purchase_date, receipt.id):
                continue
            for previous in old.items:
                price, old_unit = unit_price(previous)
                if old_unit != unit:
                    continue
                exact = (item.product_key or normalize(item.name)) == (previous.product_key or normalize(previous.name))
                if exact:
                    matches.append((old, previous, price))
                elif ratio(normalize(item.name), normalize(previous.name)) >= 80:
                    candidates.append({'item_id': item.id, 'historical_item_id': previous.id, 'name': item.name, 'historical_name': previous.name, 'merchant': old.merchant, 'date': str(old.purchase_date)})
        if matches:
            matches.sort(key=lambda entry: (entry[0].purchase_date, entry[0].id))
            old, previous, baseline = matches[-1]
            change = (current / baseline - 1) * 100 if baseline else None
            trends.append({'name': item.name, 'unit': unit, 'change': round(float(change), 1) if change is not None else None, 'points': [{'date': str(r.purchase_date), 'price': float(p)} for r, _, p in matches] + [{'date': str(receipt.purchase_date), 'price': float(current)}]})
            if change is not None and change >= 15:
                findings.append(alert(f'price-{item.id}', 'price', f'{item.name}: {change:.1f}% increase', f'Price per {unit}: {baseline:.4f} on {old.purchase_date} → {current:.4f} now. Quantity and units normalized; product identity should still be reviewed.', [item.line_index]))
    return findings, trends, candidates[:30]
