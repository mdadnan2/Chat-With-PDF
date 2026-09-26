from types import SimpleNamespace

import pytest

from app.agents.analyst_agent import AnalystAgent
from app.agents.document_agent import DocumentAgent
from app.agents.research_agent import ResearchAgent
from app.agents.summary_agent import SummaryAgent
from app.schemas.agent_schema import AgentRunRequest, AgentType
from app.schemas.chat_schema import ChatResponse
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
)
from app.services.chat_service import ChatService
from app.services.gemini_service import (
    GeminiGenerationProvider,
    GeminiRerankerProvider,
)


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
    def __init__(self, ranked_chunks=None, error=None):
        self.ranked_chunks = ranked_chunks
        self.error = error
        self.calls = []

    def rerank(self, question, chunks):
        self.calls.append((question, chunks))
        if self.error:
            raise self.error
        return self.ranked_chunks or list(reversed(chunks))


def make_chunk(chunk_id, distance):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="document-1",
        heading=f"Section {chunk_id}",
        content=f"Content {chunk_id}",
        distance=distance,
    )


def make_execution(chunks):
    retrieval = FakeRetrievalService(chunks)
    generation = FakeGenerationProvider()
    reranker = FakeRerankerProvider()
    return (
        AIExecutionService(retrieval, generation, reranker),
        retrieval,
        generation,
        reranker,
    )


@pytest.mark.parametrize(
    ("agent_class", "agent_type", "top_k", "rerank"),
    [
        (ResearchAgent, AgentType.RESEARCH, 10, True),
        (SummaryAgent, AgentType.SUMMARY, 8, False),
        (AnalystAgent, AgentType.ANALYST, 8, False),
        (DocumentAgent, AgentType.DOCUMENT, 8, False),
    ],
)
def test_each_agent_uses_shared_execution_policy(
    agent_class,
    agent_type,
    top_k,
    rerank,
):
    chunks = [make_chunk(1, 0.11), make_chunk(2, 0.23)]
    execution, retrieval, generation, reranker = make_execution(chunks)
    request = AgentRunRequest(
        agent=agent_type,
        document_id="document-1",
        question="Summarize the important findings",
        mode="executive",
    )

    result = agent_class(execution).run(request, "user-1", object())

    assert result.agent == agent_type.value
    assert result.status == "completed"
    assert result.answer == "Generated answer"
    assert len(result.sources) == 2
    assert retrieval.calls[0]["user_id"] == "user-1"
    assert retrieval.calls[0]["document_id"] == "document-1"
    assert retrieval.calls[0]["top_k"] == top_k
    assert retrieval.calls[0]["distance_threshold"] == 0.55
    assert len(reranker.calls) == int(rerank and len(chunks) > 1)
    assert len(generation.prompts) == 1
    assert result.verification is None

    if agent_type in (AgentType.SUMMARY, AgentType.DOCUMENT):
        assert result.summary == result.answer


def test_chat_uses_shared_execution_and_preserves_response_contract():
    chunks = [make_chunk(1, 0.11), make_chunk(2, 0.23)]
    execution, retrieval, generation, reranker = make_execution(chunks)

    result = ChatService(execution).chat(
        question="What are the key findings?",
        document_id="document-1",
        user_id="user-1",
        db=object(),
    )

    assert isinstance(result, ChatResponse)
    assert result.answer == "Generated answer"
    assert result.sources[0].chunk_id == 2
    assert retrieval.calls[0]["top_k"] == 10
    assert len(reranker.calls) == 1
    assert len(generation.prompts) == 1


def test_chat_preserves_no_relevant_chunks_response():
    execution, _, generation, reranker = make_execution([])

    result = ChatService(execution).chat(
        question="Unanswerable question",
        document_id="document-1",
        user_id="user-1",
        db=object(),
    )

    assert (
        result.answer
        == "I couldn't find any relevant information in the provided document."
    )
    assert result.sources == []
    assert generation.prompts == []
    assert reranker.calls == []


def test_reranking_failure_falls_back_to_vector_order():
    chunks = [make_chunk(1, 0.11), make_chunk(2, 0.23)]
    retrieval = FakeRetrievalService(chunks)
    generation = FakeGenerationProvider()
    reranker = FakeRerankerProvider(error=RuntimeError("provider unavailable"))
    execution = AIExecutionService(retrieval, generation, reranker)

    context = execution.execute(
        question="Find the point",
        user_id="user-1",
        document_id="document-1",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.ALWAYS),
        prompt_builder=lambda text, question: f"{question}\n{text}",
    )

    assert [source.chunk_id for source in context.sources] == [1, 2]
    assert context.metadata.reranking_calls == 1
    assert context.metadata.reranking_failures == 1
    assert context.metadata.generation_calls == 1


def test_gemini_adapters_use_injected_client_without_external_calls():
    class FakeModels:
        def __init__(self):
            self.contents = []

        def generate_content(self, **kwargs):
            self.contents.append(kwargs["contents"])
            return SimpleNamespace(
                text="2,1" if "ONLY" in kwargs["contents"] else "Generated"
            )

    models = FakeModels()
    client = SimpleNamespace(models=models)
    generation = GeminiGenerationProvider(client)
    reranker = GeminiRerankerProvider(client)
    chunks = [make_chunk(1, 0.1), make_chunk(2, 0.2)]

    assert generation.generate("answer prompt") == "Generated"
    assert [chunk.chunk_id for chunk in reranker.rerank("question", chunks)] == [2, 1]
    assert len(models.contents) == 2
