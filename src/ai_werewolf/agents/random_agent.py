"""Scripted random decisions, standing in for LLM agents until Phase 2."""

import random

from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Team


def choose_night_target(state: GameState, rng: random.Random) -> int:
    """Werewolves' nightly kill target: a random living non-werewolf."""
    candidates = [p for p in state.alive_by_team(Team.VILLAGERS)]
    return rng.choice(candidates).id


def choose_vote(state: GameState, voter: Player, rng: random.Random) -> int:
    """A random living player's vote: anyone alive except themselves."""
    candidates = [p for p in state.alive_players() if p.id != voter.id]
    return rng.choice(candidates).id
