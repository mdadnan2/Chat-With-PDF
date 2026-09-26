from __future__ import annotations

from dataclasses import replace

from google import genai

from app.config import settings
from app.services.cohere_reranker_provider import CohereRerankerProvider
from app.services.gemini_service import GeminiGenerationProvider, GeminiRerankerProvider
from app.services.groq_generation_provider import GroqGenerationProvider
from app.services.openrouter_generation_provider import OpenRouterGenerationProvider
from app.services.provider_errors import ProviderError, ProviderErrorCategory
from app.services.provider_interfaces import (
    GenerationProvider,
    GenerationResult,
    RerankerProvider,
)


def get_generation_provider(config=settings) -> GenerationProvider:
    primary_name = config.generation_provider.strip().lower()
    primary = _build_generation_provider(primary_name, config)

    fallback_name = config.generation_fallback_provider.strip().lower()
    if not fallback_name:
        return primary
    if fallback_name == primary_name:
        raise ProviderError(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
            provider=fallback_name,
            public_message="The generation fallback must differ from the primary provider.",
        )
    return FallbackGenerationProvider(
        primary,
        _build_generation_provider(fallback_name, config),
    )


def get_reranker_provider(config=settings) -> RerankerProvider:
    name = config.reranker_provider.strip().lower()
    timeout = config.provider_timeout_seconds

    if name == "gemini":
        client = genai.Client(
            api_key=_required(config.google_api_key, "GOOGLE_API_KEY", name)
        )
        return GeminiRerankerProvider(client)
    if name == "cohere":
        return CohereRerankerProvider(
            api_key=_required(config.cohere_api_key, "COHERE_API_KEY", name),
            model=_required(config.cohere_rerank_model, "COHERE_RERANK_MODEL", name),
            timeout=timeout,
        )
    raise _unsupported_provider(name, "reranker")


def _build_generation_provider(name: str, config) -> GenerationProvider:
    timeout = config.provider_timeout_seconds
    if name == "gemini":
        client = genai.Client(
            api_key=_required(config.google_api_key, "GOOGLE_API_KEY", name)
        )
        return GeminiGenerationProvider(client)
    if name == "openrouter":
        return OpenRouterGenerationProvider(
            api_key=_required(config.openrouter_api_key, "OPENROUTER_API_KEY", name),
            model=_required(config.openrouter_model, "OPENROUTER_MODEL", name),
            timeout=timeout,
        )
    if name == "groq":
        return GroqGenerationProvider(
            api_key=_required(config.groq_api_key, "GROQ_API_KEY", name),
            model=_required(config.groq_model, "GROQ_MODEL", name),
            timeout=timeout,
        )
    raise _unsupported_provider(name, "generation")


def _required(value: str, variable_name: str, provider: str) -> str:
    if not value or not value.strip():
        raise ProviderError(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
            provider=provider,
            public_message=f"{variable_name} is required for the selected AI provider.",
        )
    return value


def _unsupported_provider(name: str, capability: str) -> ProviderError:
    return ProviderError(
        ProviderErrorCategory.UNSUPPORTED_PROVIDER,
        provider=name or "(empty)",
        public_message=f"Unsupported {capability} provider configured: {name or '(empty)'}.",
    )


def _generate_result(provider: GenerationProvider, prompt: str) -> GenerationResult:
    generate_with_metadata = getattr(provider, "generate_with_metadata", None)
    if callable(generate_with_metadata):
        result = generate_with_metadata(prompt)
        if not isinstance(result, GenerationResult):
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=getattr(provider, "provider_name", "unknown"),
            )
        return result

    text = provider.generate(prompt)
    if not isinstance(text, str) or not text.strip():
        raise ProviderError(
            ProviderErrorCategory.INVALID_RESPONSE,
            provider=getattr(provider, "provider_name", "unknown"),
        )
    return GenerationResult(
        text=text,
        provider=getattr(provider, "provider_name", None),
        model=getattr(provider, "model_name", None),
    )


class FallbackGenerationProvider:
    def __init__(
        self,
        primary: GenerationProvider,
        fallback: GenerationProvider,
    ):
        self.primary = primary
        self.fallback = fallback
        self.provider_name = getattr(primary, "provider_name", "configured")
        self.model_name = getattr(primary, "model_name", None)

    def generate(self, prompt: str) -> str:
        return self.generate_with_metadata(prompt).text

    def generate_with_metadata(self, prompt: str) -> GenerationResult:
        primary_error_category = None
        try:
            return _generate_result(self.primary, prompt)
        except ProviderError as primary_error:
            if not primary_error.retryable:
                raise
            primary_error_category = primary_error.category.value

        try:
            fallback_result = _generate_result(self.fallback, prompt)
        except ProviderError:
            raise

        return replace(
            fallback_result,
            fallback_used=True,
            provider_error_category=primary_error_category,
        )
