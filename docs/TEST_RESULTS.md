# Verification — 17 October 2026

## Passwords, readability, and detailed insights — 18 October 2026

- Backend suite: **39 passed**, with one existing test-client deprecation warning.
- Final TypeScript compilation and Vite production build passed.
- Browser registration with exactly eight password characters, logout, and login all reached the expected pages. Seven-character passwords are rejected by automated validation tests.
- Detailed analytics tests cover decimal totals, running totals, merchant grouping, weekday averages, empty history, account isolation, and currency filtering.
- Browser verified daily spending/running totals, merchant totals, monthly category breakdown, and weekday averages against a fictional confirmed QA receipt. Date filtering and the underlying values table worked.
- Larger typography checked at desktop and 390px mobile width without horizontal page overflow. Screenshot: `screenshots/detailed-insights.jpg`.
- Local frontend and backend restarted successfully; the backend cold start exceeded the launcher's initial readiness window, then health and browser authentication checks passed.


## Authentication origin fix

- Final suite after the origin/CSRF fix: **36 passed, 1 existing test-client deprecation warning in 2.77 seconds**.
- TypeScript and Vite production build pass after the API client change.
- Browser registration, logout, password login, and dashboard redirects passed on all four development origins: localhost and 127.0.0.1, ports 5173 and 5174.
- Verified session persistence across a reload on port 5174.
- Automated checks verify database insertion and password hashing, credentialed CORS preflight, random cookie-backed CSRF validation, and rejection of foreign origins, missing cookies, and mismatched tokens.
- UI/UX files were unchanged. Details and modified-file list: [AUTH_FIX.md](AUTH_FIX.md).

## Automated checks

- Frontend: TypeScript strict compilation and Vite production build pass.
- Database: `alembic upgrade head` succeeds on a fresh local SQLite database.
- Backend tests cover password/session lifecycle, CSRF checks, cross-account receipt/image/report isolation, invalid uploads, confirmation rules, persistent alert decisions, analytics, currency isolation, duplicate detection, decimal reconciliation, unit normalization, uncertain product matches, insufficient history, and real scikit-learn execution.
- Real OCR test: Tesseract 5.4 reads a generated receipt and returns line coordinates. No OCR accuracy benchmark is inferred from this fixture.
- Final regression suite: **21 passed, 1 deprecation warning in 2.59 seconds**, including the Coffee Beans/fee regression, single-page/multi-page PDF validation, and launch-directory-independent configuration.

## Browser checks

- Reference-inspired landing and login rendered successfully.
- A separate local QA account signed in and reached an empty live dashboard.
- Fictional PNG uploaded through the file chooser and processed by real OCR.
- Review showed merchant, purchase date, quantities, subtotal, tax, discount, and total.
- Browser testing exposed `Coffee Beans` matching `fee`; parser fixed to match whole fee words and regression coverage added.
- Corrected extracted fields, added a missing line, and confirmed the receipt through the UI.
- Investigation calculated the fixture's intended 20.00 discrepancy, with no invented historical price or spending conclusions.
- Selecting the alert highlighted OCR evidence on the original receipt preview.
- Marking an alert as expected persisted its state and reduced the open-alert count; reopening restored it.
- Dashboard displayed 566.50 INR, one confirmed receipt, one billing alert, and the stored grocery category.
- Logout returned to the sign-in screen.
- At a 390px viewport, the dashboard and landing had no horizontal overflow. Mobile layouts and screenshots were checked; screenshots are saved in `docs/screenshots/`.
- A live-server check found that launching from `backend/` previously opened a separate empty database. Configuration now anchors `.env`, relative SQLite paths, and upload paths to the project root. Login and real PDF OCR were reverified against the running server: four products extracted, Coffee Beans retained as an item, zero fees, draft excluded from analytics.

## Scope

Sample records are fictional and confined to the local QA account. Actual user accounts start empty. Tests exercise SQLite; PostgreSQL, public HTTPS deployment, sustained load, and exhaustive accessibility testing are not verified here. Starlette emits a test-client deprecation warning about its httpx integration; the tests still execute successfully.
