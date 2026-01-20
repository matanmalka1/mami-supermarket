# Mami Supermarket Backend

Flask + PostgreSQL backend for a real-inventory, multi-branch supermarket with tokenized payments and audit-first workflows.

```text
| \/ | (_) | |
| \ / | \__ _ _ __ _ | |
| |\/| |/ _` | '_ ` _ \ |
| | | | (_| | | | | | |
|_| |_|\__,_|_| |_| |_|
```

## What this backend delivers
- Real per-branch inventory (warehouse + stores) with soft-delete everywhere
- Checkout with pessimistic locking, tokenized card payments, and idempotency keys
- Cart, catalog, and orders with ownership checks and RBAC across customer/employee/manager/admin
- Ops workflows: picking → missing → ready, plus stock-request approvals
- Full audit trail (old/new values) written inside the same DB transaction

## Tech stack
- Python 3.11+, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Limiter, Flask-CORS
- PostgreSQL + Alembic migrations
- SQLAlchemy ORM + Pydantic DTOs
- httpx for payment provider calls
- pytest + pytest-cov, ruff for linting

## Directory map
```text
backend/
├── app/                 # Flask app factory, blueprints, services, models, schemas
├── alembic/             # DB migrations
├── docs/api.md          # HTTP contract reference
├── scripts/             # gunicorn entry + seed data
├── tests/               # pytest suite for auth, checkout, ops, etc.
├── run.py               # local dev server (debug)
├── wsgi.py              # production entrypoint
├── requirements.txt     # Python deps
└── .env.example         # env template
```

## Quickstart (local)
```bash
# 1) Python + virtualenv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure env
cp .env.example .env
# Set DATABASE_URL, JWT_SECRET_KEY, DELIVERY_SOURCE_BRANCH_ID, CORS_ALLOWED_ORIGINS

# 4) Migrate + seed
alembic upgrade head
python scripts/seed.py    # warehouse + delivery slots for dev

# 5) Run
python run.py             # http://localhost:5000
# Production: ./scripts/gunicorn.sh
```

## Environment
| Key | Required | Purpose |
| --- | :------: | ------- |
| `DATABASE_URL` | ✓ | PostgreSQL URI for SQLAlchemy |
| `JWT_SECRET_KEY` | ✓ | Secret for access/refresh tokens |
| `DELIVERY_SOURCE_BRANCH_ID` | ✓ | Branch ID used as the delivery warehouse |
| `CORS_ALLOWED_ORIGINS` | ✓ | Allowed origins for the frontend |
| `DELIVERY_MIN_TOTAL` |  | Minimum cart total before free delivery (default 150) |
| `DELIVERY_FEE_UNDER_MIN` |  | Delivery fee when under minimum (default 30) |
| `DEFAULT_LIMIT` / `MAX_LIMIT` |  | Pagination defaults for list endpoints |

## Core flows to know
- Checkout confirm locks inventory rows (`SELECT ... FOR UPDATE`), charges tokenized payment, writes audit rows, then commits; any failure rolls back before payment capture is marked.
- Ownership middleware returns 404 when a user hits a resource they don’t own.
- Rate limiting is enabled globally (`200/day`, `50/hour`) except for health endpoints.
- Delivery orders always deduct from the warehouse branch ID provided in env.

## Developing & testing
- Run tests: `pytest`
- Lint/format: `ruff check .`
- Regenerate DB after schema changes: add an Alembic migration under `alembic/versions/` and run `alembic upgrade head`.
- Seed data can be rerun; duplicate inserts are ignored when constraints block them.

## API surface
- Routes are namespaced under `/api/v1/*` (auth, catalog, cart, checkout, orders, ops, admin, audit).
- Detailed request/response samples live in `docs/api.md`.

## Deployment notes
- Use `wsgi.py` or `scripts/gunicorn.sh` behind a process manager (systemd/supervisor) with a PostgreSQL instance reachable by `DATABASE_URL`.
- Ensure `DELIVERY_SOURCE_BRANCH_ID` exists in the DB before serving traffic (validated on startup per request).
