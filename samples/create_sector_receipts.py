"""Create two fictional PNG receipt documents per supported app category."""
from pathlib import Path
from decimal import Decimal as D
from zipfile import ZipFile, ZIP_DEFLATED
import json
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parent
out=root/'seven-sectors'; out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/cour.ttf',28)
sectors={
 'Groceries':('DEMO FRESH GROCERY MARKET',[('Milk',60),('Bread',40),('Rice',100),('Lentils',90),('Apples',150),('Eggs',80),('Butter',120),('Cheese',160)]),
 'Dining':('DEMO GARDEN RESTAURANT',[('Vegetable Soup',120),('Paneer Curry',260),('Rice Bowl',140),('Roti',60),('Salad',100),('Lemonade',90),('Dessert',180),('Tea',50)]),
 'Transport':('DEMO CITY TRANSPORT',[('Metro ticket',60),('Bus ticket',40),('Airport shuttle',350),('Taxi ride',220),('Parking',80),('Toll',100),('Train ticket',180),('Bicycle rental',70)]),
 'Shopping':('DEMO CLOTHING RETAIL STORE',[('Cotton Shirt',799),('Jeans',1299),('Socks',149),('Belt',399),('Shoes',1799),('Cap',249),('Scarf',349),('Tote Bag',299)]),
 'Health':('DEMO HEALTH PHARMACY',[('Vitamin Supplement',240),('Bandages',80),('Thermometer',350),('Hand Sanitizer',120),('Oral Care Kit',190),('First Aid Kit',450),('Face Masks',100),('Cotton Pads',60)]),
 'Utilities':('DEMO HOME UTILITY SERVICES',[('Broadband Internet',699),('Water Supply',250),('Electricity',1250),('Mobile Recharge',299),('Waste Collection',150),('Gas Supply',850),('Telephone Plan',199),('Equipment Rental',100)]),
 'Other':('DEMO COMMUNITY SERVICES',[('Workshop Admission',450),('Craft Materials',180),('Club Membership',300),('Locker Rental',80),('Printing',60),('Event Admission',250),('Garden Visit',120),('Equipment Hire',200)]),
}
guide=['# Seven categories, two fictional bills each','', 'Use INR and a test account. Upload A before B within each category. Review OCR and manually choose the category named in the filename; classification is a suggestion, especially for Other and mixed utility/transport examples. Each bill is an intentionally fictional consolidated receipt, not a real supplier invoice.','', 'A is an eight-item clean baseline. B has 66 items, including two exact repeated pairs. The first two products have quantity 2 and a 25% higher price per item than A. Printed subtotal is 137.25 below the item sum; the service charge is 20% of printed subtotal; two separate taxes, a discount and negative rounding must be accounted for. Final total is 249.99 above the printed-subtotal calculation. JSON and TXT answer keys accompany each PNG. Two bills per category are insufficient for category spending anomaly detection (minimum five earlier comparable receipts) or Isolation Forest (30 earlier receipts). Re-upload the same B image to exercise duplicate receipt detection.','']
for category,(merchant,products) in sectors.items():
 for index in range(2):
  rows=[(name,2 if index and j<2 else 1,D(price)*(D('2.50') if index and j<2 else D(1))) for j,(name,price) in enumerate(products)]
  if index:
   for batch in range(2,9):
    rows += [(f'{name} Lot {batch}',batch%3+1,(D(price)*D(batch%3+1)+D(batch)*D('.35')).quantize(D('.01'))) for name,price in products]
   rows += [rows[22],rows[47]]
  item_sum=sum((price for _,_,price in rows),D(0))
  subtotal=item_sum-(D('137.25') if index else D(0))
  tax_part=(subtotal*D('.025')).quantize(D('.01'))
  tax=tax_part*2 if index else (subtotal*D('.05')).quantize(D('.01'))
  fees=(subtotal*D('.20')).quantize(D('.01')) if index else D(0)
  discount=D('120.75') if index else D('20.00')
  rounding=D('-.25') if index else D(0)
  expected=subtotal+tax+fees-discount+rounding; total=expected+(D('249.99') if index else D(0))
  filename=f'{category.lower()}-{"B-challenge" if index else "A-baseline"}'
  lines=[merchant,'FICTIONAL DEMO - NOT VALID FOR PAYMENT',f'Date: 2026-10-{"18" if index else "10"}','Currency: INR', '-'*54]
  lines += [f'{str(qty)+" x "+name:<40}{price:>10.2f}' for name,qty,price in rows]
  lines += ['-'*54]
  adjustments=[('Subtotal',subtotal)]+([('CGST',tax_part),('SGST',tax_part)] if index else [('Tax',tax)])+[('Service charge',fees),('Discount',discount)]+([('Rounding',rounding)] if index else [])+[('TOTAL',total)]
  lines += [f'{label:<40}{amount:>10.2f}' for label,amount in adjustments]
  lines += ['-'*54,'Receipt IQ synthetic test receipt']
  image=Image.new('RGB',(1100,80+len(lines)*44),'white'); draw=ImageDraw.Draw(image)
  for i,line in enumerate(lines):draw.text((35,35+i*44),line,font=font,fill='black')
  image.save(out/f'{filename}.png')
  (out/f'{filename}.txt').write_text('\n'.join(lines),encoding='utf-8')
  key=dict(category=category,item_count=len(rows),item_sum=str(item_sum),subtotal=str(subtotal),tax=str(tax),fees=str(fees),discount=str(discount),rounding=str(rounding),expected_total=str(expected),printed_total=str(total),items=[dict(name=name,quantity=qty,amount=str(price)) for name,qty,price in rows])
  (out/f'{filename}.json').write_text(json.dumps(key,indent=2),encoding='utf-8')
  guide.append(f'- {filename}.png: {len(rows)} items; category {category}; item sum {item_sum:.2f}; subtotal {subtotal:.2f}; tax {tax:.2f}; fees {fees:.2f}; discount {discount:.2f}; rounding {rounding:.2f}; expected total {expected:.2f}; printed total {total:.2f}.')
(out/'START-HERE.md').write_text('\n'.join(guide),encoding='utf-8')
with ZipFile(root/'seven-sectors-14-png-bills.zip','w',ZIP_DEFLATED) as z:
 for p in sorted(out.iterdir()):z.write(p,'seven-sectors/'+p.name)
print('Created 14 PNG bills in '+str(out))
