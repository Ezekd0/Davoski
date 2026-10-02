# AI-CTDRS

A working academic Security Operations Center demonstration, built with React 19, TypeScript, Tailwind CSS 4, Chart.js, Django REST Framework, JWT authentication, and SQLite. PostgreSQL is supported through `DATABASE_URL`.

The workspace was empty at inspection: no existing app, usable Git repository, dependency manifests, database, model artifacts, datasets, or additional project documentation were present. This implementation follows the supplied master prompt.

**Analysis is deterministic demo logic, not trained AI.** Scores are illustrative, explanations describe rule triggers rather than SHAP/LIME, and response actions never modify a firewall, network interface, or host. These limitations are visible throughout the interface. Detection accuracy is not reported because no evaluated model exists.

## Start locally

Prerequisites: Python 3.12–3.14, Node 22+, npm, and internet access for the initial dependency install.

```bash
./scripts/dev.sh
```

This installs dependencies, applies migrations, creates idempotent demo fixtures, and starts both servers. It does not overwrite existing user passwords or existing threat data. `Ctrl+C` stops the servers. Optional: copy `backend/.env.example` to `backend/.env`; the development script loads it and explicitly enables development mode. Production uses platform environment variables, not this script.

Or run manually from the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
npm ci --prefix frontend
DEBUG=true .venv/bin/python backend/manage.py migrate
DEBUG=true .venv/bin/python backend/manage.py seed_demo
DEBUG=true .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
# In a second terminal:
npm run dev --prefix frontend
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000/api/
- Health: http://localhost:8000/api/health/
- Admin demo account: `admin` / `DemoSecure!2026`
- Analyst demo account: `analyst` / `DemoSecure!2026`

`DEMO_PASSWORD` can override the local seed password when creating the accounts. The admin account has seeded records; the analyst account starts empty. Public registration creates analysts only. Demo seeding is blocked when `DEBUG=false`.

## Two-minute demonstration

1. Sign in as `admin` and inspect dashboard metrics, activity chart, categories, and recent alerts.
2. Open **Threat analysis**, choose **DDoS**, and click **Analyze traffic**.
3. Show the Critical severity, 97.4% illustrative confidence, rule explanation, network features, and automatically created incident.
4. Click **Investigate & respond**, select **Block source**, and record the simulated response.
5. Open the linked incident, change status to **Resolved**, add a resolution note, and save.
6. Open **Alerts** and acknowledge an event; open **Audit history** to see the recorded analysis and response.
7. Return to the dashboard / analytics to see updated persisted data. Reload a details page to demonstrate persistence.

## Implemented features

- Login, registration, profile, logout, protected routes, rotating refresh JWTs, role-aware navigation and API authorization.
- SOC dashboard backed by aggregate API queries; seven-day activity, category and severity charts; status analytics.
- Validated network-flow submission, seven repeatable scenarios, stored results and transparent explanations.
- Threat history with search, severity, status and type filters; details, features, linked incidents and audit timeline.
- Automatic high-risk incident creation (configurable), manual grouping of multiple threats, self-assignment, status changes, required resolution notes, incident timeline.
- Alerts from detection, incident changes and simulated responses; acknowledgement and configurable API polling.
- Six safe simulated response actions, persistent audit events, user listing for admins, stored analyst settings.
- Loading, empty, retry, connection failure, session expiry and UI error states; mobile navigation and layouts.

## Architecture

```text
frontend/src/
  components/   Shared controls, charts, layout, result presentation
  hooks/        Authentication and API resource loading
  pages/        Dashboard, analysis, threats, incidents, alerts, workspace
  services/     API transport, token refresh, centralized demo input fixtures
  types.ts      Typed API contracts
backend/
  config/       Environment-driven Django settings, URLs, WSGI
  soc/models.py Persistent threats, incidents, alerts, audit events, preferences
  soc/serializers.py Input validation and output contracts
  soc/views.py  Authenticated REST API and dashboard aggregation
  soc/services/ Classifier adapter boundary and transactional workflow
  soc/migrations/ Versioned schema
```

Demo data is seeded in the backend through the same analysis service used by the application. The browser reads actual API data; it does not silently fall back to fake records when the backend is unavailable. Alerts use polling, not WebSockets. No datasets are bundled.

## API

All endpoints except health, registration, login, and token refresh require `Authorization: Bearer <access-token>`.

| Endpoint | Methods | Purpose |
| --- | --- | --- |
| `/api/health/` | GET | Service and database health |
| `/api/auth/login/` | POST | Username/password to access/refresh tokens |
| `/api/auth/register/` | POST | Create analyst account |
| `/api/auth/refresh/` | POST | Rotate refresh token |
| `/api/auth/profile/` | GET | Current user and role |
| `/api/auth/logout/` | POST | Blacklist supplied refresh token |
| `/api/threats/` | GET | Threat list; `search`, `severity`, `status`, `threat_type` |
| `/api/threats/analyze/` | POST | Analyze a validated flow and persist workflow |
| `/api/threats/{id}/` | GET | Threat details |
| `/api/threats/{id}/respond/` | POST | Record simulated response |
| `/api/incidents/` | GET, POST | List / create a grouped incident |
| `/api/incidents/{id}/` | GET, PATCH | Read / update incident and assignment |
| `/api/alerts/` | GET | Workspace alerts |
| `/api/alerts/{id}/acknowledge/` | POST | Acknowledge alert and record audit event |
| `/api/analytics/dashboard/` | GET | Aggregates, timeline and recent activity |
| `/api/audit/` | GET | Audit events |
| `/api/settings/` | GET, PATCH | Analyst preferences |
| `/api/users/` | GET | Admin-only active account listing |

Lists return JSON arrays. Object endpoints return JSON objects. Validation/authentication errors use `{ "error": ..., "status": <http status> }`. Passwords use Django hashing. Analysts see their own records; admins can read/respond to all records, with the action attributed to the admin and retained under the record owner. Manual incident creation groups the current user's threats only.

`backend/requirements-lock.txt` records the exact backend versions tested with Python 3.14.3.

## Verify

```bash
DEBUG=true .venv/bin/python backend/manage.py test soc
DEBUG=true .venv/bin/python backend/manage.py check
DEBUG=true .venv/bin/python backend/manage.py makemigrations --check --dry-run
npm run build --prefix frontend
# With both servers running:
cd frontend
PLAYWRIGHT_BROWSERS_PATH=/tmp/ai-ctdrs-browsers npx playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/ai-ctdrs-browsers npm run test:e2e
```

Browser tests modify demo data by creating analyses, incidents, and a unique test analyst. Use a disposable database when repeatedly testing. `E2E_BASE_URL` changes the tested frontend URL. The tests assume the documented local demo password.

## Deployment

Frontend: `netlify.toml`, Netlify `_redirects`, and `frontend/vercel.json` provide build and SPA routing configuration. Set `VITE_API_URL=https://YOUR-BACKEND/api` **at build time**. No secrets belong in frontend environment variables.

Backend: `render.yaml` defines a Gunicorn service, database, migration step and health check. Set `ALLOWED_HOSTS` to backend hostnames (no scheme) and `CORS_ALLOWED_ORIGINS` to exact frontend origins (with scheme, no trailing slash). The blueprint generates a secret and sets `DEBUG=false`. `TRUST_PROXY=true` is for Render's trusted HTTPS proxy; do not enable it on an untrusted proxy. PostgreSQL migrations use the same schema as SQLite.

Do not run demo seeding on a public production deployment. Create production accounts with registration and promote an administrator through an authorized Django shell. HTTPS, a strong secret, correct CORS/hosts, and a persistent database are required. Backend settings refuse production startup with the development fallback secret. Use `python manage.py check --deploy` with production variables. Set `PYTHON_VERSION` to a supported Python 3.12+ runtime if your host does not offer 3.14.

No hosting accounts or deployment credentials were supplied; the application is prepared for deployment but has not been published. PostgreSQL support is configured; local validation uses SQLite.

## Replacing demo analysis

Replace `soc/services/classifier.py:classify()` with a trained Random Forest / XGBoost prediction adapter that returns the same typed fields. Supply artifacts, preprocessing/feature order, class mapping, model version, evaluated metrics, and genuine SHAP/LIME output. Add model contract tests. Update engine/score/method labels only after integrating and validating the real model. Live traffic ingestion and executable response integrations are outside this MVP.
