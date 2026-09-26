from app.schemas.retrieval_schema import RetrievedChunk
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
    should_rerank,
)


class FakeRetrieval:
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, **kwargs):
        return self.chunks


class FakeGeneration:
    def generate(self, prompt):
        return "answer"


class FakeReranker:
    def __init__(self):
        self.calls = 0

    def rerank(self, question, chunks):
        self.calls += 1
        return list(reversed(chunks))


def chunk(chunk_id, distance):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        heading=f"Section {chunk_id}",
        content=f"Evidence {chunk_id}",
        distance=distance,
    )


def test_single_candidate_needs_no_reranking_even_when_distance_is_weak():
    strong = [chunk(1, 0.08)]
    weak = [chunk(1, 0.54)]

    assert should_rerank(RerankMode.WHEN_MULTIPLE_CANDIDATES, strong) is False
    assert should_rerank(RerankMode.WHEN_MULTIPLE_CANDIDATES, weak) is False


def test_multiple_candidates_are_reranked_for_ambiguous_and_weak_results():
    ambiguous = [chunk(1, 0.20), chunk(2, 0.21), chunk(3, 0.24)]
    weak = [chunk(1, 0.49), chunk(2, 0.53)]

    assert should_rerank(RerankMode.WHEN_MULTIPLE_CANDIDATES, ambiguous) is True
    assert should_rerank(RerankMode.WHEN_MULTIPLE_CANDIDATES, weak) is True


def test_no_retrieval_never_reranks():
    assert should_rerank(RerankMode.ALWAYS, []) is False


def test_policy_can_explicitly_enable_or_disable_reranking():
    candidates = [chunk(1, 0.2), chunk(2, 0.3)]

    assert should_rerank(RerankMode.ALWAYS, candidates) is True
    assert should_rerank(RerankMode.NEVER, candidates) is False


def test_execution_skips_single_candidate_rerank_and_tracks_call_count():
    candidates = [chunk(1, 0.2)]
    reranker = FakeReranker()
    execution = AIExecutionService(
        FakeRetrieval(candidates), FakeGeneration(), reranker
    )

    context = execution.execute(
        question="question",
        user_id="user-1",
        document_id="doc-1",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.WHEN_MULTIPLE_CANDIDATES),
        prompt_builder=lambda content, question: f"{question}: {content}",
    )

    assert reranker.calls == 0
    assert context.metadata.embedding_calls == 1
    assert context.metadata.reranking_calls == 0
    assert context.metadata.generation_calls == 1
    assert context.metadata.total_model_calls == 2


def test_execution_reranks_multiple_candidates_and_tracks_call_count():
    candidates = [chunk(1, 0.2), chunk(2, 0.3)]
    reranker = FakeReranker()
    execution = AIExecutionService(
        FakeRetrieval(candidates), FakeGeneration(), reranker
    )

    context = execution.execute(
        question="question",
        user_id="user-1",
        document_id="doc-1",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.WHEN_MULTIPLE_CANDIDATES),
        prompt_builder=lambda content, question: f"{question}: {content}",
    )

    assert reranker.calls == 1
    assert context.metadata.reranking_calls == 1
    assert context.metadata.total_model_calls == 3
