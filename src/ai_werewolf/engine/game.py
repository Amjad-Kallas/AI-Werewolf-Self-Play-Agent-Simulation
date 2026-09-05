import random
from typing import Protocol

from .models import GameState
from .voting import tally_votes
from .win_conditions import check_win_condition


class NightDecider(Protocol):
    def __call__(self, state: GameState, rng: random.Random) -> int: ...


class VoteDecider(Protocol):
    def __call__(self, state: GameState, voter, rng: random.Random) -> int: ...


def run_game(
    state: GameState,
    choose_night_target: NightDecider,
    choose_vote: VoteDecider,
    rng: random.Random | None = None,
    max_rounds: int = 100,
) -> GameState:
    """Run Night -> Vote -> Resolution until a team wins, mutating and returning `state`."""
    rng = rng or random.Random()

    while state.winner is None and state.round < max_rounds:
        state.round += 1

        # Night: werewolves eliminate one villager.
        target_id = choose_night_target(state, rng)
        victim = state.eliminate(target_id)
        state.log.append(f"Round {state.round}: {victim.name} was killed during the night.")

        state.winner = check_win_condition(state)
        if state.winner is not None:
            break

        # Day vote: every living player votes; the top target is eliminated (no elimination on a tie).
        votes = {p.id: choose_vote(state, p, rng) for p in state.alive_players()}
        eliminated_id = tally_votes(votes)
        if eliminated_id is None:
            state.log.append(f"Round {state.round}: the vote was tied, no one was eliminated.")
        else:
            eliminated = state.eliminate(eliminated_id)
            state.log.append(f"Round {state.round}: {eliminated.name} was voted out.")

        state.winner = check_win_condition(state)

    return state
