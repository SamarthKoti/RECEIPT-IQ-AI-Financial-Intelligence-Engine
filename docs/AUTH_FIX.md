# Authentication origin / CSRF fix

## Root cause

The original `.env` set `FRONTEND_ORIGIN=http://127.0.0.1:5173`. FastAPI CORS used that one origin, and the request guard compared every mutation's Origin header against that same single string. A frontend at `http://127.0.0.1:5174` therefore received 403 even though it correctly sent cookies and `X-Receipt-IQ: 1`. The hostname `localhost` was also a different, rejected origin. The generic error incorrectly combined both possible causes.

There was no generated CSRF token in the previous implementation: `X-Receipt-IQ: 1` was a fixed anti-CSRF custom header, backed by origin validation and SameSite cookies.

## Changes

- `backend/app/config.py`: validated explicit `FRONTEND_ORIGINS` list; legacy single-origin fallback; reject wildcard/path/credential origin configurations.
- `backend/app/main.py`: common origin allowlist for CORS and mutations; CORS wraps validation errors; `GET /api/auth/csrf`; specific origin/token errors; require cookie/header token equality in addition to the existing custom header.
- `backend/app/security.py`: 32-byte random CSRF issuance, host-only HttpOnly/SameSite cookie, constant-time validation; reuse valid tokens for multiple tabs.
- `frontend/src/api.ts`: acquire CSRF token before mutations; send `X-CSRF-Token`, `X-Receipt-IQ`, and cookies; share concurrent bootstrap requests. Same-origin `/api` continues to use the existing Vite proxy to port 8000.
- `.env`, `.env.example`: allow exactly the four requested local development origins.
- `backend/tests/conftest.py`: initialize CSRF cookies/headers in test clients.
- `backend/tests/test_auth_origins.py`, `backend/tests/test_config.py`: origin, token, cookie, registration, persistence, CORS, and configuration regression tests.
- `README.md`, `docs/TEST_RESULTS.md`, this report: updated setup and verification notes.

No UI/UX, CSS, routing, password hashing, session expiration, ownership restrictions, or database schema changed. The existing Vite proxy was already correct and did not need modification.

## Browser verification

Separate synthetic local QA accounts were created through the actual forms. Each completed registration → authenticated dashboard → logout → password login → authenticated dashboard:

| Frontend origin | Register | Login | Dashboard |
| --- | --- | --- | --- |
| `http://127.0.0.1:5174` | Passed | Passed | Passed |
| `http://localhost:5174` | Passed | Passed | Passed |
| `http://localhost:5173` | Passed | Passed | Passed |
| `http://127.0.0.1:5173` | Passed | Passed | Passed |

The authenticated session on 127.0.0.1:5174 survived a full reload. All QA sessions were logged out after testing. The dashboard screenshot is `screenshots/auth-fixed-5174.jpg`. These accounts contain no user receipts.

Automated tests independently assert that registration inserts the user with an Argon2-verifiable hash, unauthenticated requests are rejected after logout, and re-login restores protected analytics access. Allowed-origin preflights succeed with credential support. Foreign origins, missing cookies, malformed/missing tokens, and another client's token remain rejected.

Final results: **36 tests passed**, one existing Starlette/httpx test-client deprecation warning; TypeScript compilation and Vite production build passed.
