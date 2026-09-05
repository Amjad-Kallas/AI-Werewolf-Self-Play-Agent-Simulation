import pytest
from pydantic import BaseModel

from ai_werewolf.llm.client import LLMDecisionError, invoke_structured


class Choice(BaseModel):
    target_id: int
    reasoning: str


class _StructuredProxy:
    def __init__(self, responses: list):
        self.responses = responses
        self.calls: list = []

    def invoke(self, messages):
        self.calls.append(messages)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class FakeLLM:
    """Duck-typed stand-in for a BaseChatModel: only `with_structured_output` is used."""

    def __init__(self, responses: list):
        self.proxy = _StructuredProxy(responses)

    def with_structured_output(self, schema):
        return self.proxy


def test_succeeds_on_first_valid_response():
    llm = FakeLLM([Choice(target_id=1, reasoning="ok")])
    result = invoke_structured(llm, Choice, "sys", "human")
    assert result.target_id == 1


def test_retries_after_parse_error_and_then_succeeds():
    llm = FakeLLM([ValueError("bad json"), Choice(target_id=2, reasoning="ok")])
    result = invoke_structured(llm, Choice, "sys", "human")
    assert result.target_id == 2
    assert len(llm.proxy.calls) == 2
    # the repair attempt should include feedback about the earlier failure
    assert "bad json" in llm.proxy.calls[1][-1].content


def test_retries_after_domain_validation_rejects_result():
    llm = FakeLLM([Choice(target_id=99, reasoning="bad"), Choice(target_id=1, reasoning="ok")])

    def validate(choice: Choice) -> str | None:
        return None if choice.target_id == 1 else "not a valid target"

    result = invoke_structured(llm, Choice, "sys", "human", validate=validate)
    assert result.target_id == 1
    assert len(llm.proxy.calls) == 2


def test_raises_after_exhausting_max_attempts():
    llm = FakeLLM([ValueError("bad"), ValueError("bad"), ValueError("bad")])
    with pytest.raises(LLMDecisionError):
        invoke_structured(llm, Choice, "sys", "human", max_attempts=3)
    assert len(llm.proxy.calls) == 3
