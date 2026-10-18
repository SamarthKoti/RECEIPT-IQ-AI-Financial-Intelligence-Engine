from datetime import date
from decimal import Decimal as D
from types import SimpleNamespace as Obj
from app.engines.parser import parse_receipt
from app.engines.billing import investigate_billing
from app.engines.prices import price_memory, unit_price
from app.engines.anomalies import detect_anomalies
from app.engines.categorizer import categorize

def item(**changes):
    return Obj(**({'id': 1, 'name': 'Milk', 'quantity': D('1'), 'unit': 'l', 'amount': D('60'), 'line_index': 1, 'product_key': None} | changes))

def receipt(**changes):
    return Obj(**({'id': 1, 'items': [item()], 'subtotal': D('60'), 'tax': D('3'), 'fees': D('2'), 'discount': D('5'), 'rounding': D('.01'), 'total': D('60.01'), 'purchase_date': date(2026, 10, 10), 'currency': 'INR', 'category': 'Groceries', 'merchant': 'Market', 'file_hash': 'a'} | changes))

def test_parser_preserves_decimal_and_adjustments():
    parsed = parse_receipt('FRESH MARKET\n2026-10-10\n2 x Milk 120.00\nBread 40.00\nSubtotal 160.00\nCGST 4.00\nSGST 4.00\nDiscount 10.00\nService charge 2.00\nRounding -0.01\nTOTAL 159.99\nCash 200.00\nChange 40.01')
    assert parsed['merchant'] == 'FRESH MARKET'
    assert parsed['total'] == D('159.99')
    assert parsed['tax'] == D('8')
    assert parsed['rounding'] == D('-.01')
    assert len(parsed['items']) == 2
    assert parsed['items'][0]['quantity'] == D(2)

def test_billing_accounts_for_taxes_discounts_fees_rounding():
    assert investigate_billing(receipt()) == []

def test_coffee_is_a_product_not_a_fee():
    parsed = parse_receipt('MARKET\nCoffee Beans 250.00\nDelivery fee 5.00\nTOTAL 255.00')
    assert parsed['items'][0]['name'] == 'Coffee Beans'
    assert parsed['fees'] == D('5.00')

def test_billing_difference_and_duplicate_evidence():
    findings = investigate_billing(receipt(total=D('70')))
    assert findings[0]['key'] == 'total'
    assert '60.01' in findings[0]['evidence']
    findings = investigate_billing(receipt(items=[item(), item(id=2)], subtotal=D('120'), total=D('120.01')))
    assert any(f['key'] == 'duplicate-item-2' for f in findings)

def test_unit_normalization_and_price_change():
    assert unit_price(item(quantity=D(1000), unit='ml')) == unit_price(item())
    old = receipt(id=2, purchase_date=date(2026, 9, 1), items=[item(amount=D('40'), quantity=D(1000), unit='ml')])
    alerts, trends, candidates = price_memory(receipt(), [old])
    assert len(alerts) == 1 and trends[0]['change'] == 50
    assert not candidates

def test_prices_do_not_mix_currencies_or_future_transactions():
    assert price_memory(receipt(), [receipt(currency='USD'), receipt(purchase_date=date(2027, 1, 1))])[1] == []

def test_fuzzy_matches_need_confirmation():
    old = receipt(id=2, purchase_date=date(2026, 9, 1), items=[item(name='Whole milks')])
    alerts, trends, candidates = price_memory(receipt(items=[item(name='Whole milk')]), [old])
    assert candidates and not alerts and not trends

def test_insufficient_history_never_fabricates_anomaly():
    findings, message = detect_anomalies(receipt(), [])
    assert findings == [] and 'Insufficient' in message

def test_spending_comparison_has_explanation():
    history = [receipt(id=i+2, total=D(10), file_hash=str(i), purchase_date=date(2026, 9, i+1)) for i in range(5)]
    findings, _ = detect_anomalies(receipt(), history)
    assert any('6.0×' in a['evidence'] for a in findings)

def test_isolation_forest_path_is_exercised(monkeypatch):
    import app.engines.anomalies as module
    real_model = module.IsolationForest
    fitted = []
    class ObservedForest(real_model):
        def fit(self, X, y=None, sample_weight=None):
            fitted.append(len(X))
            return super().fit(X, y, sample_weight)
    monkeypatch.setattr(module, 'IsolationForest', ObservedForest)
    history = [receipt(id=i+2, total=D(10+i%5), file_hash=str(i), purchase_date=date(2026, 8, i%28+1)) for i in range(35)]
    findings, message = detect_anomalies(receipt(total=D(500)), history)
    assert fitted == [35]
    assert any(a['key'] == 'large-expense' for a in findings)
    assert '35' in message

def test_nlp_categorizer_is_real_and_unknown_safe():
    assert categorize('grocery supermarket milk bread eggs rice')['category'] == 'Groceries'
    assert categorize('unrecognizable zqxv')['category'] == 'Other'
