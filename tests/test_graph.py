import random

from ai_werewolf.engine.roles import Team
from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.graph.nodes import route_after_night, route_after_vote
from ai_werewolf.llm.schemas import NightAction, Statement, VoteAction


class FakeAgent:
    """Duck-typed stand-in for LLMAgent: deterministic, no network calls."""

    def __init__(self, night_target_fn, vote_fn):
        self.night_target_fn = night_target_fn
        self.vote_fn = vote_fn
        self.statement_calls = 0

    def choose_night_target(self, state, wolf):
        return NightAction(target_id=self.night_target_fn(state, wolf), reasoning="scripted")

    def make_statement(self, state, player, discussion):
        self.statement_calls += 1
        return Statement(speech=f"{player.name} shares a thought.", reasoning="scripted")

    def choose_vote(self, state, player, discussion):
        return VoteAction(target_id=self.vote_fn(state, player), reasoning="scripted")


def first_villager_id(state, wolf):
    return next(p.id for p in state.alive_by_team(Team.VILLAGERS))


def vote_out_the_werewolf(werewolf_id):
    def vote_fn(state, voter):
        if voter.id != werewolf_id:
            return werewolf_id
        return next(p.id for p in state.alive_players() if p.id != voter.id)

    return vote_fn


def test_werewolves_win_immediately_at_parity_skipping_discussion_and_vote():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=lambda *_: 0)
    app = build_graph(agent, rng=random.Random(0))

    result = app.invoke({"game": game, "discussion": []})
    final = result["game"]

    assert final.winner == Team.WEREWOLVES
    assert agent.statement_calls == 0  # discussion never reached


def test_full_loop_reaches_villager_win_via_discussion_and_vote():
    game = new_game(["a", "b", "c", "d", "e"], num_werewolves=1, rng=random.Random(1))
    werewolf_id = next(p.id for p in game.players if p.role.value == "werewolf")

    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=vote_out_the_werewolf(werewolf_id))
    app = build_graph(agent, rng=random.Random(0))

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 50})
    final = result["game"]

    assert final.winner == Team.VILLAGERS
    assert not final.get(werewolf_id).alive
    assert agent.statement_calls > 0  # discussion phase ran


def test_route_after_night_ends_when_winner_set():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.winner = Team.WEREWOLVES
    assert route_after_night({"game": game, "discussion": []}) == "end"


def test_route_after_night_continues_when_no_winner():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    assert route_after_night({"game": game, "discussion": []}) == "discussion"


def test_route_after_vote_ends_when_winner_set():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.winner = Team.VILLAGERS
    assert route_after_vote({"game": game, "discussion": []}) == "end"
