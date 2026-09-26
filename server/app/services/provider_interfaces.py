from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas.retrieval_schema import RetrievedChunk


class GenerationProvider(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str | None = None
    model: str | None = None
    fallback_used: bool = False
    provider_error_category: str | None = None
    latency_ms: float | None = None
    usage: dict[str, int] | None = None


class GenerationMetadataProvider(Protocol):
    def generate_with_metadata(self, prompt: str) -> GenerationResult: ...


class RerankerProvider(Protocol):
    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]: ...
