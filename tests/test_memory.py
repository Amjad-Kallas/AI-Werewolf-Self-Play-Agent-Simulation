import random

from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.nodes import make_resolution_node
from ai_werewolf.llm.prompts import describe_log
from ai_werewolf.llm.summary import RoundSummary, make_llm_summarizer


class _StructuredProxy:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return self.response


class FakeLLM:
    def __init__(self, response: RoundSummary):
        self.proxy = _StructuredProxy(response)

    def with_structured_output(self, schema):
        return self.proxy


def test_summarizer_only_sends_events_since_last_watermark():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.log = ["Round 1: X died.", "Round 1: Y accused Z.", "Round 2: Z was voted out."]
    game.summarized_through = 2
    game.summary = "Earlier: X died and Y accused Z."

    llm = FakeLLM(RoundSummary(summary="updated summary"))
    summarize = make_llm_summarizer(llm)
    result = summarize(game)

    assert result == "updated summary"
    human_prompt = llm.proxy.calls[0][-1].content
    assert "Earlier: X died and Y accused Z." in human_prompt  # the old summary itself is included

    new_events_section = human_prompt.split("New public events since then:\n", 1)[1]
    assert "Z was voted out" in new_events_section
    assert "X died" not in new_events_section  # already folded into the summary, not resent raw


def test_summarizer_is_a_no_op_when_nothing_new_happened():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.log = ["Round 1: X died."]
    game.summarized_through = 1
    game.summary = "Earlier: X died."

    llm = FakeLLM(RoundSummary(summary="should not be used"))
    summarize = make_llm_summarizer(llm)
    result = summarize(game)

    assert result == "Earlier: X died."
    assert llm.proxy.calls == []


def test_resolution_node_advances_summary_and_watermark():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.log = ["Round 1: X died."]

    node = make_resolution_node(lambda state: "compact summary")
    result = node({"game": game, "discussion": ["stale round data"]})

    assert result["game"].summary == "compact summary"
    assert result["game"].summarized_through == 1
    assert result["discussion"] == []


def test_describe_log_bounds_prompt_to_summary_plus_fresh_events():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.log = ["e1", "e2", "e3", "e4"]
    game.summarized_through = 2
    game.summary = "Earlier: e1 and e2 happened."

    text = describe_log(game)

    assert "Earlier: e1 and e2 happened." in text
    fresh_section = text.split("Recent events:\n", 1)[1]
    assert "e3" in fresh_section and "e4" in fresh_section
    assert "e1" not in fresh_section and "e2" not in fresh_section
