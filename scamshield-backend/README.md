# ScamShield AI – Backend

Flask + SQLAlchemy + SQLite modular monolith. It owns **auth, persistence, validation, QR decoding,
security, history, dashboard and reports**. It does **not** contain any ML: all classification and risk
scoring comes from the separate `ml/` project through a thin adapter.

## 1. Folder tree

```
backend/
├── app/
│   ├── __init__.py              # create_app() factory
│   ├── config.py                # env-driven config (Dev / Prod / Test)
│   ├── extensions.py            # db, jwt, cors, limiter, migrate
│   ├── models/                  # User, Scan, AnalysisResult, ThreatIndicator, Report,
│   │                            # TokenBlocklist, GmailConnection
│   ├── routes/                  # auth, analyze, scans, dashboard, reports, gmail, settings, system
│   ├── schemas/                 # Pydantic request validation
│   ├── services/
│   │   ├── ml_adapter.py        # the ONLY place that imports the ML project
│   │   ├── result_normalizer.py # ML <-> backend contract validation
│   │   ├── severity.py          # score -> LOW/MEDIUM/HIGH/CRITICAL
│   │   ├── analysis_service.py  # validate -> ML -> persist
│   │   ├── scan_service.py     # history + dashboard queries (always user-scoped)
│   │   ├── report_service.py    # JSON + PDF (ReportLab)
│   │   └── serializers.py       # API response shapes
│   ├── analyzers/               # qr_decoder (OpenCV), payload typing, UPI parser
│   ├── security/                # passwords, auth helpers, upload validation, headers
│   ├── errors/                  # exceptions + central handlers
│   ├── utils/  data/            # helpers, labelled demo-Gmail sample inputs
├── migrations/                  # created by `flask db init` (see §4)
├── instance/                    # SQLite file lives here (git-ignored)
├── tests/                       # pytest suite (TC01–TC17 + extras)
├── run.py  requirements.txt  requirements-dev.txt  pytest.ini  .env.example  README.md
```

## 2. Setup (Windows, PowerShell or CMD)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# put two random secrets into .env (SECRET_KEY, JWT_SECRET_KEY):
python -c "import secrets; print(secrets.token_urlsafe(48))"
python run.py
```

In **VS Code**: `Ctrl+Shift+P → Python: Select Interpreter → .venv`. API runs at `http://127.0.0.1:5000`.
Check: `http://127.0.0.1:5000/api/health`.

If `SECRET_KEY` / `JWT_SECRET_KEY` are missing in development, ephemeral ones are generated (tokens stop
working after a restart). In `APP_ENV=production` the app refuses to start without them.

## 3. Database initialisation

Tables are created automatically on startup (`AUTO_CREATE_DB=True`) in `instance/scamshield.db`.
To reset: stop the server and delete `instance\scamshield.db`.

## 4. Migrations (optional, recommended once the schema stabilises)

```powershell
$env:FLASK_APP = "run.py"
flask db init          # once
flask db migrate -m "initial schema"
flask db upgrade
```

## 5. Tests

```powershell
pip install -r requirements-dev.txt
python -m pytest
python -m pytest tests/test_qr.py -v
```

The suite uses an in-memory SQLite DB and a **test double** for the ML engine (`tests/fake_engine.py`).
The double is not a classifier and is never imported by app code; it exists so the backend plumbing
(validation, persistence, isolation, contracts) is tested independently of the ML project. The
"model unavailable" test (TC15) uses the *real* `MLEngine` pointed at modules that don't exist.

| Test | Where |
|---|---|
| TC01 legit email, TC02 phishing email, TC03 URL, TC06 spam, TC15 model unavailable | `tests/test_analyze.py` |
| TC04 legit QR, TC05 suspicious QR, TC07 UPI, TC08 invalid QR, TC09 oversized upload | `tests/test_qr.py`, `tests/unit/test_analyzers.py` |
| TC10 unauthorized, TC16 authentication, TC17 malformed | `tests/test_auth.py` |
| TC11 user isolation | `tests/test_isolation.py` |
| TC12 risk determinism | `tests/test_risk.py` |
| TC13 dashboard, TC14 pagination/filter/sort/search | `tests/test_dashboard_history.py` |
| reports, demo Gmail, settings, health | `tests/test_reports_gmail_settings.py` |

## 6. API

All responses: success → `{"success": true, ...}`; error → `{"success": false, "error": {"code", "message", "details?"}}`.
Protected endpoints need `Authorization: Bearer <access_token>`.

| Method & path | Auth | Notes |
|---|---|---|
| `POST /api/auth/register` | – | `{email, password, display_name?}` → 201 + token (auto-login) |
| `POST /api/auth/login` | – | `{email, password}` → `{access_token, token_type, expires_in, user}` |
| `POST /api/auth/logout` | ✔ | revokes the token (blocklist) |
| `GET /api/auth/me` | ✔ | current user |
| `GET /api/health` | – | `{status: ok\|degraded, database, ml:{available}}` |
| `GET /api/model/info` | ✔ | analyzer availability (+ `ML_INFO_FUNC` output) |
| `POST /api/analyze/email` | ✔ | `{sender?, subject?, body, url?, attachments?[{filename,content_type?,size?}], source?}` |
| `POST /api/analyze/text` | ✔ | `{text}` (≤ 50 000 chars) |
| `POST /api/analyze/url` | ✔ | `{url}` – syntactic validation only, never fetched |
| `POST /api/analyze/qr` | ✔ | multipart, field `file` (png/jpg/webp/bmp/gif, ≤ `QR_MAX_UPLOAD_BYTES`) |
| `GET /api/scans` | ✔ | `page, per_page(≤100), classification, scan_type, sort=created_at\|risk_score, order, q` |
| `GET /api/scans/<id>` | ✔ | full detail incl. `input`; other users' scans → **404** |
| `GET /api/dashboard/stats` | ✔ | computed from DB, per user |
| `GET /api/reports/<id>?format=json\|pdf` | ✔ | detailed report; PDF is `application/pdf` |
| `GET/PUT /api/settings` | ✔ | `display_name, theme, email_notifications` |
| `GET /api/gmail/status`, `POST /api/gmail/demo/connect`, `POST /api/gmail/disconnect`, `GET /api/gmail/messages` | ✔ | **Demo mode only** (see §9) |

Analysis response (HTTP 201):

```json
{ "success": true,
  "scan": {
    "id": "…", "scan_type": "email", "classification": "phishing",
    "risk_score": 91, "confidence": 0.96, "severity": "CRITICAL",
    "indicators": [{"type":"…","description":"…","severity":"HIGH","weight":0.3,"evidence":"…","source":"ml"}],
    "explanation": {}, "recommendation": "…", "created_at": "2026-10-08T10:00:00Z",
    "model_version": "…", "input_summary": "…", "details": {}, "input": {} } }
```

`details` – QR scans: `payload_type`, `decoded_payload`, `parsed` (UPI fields / Wi-Fi SSID), `filename`,
`safety_notice`. Email scans: `sender`, `subject`, `source`. `indicators[].source` is `"ml"` or `"backend"`;
backend indicators are always `severity: "INFO"`, `weight: null` and never change the score.

History list items are compact (no `indicators` / `explanation`, but `indicator_count`) and the response is
`{success, scans:[…], pagination:{page, per_page, total, pages, has_next, has_prev}}`.

Dashboard (flat, as specified, plus `success`):
`{success, total_scans, safe, spam, phishing, malicious, average_risk, by_scan_type, by_severity, trend[], recent_scans[]}`.

Error codes: `VALIDATION_ERROR 400`, `INVALID_IMAGE 400`, `AUTHENTICATION_ERROR/INVALID_TOKEN/TOKEN_EXPIRED/TOKEN_REVOKED/INVALID_CREDENTIALS 401`,
`FORBIDDEN 403`, `NOT_FOUND 404`, `EMAIL_IN_USE 409`, `FILE_TOO_LARGE 413`, `UNSUPPORTED_FILE_TYPE 415`,
`QR_NOT_DECODABLE 422`, `RATE_LIMITED 429`, `INTERNAL_ERROR/ANALYSIS_FAILED 500`, `NOT_IMPLEMENTED 501`,
`ML_INVALID_RESPONSE 502`, `MODEL_UNAVAILABLE 503`.

### Example requests (PowerShell)

```powershell
$base = "http://127.0.0.1:5000"
$r = Invoke-RestMethod "$base/api/auth/register" -Method Post -ContentType "application/json" `
     -Body '{"email":"me@example.com","password":"Str0ngPassw0rd"}'
$h = @{ Authorization = "Bearer $($r.access_token)" }

Invoke-RestMethod "$base/api/analyze/text" -Method Post -Headers $h -ContentType "application/json" `
     -Body '{"text":"You have won a free prize, claim now"}'

Invoke-RestMethod "$base/api/analyze/url" -Method Post -Headers $h -ContentType "application/json" `
     -Body '{"url":"http://paypal-verify.xyz/login"}'

curl.exe -H "Authorization: Bearer $($r.access_token)" -F "file=@C:\path\to\qr.png;type=image/png" "$base/api/analyze/qr"

Invoke-RestMethod "$base/api/scans?page=1&per_page=10&classification=phishing" -Headers $h
Invoke-RestMethod "$base/api/dashboard/stats" -Headers $h
curl.exe -H "Authorization: Bearer $($r.access_token)" -o report.pdf "$base/api/reports/<scan_id>?format=pdf"
```

## 7. ML integration

The adapter (`app/services/ml_adapter.py`) imports analyzers **lazily, once**, from `module:function` specs
in `.env`. Defaults:

```
ML_TEXT_ANALYZER=ml.inference.text_analyzer:analyze_text
ML_URL_ANALYZER=ml.inference.url_analyzer:analyze_url
ML_PAYLOAD_ANALYZER=ml.inference.qr_analyzer:analyze_payload
ML_INFO_FUNC=                       # optional: "ml.inference.info:get_model_info"
ML_PROJECT_PATH=                    # folder that CONTAINS the `ml` package
```

If the ML project uses other names, change only these lines. Default layout:

```
ScamShield/
├── backend/   (this project)
└── ml/        (ML project, containing ml/inference/…)
```

**Function contract** – the adapter passes only the optional keyword arguments a function declares
(`inspect.signature`), so simple signatures also work:

```python
analyze_text(text: str, *, context: dict | None = None) -> dict
analyze_url(url: str,  *, context: dict | None = None) -> dict
analyze_payload(payload: str, payload_type: str | None = None,
                parsed: dict | None = None, context: dict | None = None) -> dict
```

* Email scans call `analyze_text("Subject: …\n\n<body>", context={sender, subject, body, urls, attachments})`.
  If the request has an explicit `url`, `analyze_url` is also called and the **higher ML `risk_score` wins**
  (documented in `explanation.combination_policy`). To own this combination yourself, handle
  `context["urls"]` inside `analyze_text`.
* `payload_type` ∈ `url, upi, wifi, phone, sms, email, geo, contact, calendar, crypto, other_uri, text`.
  Wi-Fi passwords are redacted before the ML layer ever sees them. If `analyze_payload` doesn't exist,
  `url` payloads go to `analyze_url`, `text` payloads to `analyze_text`; other types return 503.

**Return value** (dict, dataclass or Pydantic model; common aliases such as `label`/`risk`/`probability` are accepted):

```python
{ "classification": "safe|spam|phishing|malicious",   # required
  "risk_score": 0..100,                               # required (rounded half-up to int)
  "confidence": 0.0..1.0,                             # required, NOT the same as risk
  "indicators": [{"type","description","severity","weight","evidence"} | "plain string"],
  "explanation": {...} | "text",
  "recommendation": "…",                              # a generic one is used if omitted
  "model_version": "…" }
```

Anything invalid → HTTP 502 `ML_INVALID_RESPONSE` and **nothing is stored**. Raise `FileNotFoundError` /
`ImportError` (or an exception whose class name contains `ModelNotLoaded`/`ModelUnavailable`) when the
artifact is missing → HTTP 503 `MODEL_UNAVAILABLE`. Any other exception → 500 `ANALYSIS_FAILED`
(details are logged, never returned).

**Where risk scoring lives:** entirely in the ML risk engine. The backend never computes or adjusts a
score; `app/services/severity.py` only maps the integer score to the band
(LOW 0–24, MEDIUM 25–49, HIGH 50–74, CRITICAL 75–100). A `severity` sent by ML is ignored.
Determinism of the score is therefore the ML engine's responsibility (no randomness, fixed seeds).

## 8. Security summary

* Passwords: PBKDF2-SHA256 (Werkzeug, salted), policy ≥ 8 chars with letter + digit; never logged or returned;
  uniform "Invalid email or password" + dummy hash for unknown emails.
* JWT access tokens (`JWT_ACCESS_TOKEN_MINUTES`), logout revokes the `jti` (table `token_blocklist`).
* Every Scan query filters on `user_id`; other users' scans/reports return 404. Tested.
* Pydantic validation on every body/query; `MAX_CONTENT_LENGTH` cap; per-field length caps.
* Uploads: extension + MIME + real format sniffing (Pillow) + size + pixel-count caps; processed **in memory**
  (nothing written to disk → no temp files, no path traversal); filename only kept after `secure_filename`.
* QR: decoded locally with OpenCV; payload is only classified as text. Nothing is opened, fetched, paid or connected.
  The frontend must also render `decoded_payload` as plain text (never `innerHTML`, never auto-navigate).
* URLs submitted for analysis are validated syntactically only; the backend never requests them.
* CORS allow-list (`CORS_ORIGINS`), security headers, `Cache-Control: no-store`, rate limits
  (`RATELIMIT_*`, in-memory storage → use Redis via `RATELIMIT_STORAGE_URI` if you run multiple workers).
* Central error handling; stack traces only in server logs. SQLAlchemy ORM only (parameterised queries,
  `LIKE` wildcards escaped).

## 9. Gmail

Only a clearly labelled **Demo Gmail Mode** exists: `POST /api/gmail/demo/connect`, then
`GET /api/gmail/messages` returns sample *inputs* (`is_demo: true`, `label: "DEMO MODE …"`, no verdicts).
The frontend sends a chosen message to `POST /api/analyze/email` (optionally `"source": "gmail_demo"`), so
the result still comes from the real ML engine. Real OAuth is **not implemented**
(`GET /api/gmail/oauth/start` → 501, `oauth_supported: false`); `GOOGLE_CLIENT_ID/SECRET` are reserved env
names only, nothing is stored in source.

## 10. Frontend integration (React/Vite)

1. **Remove** the mock auth, seeded scans, mock Gmail and mock classifier.
2. Vite proxy (avoids CORS in dev) – `vite.config.js`:
   ```js
   export default { server: { proxy: { "/api": "http://127.0.0.1:5000" } } }
   ```
   (or set `VITE_API_URL=http://127.0.0.1:5000` and add that origin to `CORS_ORIGINS`.)
3. One fetch wrapper:
   ```js
   let token = null;                                   // keep in memory (or sessionStorage)
   export async function api(path, { method = "GET", json, form, raw } = {}) {
     const headers = token ? { Authorization: `Bearer ${token}` } : {};
     if (json) headers["Content-Type"] = "application/json";
     const res = await fetch(`/api${path}`, { method, headers, body: json ? JSON.stringify(json) : form });
     if (raw) return res;                              // e.g. PDF -> res.blob()
     const data = await res.json();
     if (!data.success) throw Object.assign(new Error(data.error.message), data.error);
     return data;
   }
   // login:   const d = await api("/auth/login", {method:"POST", json:{email,password}}); token = d.access_token;
   // QR:      const f = new FormData(); f.append("file", file); await api("/analyze/qr", {method:"POST", form:f});
   // history: await api("/scans?page=1&per_page=20&classification=phishing")
   ```
   On a 401 with `TOKEN_EXPIRED`/`TOKEN_REVOKED`, clear the token and send the user to login.
4. Mapping: `scan.risk_score` (0–100) drives gauges; `scan.confidence` (0–1) is shown separately;
   `scan.severity` drives colour; `/dashboard/stats` fields feed the charts directly.
5. Show a visible **"Demo Gmail Mode"** badge whenever `is_demo` is true.
6. PDF: `const r = await api(`/reports/${id}?format=pdf`, {raw:true}); const url = URL.createObjectURL(await r.blob());`

## 11. Known limitations

* PDF reports use ReportLab's built-in Latin fonts: non-Latin text (e.g. Tamil/Hindi) will not render in the PDF
  (the JSON report is unaffected). Register a Unicode TTF in `report_service.py` if you need it.
* Real Gmail OAuth is not implemented (by design, see §9).
* Rate-limit counters are per-process (in-memory) unless you configure a shared storage URI.
