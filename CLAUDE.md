# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Junior Tracker is a FastAPI backend for tracking infant development events (sleep, feeding, activities, etc.). Telegram messages sent to a bot are parsed and stored as structured events. There are two runtime processes: an HTTP API server and a background worker consuming from RabbitMQ.

## Commands

```bash
# Run API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run background worker
python worker.py

# Run all tests
pytest tests/

# Run a single test file
pytest tests/src/services/test_tg_msg_parser.py

# Run tests matching a pattern
pytest tests/ -k "test_parse_sleep"

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Start only Postgres (for local dev)
docker-compose up postgres
```

## Architecture

### Request Flow
```
HTTP Client → FastAPI (main.py) → Router (src/api/) → Service (src/services/) → Repository (src/repositories/) → PostgreSQL
Telegram Bot → RabbitMQ → Worker (worker.py) → TgMsgParser → EventService → EventRepository → PostgreSQL
```

### Layer Responsibilities

**API layer** (`src/api/`): Route definitions only. Two auth mechanisms:
- `current_active_user` — JWT-based user auth (fastapi-users) for human clients
- `get_api_key` — API key auth for device endpoints (`/api/device/`)

**Service layer** (`src/services/`): Business logic, access control (verifies user owns child before operations), timezone handling.

**Repository layer** (`src/repositories/`): Database queries. `BaseRepository[ModelType]` provides generic CRUD. `EventRepository.update_or_create()` upserts by `(tg_message_id, child_id, event_type_id)`. `ChartRepository` uses raw SQL with `text()` for complex time-series queries.

### Core Data Model

- **Child** — the tracked infant; has a `tg_chat_id` (Telegram) and `timezone`; many-to-many with User
- **EventType** — configurable categories per child; has `keywords` (ARRAY), `format` (range/metric/described/plain), optional `parent_id` for start/end pairs
- **Event** — the core entity; linked to Child and EventType; stores `occurred_at` (UTC), `volume`, `description`, `tg_message_id`

### Telegram Message Parsing (`src/services/tg_msg_parser.py`)

Parses free-form Telegram text into `EventCreateInternal` objects. EventType formats:
- `range` — start/end events (e.g., sleep start/end)
- `metric` — numeric value (e.g., formula volume)
- `described` — text description
- `plain` — keyword presence only

Parser uses keyword matching + regex. Timestamps from Telegram are in the child's local timezone and converted to UTC before storage.

### Worker (`worker.py`)

Connects to RabbitMQ, consumes messages, extracts `{chat_id, timestamp, text, message_id}`, looks up child by `tg_chat_id`, fetches that child's event types, parses, and upserts events. Runs under Supervisor in Docker alongside Uvicorn.

## Configuration

Settings are loaded from `src/.env` via pydantic-settings (`src/config.py`). Key vars:
- `DB_URL` — `postgresql+asyncpg://...`
- `RABBIT_URL` — `amqp://...`
- `QUEUE_NAME` — RabbitMQ queue name
- `SENTRY_DSN` — optional; Sentry only initializes when set

Tests use `tests/.env.test` with a separate test database (port 54321).

## Testing

Tests use `pytest-asyncio`. `tests/conftest.py` sets up a session-scoped schema and per-test connection with rollback — no test data persists between tests. The test DB must exist before running tests. No mocking of the database; tests hit real PostgreSQL.

## Python environment

This project uses a virtual environment located at `.venv/`.
Always activate it before running any Python, Poetry, or pytest commands:

source .venv/bin/activate && <command>

Or run executables directly via:
- `.venv/bin/python`
- `.venv/bin/poetry`
- `.venv/bin/pytest`

Never use bare `python`, `poetry`, or `pytest` without activating the venv first.
