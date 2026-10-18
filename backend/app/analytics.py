"""Descriptive analytics from reviewed transactions; all arithmetic stays decimal."""
from collections import defaultdict
from decimal import Decimal

def detailed_analytics(records):
    daily = defaultdict(lambda: {'total': Decimal(0), 'count': 0})
    merchants = {}
    monthly = {}
    weekdays = [{'day': day, 'total': Decimal(0), 'count': 0} for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]
    categories = sorted({r.category for r in records})
    for r in records:
        day = r.purchase_date.isoformat()
        daily[day]['total'] += r.total
        daily[day]['count'] += 1
        key = r.merchant.strip().casefold()
        merchant = merchants.setdefault(key, {'name': r.merchant, 'total': Decimal(0), 'count': 0})
        merchant['total'] += r.total
        merchant['count'] += 1
        month = r.purchase_date.strftime('%Y-%m')
        monthly.setdefault(month, {c: Decimal(0) for c in categories})[r.category] += r.total
        weekday = weekdays[r.purchase_date.weekday()]
        weekday['total'] += r.total
        weekday['count'] += 1
    cumulative = Decimal(0)
    days = []
    for day, values in sorted(daily.items()):
        cumulative += values['total']
        days.append({'date': day, 'total': str(values['total']), 'cumulative': str(cumulative), 'count': values['count']})
    return {
        'count': len(records), 'total': str(cumulative),
        'average': str((cumulative / len(records)).quantize(Decimal('.01'))) if records else '0.00',
        'daily': days,
        'merchants': [{'name': m['name'], 'total': str(m['total']), 'count': m['count']} for m in sorted(merchants.values(), key=lambda m: m['total'], reverse=True)[:6]],
        'categories': categories,
        'monthly_categories': [{'month': month, **{c: str(v) for c, v in values.items()}} for month, values in sorted(monthly.items())],
        'weekdays': [{**w, 'total': str(w['total']), 'average': str((w['total']/w['count']).quantize(Decimal('.01'))) if w['count'] else None} for w in weekdays],
    }
