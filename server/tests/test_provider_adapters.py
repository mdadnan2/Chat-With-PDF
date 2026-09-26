import httpx
import pytest
from google.genai.errors import APIError

from app.schemas.retrieval_schema import RetrievedChunk
from app.services.cohere_reranker_provider import CohereRerankerProvider
from app.services.groq_generation_provider import GroqGenerationProvider
from app.services.gemini_service import GeminiGenerationProvider
from app.services.openrouter_generation_provider import OpenRouterGenerationProvider
from app.services.provider_errors import ProviderError, ProviderErrorCategory


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


def make_chunk(chunk_id, content):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        heading=f"Section {chunk_id}",
        content=content,
        distance=0.2,
    )


@pytest.mark.parametrize(
    ("provider_class", "endpoint", "model"),
    [
        (
            OpenRouterGenerationProvider,
            "https://openrouter.ai/api/v1/chat/completions",
            "vendor/model-x",
        ),
        (
            GroqGenerationProvider,
            "https://api.groq.com/openai/v1/chat/completions",
            "vendor/model-y",
        ),
    ],
)
def test_openai_compatible_generation_providers_extract_text_and_usage(
    monkeypatch, provider_class, endpoint, model
):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse(
            200,
            {
                "choices": [{"message": {"content": "Generated text"}}],
                "usage": {"prompt_tokens": 8, "completion_tokens": 4},
            },
        )

    monkeypatch.setattr("app.services.openai_compatible_provider.httpx.post", fake_post)
    provider = provider_class(api_key="secret-test-key", model=model)

    result = provider.generate_with_metadata("prompt body")

    assert captured["url"] == endpoint
    assert captured["headers"]["Authorization"] == "Bearer secret-test-key"
    assert captured["json"]["model"] == model
    assert result.text == "Generated text"
    assert result.model == model
    assert result.usage == {"prompt_tokens": 8, "completion_tokens": 4}


@pytest.mark.parametrize(
    "provider_class",
    [OpenRouterGenerationProvider, GroqGenerationProvider],
)
def test_generation_provider_normalizes_auth_rate_limit_and_timeout(
    monkeypatch, provider_class
):
    provider = provider_class(api_key="key", model="configured-model")

    monkeypatch.setattr(
        "app.services.openai_compatible_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(401, {"error": "secret details"}),
    )
    with pytest.raises(ProviderError) as auth_error:
        provider.generate("prompt")
    assert (
        auth_error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    )
    assert "secret details" not in str(auth_error.value)

    monkeypatch.setattr(
        "app.services.openai_compatible_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(429, {"error": "rate limit"}),
    )
    with pytest.raises(ProviderError) as rate_error:
        provider.generate("prompt")
    assert rate_error.value.category == ProviderErrorCategory.RATE_LIMIT
    assert rate_error.value.retryable is True

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout("provider timed out")

    monkeypatch.setattr("app.services.openai_compatible_provider.httpx.post", timeout)
    with pytest.raises(ProviderError) as timeout_error:
        provider.generate("prompt")
    assert timeout_error.value.category == ProviderErrorCategory.TIMEOUT
    assert timeout_error.value.retryable is True


@pytest.mark.parametrize(
    "provider_class",
    [OpenRouterGenerationProvider, GroqGenerationProvider],
)
def test_generation_provider_rejects_malformed_response(monkeypatch, provider_class):
    monkeypatch.setattr(
        "app.services.openai_compatible_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(200, {"choices": []}),
    )
    provider = provider_class(api_key="key", model="configured-model")

    with pytest.raises(ProviderError) as error:
        provider.generate("prompt")

    assert error.value.category == ProviderErrorCategory.INVALID_RESPONSE


def test_missing_generation_credentials_fail_as_configuration_error():
    provider = OpenRouterGenerationProvider(api_key="", model="configured-model")

    with pytest.raises(ProviderError) as error:
        provider.generate("prompt")

    assert error.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


@pytest.mark.parametrize(
    ("status_code", "payload", "expected"),
    [
        (
            429,
            {
                "error": {
                    "code": 429,
                    "message": "quota exceeded",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
            ProviderErrorCategory.QUOTA,
        ),
        (
            503,
            {"error": {"code": 503, "message": "temporary provider details"}},
            ProviderErrorCategory.UNAVAILABLE,
        ),
    ],
)
def test_gemini_sdk_errors_are_normalized(status_code, payload, expected):
    class FakeModels:
        def generate_content(self, **kwargs):
            raise APIError(status_code, payload)

    provider = GeminiGenerationProvider(type("Client", (), {"models": FakeModels()})())

    with pytest.raises(ProviderError) as error:
        provider.generate("prompt")

    assert error.value.category == expected
    assert error.value.retryable is True
    assert "temporary provider details" not in str(error.value)


def test_cohere_reranker_maps_result_indices_back_to_chunks(monkeypatch):
    chunks = [make_chunk(1, "First evidence"), make_chunk(2, "Second evidence")]
    captured = {}

    def fake_post(url, **kwargs):
        captured.update(kwargs)
        return FakeResponse(200, {"results": [{"index": 1}, {"index": 0}]})

    monkeypatch.setattr("app.services.cohere_reranker_provider.httpx.post", fake_post)
    provider = CohereRerankerProvider(api_key="secret", model="rerank-model")

    result = provider.rerank("question", chunks)

    assert [chunk.chunk_id for chunk in result] == [2, 1]
    assert captured["json"]["model"] == "rerank-model"
    assert captured["json"]["query"] == "question"


def test_cohere_empty_input_does_not_call_provider(monkeypatch):
    def unexpected_call(*args, **kwargs):
        raise AssertionError("empty rerank must not make a provider call")

    monkeypatch.setattr(
        "app.services.cohere_reranker_provider.httpx.post", unexpected_call
    )
    provider = CohereRerankerProvider(api_key="secret", model="rerank-model")

    assert provider.rerank("question", []) == []


def test_cohere_malformed_indices_fail_as_invalid_response(monkeypatch):
    monkeypatch.setattr(
        "app.services.cohere_reranker_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(200, {"results": [{"index": 99}]}),
    )
    provider = CohereRerankerProvider(api_key="secret", model="rerank-model")

    with pytest.raises(ProviderError) as error:
        provider.rerank("question", [make_chunk(1, "Evidence")])

    assert error.value.category == ProviderErrorCategory.INVALID_RESPONSE


def test_cohere_empty_ranking_for_nonempty_input_is_invalid_response(monkeypatch):
    monkeypatch.setattr(
        "app.services.cohere_reranker_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(200, {"results": []}),
    )
    provider = CohereRerankerProvider(api_key="secret", model="rerank-model")

    with pytest.raises(ProviderError) as error:
        provider.rerank("question", [make_chunk(1, "Evidence")])

    assert error.value.category == ProviderErrorCategory.INVALID_RESPONSE


def test_cohere_rate_limit_is_normalized(monkeypatch):
    monkeypatch.setattr(
        "app.services.cohere_reranker_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(429, {"message": "quota exceeded"}),
    )
    provider = CohereRerankerProvider(api_key="secret", model="rerank-model")

    with pytest.raises(ProviderError) as error:
        provider.rerank("question", [make_chunk(1, "Evidence")])

    assert error.value.category == ProviderErrorCategory.QUOTA
    assert error.value.retryable is True
