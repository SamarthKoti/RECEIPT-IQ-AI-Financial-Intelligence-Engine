"""Generate an explicitly fictional receipt for local OCR/UI testing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

target = Path('samples')
target.mkdir(exist_ok=True)
image = Image.new('RGB', (1000, 1400), '#fffdf7')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 32)
small = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 24)
title = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 46)
draw.text((80, 70), 'FRESH MARKET', fill='#25251f', font=title)
draw.text((80, 145), 'FICTIONAL SAMPLE - NOT A REAL PURCHASE', fill='#625f52', font=small)
lines = ['2026-10-17', '----------------------------------------', '2 x Whole Milk                   120.00', 'Sourdough Bread                   85.00', 'Greek Yogurt                      75.00', 'Coffee Beans                     250.00', '----------------------------------------', 'Subtotal                         530.00', 'Tax                               26.50', 'Discount                          10.00', 'TOTAL                            566.50', '----------------------------------------']
draw.multiline_text((80, 230), '\n'.join(lines), font=font, fill='#25251f', spacing=34)
draw.text((80, 1120), 'SAMPLE: total intentionally differs by 20.', fill='#625f52', font=small)
draw.text((80, 1170), 'Review the extraction, then investigate.', fill='#625f52', font=small)
image.save(target / 'fictional-receipt.png')
image.save(target / 'fictional-receipt.pdf', 'PDF')
print(target / 'fictional-receipt.png')
