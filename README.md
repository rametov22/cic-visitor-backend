# CIC Visitor

Django/DRF backend on the production-oriented structure from
[`igorkhaylov/django-template`](https://github.com/igorkhaylov/django-template):
Python 3.13, Django 5.2, PostgreSQL, Redis, Celery, Nginx, Docker Compose,
`uv`, Ruff and reproducible registry-based deployment.

The existing `iccu` models, migrations, API routes and Django `auth.User` are
preserved. The template's custom user model is intentionally not enabled because
changing `AUTH_USER_MODEL` after a production database already exists is unsafe.

## Local development

```bash
cp .env.example .env
# Fill every CHANGE_ME.
make dev up
make dev run
```

The service is available on `http://localhost:${APP_PORT}`. The development
backend container stays idle until `make dev run` is started in the foreground.

Uploaded files are always stored in the `django-media` Docker volume. Static
files use `django-static`; Nginx serves both volumes.

## Common commands

```bash
make dev test
make dev lint
make dev makemigrations
make dev migrate
make dev createsuperuser

make up                 # local production-like build
make prod deploy        # server: pull image and start
make prod logs backend
make prod dump media    # PostgreSQL + all media
make prod restore dumps/<timestamp>
```

Never run `docker compose down -v` on a server containing production data.

## Environment migration

The old environment names map as follows:

| Old | New |
| --- | --- |
| `DEBUG` / `PRODUCTION` | `ENVIRONMENT=dev|stage|prod` |
| `SECRET_KEY` | `DJANGO_SECRET_KEY` |
| fixed image in Compose | `BACKEND_IMAGE` |
| local media directory/volume | `django-media` Docker volume |

Keep the current secret key during the server migration so active sessions remain
valid. In `stage` and `prod`, it must contain at least 50 characters.

Production runs behind an external edge proxy that terminates TLS and sets
`X-Forwarded-Proto`. The in-stack Nginx deliberately does not overwrite that
header.

## Health checks

`/healthcheck/` remains the shallow Docker healthcheck. `/deep-health/` is the
protected monitoring endpoint and concurrently checks `backend`, `db`, `redis`,
`celery` and `celery-beat`. Configure a separate random key in `.env`:

```dotenv
DEEP_HEALTH_API_KEY=<output of openssl rand -hex 32>
```

Call it through HTTPS in production:

```bash
KEY='<same value as DEEP_HEALTH_API_KEY in .env>'
curl -sS -H "X-API-Key: ${KEY}" https://api.visitor.iccu.uz/deep-health/
unset KEY
```

Missing or invalid credentials return HTTP 401. An authorized request always
returns HTTP 200; health is carried by the JSON `status` fields. Celery beat
writes a shared Redis heartbeat, so its liveness is checked independently from
the worker.

See [docs/server-migration.md](docs/server-migration.md) for the staged database
and media migration runbook.

## CI/CD variables

GitHub Actions needs `REGISTRY_USER` and `REGISTRY_PASSWORD`. Each GitHub
Environment (`prod`/`dev`) also needs `SERVER_HOST`, `SERVER_USER`,
`SERVER_PORT`, `SERVER_SSH_KEY`, `SERVER_FINGERPRINT` and `PROJECT_PATH`.
Set the repository variable `AUTO_DEPLOY=true` only after a manual deployment
has succeeded; otherwise deployment remains manual.

Pushes to `refactor/django-template` publish both an immutable `sha-<full-sha>`
tag and the moving `refactor-django-template` tag. The server uses the moving
tag for routine `make prod deploy`; keep SHA tags for an exact rollback.
