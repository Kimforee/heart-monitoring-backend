# Heart Monitoring Backend (Django)

Small backend to manage users, patients, and heart-rate readings. Built with Django, Django REST Framework and Simple JWT.

## Quick setup (development)

```bash
# clone
git clone <your-repo-url>
cd heart_monitoring

# virtualenv
python -m venv .venv
source .venv/bin/activate

# install
pip install -r requirements.txt

# run migrations + create superuser
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# run server
python manage.py runserver
````

## API docs (auto-generated)

* JSON schema: `GET /api/schema/`
* Swagger UI: `GET /api/docs/swagger/`
* Redoc: `GET /api/docs/redoc/`

Open them in a browser while the dev server is running.

## Useful endpoints (summary)

### Auth

* `POST /api/accounts/register/` — register (body: `username`, `password`, `email`, `phone` optional)
* `POST /api/auth/token/` — obtain JWT (`username`, `password`) → returns `access` & `refresh`
* `POST /api/auth/token/refresh/` — refresh token

### User

* `GET /api/accounts/me/` — current user (requires `Authorization: Bearer <access>`)

### Patients & Heart Rates

* `GET/POST /api/patients/patients/` — list/create patients
* `GET/PUT/PATCH/DELETE /api/patients/patients/{id}/` — patient detail
* `GET/POST /api/patients/heartrates/` — list/create readings
* `GET/PUT/PATCH/DELETE /api/patients/heartrates/{id}/` — heart rate detail

Filtering for heartrates:

* `?patient={patient_id}&device_id={device_id}&start={YYYY-MM-DD|ISO}&end={YYYY-MM-DD|ISO}`
* Pagination: `?limit=25&offset=0`

## Example curl flows

1. Register:

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@example.com","password":"supersecret123"}'
```

2. Obtain token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"supersecret123"}'
# use returned access token for subsequent requests
```

3. Create patient (authenticated):

```bash
curl -X POST http://127.0.0.1:8000/api/patients/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"first_name":"Bob","last_name":"B"}'
```

4. Create heart rate reading:

```bash
curl -X POST http://127.0.0.1:8000/api/patients/heartrates/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"patient": 1, "bpm": 78, "recorded_at":"2025-09-20T10:00:00Z"}'
```

## Testing

Run tests:

```bash
python manage.py test
# or using pytest (if installed)
pytest -q
```

CI: a GitHub Actions workflow at `.github/workflows/ci.yml` will run `makemigrations`, `migrate`, and `test`.

## Assumptions & decisions

* Custom user model `accounts.CustomUser` exists to allow future extension (`is_clinician`, `phone`).
* `Patient.owner` is optional; if null, patient is "unowned" and only staff/clinician can operate on it.
* Simple JWT used for stateless auth.
* SQLite for dev, easy to switch to Postgres by changing `DATABASES`.
* Basic permission model: owner, clinician, or staff can create/update/delete; others only read their own patients/readings.
* Heart rate `bpm` validation: sane bounds (20–300). `recorded_at` cannot be far in the future.

## Next steps (Part 4 preview)

* Add nicer OpenAPI annotations (examples, response examples).
* Add Postman collection file or exported HTTP collection JSON.
* Add production-ready config: Dockerfile, gunicorn, env-based settings, Postgres in production, static files handling, and deployment instructions.
* Increase test coverage and add code coverage reporting.

````

---

# 7) Postman / HTTP collection (curl snippets already provided)

If you want a Postman collection JSON I can generate one — say so and I’ll produce an exportable JSON you can import.

---

# 8) What I did not run (and what you should run locally)

I provided tests and CI config, but I didn't run them in your environment. Run locally:

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py test
````

If any tests fail due to timezone behavior or slight serializer differences, tweak the test tolerances (the code includes small flexibility points). Tell me test failures and I'll help fix them.

---

# 9) Suggestions / improvements for production

* Replace SQLite with Postgres and configure DB credentials via env vars.
* Use `django-environ` or `python-decouple` for environment configuration.
* Add request/response logging and Sentry for error monitoring.
* Add throttling (DRF throttling classes) for rate-limiting device ingestion endpoints.
* Consider batching heart rate ingestion (bulk create) for device uploads.
* Add API key or client credentials for devices to authenticate ingestion (device-level auth), separate from user JWTs.
* Add background jobs for heavy processing (Celery + Redis) if you process streams or compute metrics.

---

## Deployment (Docker + Postgres)

1. Copy .env.example -> .env and update values.
2. Build and run:
   docker compose up --build -d
3. Check logs:
   docker compose logs -f web
4. Admin: http://localhost:8000/admin

Notes:
- The service runs with Gunicorn behind optional Nginx.
- For production, run behind HTTPS (use Let's Encrypt / certbot) and put nginx in front.

deploy locally with Docker

# 1) Prepare env
cp .env.example .env
# edit the .env (DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS)

# 2) Build + run
docker compose up --build -d

# 3) Tail logs
docker compose logs -f web

# 4) Create superuser (if not created by env)
docker compose exec web python manage.py createsuperuser

# 5) Stop
docker compose down


# Wrap-up checklist (what Part 3 added)

* [x] OpenAPI schema + Swagger & Redoc
* [x] Expanded unit tests for validation, filtering, pagination, permissions
* [x] GitHub Actions workflow for tests
* [x] README updated with API docs, curl examples, testing & CI instructions
* [x] Guidance for Part 4 (production + deployment + docs polishing)

---
