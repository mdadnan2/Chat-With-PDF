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

_RETRYABLE_CATEGORIES = {
    ProviderErrorCategory.RATE_LIMIT,
    ProviderErrorCategory.QUOTA,
    ProviderErrorCategory.TIMEOUT,
    ProviderErrorCategory.UNAVAILABLE,
}


# ---------------------------------------------------------------------------
# Public factory functions
# ---------------------------------------------------------------------------


def get_generation_provider(config=settings) -> GenerationProvider:
    chain = _build_generation_chain(config)
    if len(chain) == 1:
        return chain[0]
    if len(chain) == 2:
        return FallbackGenerationProvider(chain[0], chain[1])
    return ChainedGenerationProvider(chain)


def get_reranker_provider(config=settings) -> RerankerProvider:
    chain = _build_reranker_chain(config)
    if len(chain) == 1:
        return chain[0]
    return FallbackRerankerProvider(chain)


# ---------------------------------------------------------------------------
# Chain builders
# ---------------------------------------------------------------------------


def _build_generation_chain(config) -> list[GenerationProvider]:
    names: list[str] = []
    for raw in (
        config.generation_provider,
        getattr(config, "generation_fallback_provider", ""),
        getattr(config, "generation_secondary_fallback_provider", ""),
    ):
        name = (raw or "").strip().lower()
        if not name:
            break
        if name in names:
            raise ProviderError(
                ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
                provider=name,
                public_message=(
                    f"Duplicate provider '{name}' in the generation chain. "
                    "Each provider must appear at most once."
                ),
            )
        names.append(name)
    return [_build_generation_provider(n, config) for n in names]


def _build_reranker_chain(config) -> list[RerankerProvider]:
    names: list[str] = []
    for raw in (
        config.reranker_provider,
        getattr(config, "reranker_fallback_provider", ""),
    ):
        name = (raw or "").strip().lower()
        if not name:
            break
        if name in names:
            raise ProviderError(
                ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
                provider=name,
                public_message=(
                    f"Duplicate provider '{name}' in the reranker chain. "
                    "Each provider must appear at most once."
                ),
            )
        names.append(name)
    return [_build_reranker_provider(n, config) for n in names]


# ---------------------------------------------------------------------------
# Individual provider constructors
# ---------------------------------------------------------------------------


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


def _build_reranker_provider(name: str, config) -> RerankerProvider:
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Ordered-chain providers
# ---------------------------------------------------------------------------


class ChainedGenerationProvider:
    """Tries providers in order, falling back only on retryable errors."""

    def __init__(self, providers: list[GenerationProvider]):
        assert providers, "ChainedGenerationProvider requires at least one provider"
        self.providers = providers
        self.provider_name = getattr(providers[0], "provider_name", "configured")
        self.model_name = getattr(providers[0], "model_name", None)

    def generate(self, prompt: str) -> str:
        return self.generate_with_metadata(prompt).text

    def generate_with_metadata(self, prompt: str) -> GenerationResult:
        first_error_category: str | None = None
        for provider in self.providers:
            try:
                result = _generate_result(provider, prompt)
                if first_error_category is not None:
                    return replace(
                        result,
                        fallback_used=True,
                        provider_error_category=first_error_category,
                    )
                return result
            except ProviderError as exc:
                if exc.category not in _RETRYABLE_CATEGORIES:
                    raise
                if first_error_category is None:
                    first_error_category = exc.category.value
                last_exc = exc
        raise last_exc  # all providers exhausted


# Backward-compatible alias so existing tests importing FallbackGenerationProvider
# continue to work.  The two-provider case is a degenerate chain of length 2.
class FallbackGenerationProvider(ChainedGenerationProvider):
    def __init__(
        self,
        primary: GenerationProvider,
        fallback: GenerationProvider,
    ):
        super().__init__([primary, fallback])
        self.primary = primary
        self.fallback = fallback


class FallbackRerankerProvider:
    """Tries rerankers in order, falling back only on retryable errors."""

    def __init__(self, providers: list[RerankerProvider]):
        assert providers, "FallbackRerankerProvider requires at least one provider"
        self.providers = providers
        self.provider_name = getattr(providers[0], "provider_name", "configured")
        self.model_name = getattr(providers[0], "model_name", None)

    def rerank_with_info(self, question: str, chunks):
        """Returns (reranked_chunks, actual_provider_name, actual_model_name)."""
        for provider in self.providers:
            try:
                result = provider.rerank(question, chunks)
                return result, getattr(provider, "provider_name", None), getattr(provider, "model_name", None)
            except ProviderError as exc:
                if exc.category not in _RETRYABLE_CATEGORIES:
                    raise
                last_exc = exc
        raise last_exc

    def rerank(self, question: str, chunks):
        result, _, _ = self.rerank_with_info(question, chunks)
        return result
