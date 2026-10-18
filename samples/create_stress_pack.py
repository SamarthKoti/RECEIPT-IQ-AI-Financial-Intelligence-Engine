"""Render synthetic receipt documents and independent arithmetic answer keys."""
import json
from decimal import Decimal as D
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'stress-test-receipts'
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype('C:/Windows/Fonts/cour.ttf', 28)
products = ['Milk','Bread','Rice','Coffee Beans','Brown Lentils','Red Lentils','Olive Oil','Sunflower Oil','Rolled Oats','Almonds','Cashews','Wheat Flour','Sugar','Salt','Black Tea','Green Tea','Yogurt','Butter','Cheese','Apples']
manifest = []

def items(count):
    return [{'name': products[i % 20] + (f' Batch {i // 20 + 1}' if i >= 20 else ''), 'quantity':'1', 'unit':'each', 'amount':f'{D(40+(i*17)%260)+D(".25"):.2f}'} for i in range(count)]

def render(name, day, rows, subtotal_delta='0', extra_total='0', fees='0', faint=False, adversarial=False):
    item_sum = sum((D(r['amount']) for r in rows),D(0))
    subtotal = item_sum+D(subtotal_delta)
    cgst = (subtotal*D('.025')).quantize(D('.01'))
    sgst = cgst
    discount=D('125.75'); rounding=D('-.25')
    expected=subtotal+cgst+sgst+D(fees)-discount+rounding
    total=expected+D(extra_total)
    lines=['DEMO MARATHON GROCERY','FICTIONAL TEST ONLY - NOT VALID FOR PAYMENT',f'Date: {day}','Currency: INR',f'Test reference: {name}', '='*61]
    for i,r in enumerate(rows):
        prefix=f"{r['quantity']} {r['unit'] if r['unit'] != 'each' else ''} x {r['name']}".replace('  ',' ')
        if adversarial and i%10==0:
            lines += [prefix, f"    Line amount{'':<31}{D(r['amount']):>10,.2f}"]
        else:
            lines.append(f"{prefix:<48}{D(r['amount']):>10,.2f}")
    lines += ['='*61]
    for label,amount in [('Subtotal',subtotal),('CGST',cgst),('SGST',sgst),('Service charge',D(fees)),('Discount',discount),('Rounding',rounding),('TOTAL',total)]:
        lines.append(f'{label:<48}{amount:>10,.2f}')
    lines += ['Paid by card - fictional transaction', 'Receipt IQ stress-test fixture only']
    width,height=1200,80+len(lines)*39
    assert width*height < 25_000_000
    image=Image.new('RGB',(width,height),'white'); draw=ImageDraw.Draw(image)
    for i,line in enumerate(lines):
        draw.text((35,35+i*39),line,font=FONT,fill=(175,175,175) if faint and i%4 in (1,2) else (20,20,20))
    image.save(OUT/f'{name}.png')
    (OUT/f'{name}.txt').write_text('\n'.join(lines),encoding='utf-8')
    key={'file':f'{name}.png','date':day,'currency':'INR','category':'Groceries','item_count':len(rows),'items':rows,'item_sum':str(item_sum),'subtotal':str(subtotal),'tax':str(cgst+sgst),'fees':fees,'discount':str(discount),'rounding':str(rounding),'expected_total_from_printed_subtotal':str(expected),'printed_total':str(total),'subtotal_difference':subtotal_delta,'total_difference':extra_total,'pixels':[width,height]}
    (OUT/f'{name}.json').write_text(json.dumps(key,indent=2),encoding='utf-8'); manifest.append(key)

for i in range(1,6):
    baseline=items(60)
    baseline[0].update(quantity='1000',unit='ml',amount='60.00')
    baseline[2].update(quantity='1',unit='kg',amount='100.00')
    render(f'{i:02d}-history-60-items',f'2026-09-{i*5:02d}',baseline)

main=items(120)
for r in main: r['amount']=f'{D(r["amount"])*3:.2f}'
main[0].update(quantity='2000',unit='ml',amount='180.00')
main[2].update(quantity='5000',unit='g',amount='950.00')
main[3]['name']='Coffee Bean'
main[91]=dict(main[90]);main[111]=dict(main[110])
render('06-mega-investigation-120-items','2026-10-18',main,subtotal_delta='-349.75',extra_total='499.99',fees='15000.00')
render('07-clean-control-100-items','2026-10-17',items(100))
render('08-faint-print-90-items','2026-10-16',items(90),faint=True)
tricky=items(80)
tricky[3]['name']='Coffee Beans Decaf'
tricky[4]['name']='Coffee Beans Regular'
tricky[5]['name']='Sugar Free Biscuits'
tricky[6]['name']='Discount Brand Rice'
tricky[7]['name']='Round Grain Rice'
tricky[8]['name']='Tax Saver Notebook'
render('09-wrapped-labels-80-items','2026-10-15',tricky,adversarial=True)

guide='''# Long receipt challenge pack

FICTIONAL DATA ONLY. Use a separate test account, INR currency, and Groceries for comparisons. No records have been added to the app.

## Upload order
Upload and review/confirm 01-05 first (60 items each). Then upload 06 (120 items). Five prior same-category purchases enable statistical spending comparison and price history. These five do NOT enable Isolation Forest, which needs 30 earlier receipts. You may use the earlier feature-demo history pack for that branch, but mixing histories changes comparisons.

## Challenges
- 06: 120 line items, large total, two deliberate repeated item pairs, subtotal short by 349.75, unexplained final excess of 499.99, high service charge, two taxes, discount and negative rounding. Milk: 60 per litre to 90 (+50%). Rice: 100 per kg to 190 (+90%), using grams on the new receipt. Coffee Bean versus Coffee Beans tests uncertain matching. Other price rises are intentionally large.
- 07: 100 items with CORRECT arithmetic. A control to test false positives. History-based alerts may still occur; arithmetic should reconcile after accurate extraction.
- 08: 90 items with alternating pale print. Arithmetic is correct; this challenges OCR. A low-confidence warning is not guaranteed.
- 09: 80 real items, eight wrapped description/amount pairs, similar but distinct coffee products, and product names containing Discount, Round, and Tax. Arithmetic is correct. This deliberately challenges the current line-based parser: it may lose product names or misclassify products as adjustments. Review and correct using JSON; do not treat parser errors as real billing faults. Do not confirm different coffee products as identical simply because their names look similar.
- Upload the SAME 06 PNG again for duplicate transaction testing. Both confirmed copies inflate totals; only do this in a test account.

## How to assess results
Each PNG has a TXT copy of printed text and a JSON answer key with every item, quantity/unit, tax, fee, discount, rounding and expected total. TXT/JSON are for review; upload only PNGs individually, not the ZIP.

First record what OCR extracts without corrections. Compare item counts, names, quantities, units, amounts, and totals to JSON. Then correct the extracted fields and confirm to assess the calculation/price engines independently from OCR errors. Explore evidence highlighting, expected/dismissed alert states, corrections, reports, Library search/filtering and Insights charts. Do not assume all alerts must fire or that no alert means a flawless receipt.

All images are below the current 25-megapixel limit. Long OCR can take time or reach the app's timeout; that is a useful stress result, not proof of fraud. These are single PNG receipts; PDF and invalid-file flows are separate tests. Five historical examples establish comparison eligibility, not a reliable real-world spending profile.
'''
(OUT/'START-HERE.md').write_text(guide,encoding='utf-8')
with ZipFile(ROOT/'receipt-iq-long-bill-challenge.zip','w',ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):z.write(p,f'stress-test-receipts/{p.name}')
print(json.dumps([{k:r[k] for k in ('file','item_count','item_sum','printed_total','pixels')} for r in manifest],indent=2))
