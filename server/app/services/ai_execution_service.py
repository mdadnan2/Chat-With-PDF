from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from sqlalchemy.orm import Session

from app.schemas.retrieval_schema import RetrievedChunk
from app.schemas.source_schema import Source
from app.services.provider_interfaces import GenerationProvider, RerankerProvider
from app.services.retrieval_service import RetrievalService


class RerankMode(str, Enum):
    ALWAYS = "always"
    WHEN_MULTIPLE_CANDIDATES = "when_multiple_candidates"
    NEVER = "never"


def should_rerank(mode: RerankMode, chunks: list[RetrievedChunk]) -> bool:
    if not chunks or mode == RerankMode.NEVER:
        return False
    if mode == RerankMode.ALWAYS:
        return True
    return len(chunks) > 1


@dataclass(frozen=True)
class ExecutionPolicy:
    top_k: int = 10
    retrieval_distance_threshold: float = 0.55
    context_chunk_count: int = 5
    rerank_mode: RerankMode = RerankMode.NEVER


@dataclass
class ExecutionMetadata:
    embedding_calls: int = 0
    retrieval_calls: int = 0
    reranking_calls: int = 0
    reranking_failures: int = 0
    generation_calls: int = 0
    verification_calls: int = 0

    @property
    def total_model_calls(self) -> int:
        return (
            self.embedding_calls
            + self.reranking_calls
            + self.generation_calls
            + self.verification_calls
        )


@dataclass
class ExecutionContext:
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)
    selected_chunks: list[RetrievedChunk] = field(default_factory=list)
    context_text: str = ""
    answer: str | None = None
    sources: list[Source] = field(default_factory=list)
    metadata: ExecutionMetadata = field(default_factory=ExecutionMetadata)


class AIExecutionService:
    def __init__(
        self,
        retrieval: RetrievalService,
        generation: GenerationProvider,
        reranker: RerankerProvider,
    ):
        self.retrieval = retrieval
        self.generation = generation
        self.reranker = reranker

    def execute(
        self,
        question: str,
        user_id: str,
        document_id: str,
        db: Session,
        policy: ExecutionPolicy,
        prompt_builder: Callable[[str, str], str],
    ) -> ExecutionContext:
        context = self._prepare_context(
            question=question,
            user_id=user_id,
            document_id=document_id,
            db=db,
            policy=policy,
        )

        if not context.retrieved_chunks:
            return context

        prompt = prompt_builder(context.context_text, question)
        context.metadata.generation_calls = 1
        context.answer = self.generation.generate(prompt)
        return context

    def verify_claim(
        self,
        claim: str,
        user_id: str,
        document_id: str,
        db: Session,
        policy: ExecutionPolicy,
        prompt_builder: Callable[[str, str], str],
    ) -> ExecutionContext:
        context = self._prepare_context(
            question=claim,
            user_id=user_id,
            document_id=document_id,
            db=db,
            policy=policy,
        )
        if not context.retrieved_chunks:
            return context

        evidence = "\n\n".join(
            f"[chunk_id: {chunk.chunk_id}]\nHeading: {chunk.heading}\n{chunk.content}"
            for chunk in context.selected_chunks
        )
        prompt = prompt_builder(evidence, claim)
        context.metadata.verification_calls = 1
        context.answer = self.generation.generate(prompt)
        return context

    def _prepare_context(
        self,
        question: str,
        user_id: str,
        document_id: str,
        db: Session,
        policy: ExecutionPolicy,
    ) -> ExecutionContext:
        context = ExecutionContext()
        retrieved = self.retrieval.retrieve(
            question=question,
            db=db,
            user_id=user_id,
            document_id=document_id,
            top_k=policy.top_k,
            distance_threshold=policy.retrieval_distance_threshold,
        )
        context.metadata.embedding_calls = 1
        context.metadata.retrieval_calls = 1
        context.retrieved_chunks = retrieved

        if not retrieved:
            return context

        selected = retrieved
        if should_rerank(policy.rerank_mode, retrieved):
            context.metadata.reranking_calls = 1
            try:
                selected = self.reranker.rerank(question, retrieved)
            except Exception:
                context.metadata.reranking_failures = 1
                selected = retrieved

        context.selected_chunks = selected[: policy.context_chunk_count]
        context.context_text = "\n\n".join(
            chunk.content for chunk in context.selected_chunks
        )
        context.sources = [
            Source(
                chunk_id=chunk.chunk_id,
                heading=chunk.heading,
                similarity=round(chunk.distance, 4),
            )
            for chunk in context.selected_chunks
        ]
        return context


def create_default_ai_execution_service() -> AIExecutionService:
    from app.services.gemini_service import GeminiService

    gemini = GeminiService()
    return AIExecutionService(
        retrieval=RetrievalService(),
        generation=gemini.generation_provider,
        reranker=gemini.reranker_provider,
    )
