from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from app.analytics import detailed_analytics

def test_detailed_analytics_exact_totals_and_purchase_averages():
    records = [SimpleNamespace(merchant=m, category=c, total=Decimal(v), purchase_date=date.fromisoformat(d)) for m,c,v,d in [
        ('Market','Groceries','10.10','2026-10-12'),
        ('market','Groceries','20.20','2026-10-12'),
        ('Cafe','Dining','5.05','2026-10-13'),
        ('Market','Groceries','4.65','2026-09-01'),
    ]]
    data = detailed_analytics(records)
    assert data['total'] == '40.00'
    assert data['average'] == '10.00'
    assert data['daily'][-1]['cumulative'] == '40.00'
    assert data['merchants'][0]['total'] == '34.95'
    assert data['merchants'][0]['count'] == 3
    assert data['weekdays'][0]['average'] == '15.15'
    assert data['weekdays'][2]['average'] is None
    assert data['monthly_categories'][1]['Groceries'] == '30.30'
    assert data['monthly_categories'][0]['Dining'] == '0'

def test_empty_analytics_does_not_invent_history():
    data = detailed_analytics([])
    assert data['daily'] == [] and data['merchants'] == []
    assert data['count'] == 0 and data['average'] == '0.00'
    assert all(w['average'] is None for w in data['weekdays'])
