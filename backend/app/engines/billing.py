from decimal import Decimal

def alert(key, kind, title, evidence, lines=None, severity='review', **extra):
    return dict(key=key, kind=kind, title=title, evidence=evidence, lines=[i for i in (lines or []) if i is not None], severity=severity, **extra)

def investigate_billing(receipt):
    findings = []
    items = receipt.items
    item_sum = sum((i.amount for i in items), Decimal(0))
    lines = [i.line_index for i in items]
    if items and receipt.subtotal is not None and abs(item_sum - receipt.subtotal) > Decimal('.02'):
        findings.append(alert('subtotal', 'billing', 'Subtotal needs a second look', f'Line amounts sum to {item_sum:.2f}; printed subtotal is {receipt.subtotal:.2f}. Difference: {receipt.subtotal-item_sum:+.2f}. Check for missing OCR lines.', lines))
    basis = receipt.subtotal if receipt.subtotal is not None else (item_sum if items else None)
    if basis is not None and receipt.total is not None:
        expected = basis + receipt.tax + receipt.fees - receipt.discount + receipt.rounding
        if abs(expected - receipt.total) > Decimal('.02'):
            findings.append(alert('total', 'billing', 'The total does not reconcile', f'{basis:.2f} subtotal + {receipt.tax:.2f} tax + {receipt.fees:.2f} fees − {receipt.discount:.2f} discount + {receipt.rounding:.2f} rounding = {expected:.2f}. Recorded total: {receipt.total:.2f}; difference: {receipt.total-expected:+.2f}.', lines))
    seen = {}
    for item in items:
        key = (item.name.casefold().strip(), item.quantity, item.unit, item.amount)
        if key in seen:
            findings.append(alert(f'duplicate-item-{item.id}', 'billing', 'Repeated item — worth reviewing', f'{item.name} appears with the same quantity and amount ({item.amount:.2f}) more than once. This may be intentional.', [seen[key], item.line_index]))
        seen[key] = item.line_index
    if basis and receipt.fees > basis * Decimal('.15'):
        findings.append(alert('fees', 'billing', 'Additional charges exceed 15%', f'Fees of {receipt.fees:.2f} are {receipt.fees / basis * 100:.1f}% of the {basis:.2f} subtotal. Verify the stated service or delivery charge.', lines))
    return findings
