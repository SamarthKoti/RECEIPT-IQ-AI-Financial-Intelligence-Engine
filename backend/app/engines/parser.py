import re
from datetime import datetime
from decimal import Decimal

AMOUNT = re.compile(r'(-?\d[\d,]*\.\d{2})\s*(?:[A-Z]{1,3})?\s*$')

def parse_receipt(text: str):
    result = {'merchant': 'Unknown merchant', 'purchase_date': None, 'subtotal': None, 'tax': Decimal(0), 'discount': Decimal(0), 'fees': Decimal(0), 'rounding': Decimal(0), 'total': None, 'items': []}
    lines = text.splitlines()
    for line in lines[:5]:
        if len(line.strip()) > 2 and re.search('[a-zA-Z]', line) and not AMOUNT.search(line):
            result['merchant'] = line.strip()[:200]
            break
    for index, line in enumerate(lines):
        date_match = re.search(r'\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b', line)
        if date_match:
            for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    result['purchase_date'] = datetime.strptime(date_match[0], fmt).date()
                    break
                except ValueError:
                    pass
        match = AMOUNT.search(line)
        if not match:
            continue
        value = Decimal(match[1].replace(',', ''))
        label = line[:match.start()].strip(' .:₹$€£')
        lower = label.lower()
        if re.search(r'sub\s*total', lower):
            result['subtotal'] = abs(value)
        elif re.search(r'\b(tax|gst|cgst|sgst|vat)\b', lower):
            result['tax'] += abs(value)
        elif re.search(r'discount|saving|coupon', lower):
            result['discount'] += abs(value)
        elif re.search(r'round', lower):
            result['rounding'] += value
        elif re.search(r'\bfees?\b|\bservice charge\b|\bdelivery charge\b', lower):
            result['fees'] += abs(value)
        elif re.search(r'\b(total|amount due|balance due|net amount)\b', lower):
            result['total'] = abs(value)
        elif re.search(r'cash|change|paid|card|tender|balance|payment', lower):
            continue
        elif label and value >= 0:
            quantity = Decimal(1)
            unit = 'each'
            qty_match = re.match(r'(\d+(?:\.\d+)?)\s*(kg|g|ml|l)?\s*[xX×]\s*(.+)', label)
            if qty_match:
                quantity, unit, label = Decimal(qty_match[1]), qty_match[2] or 'each', qty_match[3]
            if quantity > 0:
                result['items'].append({'name': label[:200], 'quantity': quantity, 'unit': unit, 'amount': value, 'line_index': index})
    return result
