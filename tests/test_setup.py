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


def test_assigns_seer_and_doctor_alongside_werewolves():
    state = new_game(["a", "b", "c", "d", "e"], num_werewolves=1, num_seers=1, num_doctors=1, rng=random.Random(0))
    roles = [p.role for p in state.players]
    assert roles.count(Role.WEREWOLF) == 1
    assert roles.count(Role.SEER) == 1
    assert roles.count(Role.DOCTOR) == 1
    assert roles.count(Role.VILLAGER) == 2


def test_rejects_more_special_roles_than_players():
    with pytest.raises(ValueError):
        new_game(["a", "b", "c"], num_werewolves=1, num_seers=1, num_doctors=2)
