from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.models.openai import OpenAIModel
from strands.types.exceptions import ModelThrottledException, StructuredOutputException

from app.config import settings
from app.schemas.agent_schema import AgentRoute
from app.services.provider_errors import ProviderError, ProviderErrorCategory

_SYSTEM_PROMPT = """You are an agent router. Select exactly one existing specialist agent for the user's request and give a short reason.
Never answer the user's question or provide document facts. You only select an agent.

Capabilities:
- research: factual questions and explanations grounded in document evidence; use for questions such as what a document says about a topic or risks mentioned.
- summary: concise summaries, executive summaries, overviews, key points, and takeaways.
- analyst: comparisons, calculations, trends, metrics, patterns, and interpretation of data. Numbers alone do not imply analysis.
- document: extraction of specific facts, dates, requirements, entities, sections, metadata, FAQ items, and document details.
- verification: checking whether a claim or answer is supported, contradicted, or unsubstantiated by the document.

Return only the requested structured routing result. The agent must be one of: research, summary, analyst, document, verification."""


def _required(value: str, variable: str, provider: str) -> str:
    if not value or not value.strip():
        raise ProviderError(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
            provider=provider,
            public_message=f"{variable} is required for automatic agent routing.",
        )
    return value


def _build_model(config: Any) -> Any:
    provider = config.generation_provider.strip().lower()
    if provider == "gemini":
        return GeminiModel(
            client_args={
                "api_key": _required(config.google_api_key, "GOOGLE_API_KEY", provider)
            },
            model_id=_required(config.gemini_chat_model, "GEMINI_CHAT_MODEL", provider),
            params={"temperature": 0, "max_output_tokens": 128},
        )
    if provider == "groq":
        return OpenAIModel(
            client_args={
                "api_key": _required(config.groq_api_key, "GROQ_API_KEY", provider),
                "base_url": "https://api.groq.com/openai/v1",
            },
            model_id=_required(config.groq_model, "GROQ_MODEL", provider),
            params={"temperature": 0, "max_tokens": 128},
        )
    if provider == "openrouter":
        return OpenAIModel(
            client_args={
                "api_key": _required(
                    config.openrouter_api_key, "OPENROUTER_API_KEY", provider
                ),
                "base_url": "https://openrouter.ai/api/v1",
            },
            model_id=_required(config.openrouter_model, "OPENROUTER_MODEL", provider),
            params={"temperature": 0, "max_tokens": 128},
        )
    raise ProviderError(
        ProviderErrorCategory.UNSUPPORTED_PROVIDER,
        provider=provider or "(empty)",
        public_message="The configured generation provider cannot be used for automatic routing.",
    )


def _normalize_error(error: Exception) -> ProviderError:
    if isinstance(error, ProviderError):
        return error
    if isinstance(error, (StructuredOutputException, ValidationError)):
        return ProviderError(
            ProviderErrorCategory.INVALID_RESPONSE,
            provider="strands-router",
        )

    message = str(error).lower()
    code = getattr(error, "status_code", None) or getattr(error, "code", None)
    code_name = str(code).upper()
    if isinstance(error, (TimeoutError, httpx.TimeoutException)) or code in (408, 504):
        category = ProviderErrorCategory.TIMEOUT
    elif code in (401, 403) or code_name in {"UNAUTHENTICATED", "PERMISSION_DENIED"}:
        category = ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    elif code_name == "RESOURCE_EXHAUSTED":
        category = ProviderErrorCategory.QUOTA
    elif code == 429:
        category = (
            ProviderErrorCategory.QUOTA
            if any(
                term in message
                for term in ("quota", "resource_exhausted", "insufficient_quota")
            )
            else ProviderErrorCategory.RATE_LIMIT
        )
    elif isinstance(error, ModelThrottledException):
        category = (
            ProviderErrorCategory.QUOTA
            if "quota" in message
            else ProviderErrorCategory.RATE_LIMIT
        )
    elif isinstance(error, httpx.RequestError):
        category = ProviderErrorCategory.UNAVAILABLE
    elif isinstance(code, int) and code >= 500:
        category = ProviderErrorCategory.UNAVAILABLE
    elif any(
        term in type(error).__name__.lower()
        for term in ("authentication", "permission")
    ):
        category = ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    elif "quota" in message:
        category = ProviderErrorCategory.QUOTA
    elif "rate limit" in message or "rate_limit" in message:
        category = ProviderErrorCategory.RATE_LIMIT
    else:
        category = ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR

    retryable = category in {
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    }
    return ProviderError(category, provider="strands-router", retryable=retryable)


class StrandsRouterModel:
    """Lazily builds a Strands model using existing generation settings."""

    def __init__(self, config: Any = settings):
        self.config = config
        self._model: Any | None = None

    def route(self, question: str) -> AgentRoute:
        try:
            if self._model is None:
                self._model = _build_model(self.config)
            agent = Agent(model=self._model, system_prompt=_SYSTEM_PROMPT)
            result = agent(question, structured_output_model=AgentRoute)
            try:
                structured_output = result.structured_output
            except AttributeError as exc:
                raise ProviderError(
                    ProviderErrorCategory.INVALID_RESPONSE,
                    provider="strands-router",
                ) from exc
            if isinstance(structured_output, AgentRoute):
                return structured_output
            return AgentRoute.model_validate(structured_output)
        except ProviderError:
            raise
        except (StructuredOutputException, ValidationError) as exc:
            raise _normalize_error(exc) from exc
        except Exception as exc:
            raise _normalize_error(exc) from exc


_router_model = StrandsRouterModel()


def route_with_strands(question: str) -> AgentRoute:
    return _router_model.route(question)
