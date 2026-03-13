# Crypto Price Service

A small backend service that **fetches BTC and ETH index prices from [Deribit](https://www.deribit.com/)** every minute, stores them in **PostgreSQL**, and exposes them via a **FastAPI** REST API.

---

## Table of contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick start (Docker)](#quick-start-docker)
- [Project structure](#project-structure)
- [Configuration](#configuration)
- [Local development](#local-development)
- [API reference](#api-reference)
- [Architecture](#architecture)
- [Design decisions](#design-decisions)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Scheduled fetch**: Every minute, a Celery beat task calls Deribit’s public API for `btc_usd` and `eth_usd` **index prices** and saves them to the database.
- **Storage**: One table `prices` with `id`, `ticker`, `price`, and `timestamp` (UNIX milliseconds).
- **REST API** (all GET, required query param `ticker`):
  - List all stored prices for a ticker (optional time range).
  - Get the latest price for a ticker.
  - Get prices for a ticker filtered by date range (UNIX timestamps).

Stack: **FastAPI**, **PostgreSQL** (async via SQLAlchemy + asyncpg), **Celery** + **Redis**, **aiohttp** for the Deribit client.

---

## Prerequisites

- **Docker** and **Docker Compose** (for the recommended run), or
- **Python 3.11+**, **PostgreSQL**, and **Redis** for local runs.

---

## Quick start (Docker)

From the project root:

```bash
docker compose up --build
```

Then:

- **API**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Containers:

| Service   | Role                          | Port(s)   |
|----------|-------------------------------|-----------|
| `app`    | FastAPI                       | 8000      |
| `worker` | Celery worker + beat          | —         |
| `db`     | PostgreSQL 16                 | 5432      |
| `redis`  | Celery broker & result backend| 6379      |

After a minute or two, the worker will have stored the first prices; try:

```bash
curl "http://localhost:8000/prices?ticker=btc_usd"
curl "http://localhost:8000/prices/latest?ticker=btc_usd"
```

---

## Project structure

```
crypto-price_service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Settings (env / .env), get_settings()
│   ├── database.py        # create_engine_and_session_factory(), init_db()
│   ├── main.py            # FastAPI app, routes, DI
│   ├── models.py          # SQLAlchemy Price model
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── deribit_client.py  # DeribitClient (aiohttp), fetch_prices_for_indices()
│   ├── celery_app.py      # Celery app, beat schedule, fetch_and_store_prices task
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── price_repository.py   # PriceRepository (DB access)
│   └── services/
│       ├── __init__.py
│       └── price_service.py      # PriceService (uses repository)
├── tests/
│   └── test_api.py        # API tests (pytest, pytest-asyncio)
├── .env.example           # (optional) Example env vars
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Configuration

Variables can be set in the environment or in a `.env` file in the project root.

| Variable | Description | Default (Docker) |
|----------|-------------|------------------|
| `DB_HOST` | PostgreSQL host | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | DB user | `crypto_user` |
| `DB_PASSWORD` | DB password | `crypto_password` |
| `DB_NAME` | Database name | `crypto_db` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL for results | `redis://redis:6379/1` |
| `DERIBIT_BASE_URL` | Deribit API base | `https://www.deribit.com/api/v2` |

For local runs (no Docker), set `DB_HOST=localhost` and ensure Redis is reachable (e.g. `CELERY_BROKER_URL=redis://localhost:6379/0`).

---

## Local development

1. **Create and activate a virtualenv**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Run PostgreSQL and Redis** (e.g. via Docker or system install). Set `DB_*` and `CELERY_*` in `.env` or the environment.

3. **Start the API**

   ```bash
   uvicorn app.main:app --reload
   ```

4. **Start the Celery worker with beat** (separate terminal)

   ```bash
   celery -A app.celery_app.celery_app worker -B --loglevel=info
   ```

5. Open [http://localhost:8000/docs](http://localhost:8000/docs) and call the endpoints.

---

## API reference

Base URL: `http://localhost:8000` (or your host).

All price endpoints require the query parameter **`ticker`** (e.g. `btc_usd`, `eth_usd`). Timestamps are in **UNIX milliseconds**.

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check. Returns `{"status": "ok"}`. |

### Prices

| Method | Path | Query params | Description |
|--------|------|--------------|-------------|
| GET | `/prices` | `ticker` (required), `start_ts`, `end_ts` (optional, UNIX ms) | List all stored prices for the ticker, optionally in the given time range. |
| GET | `/prices/latest` | `ticker` (required) | Latest stored price for the ticker. **404** if none. |
| GET | `/prices/by-date` | `ticker` (required), `start_ts`, `end_ts` (optional, UNIX ms) | Same as `/prices` with date filter; semantic alias for “filter by date”. |

**Example responses**

- `/prices?ticker=btc_usd` → `[{"id": 1, "ticker": "btc_usd", "price": 97500.5, "timestamp": 1710345600000}, ...]`
- `/prices/latest?ticker=eth_usd` → `{"ticker": "eth_usd", "price": 3500.25, "timestamp": 1710345660000}`

**Examples**

```bash
curl "http://localhost:8000/prices?ticker=btc_usd"
curl "http://localhost:8000/prices?ticker=btc_usd&start_ts=1710345600000&end_ts=1710432000000"
curl "http://localhost:8000/prices/latest?ticker=eth_usd"
curl "http://localhost:8000/prices/by-date?ticker=btc_usd&start_ts=1710345600000&end_ts=1710432000000"
```

---

## Architecture

- **API layer** (`main.py`): HTTP only — validates query params, calls `PriceService`, returns JSON. Depends on `get_db` and `get_price_service`.
- **Service layer** (`PriceService`): Application logic for “get all / latest / by range”. Depends only on `PriceRepository`.
- **Repository layer** (`PriceRepository`): Single place for DB access to the `prices` table (find/add). Used by both the API (via service) and the Celery task.
- **Deribit client** (`DeribitClient`): aiohttp-based client for Deribit’s public API. Used only by the Celery task.
- **Config / DB**: No module-level engine or session in the web app; settings via `get_settings()`, engine and session factory created at startup and stored in `app.state`. The Celery worker uses a process-scoped session factory (lazy-initialized).

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI + async SQLAlchemy (asyncpg)** | Async request handling and non-blocking DB access; good fit for I/O-bound API. |
| **Celery + Redis** | Reliable periodic task (every minute); easy to scale workers and inspect tasks. |
| **aiohttp for Deribit** | Async HTTP client; fetch multiple indices in parallel with `asyncio.gather`. |
| **Single `prices` table** | Simple schema; easy to add columns (e.g. source, type) later. |
| **UNIX timestamp in milliseconds** | Matches common exchange APIs; no extra conversion; simple range filters. |
| **Repository + Service** | Clear separation: repository = data access, service = use cases; testable and no business logic in routes. |
| **No global engine/session in web app** | Engine and session factory live in `app.state`; config via `get_settings()` to avoid hidden globals. |

---

## Testing

- **Location**: `tests/test_api.py`
- **Scope**: Health check; “latest price not found” (404); insert a price and assert `/prices/latest` returns it.

**Run tests**

```bash
# With local Python
pytest
# or
python -m pytest tests/ -v
```

On Windows, if `python` is not in PATH, try:

```bash
py -m pytest tests/ -v
```

Or activate the project venv and run:

```bash
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

**Run tests in Docker** (no local Python needed; ensure stack is up):

```bash
docker compose run --rm app python -m pytest tests/ -v
```

Set `DB_*` (and optionally `CELERY_*`) so the test run can connect to the same DB you use for development (e.g. via `.env` or Docker Compose env).

---

## Deployment

### Docker

- **Production-style**: Use the same `docker-compose.yml`; consider binding only needed ports, using secrets for `DB_PASSWORD`, and running the app as a non-root user.
- **Scaling**: Run more `worker` replicas if you need higher throughput for tasks.

### GitLab

1. Create a new project on GitLab.
2. In the project root:

   ```bash
   git init
   git remote add origin <your-gitlab-repo-url>
   git add .
   git commit -m "Initial commit: Crypto Price Service"
   git push -u origin main
   ```

3. Optionally add `.gitlab-ci.yml` to run tests and build the Docker image on push.

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| **Empty list from `/prices?ticker=btc_usd`** | Wait 1–2 minutes after starting the worker so the first Celery run completes. Check worker logs: `docker logs crypto-price-worker` (or your worker container name). |
| **`python` not found (Windows)** | Use `py -m pytest` / `py -m uvicorn`, or activate `.venv` and use `pytest` / `uvicorn` from there. |
| **DB connection errors** | Verify `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`. For Docker, use service name `db` as host; locally use `localhost`. |
| **Celery task not running** | Ensure Redis is up and `CELERY_BROKER_URL` is correct. Worker must be started with beat: `celery -A app.celery_app.celery_app worker -B`. |
| **Swagger/ReDoc blank** | Ensure the app container is running and not crashing (check `docker logs crypto-price-app`). |

---

## License

This project is provided as-is for evaluation and learning. Use and modify as needed.
