from .models import GameState
from .roles import Team


def check_win_condition(state: GameState) -> Team | None:
    """Return the winning team, or None if the game continues.

    Werewolves win once they equal or outnumber the villagers (they can then
    win any night/vote from here). Villagers win once every werewolf is dead.
    """
    werewolves = len(state.alive_by_team(Team.WEREWOLVES))
    villagers = len(state.alive_by_team(Team.VILLAGERS))

    if werewolves == 0:
        return Team.VILLAGERS
    if werewolves >= villagers:
        return Team.WEREWOLVES
    return None
