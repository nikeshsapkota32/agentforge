from __future__ import annotations

from app.agents.llm import call_json
from app.agents.prompts import PLANNER_SYSTEM
from app.agents.state import ResearchState, finish_step, new_step


async def planner_node(state: ResearchState) -> ResearchState:
    step = new_step("planner")
    parsed, tin, tout = await call_json(PLANNER_SYSTEM, state["query"])
    plan = parsed.get("plan") or []
    if not isinstance(plan, list):
        plan = []

    step["thought"] = "Plan:\n" + "\n".join(f"- {p}" for p in plan)
    step["tokens_in"] = tin
    step["tokens_out"] = tout
    finish_step(step)

    steps = list(state.get("steps") or [])
    steps.append(step)
    return {"plan": plan, "steps": steps}
