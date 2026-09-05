import random

import pytest

from ai_werewolf.engine.roles import Role
from ai_werewolf.engine.setup import new_game


def test_assigns_correct_role_counts():
    state = new_game(["a", "b", "c", "d", "e"], num_werewolves=2, rng=random.Random(0))
    werewolves = [p for p in state.players if p.role == Role.WEREWOLF]
    villagers = [p for p in state.players if p.role == Role.VILLAGER]
    assert len(werewolves) == 2
    assert len(villagers) == 3


def test_all_players_start_alive():
    state = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    assert all(p.alive for p in state.players)


def test_rejects_too_many_werewolves():
    with pytest.raises(ValueError):
        new_game(["a", "b"], num_werewolves=2)


def test_rejects_zero_werewolves():
    with pytest.raises(ValueError):
        new_game(["a", "b", "c"], num_werewolves=0)
