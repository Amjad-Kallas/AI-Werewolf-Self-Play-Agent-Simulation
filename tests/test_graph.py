import random

from ai_werewolf.engine.roles import Team
from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.graph.nodes import route_after_night, route_after_vote
from ai_werewolf.llm.schemas import DoctorAction, NightAction, SeerAction, Statement, VoteAction


class FakeAgent:
    """Duck-typed stand-in for LLMAgent: deterministic, no network calls."""

    def __init__(self, night_target_fn, vote_fn, doctor_fn=None, seer_fn=None):
        self.night_target_fn = night_target_fn
        self.vote_fn = vote_fn
        self.doctor_fn = doctor_fn
        self.seer_fn = seer_fn
        self.statement_calls = 0

    def choose_night_target(self, state, wolf):
        return NightAction(target_id=self.night_target_fn(state, wolf), reasoning="scripted")

    def choose_doctor_protect(self, state, doctor):
        target_id = self.doctor_fn(state, doctor) if self.doctor_fn else doctor.id
        return DoctorAction(target_id=target_id, reasoning="scripted")

    def choose_seer_target(self, state, seer):
        if self.seer_fn:
            target_id = self.seer_fn(state, seer)
        else:
            target_id = next(p.id for p in state.alive_players() if p.id != seer.id)
        return SeerAction(target_id=target_id, reasoning="scripted")

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


def fake_summarize(state):
    """No-network stand-in for the LLM summarizer used in these graph tests."""
    return f"(scripted summary through {len(state.log)} events)"


def test_werewolves_win_immediately_at_parity_skipping_discussion_and_vote():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=lambda *_: 0)
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []})
    final = result["game"]

    assert final.winner == Team.WEREWOLVES
    assert agent.statement_calls == 0  # discussion never reached


def test_full_loop_reaches_villager_win_via_discussion_and_vote():
    game = new_game(["a", "b", "c", "d", "e"], num_werewolves=1, rng=random.Random(1))
    werewolf_id = next(p.id for p in game.players if p.role.value == "werewolf")

    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=vote_out_the_werewolf(werewolf_id))
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 50})
    final = result["game"]

    assert final.winner == Team.VILLAGERS
    assert not final.get(werewolf_id).alive
    assert agent.statement_calls > 0  # discussion phase ran


def test_doctor_protection_prevents_elimination_when_target_matches():
    game = new_game(["a", "b", "c", "d"], num_werewolves=1, num_doctors=1, rng=random.Random(2))
    werewolf_id = next(p.id for p in game.players if p.role.value == "werewolf")
    doctor_id = next(p.id for p in game.players if p.role.value == "doctor")
    victim_id = next(p.id for p in game.players if p.id not in (werewolf_id, doctor_id))

    agent = FakeAgent(
        night_target_fn=lambda state, wolf: victim_id,
        vote_fn=lambda state, voter: werewolf_id if voter.id != werewolf_id else victim_id,
        doctor_fn=lambda state, doctor: victim_id,
    )
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 50})
    final = result["game"]

    assert final.get(victim_id).alive
    assert "no one died" in final.log[0]


def test_seer_investigation_is_recorded_privately_and_never_leaks_publicly():
    game = new_game(["a", "b", "c", "d"], num_werewolves=1, num_seers=1, rng=random.Random(3))
    werewolf_id = next(p.id for p in game.players if p.role.value == "werewolf")
    seer_id = next(p.id for p in game.players if p.role.value == "seer")

    agent = FakeAgent(
        night_target_fn=first_villager_id,
        vote_fn=lambda state, voter: werewolf_id if voter.id != werewolf_id else seer_id,
        seer_fn=lambda state, seer: werewolf_id,
    )
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 50})
    final = result["game"]

    seer = final.get(seer_id)
    assert any("ARE a Werewolf" in entry for entry in seer.private_log)
    assert not any("ARE a Werewolf" in entry for entry in final.log)
    for other in final.players:
        if other.id != seer_id:
            assert not other.private_log


def test_round_records_capture_night_discussion_and_vote():
    game = new_game(["a", "b", "c", "d", "e"], num_werewolves=1, rng=random.Random(1))
    werewolf_id = next(p.id for p in game.players if p.role.value == "werewolf")

    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=vote_out_the_werewolf(werewolf_id))
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 50})
    final = result["game"]

    assert len(final.rounds) == 1
    record = final.rounds[0]
    assert record.round == 1
    assert "killed during the night" in record.night_result
    assert len(record.discussion) == 4  # all 4 survivors spoke before the vote
    assert "voted out" in record.vote_result


def test_round_record_partial_when_game_ends_at_night():
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    agent = FakeAgent(night_target_fn=first_villager_id, vote_fn=lambda *_: 0)
    app = build_graph(agent, rng=random.Random(0), summarize=fake_summarize)

    result = app.invoke({"game": game, "discussion": []})
    final = result["game"]

    assert len(final.rounds) == 1
    assert final.rounds[0].discussion == []
    assert final.rounds[0].vote_result is None


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
