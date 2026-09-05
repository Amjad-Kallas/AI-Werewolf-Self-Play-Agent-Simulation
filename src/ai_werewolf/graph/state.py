from typing import TypedDict

from ai_werewolf.engine.models import GameState


class GraphState(TypedDict):
    game: GameState
    discussion: list[dict]
