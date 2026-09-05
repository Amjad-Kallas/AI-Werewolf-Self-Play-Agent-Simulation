from typing import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field

from ai_werewolf.engine.models import GameState

from .client import invoke_structured

SUMMARY_SYSTEM_PROMPT = (
    "You are the neutral narrator of a Werewolf game, maintaining a concise memory of what has "
    "happened so far for future reference. Only summarize what was publicly said or observed - "
    "never invent or reveal a hidden role that wasn't announced. Preserve details that matter for "
    "ongoing deduction: who accused whom, who died and how, and who has seemed suspicious."
)


class RoundSummary(BaseModel):
    summary: str = Field(description="a concise (3-6 sentence) updated summary of the public game so far")


def make_llm_summarizer(llm: BaseChatModel) -> Callable[[GameState], str]:
    """Build a summarizer that folds new public log entries into `state.summary`.

    Prompts read `state.summary` plus only the entries after `summarized_through`
    (see `describe_log`), so this is what keeps prompt size bounded across a long
    game instead of replaying the ever-growing transcript.
    """

    def summarize(state: GameState) -> str:
        fresh_events = state.log[state.summarized_through :]
        if not fresh_events:
            return state.summary

        human = (
            f"Previous summary:\n{state.summary or '(none yet - this is the first update)'}\n\n"
            "New public events since then:\n" + "\n".join(fresh_events) + "\n\n"
            "Write the updated summary, folding in the new events while keeping it concise."
        )
        result = invoke_structured(llm, RoundSummary, SUMMARY_SYSTEM_PROMPT, human)
        return result.summary

    return summarize
