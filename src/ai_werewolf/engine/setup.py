import random

from .models import GameState, Player
from .roles import Role


def new_game(
    names: list[str],
    num_werewolves: int,
    num_seers: int = 0,
    num_doctors: int = 0,
    rng: random.Random | None = None,
) -> GameState:
    if num_werewolves < 1:
        raise ValueError("need at least 1 werewolf")
    special_roles = num_werewolves + num_seers + num_doctors
    if special_roles > len(names):
        raise ValueError("cannot assign more special roles than players")
    if num_werewolves * 2 >= len(names):
        raise ValueError("werewolves must not outnumber or equal the villager team")

    rng = rng or random.Random()
    roles = (
        [Role.WEREWOLF] * num_werewolves
        + [Role.SEER] * num_seers
        + [Role.DOCTOR] * num_doctors
        + [Role.VILLAGER] * (len(names) - special_roles)
    )
    rng.shuffle(roles)

    players = [Player(id=i, name=name, role=role) for i, (name, role) in enumerate(zip(names, roles))]
    return GameState(players=players)
