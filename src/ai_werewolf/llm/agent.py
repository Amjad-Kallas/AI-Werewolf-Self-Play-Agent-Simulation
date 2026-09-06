from langchain_core.language_models.chat_models import BaseChatModel

from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Role

from .client import invoke_structured
from .prompts import discussion_prompt, doctor_prompt, night_prompt, seer_prompt, vote_prompt
from .schemas import DoctorAction, NightAction, SeerAction, Statement, VoteAction


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

    def choose_seer_target(self, state: GameState, seer: Player) -> SeerAction:
        valid_ids = {p.id for p in state.alive_players() if p.id != seer.id}
        system, human = seer_prompt(state, seer)

        def validate(action: SeerAction) -> str | None:
            if action.target_id not in valid_ids:
                return f"target_id {action.target_id} is not a valid living player other than yourself."
            return None

        return invoke_structured(self.llm, SeerAction, system, human, validate=validate)

    def choose_doctor_protect(self, state: GameState, doctor: Player) -> DoctorAction:
        valid_ids = {p.id for p in state.alive_players()}
        system, human = doctor_prompt(state, doctor)

        def validate(action: DoctorAction) -> str | None:
            if action.target_id not in valid_ids:
                return f"target_id {action.target_id} is not a valid living player."
            return None

        return invoke_structured(self.llm, DoctorAction, system, human, validate=validate)

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
