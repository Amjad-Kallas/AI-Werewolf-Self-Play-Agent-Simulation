import random

import pytest

from ai_werewolf.agents.random_agent import choose_night_target, choose_vote
from ai_werewolf.engine.game import run_game
from ai_werewolf.engine.roles import Team
from ai_werewolf.engine.setup import new_game
from ai_werewolf.engine.win_conditions import check_win_condition


@pytest.mark.parametrize("seed", range(20))
def test_full_game_terminates_with_a_consistent_winner(seed):
    state = new_game(["a", "b", "c", "d", "e", "f"], num_werewolves=2, rng=random.Random(seed))

    run_game(state, choose_night_target, choose_vote, rng=random.Random(seed))

    assert state.winner in (Team.VILLAGERS, Team.WEREWOLVES)
    assert state.winner == check_win_condition(state)
    assert state.round < 100
    assert state.log


def test_deterministic_werewolf_kills_lead_to_werewolf_win():
    state = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    wolf = next(p for p in state.players if p.role.value == "werewolf")
    villagers = [p for p in state.players if p.role.value == "villager"]

    def scripted_night(state, rng):
        return next(p.id for p in state.alive_by_team(Team.VILLAGERS))

    def scripted_vote(state, voter, rng):
        # everyone votes for the werewolf's first villager victim's ally, i.e. never the wolf
        return next(p.id for p in state.alive_players() if p.id != voter.id and p.id != wolf.id)

    run_game(state, scripted_night, scripted_vote, rng=random.Random(0))

    assert state.winner == Team.WEREWOLVES
    assert state.get(wolf.id).alive
