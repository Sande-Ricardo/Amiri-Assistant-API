from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from app.core.config import settings

LLMProvider = Literal["gemini", "groq"]


def get_llm(
    provider: LLMProvider | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """
    Factory function to instantiate and return a LangChain Chat Model
    based on the configured or requested provider ('gemini' or 'groq').

    Raises:
        ValueError: If an unsupported provider is specified or if required API keys are missing.
    """
    selected_provider = provider or settings.LLM_PROVIDER

    if selected_provider == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not configured in environment settings."
            )
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temperature,
        )

    elif selected_provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured in environment settings."
            )
        return ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {selected_provider}")
