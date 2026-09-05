from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Role, Team
from ai_werewolf.engine.win_conditions import check_win_condition


def make_state(role_by_alive: list[tuple[Role, bool]]) -> GameState:
    players = [
        Player(id=i, name=f"p{i}", role=role, alive=alive)
        for i, (role, alive) in enumerate(role_by_alive)
    ]
    return GameState(players=players)


def test_villagers_win_when_all_werewolves_dead():
    state = make_state(
        [
            (Role.WEREWOLF, False),
            (Role.VILLAGER, True),
            (Role.VILLAGER, True),
        ]
    )
    assert check_win_condition(state) == Team.VILLAGERS


def test_werewolves_win_when_they_equal_villagers():
    state = make_state(
        [
            (Role.WEREWOLF, True),
            (Role.VILLAGER, True),
            (Role.VILLAGER, False),
        ]
    )
    assert check_win_condition(state) == Team.WEREWOLVES


def test_werewolves_win_when_they_outnumber_villagers():
    state = make_state(
        [
            (Role.WEREWOLF, True),
            (Role.WEREWOLF, True),
            (Role.VILLAGER, True),
        ]
    )
    assert check_win_condition(state) == Team.WEREWOLVES


def test_game_continues_when_neither_condition_met():
    state = make_state(
        [
            (Role.WEREWOLF, True),
            (Role.VILLAGER, True),
            (Role.VILLAGER, True),
        ]
    )
    assert check_win_condition(state) is None
