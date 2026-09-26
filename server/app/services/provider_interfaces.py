from __future__ import annotations

from typing import Protocol

from app.schemas.retrieval_schema import RetrievedChunk


class GenerationProvider(Protocol):
    def generate(self, prompt: str) -> str: ...


class RerankerProvider(Protocol):
    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]: ...
