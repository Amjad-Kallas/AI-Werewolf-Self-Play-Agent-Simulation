from typing import Callable, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMDecisionError(RuntimeError):
    """Raised when a model fails to produce a valid, schema- and rule-conformant response."""


def invoke_structured(
    llm: BaseChatModel,
    schema: type[T],
    system_prompt: str,
    human_prompt: str,
    validate: Callable[[T], str | None] | None = None,
    max_attempts: int = 3,
) -> T:
    """Call `llm` for a `schema`-shaped decision, repairing malformed output.

    Two things can go wrong: the model's output doesn't parse into `schema`
    (a langchain/pydantic validation error), or it parses fine but breaks a
    game rule that `schema` itself can't express (e.g. voting for a dead
    player) — caught by the optional `validate` callback. Either way we feed
    the concrete error back to the model and ask it to try again, up to
    `max_attempts` times.
    """
    structured_llm = llm.with_structured_output(schema)
    messages: list[BaseMessage] = [SystemMessage(system_prompt), HumanMessage(human_prompt)]
    last_error = "unknown error"

    for _ in range(max_attempts):
        try:
            result = structured_llm.invoke(messages)
        except Exception as exc:  # malformed / non-schema-conformant output
            last_error = str(exc)
            messages.append(HumanMessage(f"Your last response was invalid: {last_error}\nRespond again, matching the required format exactly."))
            continue

        error = validate(result) if validate else None
        if error is None:
            return result

        last_error = error
        messages.append(AIMessage(result.model_dump_json()))
        messages.append(HumanMessage(f"That response was rejected: {error}\nRespond again with a valid choice."))

    raise LLMDecisionError(f"failed to get a valid {schema.__name__} after {max_attempts} attempts: {last_error}")
