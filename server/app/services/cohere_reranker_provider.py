from __future__ import annotations

from typing import Any

import httpx

from app.schemas.retrieval_schema import RetrievedChunk
from app.services.provider_errors import (
    ProviderError,
    ProviderErrorCategory,
    normalize_http_error,
)
from app.services.provider_interfaces import RerankerProvider


class CohereRerankerProvider(RerankerProvider):
    provider_name = "cohere"
    endpoint = "https://api.cohere.com/v2/rerank"

    def __init__(self, api_key: str, model: str, timeout: float = 30.0):
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []
        if not self.api_key or not self.model_name:
            raise ProviderError(
                ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
                provider=self.provider_name,
            )

        documents = [f"Heading: {chunk.heading}\n{chunk.content}" for chunk in chunks]
        try:
            response = httpx.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "query": question,
                    "documents": documents,
                    "top_n": min(5, len(chunks)),
                },
                timeout=self.timeout,
            )
        except httpx.TimeoutException as exc:
            raise ProviderError(
                ProviderErrorCategory.TIMEOUT,
                provider=self.provider_name,
                retryable=True,
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE,
                provider=self.provider_name,
                retryable=True,
            ) from exc

        if response.status_code >= 400:
            raise normalize_http_error(
                self.provider_name,
                response.status_code,
                self._safe_json(response),
            )

        try:
            result: Any = response.json()
            ranked_results = result["results"]
            if not isinstance(ranked_results, list):
                raise TypeError
            indexes = [item["index"] for item in ranked_results]
            if not indexes or any(
                not isinstance(index, int)
                or isinstance(index, bool)
                or index < 0
                or index >= len(chunks)
                for index in indexes
            ):
                raise ValueError
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            ) from exc

        ordered = []
        seen = set()
        for index in indexes:
            if index not in seen:
                ordered.append(chunks[index])
                seen.add(index)
        ordered.extend(chunk for index, chunk in enumerate(chunks) if index not in seen)
        return ordered

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text
