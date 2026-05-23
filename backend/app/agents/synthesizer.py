from __future__ import annotations

import json

from app.agents.llm import call_json
from app.agents.prompts import SYNTHESIZER_SYSTEM
from app.agents.state import ResearchState, finish_step, new_step


async def synthesizer_node(state: ResearchState) -> ResearchState:
    step = new_step("synthesizer")
    user = (
        f"Query: {state['query']}\n\n"
        f"Plan:\n{json.dumps(state.get('plan') or [], indent=2)}\n\n"
        f"Findings:\n{json.dumps(state.get('findings') or [], indent=2)}\n\n"
        f"Prior critique (if any): {state.get('critique') or '(none)'}\n"
    )
    parsed, tin, tout = await call_json(SYNTHESIZER_SYSTEM, user, temperature=0.3)
    answer = (parsed.get("answer") or "").strip()
    citations = parsed.get("citations") or []
    if not isinstance(citations, list):
        citations = []

    step["thought"] = "Drafted answer."
    step["tokens_in"] = tin
    step["tokens_out"] = tout
    finish_step(step)

    steps = list(state.get("steps") or [])
    steps.append(step)
    return {"draft_answer": answer, "answer": answer, "citations": citations, "steps": steps}
