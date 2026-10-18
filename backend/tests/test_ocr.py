import io
from PIL import Image, ImageDraw, ImageFont
import pytest
from app.engines.ocr import prepare_file, extract
from app.config import settings
from pathlib import Path

def test_decoder_normalizes_images_and_rejects_arbitrary_bytes(tmp_path):
    image = Image.new('RGB', (150, 200), 'white')
    output = io.BytesIO()
    image.save(output, 'JPEG')
    target = tmp_path / 'normalized.png'
    prepare_file(output.getvalue(), target)
    assert Image.open(target).format == 'PNG'
    with pytest.raises(Exception):
        prepare_file(b'<script>bad()</script>', target)

def test_real_tesseract_on_generated_receipt(tmp_path):
    import shutil
    windows = Path('C:/Program Files/Tesseract-OCR/tesseract.exe')
    if windows.exists():
        settings.tesseract_cmd = str(windows)
    elif not shutil.which('tesseract') and not settings.tesseract_cmd:
        pytest.skip('Tesseract executable not installed')
    image = Image.new('RGB', (900, 700), 'white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 36)
    except OSError:
        font = ImageFont.truetype('DejaVuSans.ttf', 36)
    draw.multiline_text((60, 50), 'FRESH MARKET\n2026-10-10\nMilk          60.00\nBread         40.00\nSubtotal     100.00\nTax            5.00\nTOTAL        105.00', fill='black', font=font, spacing=24)
    target = tmp_path / 'receipt.png'
    image.save(target)
    result = extract(target)
    assert 'FRESH MARKET' in result['text']
    assert '105.00' in result['text']
    assert result['confidence'] > .5
    assert result['lines'][0]['box'][2] > 0

def test_pdf_validation_and_rendering(tmp_path):
    image = Image.new('RGB', (300, 500), 'white')
    output = io.BytesIO()
    image.save(output, 'PDF')
    target = tmp_path / 'pdf-preview.png'
    prepare_file(output.getvalue(), target)
    assert Image.open(target).width >= 300
    multiple = io.BytesIO()
    image.save(multiple, 'PDF', save_all=True, append_images=[image])
    with pytest.raises(ValueError, match='single-page'):
        prepare_file(multiple.getvalue(), tmp_path / 'invalid.png')
