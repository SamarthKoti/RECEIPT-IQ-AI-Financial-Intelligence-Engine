from pathlib import Path
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps
import pypdfium2 as pdfium
from ..config import settings

Image.MAX_IMAGE_PIXELS = 25_000_000

def prepare_file(content: bytes, destination: Path):
    """Decode rather than trusting extension. Keep a normalized preview for evidence."""
    import io
    if content.startswith(b'%PDF-'):
        doc = pdfium.PdfDocument(content)
        try:
            if len(doc) != 1:
                raise ValueError('Upload a single-page receipt PDF. Split multi-page files first.')
            page = doc[0]
            w, h = page.get_size()
            if w * h * 4 > 25_000_000:
                raise ValueError('PDF dimensions are too large.')
            im = page.render(scale=2).to_pil().convert('RGB')
        finally:
            doc.close()
    else:
        im = Image.open(io.BytesIO(content))
        if im.format not in ('PNG', 'JPEG', 'WEBP'):
            raise ValueError('Use a PNG, JPEG, WebP, or single-page PDF.')
        im.load()
        im = ImageOps.exif_transpose(im).convert('RGB')
    if im.width * im.height > 25_000_000 or min(im.size) < 50:
        raise ValueError('Image must be at least 50px and at most 25 megapixels.')
    im.save(destination, 'PNG')

def extract(path: Path):
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    im = Image.open(path)
    gray = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    try:
        data = pytesseract.image_to_data(gray, config='--psm 6', output_type=pytesseract.Output.DICT, timeout=35)
    except pytesseract.TesseractNotFoundError:
        return {'text': '', 'lines': [], 'confidence': 0, 'warnings': ['OCR unavailable: install Tesseract and set TESSERACT_CMD. You can enter receipt details manually.']}
    except RuntimeError:
        return {'text': '', 'lines': [], 'confidence': 0, 'warnings': ['OCR timed out. Try a smaller, clearer image or enter details manually.']}
    groups = {}
    for i, word in enumerate(data['text']):
        if not word.strip():
            continue
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        groups.setdefault(key, []).append(i)
    lines = []
    for indices in groups.values():
        x = min(data['left'][i] for i in indices)
        y = min(data['top'][i] for i in indices)
        right = max(data['left'][i] + data['width'][i] for i in indices)
        bottom = max(data['top'][i] + data['height'][i] for i in indices)
        confidence = sum(max(0, float(data['conf'][i])) for i in indices) / len(indices) / 100
        lines.append({'text': ' '.join(data['text'][i] for i in indices), 'box': [x / im.width, y / im.height, (right-x) / im.width, (bottom-y) / im.height], 'confidence': round(confidence, 3)})
    confidence = sum(x['confidence'] for x in lines) / len(lines) if lines else 0
    return {'text': '\n'.join(x['text'] for x in lines), 'lines': lines, 'confidence': confidence, 'warnings': ['Low OCR confidence. Check every amount against the image.'] if confidence < .75 else []}
