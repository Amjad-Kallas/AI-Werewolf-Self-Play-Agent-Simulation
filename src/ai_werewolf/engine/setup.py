import random

from .models import GameState, Player
from .roles import Role


def new_game(names: list[str], num_werewolves: int, rng: random.Random | None = None) -> GameState:
    if num_werewolves < 1:
        raise ValueError("need at least 1 werewolf")
    if num_werewolves >= len(names):
        raise ValueError("werewolves must not outnumber or equal total players")

    rng = rng or random.Random()
    roles = [Role.WEREWOLF] * num_werewolves + [Role.VILLAGER] * (len(names) - num_werewolves)
    rng.shuffle(roles)

    players = [Player(id=i, name=name, role=role) for i, (name, role) in enumerate(zip(names, roles))]
    return GameState(players=players)
