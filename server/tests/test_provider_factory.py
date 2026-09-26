import pytest

from app.services.gemini_service import (
    GeminiGenerationProvider,
    GeminiRerankerProvider,
)
from app.services.groq_generation_provider import GroqGenerationProvider
from app.services.openrouter_generation_provider import OpenRouterGenerationProvider
from app.services.cohere_reranker_provider import CohereRerankerProvider
from app.services.provider_errors import ProviderError, ProviderErrorCategory
from app.services.provider_factory import (
    FallbackGenerationProvider,
    get_generation_provider,
    get_reranker_provider,
)


class FakeSettings:
    google_api_key = "google-key"
    gemini_chat_model = "gemini-model"
    generation_provider = "gemini"
    reranker_provider = "gemini"
    generation_fallback_provider = ""
    openrouter_api_key = "openrouter-key"
    openrouter_model = "openrouter-model"
    groq_api_key = "groq-key"
    groq_model = "groq-model"
    cohere_api_key = "cohere-key"
    cohere_rerank_model = "cohere-rerank-model"
    provider_timeout_seconds = 7.0


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("gemini", GeminiGenerationProvider),
        ("openrouter", OpenRouterGenerationProvider),
        ("groq", GroqGenerationProvider),
    ],
)
def test_generation_provider_resolution(monkeypatch, name, expected):
    from app.services import provider_factory

    monkeypatch.setattr(
        provider_factory.genai,
        "Client",
        lambda **kwargs: object(),
    )
    config = FakeSettings()
    config.generation_provider = name

    assert isinstance(get_generation_provider(config), expected)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("gemini", GeminiRerankerProvider),
        ("cohere", CohereRerankerProvider),
    ],
)
def test_reranker_provider_resolution(monkeypatch, name, expected):
    from app.services import provider_factory

    monkeypatch.setattr(
        provider_factory.genai,
        "Client",
        lambda **kwargs: object(),
    )
    config = FakeSettings()
    config.reranker_provider = name

    assert isinstance(get_reranker_provider(config), expected)


def test_unsupported_provider_is_reported_clearly():
    config = FakeSettings()
    config.generation_provider = "unknown-model-vendor"

    with pytest.raises(ProviderError) as error:
        get_generation_provider(config)

    assert error.value.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER
    assert "unknown-model-vendor" in str(error.value)

    config = FakeSettings()
    config.reranker_provider = "another-reranker"
    with pytest.raises(ProviderError) as error:
        get_reranker_provider(config)
    assert error.value.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER


def test_missing_selected_provider_configuration_fails_clearly():
    config = FakeSettings()
    config.generation_provider = "groq"
    config.groq_api_key = ""
    config.groq_model = ""

    with pytest.raises(ProviderError) as error:
        get_generation_provider(config)

    assert error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION

    config = FakeSettings()
    config.reranker_provider = "cohere"
    config.cohere_api_key = ""
    with pytest.raises(ProviderError) as error:
        get_reranker_provider(config)
    assert error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


def test_gemini_defaults_require_no_optional_provider_configuration(monkeypatch):
    from app.services import provider_factory

    monkeypatch.setattr(
        provider_factory.genai,
        "Client",
        lambda **kwargs: object(),
    )
    config = FakeSettings()
    config.openrouter_api_key = ""
    config.groq_api_key = ""
    config.cohere_api_key = ""

    assert isinstance(get_generation_provider(config), GeminiGenerationProvider)
    assert isinstance(get_reranker_provider(config), GeminiRerankerProvider)


def test_generation_fallback_is_optional_and_resolved_from_configuration(monkeypatch):
    from app.services import provider_factory

    monkeypatch.setattr(
        provider_factory.genai,
        "Client",
        lambda **kwargs: object(),
    )
    config = FakeSettings()
    provider = get_generation_provider(config)
    assert isinstance(provider, GeminiGenerationProvider)

    config.generation_fallback_provider = "groq"
    provider = get_generation_provider(config)
    assert isinstance(provider, FallbackGenerationProvider)
    assert isinstance(provider.primary, GeminiGenerationProvider)
    assert isinstance(provider.fallback, GroqGenerationProvider)

    config.generation_fallback_provider = "gemini"
    with pytest.raises(ProviderError) as error:
        get_generation_provider(config)
    assert error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


def test_fallback_is_used_only_for_transient_provider_errors():
    class StubProvider:
        def __init__(self, name, error=None, text="ok"):
            self.provider_name = name
            self.model_name = f"{name}-model"
            self.error = error
            self.text = text
            self.calls = 0

        def generate(self, prompt):
            self.calls += 1
            if self.error:
                raise self.error
            return self.text

        def generate_with_metadata(self, prompt):
            from app.services.provider_interfaces import GenerationResult

            return GenerationResult(
                text=self.generate(prompt),
                provider=self.provider_name,
                model=self.model_name,
            )

    primary = StubProvider("primary", text="primary result")
    fallback = StubProvider("fallback", text="fallback result")
    provider = FallbackGenerationProvider(primary, fallback)

    result = provider.generate_with_metadata("prompt")

    assert result.text == "primary result"
    assert result.fallback_used is False
    assert fallback.calls == 0

    primary = StubProvider(
        "primary",
        error=ProviderError(
            ProviderErrorCategory.UNAVAILABLE,
            provider="primary",
            retryable=True,
        ),
    )
    fallback = StubProvider("fallback", text="fallback result")
    result = FallbackGenerationProvider(primary, fallback).generate_with_metadata(
        "prompt"
    )
    assert result.text == "fallback result"
    assert result.provider == "fallback"
    assert result.fallback_used is True

    primary = StubProvider(
        "primary",
        error=ProviderError(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
            provider="primary",
            retryable=False,
        ),
    )
    fallback = StubProvider("fallback")
    with pytest.raises(ProviderError):
        FallbackGenerationProvider(primary, fallback).generate("prompt")
    assert fallback.calls == 0


def test_fallback_failure_returns_normalized_provider_error():
    class FailingProvider:
        provider_name = "provider"
        model_name = "model"

        def generate(self, prompt):
            raise ProviderError(
                ProviderErrorCategory.TIMEOUT,
                provider=self.provider_name,
                retryable=True,
            )

    with pytest.raises(ProviderError) as error:
        FallbackGenerationProvider(FailingProvider(), FailingProvider()).generate(
            "prompt"
        )

    assert error.value.category == ProviderErrorCategory.TIMEOUT
