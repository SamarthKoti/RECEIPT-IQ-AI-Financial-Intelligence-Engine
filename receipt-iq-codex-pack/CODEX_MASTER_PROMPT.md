# CODEX MASTER BUILD PROMPT — RECEIPT IQ

You are a senior full-stack engineer, AI engineer, product designer, and quality engineer. Build a complete, working, locally runnable web application called **RECEIPT IQ** — *Don't Just Scan Your Bills. Understand Them.*

## Reference-image instruction — highest visual priority

The image at `design/reference.png` is the **source of truth for visual art direction**. Open/inspect it before creating any UI. The user wants the website to look as close as reasonably possible to this reference in **composition, palette, lighting, proportions, atmosphere, and 3D ornamentation**. This is not merely a generic “glassmorphism” inspiration.

Reproduce these specific details faithfully:
- Warm matte beige/taupe/pink-gray full-viewport canvas, with softly blended salmon and peach lighting; **avoid black dashboards, generic blue/purple gradients, and default SaaS templates**.
- Large softly shaded, three-dimensional glossy orange-to-apricot spheres: a dominant partially cropped sphere at the upper-right, another partially cropped sphere at lower-left, plus smaller floating glowing orange orbs.
- Semi-transparent orange ring/torus ornaments floating behind/in front of the glass panel (one in the upper-left region, another near the lower middle). Use layered CSS radial/conic gradients, SVG, and/or lightweight Three.js as appropriate. They should feel softly luminous and volumetric, not flat outlined circles.
- A large, wide, centrally positioned **frosted glass rectangle**, with very thin translucent white border, subtle background blur, almost invisible shadows, and lots of negative space.
- Inside the glass: compact white brand wordmark at upper left, tiny spaced uppercase navigation at upper right; main hero copy aligned toward the RIGHT half of the panel, with strong large white title, small eyebrow text, delicate supporting description, and a small minimalist outlined CTA.
- Clean white/off-white typography, modern geometric sans-serif (e.g., Inter or Manrope); avoid huge heavy buttons, dense decoration, saturated neon, or excessive glass cards on the landing page.
- Desktop visual target: wide photographic/editorial framing matching the 626×358 reference proportions, translated into a responsive real website. Preserve the image’s negative space and spatial hierarchy.
- Animations are refined and low amplitude: slow sphere drift, ring rotation, entrance fade; honor `prefers-reduced-motion`.

**Do not simply set the supplied reference screenshot as the page background.** Recreate it as actual responsive HTML/CSS/3D layers with selectable text, clickable nav links, and functioning controls. You may use the screenshot solely as a development reference. Aim for a close visual match, not generic similarity. Use responsive adaptations for small screens, with a readable layout and unobstructed controls.

## Product mission

RECEIPT IQ is an AI-assisted **receipt investigation and expense-intelligence** web application. The signature interaction is **Interactive Receipt Investigation**: users can upload a real receipt, correct OCR if needed, see itemized expenses, and investigate evidence-backed alerts. It must do more than upload → categorize → pie chart.

Three flagship engines:
1. **Receipt X-Ray:** Validate arithmetic (line totals, subtotal, discounts, taxes, rounding, final total) and detect genuinely unexplained mismatches. Link any warning to specific lines/evidence in the original receipt.
2. **Price Memory:** Match repeated products across receipts using normalized names, package sizes, units, and merchant context; track unit-price history and highlight price increases. Never compare unlike quantities without normalization.
3. **Expense Detective:** Flag unusually large or duplicate transactions compared with the user's own history. Show explainable reasons, relevant baseline/comparison, confidence/quality caveats, and dismiss/confirm feedback. An anomaly is NOT proof of fraud.

Supporting functions: account creation, login/logout, dashboard, receipt upload/history, transaction list with category labels, expense breakdown and trends, investigation detail page, and downloadable evidence-based report. A conversational receipt assistant is an optional future extension, not a prerequisite for a working app.

## Preferred architecture

Use a **real frontend + backend**, not a static mockup:
- Frontend: React + Vite + TypeScript; Tailwind CSS; Framer Motion (or motion) for transitions; React Router; TanStack Query for API state; Recharts for charts; Lucide icons. Maintain CSS variables/design tokens for palette.
- Backend: Python + FastAPI; SQLAlchemy 2.x ORM; Pydantic; Alembic migrations.
- DB: SQLite by default for zero-config local demo; support PostgreSQL via `DATABASE_URL` later.
- Authentication: hashed passwords (Argon2 or bcrypt); secure **HttpOnly session cookie** with appropriate SameSite/Secure behavior; CSRF protection for mutating cookie-authenticated endpoints. Do not persist access tokens in localStorage. Protect all user data routes; enforce user ownership on receipt/image access.
- OCR: implement an adapter interface and a real locally runnable provider (EasyOCR and/or Tesseract, document setup). Include bounding boxes and OCR confidence where provider supports it. Gracefully handle OCR failure or missing binaries, without pretending parsing worked.
- Document parsing: modular receipt parser with rules/regex and explicit confidence indicators. Preserve raw OCR text, item lines, date, merchant, subtotal, tax, discount, total; allow manual correction and reconciliation. Don't imply every receipt can be parsed perfectly.
- Category inference: first deterministic/category keyword mapping; optional scikit-learn classifier if suitable labeled data exists. No fabricated “AI accuracy” metrics.
- Anomaly detection: transparent rules and robust statistics (e.g. median/MAD or IQR) first; optional Isolation Forest only once sufficient genuine transaction history exists. If not enough data, show “Insufficient history” rather than inventing an ML result.
- Product matcher: name normalization + RapidFuzz, consistent unit-size normalization and user review for uncertain matches.
- Files: local protected uploads folder in development, with size/type limits and random filenames. No unauthenticated public upload URLs. Design storage adapter for later S3 migration.
- Tests: pytest backend, React Testing Library/Vitest frontend, and at least one end-to-end smoke test if practical.

Suggested architecture: `React UI → typed API client → FastAPI (auth, receipts, investigations, analytics) → PostgreSQL/SQLite + protected receipt images`, with FastAPI orchestration calling OCR, receipt parser, categorizer, billing validator, price-history matcher, and anomaly evaluator.

## Routes and visual flow

Public routes:
- `/` **Landing** — closest recreation of supplied screenshot. Left: ornamental empty space, right: “YOUR RECEIPTS. REIMAGINED.” / “RECEIPT IQ” and succinct value proposition. Upper nav: HOME / HOW IT WORKS / FEATURES / CONTACT; header right also has **LOGIN**. Primary glass/outlined CTA: **SCAN SMARTER** navigates to login if signed out, dashboard if signed in. Add restrained below-the-fold sections for features and how-it-works, styled as a coherent extension rather than generic SaaS grids.
- `/login` **Login** — keep the exact same warm glass + floating orange spheres/rings world. Desktop two-part composition: editorial brand message left, compact frosted form panel center-right. Email, password, show/hide, remember-me if securely implemented, forgot-password UI only if actually supported, sign-in button, create-account link, field validation, helpful errors, mobile responsiveness. DO NOT introduce a black background or visually unrelated login template.
- `/register` **Create account** — same visual world, name/email/password/confirm, clear validation and working signup.

Authenticated routes (share ornamental background but prioritize usability; a persistent thin frosted navigation rail/topbar is acceptable):
- `/app` **Dashboard** — concise welcome, total spending, scanned receipts, anomalies needing review, savings/price-change insights; spend-over-time line chart, category breakdown chart, latest investigations and receipts; sensible loading/empty states.
- `/app/scan` **Upload & scan** — image/PDF upload, dropzone, preview, OCR progress, parsed item table, tax/discount/total values, field confidence, inline corrections, and explicit “Confirm and investigate” button. Do not silently save erroneous OCR as confirmed financial data.
- `/app/receipts` **Receipts library** — search/filter/sort, category, merchant/date/amount, processing state, duplicate indicators, action to open receipt.
- `/app/receipts/:id` **Interactive Receipt Investigation (HERO FEATURE)** — desktop split view: left original receipt image/PDF with clickable colored OCR bounding boxes, right frosted investigation report with tabs/panels: Summary / X-Ray / Price Memory / Expense Detective. Clicking an alert highlights the source line(s) and shows evidence: observed amount, expected/comparison, calculation, severity and confidence caveat. Include approve/correct/dismiss feedback states. Mobile uses tabs or accordion.
- `/app/insights` **Insights** — trends, categories, historical prices, comparisons with correct date/unit filters.
- `/app/reports` **Reports** — filter range and export a real CSV and printable PDF if feasible; never fake download links.
- `/app/settings` **Settings** — profile, currency default INR (₹), preferences, log out.

Use actual navigation, guarded routes, real API interactions, and a consistent design system. Seed/demo fixtures are allowed ONLY when visibly labeled as demo data and separated from actual saved receipts; provide a one-click “Load sample receipts” option if valuable for judging.

## Core data schema (may refine)

`users(id, name, email_unique, password_hash, created_at)`
`receipts(id, user_id, merchant, purchased_at, currency, receipt_number_nullable, subtotal, discount, tax, rounding, total, image_storage_key, image_sha256, raw_ocr_json, ocr_quality, status, created_at)`
`receipt_items(id, receipt_id, raw_name, normalized_name, quantity, unit, package_size, unit_price, line_total, category, ocr_box_json, field_confidence)`
`investigation_alerts(id, receipt_id, type, severity, headline, explanation, evidence_json, status_open_or_dismissed, created_at)`
`product_price_history(id, user_id, receipt_item_id, matched_product_key, normalized_unit_price, normalized_unit, matched_confidence, created_at)`
`feedback(id, user_id, alert_id, action, note, created_at)`

Use decimal-safe amounts (not floating point) and UTC-aware timestamps. Database and API must preserve the user's ownership and avoid exposing other users’ data.

## API contract (implement working equivalents)

Auth: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
Receipts: `POST /api/receipts/upload`, `GET /api/receipts`, `GET /api/receipts/{id}`, `GET /api/receipts/{id}/image`, `PATCH /api/receipts/{id}`, `POST /api/receipts/{id}/confirm`, `DELETE /api/receipts/{id}`.
Investigations: `GET /api/receipts/{id}/investigation`, `POST /api/alerts/{id}/feedback`.
Insights: `GET /api/analytics/overview`, `GET /api/analytics/categories`, `GET /api/analytics/trends`, `GET /api/analytics/price-history`.
Export: `GET /api/reports/export?format=csv&from=...&to=...` (add PDF if implemented).

Return informative typed errors and validation statuses. Never render randomly generated AI findings as real. Where confidence is low, require user confirmation. Preserve evidence provenance.

## Receipt intelligence rules

**X-Ray arithmetic**: Check whether the sum of line totals matches subtotal, then whether `subtotal - explicit_discounts + explicit_taxes + explicit_fees + rounding = displayed_total` within a configurable small rounding tolerance. Handle inclusive tax, discounts, service charges, and missing fields gracefully. If critical inputs are missing, show “Cannot verify” rather than “Fraud” or “Error”.

**Price Memory**: Compare only likely identical products and normalized quantity/units (e.g. ₹/kg, ₹/L, ₹/piece); show past price, current price, date, percent change, source receipts. For uncertain matching, flag “Possible product match — confirm”.

**Expense Detective**: Compare transaction value to user's sufficiently populated historical distribution, ideally merchant/category context, and show the actual baseline and explicit method. Duplicate detection combines SHA-256 file match and fuzzy `(merchant, date, total, item pattern)` for rephotographed receipts. Label uncertain duplicate suggestions as “possible duplicate”.

**One critical UX principle:** Clearly separate `OCR uncertain`, `billing discrepancy`, `price changed`, and `unusual spending`. They are different phenomena and must not be conflated.

## Visual design tokens & component requirements

Start with these approximate colors, then adjust while visually inspecting the screenshot:
- Canvas taupe `#B3A29B` / warm gray `#A99693`.
- Peach ambient light `#F4BE9C`.
- Orange sphere core `#E65A16` with light edges `#FFC57E`.
- Ring glow `#FF985C`.
- Text/off-white `#FFF9F5`.
- Frosted glass fill `rgba(255,255,255,0.055–0.12)`.
- Glass hairline border `rgba(255,255,255,0.22–0.45)`.

Create reusable design elements: `AmbientScene`, `Orb`, `GradientRing`, `GlassPanel`, `MinimalNav`, `GlassButton`, `GlassInput`, `MetricCard`, `AlertBadge`, `ReceiptViewer`, `EvidenceHighlight`, `InvestigationPanel`. Pay particular attention to typography, whitespace, cinematic shadow/blur, and subtle gradients.

On the landing page, the decorative scene must look **very close to the supplied image at first glance**, not like a dashboard mockup. On product screens, keep the exact aesthetic but allow more opaque frosted layers behind financial figures for legibility. Maintain WCAG-minded focus states, clear labels, and keyboard navigation even where the reference image is low contrast.

## Execution order — do the work, not just a plan

1. Inspect `design/reference.png` and repo structure. If existing code exists, adapt it without destructive changes; otherwise initialize the above monorepo with `frontend/` and `backend/`.
2. Create an explicit implementation plan and file tree, then actually implement the code in phases. Do not stop after writing a plan, scaffolding, or pretty static screens.
3. Implement global theme, ambient 3D CSS decorations, landing, login, register, responsive transitions.
4. Implement backend schema, migrations, security and authentication, then wire complete auth flow and route guards.
5. Build upload + OCR adapter + editable extraction and save/confirm workflow; then library and investigation detail.
6. Implement the three intelligence engines with deterministic test fixtures, evidence, and graceful insufficient-data states.
7. Implement dashboard charts, reports/export, settings, loading/error/empty states, and optionally sample-receipt seed script.
8. Run formatter/linter/typecheck/tests, fix errors, and provide specific commands to run both services.
9. If screenshot/browser tooling is available, compare desktop and mobile renders against `design/reference.png`; revise UI for closer composition/palette. Do not claim visual parity without checking.

## Non-negotiable acceptance criteria

- The first screen visibly resembles the exact supplied warm peach/taupe frosted-glass screenshot: frame, right-aligned hero, white micro-navigation, glossy orange spheres, glowing rings, and airy spacing.
- Login, registration, logout, and authenticated route protection work with persistent storage and secure password hashes.
- A user can upload a supported receipt image, review/adjust extraction, confirm it, and see the real record in library/dashboard.
- The investigation page shows the actual receipt and itemized explanation/evidence for a billing mismatch, price change, and/or contextual anomaly as justified by data.
- A deliberately inconsistent sample receipt produces a reproducible **billing discrepancy**; a consistent one does not. Missing information does not falsely create an anomaly.
- A repeated same-size product at a different price shows a reproducible price change; different pack sizes are normalized appropriately.
- No invented AI accuracy, fake fraud claims, decorative nonfunctional buttons, simulated auth masquerading as production, or hardcoded secrets.
- Full responsive design for mobile and desktop; accessible labels, keyboard functionality, and reduced-motion handling.
- A useful `README.md`, `.env.example`, migration instructions, data-seeding instructions, runnable tests, and an honest list of known limitations.

When you finish, summarize: implemented routes, architecture, tests run and results, what genuinely works, what is simulated/demo-only, and exact launch commands. If tool/dependency constraints block a feature, say so and ship a working fallback rather than falsely claiming completion.
