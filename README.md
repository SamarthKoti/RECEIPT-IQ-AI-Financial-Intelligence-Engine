# RECEIPT IQ

**Don't Just Scan Your Bills. Understand Them.**

A working React + FastAPI application for reviewing receipt extraction and investigating billing arithmetic, historical product prices, and unusual spending. The visual system reconstructs `design/reference.png` with CSS spheres, illuminated rings, translucent glass, and a right-aligned desktop hero. The reference is not used as a page background.

## Quick start — Windows PowerShell

After installing dependencies, start or restore the local app from the project root with `powershell -File .\Start-ReceiptIQ.ps1`. The launcher reuses running servers, starts missing servers in the background, and checks the frontend plus its backend proxy. Logs are in `data/run/`. Local URLs require these processes to remain running; run the launcher again after a reboot or if the browser reports connection refused.

Run commands from the repository root. Requires Node.js 20.19+ or 22.12+, Python 3.10+, and Tesseract 5.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
winget install --id UB-Mannheim.TesseractOCR --exact
```

In `.env`, set `TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe` for the Windows installation. `FRONTEND_ORIGINS` is a JSON list that allows `localhost` and `127.0.0.1` on ports 5173 and 5174. Both CORS and CSRF validation use this exact allowlist. The legacy singular `FRONTEND_ORIGIN` remains a fallback only when the plural setting is absent.

Initialize/migrate the database:

```powershell
.venv/Scripts/python -m alembic -c backend/alembic.ini upgrade head
```

Start the backend in one terminal:

```powershell
.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open **http://127.0.0.1:5173** (or `http://localhost:5173`). To use port 5174 explicitly, run `npm.cmd run dev -- --port 5174`. Create your own account, upload a receipt, review the draft, and confirm it to run investigations. There is no built-in account or production password. Vite proxies same-origin `/api` requests to `http://127.0.0.1:8000`; the browser never needs to mix localhost and IP-address cookies. OpenAPI documentation is at http://127.0.0.1:8000/docs.

All API mutations require `X-Receipt-IQ: 1` and a random cookie-backed CSRF token. First call `GET /api/auth/csrf`, retain its HttpOnly `receipt_csrf` cookie, and send the returned `csrf_token` as `X-CSRF-Token` with the cookie on the mutation. The frontend does this automatically with `credentials: include`. Tokens contain 32 random bytes; the backend validates format and compares header/cookie using constant-time comparison. CSRF responses are never cached. Untrusted origins and missing/mismatched tokens receive HTTP 403. Authentication session cookies remain HttpOnly/SameSite=Lax. Host-only cookies intentionally keep `localhost` and `127.0.0.1` sessions separate; sign in on the hostname you use.

Configuration is anchored to the project root: `.env`, relative SQLite paths, and relative upload paths resolve consistently even when the backend is launched from `backend/`. Database migrations are still required before the first launch.

On Linux/macOS, use `.venv/bin/python`, `npm` instead of `npm.cmd`, and install Tesseract through your OS package manager (for example `apt install tesseract-ocr` on Debian/Ubuntu). `backend/requirements.lock.txt` records the tested Windows/Python 3.10 environment; `requirements.txt` is the cross-platform dependency manifest.

## Try a fictional receipt

`samples/fictional-receipt.png` and `.pdf` are explicitly fictional fixtures, not real spending. They contain a deliberate 20.00 total difference: 530.00 subtotal + 26.50 tax − 10.00 discount = 546.50, while the printed total is 566.50. Upload one through the app, check the extracted fields, and confirm it. Select the resulting alert to highlight OCR evidence. New accounts start empty; no sample transactions are silently inserted into personal analytics.

## Implemented workflow

Registration accepts passwords from 8 to 128 characters. Existing passwords continue to work. The interface uses larger body text, form inputs, labels, and chart ticks for readability.

Financial Insights also includes daily spend/running total, top merchants, monthly category mix, and average purchase size by weekday. Its detailed view supports all dates, last 30 days, and last 90 days, plus an accessible table of daily values. Only the signed-in user's confirmed receipts in the selected currency are included. Missing weekdays are shown without a bar, not as zero-value purchases; no sample data is inserted into personal charts.

- Landing, login, registration, overview, scan, searchable/filterable library, receipt investigation, insights, and settings.
- Argon2 password hashes; random database-backed sessions stored as hashes; HttpOnly/SameSite cookies; logout revocation; explicit origin validation plus custom-header and random double-submit CSRF protection; per-process authentication throttling.
- Private, account-owned receipt images and reports. Uploaded file names never become storage paths. Files are decoded and normalized to PNG, with 12 MB and 25-megapixel limits. Single-page PDFs render through PDFium.
- Tesseract OCR with OpenCV contrast preprocessing, normalized line coordinates, confidence, and warnings. An editable draft is saved before confirmation. Unavailable OCR allows explicitly labeled manual entry.
- Decimal line totals, tax, fees, discounts, and rounding. Money travels over JSON as decimal strings; charts convert to numbers only for display.
- Confirmed receipts feed analytics. Currency settings select the analytics currency; currencies are never silently mixed or converted.
- Evidence selection, expected/dismissed/reopened alerts, manual product-match confirmation, receipt corrections, CSV reports, profile/currency settings, and logout.

## Architecture

```text
backend/
  app/
    config.py           Environment configuration
    db.py, models.py    SQLAlchemy models and sessions
    schemas.py         Validated API inputs
    security.py        Password and session handling
    main.py            REST routes and authorization
    service.py         Investigation orchestration/serialization
    engines/
      ocr.py           File decoding, preprocessing, OCR boxes
      parser.py        Receipt text → editable structured draft
      categorizer.py   TF-IDF / Naive Bayes NLP baseline
      billing.py       Decimal-safe reconciliation
      prices.py        Product matching and normalized unit prices
      anomalies.py     Median/MAD comparisons and Isolation Forest
  migrations/          Versioned Alembic schema migration
  tests/               Engine, API, ownership, and real OCR tests
frontend/
  src/
    App.tsx            Routing, authentication context, landing/auth shell
    api.ts, types.ts   Typed API client and domain contracts
    components/        Shared cards, charts, headings, fetching helper
    pages/             Individual application page modules
    style.css          Responsive reference-inspired visual system
design/reference.png
samples/               Clearly fictional PNG/PDF test receipts
docs/TEST_RESULTS.md
```

## Intelligence, without invented claims

**Receipt X-Ray:** sums full line amounts; reconciles known adjustments with a 0.02 tolerance; flags identical repeated line items and fees above 15% of subtotal. An alert means review is needed, not fraud. Incorrect or missing OCR lines can create apparent discrepancies.

**Price Memory:** exact normalized product-name matches or user-confirmed fuzzy matches. RapidFuzz similarity of at least 80 proposes a match; it does not automatically assert identity. Quantities normalize kg→g and l→ml, while per-item products remain per-item. Comparisons use earlier confirmed receipts in the same currency. Increases of at least 15% receive alerts. Different pack sizes require reviewed quantities and units; no automatic semantic SKU inference is claimed.

**Expense Detective:** same-content or merchant/date/total duplicate candidates; category median comparison after five prior purchases; robust median absolute deviation when nonzero; a real, deterministic Isolation Forest after 30 prior transactions. Amount and weekday are its features. The system explains each comparison and explicitly says when history is insufficient. Model outliers are review signals, not a guarantee that every unusual transaction will be detected.

**Categorization:** a real scikit-learn TF-IDF + Multinomial Naive Bayes pipeline trained on a small, included category seed corpus. Low-score text falls back to Other. This is a transparent baseline, not a broadly validated commercial classifier. No accuracy metric is asserted. Users can correct every category.

## Tests and builds

```powershell
.venv/Scripts/python -m pytest backend/tests -q
cd frontend
npm.cmd run build
node node_modules/prettier/bin/prettier.cjs --check src
```

See `docs/TEST_RESULTS.md` for actual test results and browser checks. API tests replace OCR with deterministic text to isolate business/security behavior; a separate test executes real Tesseract. SQLite is exercised locally. PostgreSQL compatibility is implemented through SQLAlchemy/Numeric/JSON and psycopg, but a PostgreSQL server has not been exercised in this environment.

## PostgreSQL and deployment

Set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/receipt_iq` in your private environment, then run the same Alembic command. Never commit `.env`. Existing SQLite data is not automatically transferred to PostgreSQL.

For deployment, serve `frontend/dist` with SPA fallback to `index.html`, proxy `/api` to the Python service, and install Tesseract in the backend image/host. Replace `FRONTEND_ORIGINS` with only your exact public HTTPS origin(s), set `COOKIE_SECURE=true`, and use HTTPS. Restart the backend after changing environment settings. Keep the database and `STORAGE_DIR` on persistent private volumes with restricted OS permissions and backups. SQLite plus the upload directory must both be backed up; schema migrations do not back up data.

This repository is a tested local application, not a deployed or independently security-audited production service. Before a public multi-user launch, use a shared rate limiter/reverse-proxy upload limits, background OCR workers with resource quotas, paginated/cached analytics, expired-session cleanup, operational monitoring, email verification/recovery, and a retention/deletion policy. OCR currently runs in FastAPI's worker thread pool; historical analysis is computed on request and is intended for local/modest data volumes. Tesseract uses English recognition by default. Parsing targets common decimal-dot receipt layouts and day-first or ISO dates; review is mandatory for other formats. Only single-page PDFs are supported. These limits are explicit rather than presented as complete enterprise readiness.
