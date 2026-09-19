from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

DEFAULT_MODELS = {
    "ollama": "qwen2.5:3b",
    "mistral": "mistral-small-latest",
}


def make_llm(provider: str, model: str, temperature: float) -> BaseChatModel:
    """Build a chat model for the given provider.

    "ollama" stays the default for local, free, unlimited development;
    "mistral" is the hosted API used for higher-quality showcase games.
    """
    if provider == "ollama":
        return ChatOllama(model=model, temperature=temperature)
    if provider == "mistral":
        return ChatMistralAI(model=model, temperature=temperature)
    raise ValueError(f"unknown provider {provider!r} (expected one of {sorted(DEFAULT_MODELS)})")
