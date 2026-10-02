"""
Comprehensive tests for production-grade provider failover:
- Generation chain configuration and failover
- Reranker chain configuration and failover
- Strands routing failover
- Metadata accuracy after fallback
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.schemas.agent_schema import AgentRoute, AgentType
from app.schemas.retrieval_schema import RetrievedChunk
from app.services import strands_router_model as srm_module
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
)
from app.services.provider_errors import ProviderError, ProviderErrorCategory
from app.services.provider_factory import (
    ChainedGenerationProvider,
    FallbackGenerationProvider,
    FallbackRerankerProvider,
    get_generation_provider,
    get_reranker_provider,
)
from app.services.provider_interfaces import GenerationResult


# ---------------------------------------------------------------------------
# Shared stubs
# ---------------------------------------------------------------------------


def _retryable(category: ProviderErrorCategory, provider: str = "p") -> ProviderError:
    return ProviderError(category, provider=provider, retryable=True)


def _non_retryable(
    category: ProviderErrorCategory, provider: str = "p"
) -> ProviderError:
    return ProviderError(category, provider=provider, retryable=False)


class StubGenProvider:
    def __init__(self, name: str, error=None, text: str = "ok"):
        self.provider_name = name
        self.model_name = f"{name}-model"
        self.error = error
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        if self.error:
            raise self.error
        return "ok"

    def generate_with_metadata(self, prompt: str) -> GenerationResult:
        self.calls.append(prompt)
        if self.error:
            raise self.error
        return GenerationResult(
            text="ok",
            provider=self.provider_name,
            model=self.model_name,
            latency_ms=5.0,
            usage={"prompt_tokens": 10, "completion_tokens": 5},
        )


class StubReranker:
    def __init__(self, name: str, error=None):
        self.provider_name = name
        self.model_name = f"{name}-rerank-model"
        self.error = error
        self.calls: list = []

    def rerank(self, question: str, chunks):
        self.calls.append(question)
        if self.error:
            raise self.error
        return list(reversed(chunks))


def make_chunk(chunk_id: int) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        heading=f"Section {chunk_id}",
        content=f"Content {chunk_id}",
        distance=0.2,
    )


# ---------------------------------------------------------------------------
# A. Generation configuration
# ---------------------------------------------------------------------------


class MinimalConfig:
    google_api_key = "gkey"
    gemini_chat_model = "gemini-model"
    generation_provider = "gemini"
    generation_fallback_provider = ""
    generation_secondary_fallback_provider = ""
    reranker_provider = "gemini"
    reranker_fallback_provider = ""
    openrouter_api_key = "orkey"
    openrouter_model = "or-model"
    groq_api_key = "groqkey"
    groq_model = "groq-model"
    cohere_api_key = "coherekey"
    cohere_rerank_model = "cohere-rerank-model"
    provider_timeout_seconds = 10.0


def test_generation_primary_only(monkeypatch):
    from app.services import provider_factory
    monkeypatch.setattr(provider_factory.genai, "Client", lambda **kw: object())
    cfg = MinimalConfig()
    provider = get_generation_provider(cfg)
    from app.services.gemini_service import GeminiGenerationProvider
    assert isinstance(provider, GeminiGenerationProvider)


def test_generation_primary_plus_fallback(monkeypatch):
    from app.services import provider_factory
    monkeypatch.setattr(provider_factory.genai, "Client", lambda **kw: object())
    cfg = MinimalConfig()
    cfg.generation_fallback_provider = "groq"
    provider = get_generation_provider(cfg)
    assert isinstance(provider, FallbackGenerationProvider)
    from app.services.gemini_service import GeminiGenerationProvider
    from app.services.groq_generation_provider import GroqGenerationProvider
    assert isinstance(provider.providers[0], GeminiGenerationProvider)
    assert isinstance(provider.providers[1], GroqGenerationProvider)


def test_generation_primary_fallback_secondary(monkeypatch):
    from app.services import provider_factory
    monkeypatch.setattr(provider_factory.genai, "Client", lambda **kw: object())
    cfg = MinimalConfig()
    cfg.generation_fallback_provider = "groq"
    cfg.generation_secondary_fallback_provider = "openrouter"
    provider = get_generation_provider(cfg)
    assert isinstance(provider, ChainedGenerationProvider)
    assert len(provider.providers) == 3


def test_generation_duplicate_primary_fallback_rejected():
    cfg = MinimalConfig()
    cfg.generation_provider = "groq"
    cfg.generation_fallback_provider = "groq"
    with pytest.raises(ProviderError) as exc:
        get_generation_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    assert "groq" in exc.value.public_message


def test_generation_duplicate_in_secondary_rejected():
    cfg = MinimalConfig()
    cfg.generation_provider = "gemini"
    cfg.generation_fallback_provider = "groq"
    cfg.generation_secondary_fallback_provider = "groq"
    with pytest.raises(ProviderError) as exc:
        get_generation_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


def test_generation_unsupported_provider_rejected():
    cfg = MinimalConfig()
    cfg.generation_provider = "unknown-vendor"
    with pytest.raises(ProviderError) as exc:
        get_generation_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER


def test_generation_missing_credentials_rejected():
    cfg = MinimalConfig()
    cfg.generation_provider = "groq"
    cfg.groq_api_key = ""
    with pytest.raises(ProviderError) as exc:
        get_generation_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


# ---------------------------------------------------------------------------
# B. Generation failover
# ---------------------------------------------------------------------------


def _chain(*providers) -> ChainedGenerationProvider:
    return ChainedGenerationProvider(list(providers))


def test_generation_primary_succeeds_fallback_not_called():
    primary = StubGenProvider("primary")
    fallback = StubGenProvider("fallback")
    chain = _chain(primary, fallback)
    result = chain.generate_with_metadata("q")
    assert result.provider == "primary"
    assert result.fallback_used is False
    assert fallback.calls == []


@pytest.mark.parametrize(
    "category",
    [
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    ],
)
def test_generation_retryable_error_triggers_fallback(category):
    primary = StubGenProvider("primary", error=_retryable(category, "primary"))
    fallback = StubGenProvider("fallback")
    chain = _chain(primary, fallback)
    result = chain.generate_with_metadata("q")
    assert result.provider == "fallback"
    assert result.fallback_used is True
    assert result.provider_error_category == category.value


def test_generation_auth_error_does_not_fallback():
    primary = StubGenProvider(
        "primary",
        error=_non_retryable(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION, "primary"
        ),
    )
    fallback = StubGenProvider("fallback")
    chain = _chain(primary, fallback)
    with pytest.raises(ProviderError) as exc:
        chain.generate_with_metadata("q")
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    assert fallback.calls == []


def test_generation_invalid_response_does_not_fallback():
    primary = StubGenProvider(
        "primary",
        error=_non_retryable(ProviderErrorCategory.INVALID_RESPONSE, "primary"),
    )
    fallback = StubGenProvider("fallback")
    chain = _chain(primary, fallback)
    with pytest.raises(ProviderError) as exc:
        chain.generate_with_metadata("q")
    assert exc.value.category == ProviderErrorCategory.INVALID_RESPONSE
    assert fallback.calls == []


def test_generation_primary_and_fallback_fail_secondary_succeeds():
    primary = StubGenProvider("primary", error=_retryable(ProviderErrorCategory.QUOTA))
    fallback = StubGenProvider(
        "fallback", error=_retryable(ProviderErrorCategory.TIMEOUT)
    )
    secondary = StubGenProvider("secondary")
    chain = _chain(primary, fallback, secondary)
    result = chain.generate_with_metadata("q")
    assert result.provider == "secondary"
    assert result.fallback_used is True


def test_generation_all_providers_fail_raises_last_error():
    err = _retryable(ProviderErrorCategory.UNAVAILABLE)
    chain = _chain(
        StubGenProvider("p1", error=err),
        StubGenProvider("p2", error=err),
        StubGenProvider("p3", error=err),
    )
    with pytest.raises(ProviderError) as exc:
        chain.generate_with_metadata("q")
    assert exc.value.category == ProviderErrorCategory.UNAVAILABLE


# ---------------------------------------------------------------------------
# C. Generation metadata
# ---------------------------------------------------------------------------


def test_generation_metadata_reflects_actual_provider():
    primary = StubGenProvider("gemini", error=_retryable(ProviderErrorCategory.QUOTA))
    fallback = StubGenProvider("groq")
    chain = _chain(primary, fallback)
    result = chain.generate_with_metadata("q")
    assert result.provider == "groq"
    assert result.model == "groq-model"
    assert result.fallback_used is True
    assert result.provider_error_category == ProviderErrorCategory.QUOTA.value
    assert result.latency_ms == 5.0
    assert result.usage == {"prompt_tokens": 10, "completion_tokens": 5}


def test_generation_metadata_primary_success_no_fallback_flag():
    primary = StubGenProvider("gemini")
    chain = _chain(primary)
    result = chain.generate_with_metadata("q")
    assert result.provider == "gemini"
    assert result.fallback_used is False
    assert result.provider_error_category is None


# ---------------------------------------------------------------------------
# D. Reranker configuration
# ---------------------------------------------------------------------------


def test_reranker_primary_only(monkeypatch):
    from app.services import provider_factory
    monkeypatch.setattr(provider_factory.genai, "Client", lambda **kw: object())
    cfg = MinimalConfig()
    provider = get_reranker_provider(cfg)
    from app.services.gemini_service import GeminiRerankerProvider
    assert isinstance(provider, GeminiRerankerProvider)


def test_reranker_primary_plus_fallback(monkeypatch):
    from app.services import provider_factory
    monkeypatch.setattr(provider_factory.genai, "Client", lambda **kw: object())
    cfg = MinimalConfig()
    cfg.reranker_fallback_provider = "cohere"
    provider = get_reranker_provider(cfg)
    assert isinstance(provider, FallbackRerankerProvider)
    from app.services.gemini_service import GeminiRerankerProvider
    from app.services.cohere_reranker_provider import CohereRerankerProvider
    assert isinstance(provider.providers[0], GeminiRerankerProvider)
    assert isinstance(provider.providers[1], CohereRerankerProvider)


def test_reranker_duplicate_rejected():
    cfg = MinimalConfig()
    cfg.reranker_provider = "cohere"
    cfg.reranker_fallback_provider = "cohere"
    with pytest.raises(ProviderError) as exc:
        get_reranker_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


def test_reranker_unsupported_provider_rejected():
    cfg = MinimalConfig()
    cfg.reranker_provider = "unknown-reranker"
    with pytest.raises(ProviderError) as exc:
        get_reranker_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER


def test_reranker_missing_credentials_rejected():
    cfg = MinimalConfig()
    cfg.reranker_provider = "cohere"
    cfg.cohere_api_key = ""
    with pytest.raises(ProviderError) as exc:
        get_reranker_provider(cfg)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


# ---------------------------------------------------------------------------
# E. Reranker failover
# ---------------------------------------------------------------------------


def _reranker_chain(*providers) -> FallbackRerankerProvider:
    return FallbackRerankerProvider(list(providers))


def test_reranker_primary_succeeds():
    chunks = [make_chunk(1), make_chunk(2)]
    primary = StubReranker("gemini")
    chain = _reranker_chain(primary)
    result = chain.rerank("q", chunks)
    assert [c.chunk_id for c in result] == [2, 1]
    assert primary.calls == ["q"]


@pytest.mark.parametrize(
    "category",
    [
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    ],
)
def test_reranker_retryable_error_triggers_fallback(category):
    chunks = [make_chunk(1), make_chunk(2)]
    primary = StubReranker("gemini", error=_retryable(category, "gemini"))
    fallback = StubReranker("cohere")
    chain = _reranker_chain(primary, fallback)
    result, pname, mname = chain.rerank_with_info("q", chunks)
    assert pname == "cohere"
    assert [c.chunk_id for c in result] == [2, 1]


def test_reranker_auth_error_does_not_fallback():
    chunks = [make_chunk(1)]
    primary = StubReranker(
        "gemini",
        error=_non_retryable(
            ProviderErrorCategory.CONFIGURATION_AUTHENTICATION, "gemini"
        ),
    )
    fallback = StubReranker("cohere")
    chain = _reranker_chain(primary, fallback)
    with pytest.raises(ProviderError) as exc:
        chain.rerank("q", chunks)
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    assert fallback.calls == []


def test_reranker_all_fail_execution_service_falls_open():
    """When all rerankers fail, AIExecutionService returns retrieved chunks."""
    chunks = [make_chunk(1), make_chunk(2)]

    class FailingReranker:
        provider_name = "gemini"
        model_name = "gemini-model"

        def rerank(self, question, chunks):
            raise _retryable(ProviderErrorCategory.UNAVAILABLE, "gemini")

    class FakeRetrieval:
        def retrieve(self, **kw):
            return chunks

    class FakeGeneration:
        def generate(self, prompt):
            return "answer"

    execution = AIExecutionService(FakeRetrieval(), FakeGeneration(), FailingReranker())
    context = execution.execute(
        question="q",
        user_id="u",
        document_id="d",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.ALWAYS),
        prompt_builder=lambda text, q: f"{q}\n{text}",
    )
    assert [s.chunk_id for s in context.sources] == [1, 2]
    assert context.metadata.reranking_failures == 1
    assert context.answer == "answer"


# ---------------------------------------------------------------------------
# F. Reranker metadata
# ---------------------------------------------------------------------------


def test_reranker_metadata_reflects_actual_provider_after_fallback():
    chunks = [make_chunk(1), make_chunk(2)]
    primary = StubReranker("gemini", error=_retryable(ProviderErrorCategory.QUOTA))
    fallback = StubReranker("cohere")
    chain = _reranker_chain(primary, fallback)

    class FakeRetrieval:
        def retrieve(self, **kw):
            return chunks

    class FakeGeneration:
        def generate(self, prompt):
            return "answer"

    execution = AIExecutionService(FakeRetrieval(), FakeGeneration(), chain)
    context = execution.execute(
        question="q",
        user_id="u",
        document_id="d",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.ALWAYS),
        prompt_builder=lambda text, q: f"{q}\n{text}",
    )
    assert context.metadata.reranker_provider == "cohere"
    assert context.metadata.reranker_model == "cohere-rerank-model"
    assert context.metadata.reranker_fallback_used is True


def test_reranker_metadata_primary_success_no_fallback_flag():
    chunks = [make_chunk(1), make_chunk(2)]
    primary = StubReranker("gemini")
    chain = _reranker_chain(primary)

    class FakeRetrieval:
        def retrieve(self, **kw):
            return chunks

    class FakeGeneration:
        def generate(self, prompt):
            return "answer"

    execution = AIExecutionService(FakeRetrieval(), FakeGeneration(), chain)
    context = execution.execute(
        question="q",
        user_id="u",
        document_id="d",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.ALWAYS),
        prompt_builder=lambda text, q: f"{q}\n{text}",
    )
    assert context.metadata.reranker_provider == "gemini"
    assert context.metadata.reranker_fallback_used is False


# ---------------------------------------------------------------------------
# G. Strands routing failover
# ---------------------------------------------------------------------------


class StrandsFakeSettings:
    generation_provider = "gemini"
    generation_fallback_provider = "groq"
    generation_secondary_fallback_provider = "openrouter"
    google_api_key = "gkey"
    gemini_chat_model = "gemini-model"
    groq_api_key = "groqkey"
    groq_model = "groq-model"
    openrouter_api_key = "orkey"
    openrouter_model = "or-model"


def _good_agent():
    class FakeAgent:
        def __init__(self, **_kw):
            pass

        def __call__(self, *_a, **_kw):
            return SimpleNamespace(
                structured_output={"agent": "research", "reason": "factual"}
            )

    return FakeAgent


def test_strands_primary_succeeds_no_fallback(monkeypatch):
    built = []

    def build(config):
        built.append(config.generation_provider)
        return object()

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", _good_agent())
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    result = router.route("What are the risks?")
    assert result == AgentRoute(agent=AgentType.RESEARCH, reason="factual")
    assert built == ["gemini"]


@pytest.mark.parametrize(
    "category",
    [
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    ],
)
def test_strands_retryable_error_triggers_fallback(monkeypatch, category):
    call_count = [0]

    def build(config):
        return SimpleNamespace(provider=config.generation_provider)

    class FakeAgent:
        def __init__(self, model, **_kw):
            self.provider = model.provider

        def __call__(self, *_a, **_kw):
            call_count[0] += 1
            if self.provider == "gemini":
                raise ProviderError(category, provider="gemini", retryable=True)
            return SimpleNamespace(
                structured_output={"agent": "summary", "reason": "ok"}
            )

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", FakeAgent)
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    result = router.route("Summarize this.")
    assert result.agent == AgentType.SUMMARY
    assert call_count[0] == 2


def test_strands_auth_error_does_not_fallback(monkeypatch):
    def build(config):
        return object()

    class FakeAgent:
        def __init__(self, **_kw):
            pass

        def __call__(self, *_a, **_kw):
            raise ProviderError(
                ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
                provider="gemini",
                retryable=False,
            )

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", FakeAgent)
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    with pytest.raises(ProviderError) as exc:
        router.route("q")
    assert exc.value.category == ProviderErrorCategory.CONFIGURATION_AUTHENTICATION


def test_strands_invalid_structured_output_does_not_fallback(monkeypatch):
    call_count = [0]

    def build(config):
        return object()

    class FakeAgent:
        def __init__(self, **_kw):
            pass

        def __call__(self, *_a, **_kw):
            call_count[0] += 1
            return SimpleNamespace(structured_output={"agent": "unknown_agent", "reason": "x"})

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", FakeAgent)
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    with pytest.raises(ProviderError) as exc:
        router.route("q")
    assert exc.value.category == ProviderErrorCategory.INVALID_RESPONSE
    assert call_count[0] == 1


def test_strands_all_providers_fail_raises_error(monkeypatch):
    def build(config):
        return object()

    class FakeAgent:
        def __init__(self, **_kw):
            pass

        def __call__(self, *_a, **_kw):
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE, provider="p", retryable=True
            )

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", FakeAgent)
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    with pytest.raises(ProviderError) as exc:
        router.route("q")
    assert exc.value.category == ProviderErrorCategory.UNAVAILABLE


def test_strands_lazy_initialization(monkeypatch):
    built = []

    def build(config):
        built.append(config.generation_provider)
        return object()

    monkeypatch.setattr(srm_module, "_build_model", build)
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    assert built == []
    # No route call yet — nothing built


def test_strands_unused_providers_not_initialized(monkeypatch):
    built = []

    def build(config):
        built.append(config.generation_provider)
        return object()

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", _good_agent())
    router = srm_module.StrandsRouterModel(config=StrandsFakeSettings())
    router.route("q")
    # Primary succeeded — only gemini should be built
    assert built == ["gemini"]
    assert "groq" not in built
    assert "openrouter" not in built


def test_strands_primary_only_config_passes_config_directly(monkeypatch):
    """Single-provider chain passes config object directly to _build_model."""
    received = []

    def build(config):
        received.append(config)
        return object()

    monkeypatch.setattr(srm_module, "_build_model", build)
    monkeypatch.setattr(srm_module, "Agent", _good_agent())

    class SingleProviderSettings:
        generation_provider = "gemini"
        generation_fallback_provider = ""
        generation_secondary_fallback_provider = ""
        google_api_key = "gkey"
        gemini_chat_model = "gemini-model"
        groq_api_key = ""
        groq_model = ""
        openrouter_api_key = ""
        openrouter_model = ""

    cfg = SingleProviderSettings()
    router = srm_module.StrandsRouterModel(config=cfg)
    router.route("q")
    assert received[0] is cfg
