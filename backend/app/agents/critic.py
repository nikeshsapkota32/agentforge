from __future__ import annotations

from app.agents.llm import call_json
from app.agents.prompts import CRITIC_SYSTEM
from app.agents.state import ResearchState, finish_step, new_step


async def critic_node(state: ResearchState) -> ResearchState:
    step = new_step("critic")
    user = (
        f"Query: {state['query']}\n\n"
        f"Drafted answer:\n{state.get('answer') or ''}\n\n"
        f"Citations: {state.get('citations') or []}\n"
    )
    parsed, tin, tout = await call_json(CRITIC_SYSTEM, user, temperature=0.0)
    score_raw = parsed.get("score", 0)
    try:
        score = max(1, min(10, int(score_raw)))
    except (TypeError, ValueError):
        score = 0
    critique = parsed.get("critique") or ""

    step["thought"] = f"Score: {score}/10. {critique}"
    step["tokens_in"] = tin
    step["tokens_out"] = tout
    finish_step(step)

    steps = list(state.get("steps") or [])
    steps.append(step)
    loop_count = int(state.get("loop_count") or 0) + 1
    return {"score": score, "critique": critique, "loop_count": loop_count, "steps": steps}
