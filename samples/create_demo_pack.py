"""Generate clearly fictional, OCR-friendly receipts. Never inserts account data."""
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'feature-demo'
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype('C:/Windows/Fonts/cour.ttf', 32)

def receipt(filename, merchant, day, items, subtotal, tax='0.00', fees='0.00', discount='0.00', rounding='0.00', total=None):
    subtotal = Decimal(subtotal)
    total = total or str(subtotal + Decimal(tax) + Decimal(fees) - Decimal(discount) + Decimal(rounding))
    lines = [merchant, 'FICTIONAL DEMO - NOT VALID FOR PAYMENT', f'Date: {day}', 'Currency: INR', '----------------------------------------']
    lines += [f'{name:<29} {amount:>8}' for name, amount in items]
    lines += ['----------------------------------------']
    lines += [f'{name:<29} {value:>8}' for name, value in [('Subtotal',f'{subtotal:.2f}'),('Tax',tax),('Service charge',fees),('Discount',discount),('Rounding',rounding),('TOTAL',f'{Decimal(total):.2f}')]]
    lines += ['----------------------------------------', 'Receipt IQ testing sample only']
    image = Image.new('RGB', (1000, 80 + len(lines)*49), 'white')
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((40,40+i*49), line, font=FONT, fill='black')
    image.save(OUT / f'{filename}.png')
    (OUT / f'{filename}.txt').write_text('\n'.join(lines),encoding='utf-8')

for i in range(1,31):
    rice = Decimal(90 + (i % 5)*5)
    items = [('1000 ml x Milk','60.00'),('1 x Bread','40.00'),('1 kg x Rice',f'{rice:.2f}'),('1 x Coffee Beans','100.00')]
    receipt(f'{i:02d}-grocery-history', 'DEMO FRESH MARKET', date(2026,7,19)+timedelta(days=(i-1)*3), items, str(rice+200))

receipt('31-investigate-this', 'DEMO FRESH MARKET', date(2026,10,18), [('2000 ml x Milk','180.00'),('1 x Bread','70.00'),('1 x Bread','70.00'),('5 kg x Rice','1000.00'),('1 x Coffee Bean','200.00')], '1450.00',tax='72.50',fees='300.00',discount='50.00',rounding='0.50',total='1900.00')
receipt('32-optional-dining', 'DEMO CORNER CAFE', date(2026,9,20), [('1 x Sandwich','180.00'),('1 x Tea','40.00')], '220.00', tax='11.00')
receipt('33-optional-transport', 'DEMO METRO TRANSPORT', date(2026,10,4), [('1 x Metro ticket','80.00')], '80.00')
receipt('34-optional-health', 'DEMO PHARMACY', date(2026,10,10), [('1 x Vitamins','250.00')], '250.00')

guide = '''# Receipt IQ fictional feature demo

All receipts are fictional. Use a separate test account to keep these out of your real spending.
Currency: INR. PNG files are uploaded individually; TXT companions are answer keys, not uploads.

## Quick walkthrough (six uploads)
1. Set your account currency to INR.
2. Upload and CONFIRM 01 through 05 in order. Review dates, amounts, quantities and units; choose Groceries for each.
3. Upload 31-investigate-this.png last. Review the extracted values against its TXT answer key; choose Groceries and confirm.
4. Open its investigation. Click billing/price alerts to highlight related receipt lines; try View evidence, Mark as expected, Dismiss, and report export.
5. Upload the SAME 31 PNG again to try duplicate detection. Confirming both intentionally increases totals; do this only in a test account.

## Full history walkthrough
Before uploading 31, confirm ALL 01 through 30 in numerical order. These span July through October and meet the Isolation Forest threshold of 30 earlier receipts. A model alert is not guaranteed merely by reaching the threshold.
Optional 32-34 add chart categories; review and choose Dining, Transport, and Health respectively. They also add merchant diversity.
Visit Dashboard and Insights: compare monthly/category spending, merchant totals, daily running totals, weekday averages, date filters, product trends and the values table. Search/filter the Library and export a report.

## Main receipt answer key and intended findings
- Item sum: 1520.00; printed subtotal: 1450.00 (difference -70.00).
- 1450.00 + 72.50 tax + 300.00 fee - 50.00 discount + 0.50 rounding = 1773.00. Printed total 1900.00 differs by +127.00.
- Bread appears twice with identical quantity and amount; may be intentional.
- Fee is 20.69% of the subtotal, above the 15% review threshold.
- Milk: historical 60.00/l versus current 90.00/l (+50%). Rice also demonstrates kg normalization and a price increase; Bread increases from 40.00 to 70.00 (+75%).
- Coffee Bean versus Coffee Beans offers an uncertain product match. Confirm only for this fictional demonstration, then inspect its price comparison.
- Main total is over 6 times the typical grocery receipt, provided at least five baseline receipts are confirmed in the same category/currency.
- First receipt intentionally has insufficient history. This is the correct state, not an error.

OCR may misread any receipt. Correct fields before confirmation; keep original values initially to explore alerts. Later correct subtotal to 1520.00 and total to 1843.00 to reconcile arithmetic while retaining the repeated item and fee. Correcting quantities or removing items requires recalculating these totals.

No single receipt exercises every feature: authentication/settings are separate, price/spending models require history, and these clear PNGs do not deliberately trigger low-confidence OCR, invalid-file handling, or the PDF upload path. Existing samples/fictional-receipt.pdf can test PDF upload separately. These are test scenarios, not claims of fraud or AI accuracy.
'''
(OUT/'START-HERE.md').write_text(guide,encoding='utf-8')
with ZipFile(ROOT/'receipt-iq-feature-demo.zip','w',ZIP_DEFLATED) as archive:
    for path in sorted(OUT.iterdir()):
        archive.write(path, f'feature-demo/{path.name}')
print(f'Created 34 PNG receipts and answer keys: {OUT}')

