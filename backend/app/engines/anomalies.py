from decimal import Decimal
from statistics import median
from sklearn.ensemble import IsolationForest
from .billing import alert

def detect_anomalies(receipt, history):
    findings = []
    comparable = [r for r in history if r.currency == receipt.currency and (r.purchase_date, r.id) < (receipt.purchase_date, receipt.id)]
    duplicates = [r for r in history if r.currency == receipt.currency and (r.file_hash == receipt.file_hash or (r.merchant.casefold().strip() == receipt.merchant.casefold().strip() and r.purchase_date == receipt.purchase_date and r.total == receipt.total))]
    if duplicates:
        findings.append(alert('duplicate-transaction', 'spending', 'Possible duplicate transaction', f'Matches receipt #{duplicates[0].id} by uploaded content or merchant, date, and total. Verify before counting both.'))
    category = [r for r in comparable if r.category == receipt.category and r.total is not None]
    message = f'Insufficient history: {len(category)} comparable {receipt.category.lower()} receipts; at least 5 are needed for a spending comparison.'
    if len(category) >= 5:
        typical = median([r.total for r in category])
        message = f'Compared with {len(category)} earlier {receipt.category.lower()} receipts. Median: {typical:.2f} {receipt.currency}.'
        if typical > 0 and receipt.total >= typical * 3:
            findings.append(alert('large-expense', 'spending', 'Larger than your usual purchase', f'{receipt.total:.2f} is {receipt.total/typical:.1f}× the median {typical:.2f} across {len(category)} prior {receipt.category.lower()} purchases.'))
        # Robust deviation resists single extreme historical observations.
        mad = median([abs(r.total - typical) for r in category])
        if mad > 0 and (receipt.total - typical) / (Decimal('1.4826') * mad) > 3.5 and not any(f['key'] == 'large-expense' for f in findings):
            findings.append(alert('category-deviation', 'spending', 'Outside your category’s usual range', f'Total {receipt.total:.2f}; category median {typical:.2f}; median absolute deviation {mad:.2f}. Robust deviation exceeds 3.5.'))
    if len(comparable) >= 30:
        training = [[float(r.total), r.purchase_date.weekday()] for r in comparable]
        forest = IsolationForest(n_estimators=100, contamination=.05, random_state=42).fit(training)
        if forest.predict([[float(receipt.total), receipt.purchase_date.weekday()]])[0] == -1:
            findings.append(alert('isolation', 'spending', 'Unusual amount / weekday combination', f'Isolation Forest flagged this amount and weekday against {len(comparable)} earlier transactions. This is a statistical outlier, not evidence of wrongdoing. Historical median: {median([r.total for r in comparable]):.2f}.'))
    return findings, message
