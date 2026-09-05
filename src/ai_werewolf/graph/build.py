import random

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ai_werewolf.llm.agent import LLMAgent

from .nodes import (
    make_discussion_node,
    make_night_node,
    make_vote_node,
    resolution_node,
    route_after_night,
    route_after_vote,
)
from .state import GraphState


def build_graph(agent: LLMAgent, rng: random.Random | None = None) -> CompiledStateGraph:
    """Wire the Night -> Discussion -> Vote -> Resolution state machine."""
    rng = rng or random.Random()

    graph = StateGraph(GraphState)
    graph.add_node("night", make_night_node(agent, rng))
    graph.add_node("discussion", make_discussion_node(agent))
    graph.add_node("vote", make_vote_node(agent))
    graph.add_node("resolution", resolution_node)

    graph.add_edge(START, "night")
    graph.add_conditional_edges("night", route_after_night, {"discussion": "discussion", "end": END})
    graph.add_edge("discussion", "vote")
    graph.add_conditional_edges("vote", route_after_vote, {"resolution": "resolution", "end": END})
    graph.add_edge("resolution", "night")

    return graph.compile()
