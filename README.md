# AgentForge

Autonomous Multi-Agent Research Assistant powered by LangGraph, OpenAI, and Pinecone.

## Architecture

```
frontend/     Next.js 14 + TypeScript + Tailwind
backend/      FastAPI + LangGraph + LangChain
infrastructure/  Docker Compose + Nginx
.github/      CI/CD workflows
```

## Agents

- **Planner** — decomposes query into subtasks
- **Researcher** — executes tools per subtask, stores findings to Pinecone
- **Synthesizer** — merges findings into draft answer
- **Critic** — scores answer, loops back if quality < threshold

## Tools (12+)

Web search, arXiv retrieval, sandboxed code execution, SQL query, file read, Wikipedia, news, calculator, URL scrape, PDF extract, image analysis, structured data extraction.

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, LangGraph, LangChain, OpenAI |
| Memory | Pinecone (text-embedding-3-large) |
| DB | PostgreSQL 16 |
| Cache | Redis 7 |
| Observability | LangSmith |
| Auth | JWT RS256 |
| Deploy | Docker, Nginx, GitHub Actions |

## Quick Start

```bash
# Clone
git clone https://github.com/nikeshsapkota32/agentforge.git
cd agentforge

# Copy env
cp .env.example .env
# Fill in: OPENAI_API_KEY, PINECONE_API_KEY, LANGSMITH_API_KEY

# Run
docker compose up --build
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
API docs: http://localhost:8000/docs
