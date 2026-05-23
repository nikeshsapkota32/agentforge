from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.critic import critic_node
from app.agents.planner import planner_node
from app.agents.researcher import researcher_node
from app.agents.state import ResearchState
from app.agents.synthesizer import synthesizer_node
from app.config import settings


def _route_after_critic(state: ResearchState) -> Literal["synthesizer", "__end__"]:
    score = int(state.get("score") or 0)
    loops = int(state.get("loop_count") or 0)
    if score >= settings.min_passing_score:
        return "__end__"
    if loops >= settings.max_critic_loops:
        return "__end__"
    return "synthesizer"


@lru_cache(maxsize=1)
def build_graph():
    graph: StateGraph = StateGraph(ResearchState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("critic", critic_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "synthesizer")
    graph.add_edge("synthesizer", "critic")
    graph.add_conditional_edges(
        "critic",
        _route_after_critic,
        {"synthesizer": "synthesizer", "__end__": END},
    )

    return graph.compile()
