import random
from typing import Callable

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ai_werewolf.engine.models import GameState
from ai_werewolf.llm.agent import LLMAgent
from ai_werewolf.llm.summary import make_llm_summarizer

from .nodes import (
    make_discussion_node,
    make_night_node,
    make_resolution_node,
    make_vote_node,
    route_after_night,
    route_after_vote,
)
from .state import GraphState


def build_graph(
    agent: LLMAgent,
    rng: random.Random | None = None,
    summarize: Callable[[GameState], str] | None = None,
) -> CompiledStateGraph:
    """Wire the Night -> Discussion -> Vote -> Resolution state machine.

    `summarize` folds each round's new events into a rolling summary so
    prompts stay bounded in a long game; defaults to an LLM-backed summarizer
    using `agent`'s own model.
    """
    rng = rng or random.Random()
    summarize = summarize or make_llm_summarizer(agent.llm)

    graph = StateGraph(GraphState)
    graph.add_node("night", make_night_node(agent, rng))
    graph.add_node("discussion", make_discussion_node(agent))
    graph.add_node("vote", make_vote_node(agent))
    graph.add_node("resolution", make_resolution_node(summarize))

    graph.add_edge(START, "night")
    graph.add_conditional_edges("night", route_after_night, {"discussion": "discussion", "end": END})
    graph.add_edge("discussion", "vote")
    graph.add_conditional_edges("vote", route_after_vote, {"resolution": "resolution", "end": END})
    graph.add_edge("resolution", "night")

    return graph.compile()
