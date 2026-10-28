---
title: "05 Backend Frameworks and Tools"
part: "01"
chapter: "05"
topic: backend-frameworks
versions: [python, uv]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.djangoproject.com/en/dev/faq/install/
  - https://fastapi.tiangolo.com/
---

# 05 Backend Frameworks and Tools

## Purpose

Per-project Python backend stacks. Frameworks and drivers are never installed into the system Python: each project gets its own uv environment (chapter 03), so versions live in that project's `pyproject.toml` and `uv.lock`. Current releases on 2026-10-28: Django 6.1.2 (5.2.18 is the LTS, supported to April 2028), Django REST Framework 3.18.3, FastAPI 0.162.0, Starlette 1.10.0, Flask 3.1.3, Celery 5.6.3 (5.7 is in release candidate), gunicorn 26.x, uvicorn 0.54.0, pydantic 2.14.1, SQLAlchemy 2.1.6. All of the groups below resolve as binary wheels on Python 3.14 (`verified-in-cloud`).

## 5.1 Django + Django REST Framework

```bash
uv add 'django>=5.2,<5.3' djangorestframework django-cors-headers django-filter \
       django-celery-beat django-celery-results whitenoise
uv add --dev django-debug-toolbar factory-boy

uv run django-admin startproject myproject && cd myproject
uv run python manage.py startapp api
```

The `<5.3` pin selects the 5.2 LTS. An unpinned `django` resolves to **6.0.9**, not 6.1, because `django-celery-beat` 2.9.0 requires `Django<6.1` (forcing `django>=6.1` fails to resolve); Django 6.0 is a non-LTS series. A Django 6.0.9 + DRF 3.18.3 + celery-beat 2.9.0 project passed `manage.py check` on Python 3.14.10 (`verified-in-cloud`).

## 5.2 FastAPI + Uvicorn + Gunicorn

```bash
uv add fastapi "uvicorn[standard]" gunicorn uvicorn-worker python-multipart
uv add --dev httpx   # For testing

# Dev:  uv run uvicorn main:app --reload
# Prod: uv run gunicorn main:app -w 4 -k uvicorn_worker.UvicornWorker --bind 127.0.0.1:8000
#       (or without gunicorn: uv run uvicorn main:app --workers 4 --host 127.0.0.1)
```

## 5.3 Flask

```bash
uv add flask flask-sqlalchemy flask-migrate flask-cors
```

## 5.4 Celery + Redis

```bash
uv add celery redis
```

```python
# celery_app.py
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def process_document(doc_id):
    pass

# Run: uv run celery -A celery_app worker --loglevel=info
# Beat: uv run celery -A celery_app beat -l info
```

## 5.5 WebSockets & Async

```bash
uv add channels channels-redis websockets   # WebSockets
uv add aiohttp httpx asyncpg aiofiles       # Async HTTP/DB/IO
```

| Library | Purpose |
|---|---|
| `httpx` | Modern async/sync HTTP client with HTTP/2 |
| `aiohttp` | Async HTTP client/server |
| `asyncpg` | Fast async PostgreSQL driver |
| `aiofiles` | Async file I/O |
