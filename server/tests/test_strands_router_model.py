from types import SimpleNamespace

import pytest

from app.schemas.agent_schema import AgentRoute, AgentType
from app.services import strands_router_model
from app.services.provider_errors import ProviderError, ProviderErrorCategory


class FakeSettings:
    generation_provider = "gemini"
    google_api_key = "google-key"
    gemini_chat_model = "gemini-router-model"
    groq_api_key = "groq-key"
    groq_model = "groq-router-model"
    openrouter_api_key = "openrouter-key"
    openrouter_model = "openrouter/router-model"


def test_strands_model_and_agent_are_created_lazily_and_structured_output_is_validated(
    monkeypatch,
):
    model = object()
    created_models = []
    calls = []

    def build_model(config):
        created_models.append(config)
        return model

    class FakeAgent:
        def __init__(self, model, system_prompt):
            assert model is globals_model
            assert "Never answer the user's question" in system_prompt

        def __call__(self, question, structured_output_model):
            assert structured_output_model is AgentRoute
            calls.append(question)
            return SimpleNamespace(
                structured_output={
                    "agent": "analyst",
                    "reason": "The request requires comparing data points.",
                }
            )

    globals_model = model
    monkeypatch.setattr(strands_router_model, "_build_model", build_model)
    monkeypatch.setattr(strands_router_model, "Agent", FakeAgent)
    router = strands_router_model.StrandsRouterModel(config=FakeSettings())

    first = router.route("Analyze these measures.")
    second = router.route("Compare these values.")

    assert first == AgentRoute(
        agent=AgentType.ANALYST,
        reason="The request requires comparing data points.",
    )
    assert second == first
    assert created_models == [router.config]
    assert calls == ["Analyze these measures.", "Compare these values."]


def test_strands_invalid_structured_output_fails_closed(monkeypatch):
    monkeypatch.setattr(strands_router_model, "_build_model", lambda _config: object())

    class FakeAgent:
        def __init__(self, **_kwargs):
            pass

        def __call__(self, *_args, **_kwargs):
            return SimpleNamespace(
                structured_output={"agent": "unknown_agent", "reason": "Invalid."}
            )

    monkeypatch.setattr(strands_router_model, "Agent", FakeAgent)

    with pytest.raises(ProviderError) as error:
        strands_router_model.StrandsRouterModel(config=FakeSettings()).route(
            "An ambiguous request."
        )

    assert error.value.category == ProviderErrorCategory.INVALID_RESPONSE


@pytest.mark.parametrize(
    ("provider", "expected_model", "expected_endpoint"),
    [
        ("gemini", "GeminiModel", None),
        ("groq", "OpenAIModel", "https://api.groq.com/openai/v1"),
        ("openrouter", "OpenAIModel", "https://openrouter.ai/api/v1"),
    ],
)
def test_strands_model_uses_existing_provider_settings(
    monkeypatch, provider, expected_model, expected_endpoint
):
    config = FakeSettings()
    config.generation_provider = provider
    constructed = []

    class FakeModel:
        def __init__(self, **kwargs):
            constructed.append(kwargs)

    monkeypatch.setattr(strands_router_model, "GeminiModel", FakeModel)
    monkeypatch.setattr(strands_router_model, "OpenAIModel", FakeModel)

    model = strands_router_model._build_model(config)

    assert isinstance(model, FakeModel)
    assert len(constructed) == 1
    if expected_model == "GeminiModel":
        assert constructed[0]["client_args"]["api_key"] == "google-key"
        assert constructed[0]["model_id"] == "gemini-router-model"
    else:
        assert constructed[0]["client_args"]["base_url"] == expected_endpoint
        expected_model_id = (
            config.groq_model if provider == "groq" else config.openrouter_model
        )
        assert constructed[0]["model_id"] == expected_model_id


def test_strands_unsupported_provider_uses_normalized_error():
    config = FakeSettings()
    config.generation_provider = "unsupported"

    with pytest.raises(ProviderError) as error:
        strands_router_model._build_model(config)

    assert error.value.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER


@pytest.mark.parametrize(
    ("status_code", "message", "expected_category"),
    [
        (401, "unauthorized", ProviderErrorCategory.CONFIGURATION_AUTHENTICATION),
        (429, "rate limit exceeded", ProviderErrorCategory.RATE_LIMIT),
        (429, "insufficient_quota", ProviderErrorCategory.QUOTA),
        (503, "provider unavailable", ProviderErrorCategory.UNAVAILABLE),
        (504, "gateway timeout", ProviderErrorCategory.TIMEOUT),
    ],
)
def test_strands_http_errors_use_normalized_categories(
    status_code, message, expected_category
):
    class CodedError(Exception):
        def __init__(self, status, error_message):
            self.status_code = status
            super().__init__(error_message)

    normalized = strands_router_model._normalize_error(CodedError(status_code, message))

    assert normalized.category == expected_category


def test_strands_resource_exhausted_error_maps_to_quota():
    class CodedError(Exception):
        code = "RESOURCE_EXHAUSTED"

    normalized = strands_router_model._normalize_error(CodedError("quota exhausted"))

    assert normalized.category == ProviderErrorCategory.QUOTA


def test_strands_timeout_uses_normalized_provider_error(monkeypatch):
    monkeypatch.setattr(strands_router_model, "_build_model", lambda _config: object())

    class FakeAgent:
        def __init__(self, **_kwargs):
            pass

        def __call__(self, *_args, **_kwargs):
            raise TimeoutError("model request timed out")

    monkeypatch.setattr(strands_router_model, "Agent", FakeAgent)

    with pytest.raises(ProviderError) as error:
        strands_router_model.StrandsRouterModel(config=FakeSettings()).route(
            "An ambiguous request."
        )

    assert error.value.category == ProviderErrorCategory.TIMEOUT


def test_strands_model_configuration_error_is_preserved(monkeypatch):
    config_error = ProviderError(
        ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
        provider="gemini",
    )
    monkeypatch.setattr(
        strands_router_model,
        "_build_model",
        lambda _config: (_ for _ in ()).throw(config_error),
    )

    with pytest.raises(ProviderError) as error:
        strands_router_model.StrandsRouterModel(config=FakeSettings()).route(
            "An ambiguous request."
        )

    assert error.value is config_error
    assert error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
