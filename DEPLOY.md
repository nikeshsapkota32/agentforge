# AgentForge — free-tier deployment

This deploys AgentForge to the public internet at **zero recurring cost** and **zero LLM token spend** by using:

| Layer | Provider | Free tier (May 2026) |
|---|---|---|
| LLM | **Groq** (Llama 3.3 70B) | Generous RPM / RPD limit, no credit card |
| Postgres | **Neon** | 0.5 GB storage, autoscaling compute |
| Redis | **Upstash** | 10,000 commands/day |
| Backend | **Render** (Web Service) | 750 hrs/month, sleeps after 15 min idle |
| Frontend | **Vercel** | Hobby plan, unlimited static, 100 GB bandwidth |
| Vector memory | *Disabled* (Pinecone optional) | — |

Total bill: **$0/month**. The only catch is Render's free tier sleeps after ~15 min of inactivity, so the first request after idle takes ~30 s to wake.

---

## 0 · Prereqs

- A GitHub account that owns the `agentforge` repo (you already do)
- OpenSSL on your laptop for the one-time JWT key pair

```bash
cd backend
mkdir -p keys
openssl genrsa -out keys/jwt_private.pem 2048
openssl rsa -in keys/jwt_private.pem -pubout -out keys/jwt_public.pem
```

Keep both files handy — you'll paste their contents into Render in step 5.

---

## 1 · Groq (free LLM)

1. Sign up at <https://console.groq.com>.
2. Create an API key. Copy it. Format: `gsk_...`.
3. Verify the free model is available: **`llama-3.3-70b-versatile`**.

No credit card. No monthly cap on the key, just per-minute RPM caps.

---

## 2 · Neon (free Postgres)

1. Sign up at <https://neon.tech>.
2. Create a project. Pick a region close to Render (e.g. `us-east-2`).
3. From the dashboard, copy the **Pooled connection** URL.
4. Rewrite it for `asyncpg`:

   Neon gives you:
   ```
   postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

   Convert to:
   ```
   postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?ssl=require
   ```
   (Two changes: `postgresql` → `postgresql+asyncpg`, and `sslmode=require` → `ssl=require`.)

Save that — it becomes `DATABASE_URL` on Render.

---

## 3 · Upstash (free Redis)

1. Sign up at <https://upstash.com>.
2. Create a Redis database. Pick a region near Render.
3. Copy the **TLS Redis URL** (starts with `rediss://...`).

Save that — it becomes `REDIS_URL` on Render.

---

## 4 · Render (backend)

The repo already ships a `render.yaml` Blueprint, so Render builds the backend Docker image and provisions a free Web Service.

1. Sign up at <https://render.com>.
2. **New → Blueprint** → connect your GitHub `agentforge` repo → Render reads `render.yaml`.
3. It will create one service: `agentforge-backend`. **Don't deploy yet** — fill in env vars first.
4. In the service's **Environment** tab, set each `sync: false` value:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | the Neon URL from step 2 |
   | `REDIS_URL` | the Upstash URL from step 3 |
   | `LLM_API_KEY` | your Groq key from step 1 |
   | `JWT_PRIVATE_KEY` | paste full contents of `keys/jwt_private.pem` (newlines as `\n` or use Render's multi-line editor) |
   | `JWT_PUBLIC_KEY` | paste full contents of `keys/jwt_public.pem` |
   | `CORS_ORIGINS` | `["https://<your-vercel-app>.vercel.app"]` — leave a placeholder for now, update after step 5 |

5. Click **Manual Deploy → Deploy latest commit**. First build ≈ 4 min.
6. Once healthy, Render gives you a public URL like `https://agentforge-backend.onrender.com`. Copy it — you'll need it next.

The container runs `alembic upgrade head` before serving, so the Neon schema is created automatically on first boot.

---

## 5 · Vercel (frontend)

1. Sign up at <https://vercel.com> with GitHub.
2. **Add New → Project** → select the `agentforge` repo.
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL` = your Render backend URL from step 4
4. Deploy. First build ≈ 2 min.
5. Vercel gives you a URL like `https://agentforge.vercel.app`.
6. **Go back to Render** and update `CORS_ORIGINS` to include this URL:
   ```
   ["https://agentforge.vercel.app"]
   ```
   (or multiple, e.g. `["https://agentforge.vercel.app","https://agentforge-git-main-you.vercel.app"]`).
   Save → Render restarts.

---

## 6 · Smoke test

1. Open your Vercel URL.
2. Click **Get started**, create an account.
3. You should land on `/research` with the four-agent UI.
4. Ask: *"Compare LangGraph vs CrewAI for production multi-agent systems."*
5. Within a few seconds you should see Planner → Researcher (with tool-call badges) → Synthesizer → Critic stream in, then a final answer with score.

If the first request is slow, Render is waking up — subsequent requests are instant for ~15 minutes of activity.

---

## Troubleshooting

**`CORS error` in the browser console.** Render's `CORS_ORIGINS` doesn't match your Vercel URL. JSON-list, quoted, exact match (no trailing slash).

**`websocket: bad handshake` or SSE drops after 30 s.** Vercel's Edge Network is fine; Render's free plan is fine for SSE. Most likely cause is the backend exiting due to an exception — check Render → Logs.

**`401 invalid token`.** The PEM env vars didn't paste cleanly. Re-copy from disk; Render's editor preserves newlines if you use the multi-line input.

**`alembic.util.exc.CommandError`.** Your `DATABASE_URL` is the wrong dialect. Must start with `postgresql+asyncpg://`, not `postgresql://`. Must use `ssl=require`, not `sslmode=require`.

**LLM returns garbage / 401.** Groq's free tier may rate-limit. Check Render logs for `429` on the upstream call. Wait a minute and retry.

**`vector memory disabled` in tool output.** Expected on the free stack. Pinecone is optional; the agents work without it.

---

## Upgrade paths (later, optional)

| Want | Pay | How |
|---|---|---|
| Always-on backend | $7/mo | Render Starter plan |
| OpenAI GPT-4o instead of Groq | usage | Set `LLM_PROVIDER=openai` + `LLM_API_KEY=sk-...` + `LLM_MODEL=gpt-4o` |
| Working memory | usage | Set `OPENAI_API_KEY` (or `EMBEDDINGS_API_KEY`) + `PINECONE_API_KEY` |
| Real web search | $0 | SerpAPI free tier 100 req/mo: set `SERPAPI_API_KEY` |
| LangSmith traces | $0 | Free hobby project: set `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY=...` |
