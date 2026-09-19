import pytest
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

from ai_werewolf.llm.providers import DEFAULT_MODELS, make_llm


def test_ollama_provider_builds_chat_ollama():
    llm = make_llm("ollama", "qwen2.5:3b", 0.7)
    assert isinstance(llm, ChatOllama)


def test_mistral_provider_builds_chat_mistral(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    llm = make_llm("mistral", "mistral-small-latest", 0.7)
    assert isinstance(llm, ChatMistralAI)


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        make_llm("openai", "gpt-4", 0.7)


def test_default_models_cover_every_provider():
    assert set(DEFAULT_MODELS) == {"ollama", "mistral"}
