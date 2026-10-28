---
title: "05 Backend Frameworks and Tools"
part: "01"
chapter: "05"
topic: backend-frameworks
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 05 Backend Frameworks and Tools


## 5.1 Django + Django REST Framework

```bash
uv add django djangorestframework django-cors-headers django-filter \
       django-celery-beat django-celery-results whitenoise
uv add --dev django-debug-toolbar factory-boy

uv run django-admin startproject myproject && cd myproject
uv run python manage.py startapp api
```

## 5.2 FastAPI + Uvicorn + Gunicorn

```bash
uv add fastapi "uvicorn[standard]" gunicorn python-multipart
uv add --dev httpx   # For testing

# Dev:  uv run uvicorn main:app --reload
# Prod: uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
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
