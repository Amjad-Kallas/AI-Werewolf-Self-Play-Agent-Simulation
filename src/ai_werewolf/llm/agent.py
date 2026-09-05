from langchain_core.language_models.chat_models import BaseChatModel

from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Role

from .client import invoke_structured
from .prompts import discussion_prompt, night_prompt, vote_prompt
from .schemas import NightAction, Statement, VoteAction


class LLMAgent:
    """Wraps a chat model as a Werewolf decision-maker: prompt in, validated schema out."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def choose_night_target(self, state: GameState, wolf: Player) -> NightAction:
        valid_ids = {p.id for p in state.alive_players() if p.role != Role.WEREWOLF}
        system, human = night_prompt(state, wolf)

        def validate(action: NightAction) -> str | None:
            if action.target_id not in valid_ids:
                return f"target_id {action.target_id} is not a living non-werewolf player."
            return None

        return invoke_structured(self.llm, NightAction, system, human, validate=validate)

    def make_statement(self, state: GameState, player: Player, discussion: list[dict]) -> Statement:
        system, human = discussion_prompt(state, player, discussion)
        return invoke_structured(self.llm, Statement, system, human)

    def choose_vote(self, state: GameState, player: Player, discussion: list[dict]) -> VoteAction:
        valid_ids = {p.id for p in state.alive_players() if p.id != player.id}
        system, human = vote_prompt(state, player, discussion)

        def validate(action: VoteAction) -> str | None:
            if action.target_id not in valid_ids:
                return f"target_id {action.target_id} is not a valid living vote target."
            return None

        return invoke_structured(self.llm, VoteAction, system, human, validate=validate)
