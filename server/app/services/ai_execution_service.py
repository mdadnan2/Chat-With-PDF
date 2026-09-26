from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Callable

from sqlalchemy.orm import Session

from app.schemas.retrieval_schema import RetrievedChunk
from app.schemas.source_schema import Source
from app.services.provider_errors import ProviderError, ProviderErrorCategory
from app.services.provider_interfaces import (
    GenerationProvider,
    GenerationResult,
    RerankerProvider,
)
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
    generation_provider: str | None = None
    generation_model: str | None = None
    reranker_provider: str | None = None
    reranker_model: str | None = None
    fallback_used: bool = False
    provider_error_category: str | None = None
    generation_latency_ms: float | None = None
    reranking_latency_ms: float | None = None
    token_usage: dict[str, int] | None = None

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
        context.answer = self._generate(prompt, context.metadata)
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
        context.answer = self._generate(prompt, context.metadata)
        return context

    def _generate(self, prompt: str, metadata: ExecutionMetadata) -> str:
        started = perf_counter()
        provider = self.generation
        try:
            generate_with_metadata = getattr(provider, "generate_with_metadata", None)
            if callable(generate_with_metadata):
                result = generate_with_metadata(prompt)
                if not isinstance(result, GenerationResult):
                    raise ProviderError(
                        category=ProviderErrorCategory.INVALID_RESPONSE,
                        provider=getattr(provider, "provider_name", "unknown"),
                    )
            else:
                text = provider.generate(prompt)
                if not isinstance(text, str) or not text.strip():
                    raise ProviderError(
                        category=ProviderErrorCategory.INVALID_RESPONSE,
                        provider=getattr(provider, "provider_name", "unknown"),
                    )
                result = GenerationResult(
                    text=text,
                    provider=getattr(provider, "provider_name", None),
                    model=getattr(provider, "model_name", None),
                )
        except ProviderError as exc:
            metadata.provider_error_category = exc.category.value
            raise
        finally:
            metadata.generation_latency_ms = (perf_counter() - started) * 1000

        metadata.generation_provider = result.provider
        metadata.generation_model = result.model
        metadata.fallback_used = result.fallback_used
        if result.provider_error_category is not None:
            metadata.provider_error_category = result.provider_error_category
        metadata.generation_latency_ms = (
            result.latency_ms or metadata.generation_latency_ms
        )
        metadata.token_usage = result.usage
        return result.text

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
            context.metadata.reranker_provider = getattr(
                self.reranker, "provider_name", None
            )
            context.metadata.reranker_model = getattr(self.reranker, "model_name", None)
            rerank_started = perf_counter()
            try:
                selected = self.reranker.rerank(question, retrieved)
            except ProviderError as exc:
                context.metadata.reranking_failures = 1
                context.metadata.provider_error_category = exc.category.value
                selected = retrieved
            finally:
                context.metadata.reranking_latency_ms = (
                    perf_counter() - rerank_started
                ) * 1000

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
    from app.services.provider_factory import (
        get_generation_provider,
        get_reranker_provider,
    )

    return AIExecutionService(
        retrieval=RetrievalService(),
        generation=get_generation_provider(),
        reranker=get_reranker_provider(),
    )
