# AgentForge Backend

FastAPI + LangGraph + PostgreSQL + Redis + Pinecone.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # macOS/Linux

pip install -e ".[dev]"
cp .env.example .env

# generate JWT keys
mkdir keys
openssl genrsa -out keys/jwt_private.pem 2048
openssl rsa -in keys/jwt_private.pem -pubout -out keys/jwt_public.pem

# run migrations (requires Postgres up)
alembic upgrade head

# start dev server
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs
