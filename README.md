# AgentForge

Autonomous multi-agent research assistant. A user submits a query; four LangGraph agents — **Planner → Researcher → Synthesizer → Critic** — collaborate to produce a grounded, cited answer streamed back to the browser over SSE. The Critic scores every draft and loops back to the Synthesizer until the answer crosses a quality threshold.

## Architecture

```
frontend/         Next.js 16, TypeScript, Tailwind v4 — UI + SSE client
backend/          FastAPI, LangGraph 0.2, SQLAlchemy async — agents + API
infrastructure/   docker-compose + nginx reverse proxy
.github/          ci, cd, security workflows
```

## Agents

- **Planner** — decomposes the query into 3–6 concrete sub-questions
- **Researcher** — calls tools to gather evidence and citations
- **Synthesizer** — writes a grounded answer with inline `[n]` citations
- **Critic** — scores 1–10 across groundedness, completeness, clarity; routes back to Synthesizer if `score < MIN_PASSING_SCORE` and `loop_count < MAX_CRITIC_LOOPS`

## Tools (12)

`web_search` (SerpAPI → DuckDuckGo fallback) · `web_fetch` · `wikipedia` · `arxiv` · `pdf_read` · `python_exec` (sandboxed) · `calculator` · `vector_search` · `vector_write` · `summarize` · `translate` · `datetime`

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, LangGraph 0.2, LangChain, OpenAI GPT-4o |
| Vector memory | Pinecone serverless (`text-embedding-3-large`) |
| Database | PostgreSQL 16 (SQLAlchemy 2 async + Alembic) |
| Cache / RL | Redis 7 (token-bucket via Lua) |
| Observability | LangSmith |
| Auth | JWT RS256 (15-min access + 7-day refresh with rotation) |
| Deploy | Docker, Nginx, GitHub Actions |

## API

```
POST   /api/v1/auth/signup     -> { accessToken, refreshToken }
POST   /api/v1/auth/login      -> { accessToken, refreshToken }
POST   /api/v1/auth/refresh    -> { accessToken, refreshToken }  (rotates)
DELETE /api/v1/auth/logout
GET    /api/v1/auth/me

POST   /api/v1/research        -> SSE: agent_step | tool_call | done | error
GET    /api/v1/sessions
GET    /api/v1/sessions/{id}
```

## Deploy free

Full walkthrough in [`DEPLOY.md`](./DEPLOY.md). TL;DR — Vercel (frontend) + Render (backend) + Neon (Postgres) + Upstash (Redis) + Groq (LLM) all on free tiers, total cost $0/month, no LLM token spend.

## Quick start (Docker)

```bash
git clone https://github.com/nikeshsapkota32/agentforge.git
cd agentforge

cp .env.example .env
# Fill OPENAI_API_KEY (required), PINECONE_API_KEY, LANGSMITH_API_KEY, SERPAPI_API_KEY (all optional)

cd infrastructure
docker compose up --build
```

App: <http://localhost> · Backend API: <http://localhost:8000> · Docs: <http://localhost:8000/docs>

## Local dev

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
mkdir keys
openssl genrsa -out keys/jwt_private.pem 2048
openssl rsa -in keys/jwt_private.pem -pubout -out keys/jwt_public.pem
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Security

- Bcrypt password hashing, RS256 JWTs, sha256-hashed refresh tokens with rotation
- Redis token-bucket rate limiting (per-user and per-IP)
- Security headers middleware (X-Frame-Options, HSTS over HTTPS, Permissions-Policy)
- Per-request UUIDs in logs; 500s sanitized before leaving the server
- `python_exec` runs in an isolated subprocess (`-I -S -B`) with POSIX `RLIMIT_CPU`/`RLIMIT_AS`/`RLIMIT_NOFILE`/`RLIMIT_FSIZE`, 8 s wall-clock timeout, 16 KB output cap
- CI runs gitleaks, bandit, and Trivy with SARIF upload to the Security tab
