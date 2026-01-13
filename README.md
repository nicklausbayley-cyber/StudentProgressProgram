# Student Risk Platform (Starter)

This is a **starter** FastAPI + PostgreSQL + SQLAlchemy (async) project that implements the core rules engine:

- Attendance < 94% → Attendance risk
- Growth status BELOW → Academic risk
- Credits earned < expected credits for grade → Graduation risk
- 2+ risk flags → Intervention required
- Status: 0=ON_TRACK, 1=WATCH, 2=AT_RISK, 3=HIGH_RISK

## Quick start (Docker)
1. Install Docker Desktop
2. From this folder:

```bash
cp .env.example .env
docker compose up --build
```

Then open:
- API docs: http://localhost:8000/docs

## Local dev (no Docker)
1. Create a venv
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Set env vars (example)
```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/student_risk"
export JWT_SECRET="change-me"
```

3. Run migrations
```bash
alembic upgrade head
```

4. Run the API
```bash
uvicorn app.main:app --reload
```

## Default Roles
- admin
- counselor
- student

## CSV Imports (MVP)
- `POST /imports/students_csv`
- `POST /imports/metrics_csv`

CSV templates are in `sample_data/`.

> This is a base you can extend (SIS integrations, vendor APIs, richer graduation rules, dashboards).
