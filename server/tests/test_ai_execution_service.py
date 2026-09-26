from app.schemas.retrieval_schema import RetrievedChunk
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
)
from app.services.provider_interfaces import GenerationResult


class FakeRetrievalService:
    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def retrieve(self, **kwargs):
        self.calls.append(kwargs)
        return self.chunks


class FakeGenerationProvider:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return "Generated answer"


class FakeRerankerProvider:
    def __init__(self, ranked_chunks):
        self.ranked_chunks = ranked_chunks
        self.questions = []

    def rerank(self, question, chunks):
        self.questions.append(question)
        return self.ranked_chunks


def make_chunk(chunk_id, distance):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="document-1",
        heading=f"Section {chunk_id}",
        content=f"Content {chunk_id}",
        distance=distance,
    )


def test_shared_execution_tracks_calls_and_preserves_ownership_context():
    retrieved = [make_chunk(1, 0.12), make_chunk(2, 0.24)]
    reranked = list(reversed(retrieved))
    retrieval = FakeRetrievalService(retrieved)
    generation = FakeGenerationProvider()
    reranker = FakeRerankerProvider(reranked)
    execution = AIExecutionService(retrieval, generation, reranker)

    context = execution.execute(
        question="Compare the findings",
        user_id="user-1",
        document_id="document-1",
        db=object(),
        policy=ExecutionPolicy(
            top_k=10,
            context_chunk_count=1,
            rerank_mode=RerankMode.ALWAYS,
        ),
        prompt_builder=lambda text, question: f"{question}\n{text}",
    )

    assert retrieval.calls[0]["user_id"] == "user-1"
    assert retrieval.calls[0]["document_id"] == "document-1"
    assert reranker.questions == ["Compare the findings"]
    assert generation.prompts == ["Compare the findings\nContent 2"]
    assert context.answer == "Generated answer"
    assert [source.chunk_id for source in context.sources] == [2]
    assert context.sources[0].similarity == 0.24
    assert context.metadata.embedding_calls == 1
    assert context.metadata.retrieval_calls == 1
    assert context.metadata.reranking_calls == 1
    assert context.metadata.generation_calls == 1
    assert context.metadata.verification_calls == 0
    assert context.metadata.total_model_calls == 3


def test_shared_execution_skips_reranking_and_generation_for_no_results():
    retrieval = FakeRetrievalService([])
    generation = FakeGenerationProvider()
    reranker = FakeRerankerProvider([])
    execution = AIExecutionService(retrieval, generation, reranker)

    context = execution.execute(
        question="Find the risks",
        user_id="user-1",
        document_id="document-1",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.ALWAYS),
        prompt_builder=lambda text, question: f"{question}\n{text}",
    )

    assert context.answer is None
    assert context.sources == []
    assert reranker.questions == []
    assert generation.prompts == []
    assert context.metadata.embedding_calls == 1
    assert context.metadata.retrieval_calls == 1
    assert context.metadata.reranking_calls == 0
    assert context.metadata.generation_calls == 0
    assert context.metadata.total_model_calls == 1


def test_execution_records_provider_fallback_latency_and_real_usage_metadata():
    class MetadataGenerationProvider:
        provider_name = "openrouter"
        model_name = "configured-model"

        def generate(self, prompt):
            return "Generated answer"

        def generate_with_metadata(self, prompt):
            return GenerationResult(
                text="Generated answer",
                provider="groq",
                model="fallback-model",
                fallback_used=True,
                provider_error_category="rate_limit",
                latency_ms=12.5,
                usage={"prompt_tokens": 17, "completion_tokens": 8},
            )

    execution = AIExecutionService(
        FakeRetrievalService([make_chunk(1, 0.2)]),
        MetadataGenerationProvider(),
        FakeRerankerProvider([]),
    )

    context = execution.execute(
        question="question",
        user_id="user-1",
        document_id="document-1",
        db=object(),
        policy=ExecutionPolicy(),
        prompt_builder=lambda text, question: f"{question}\n{text}",
    )

    assert context.metadata.generation_provider == "groq"
    assert context.metadata.generation_model == "fallback-model"
    assert context.metadata.fallback_used is True
    assert context.metadata.provider_error_category == "rate_limit"
    assert context.metadata.generation_latency_ms == 12.5
    assert context.metadata.token_usage == {
        "prompt_tokens": 17,
        "completion_tokens": 8,
    }
