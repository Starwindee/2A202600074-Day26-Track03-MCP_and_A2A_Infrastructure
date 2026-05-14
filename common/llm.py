"""Shared LLM factory for all agents.

Uses OpenRouter as an OpenAI-compatible API, so any provider's model
can be selected via the OPENROUTER_MODEL env var.
"""

import os

from langchain_openai import ChatOpenAI

from common.mock_llm import MockChatModel


def _is_mock_enabled() -> bool:
    value = os.getenv("MOCK_LLM", "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    # Auto-fallback to mock mode when no key is provided.
    return not bool(os.getenv("OPENROUTER_API_KEY"))


def get_llm():
    """Return the configured LLM client.

    - Real mode: ChatOpenAI via OpenRouter
    - Mock mode: deterministic local model for offline lab execution
    """
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    if _is_mock_enabled():
        return MockChatModel(temperature=temperature)
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
    )
