from time import perf_counter

from google import genai
from google.genai.errors import APIError

from app.config import settings
import re
import httpx
import requests
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.provider_errors import (
    ProviderError,
    ProviderErrorCategory,
    normalize_gemini_error,
)
from app.services.provider_interfaces import (
    GenerationProvider,
    GenerationResult,
    RerankerProvider,
)


class GeminiGenerationProvider(GenerationProvider):
    provider_name = "gemini"

    def __init__(self, client: genai.Client):
        self.client = client
        self.model_name = settings.gemini_chat_model

    def generate(self, prompt: str) -> str:
        return self.generate_with_metadata(prompt).text

    def generate_with_metadata(self, prompt: str) -> GenerationResult:
        started = perf_counter()
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except APIError as exc:
            raise normalize_gemini_error(exc) from exc
        except (
            TimeoutError,
            httpx.TimeoutException,
            requests.exceptions.Timeout,
        ):
            raise ProviderError(
                ProviderErrorCategory.TIMEOUT,
                provider=self.provider_name,
                retryable=True,
            ) from None
        except httpx.RequestError:
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE,
                provider=self.provider_name,
                retryable=True,
            ) from None
        except requests.exceptions.ConnectionError:
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE,
                provider=self.provider_name,
                retryable=True,
            ) from None

        try:
            text = response.text
        except (AttributeError, ValueError, TypeError) as exc:
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            ) from exc
        if not isinstance(text, str) or not text.strip():
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            )

        usage_metadata = getattr(response, "usage_metadata", None)
        usage = self._usage(usage_metadata)
        return GenerationResult(
            text=text,
            provider=self.provider_name,
            model=self.model_name,
            latency_ms=(perf_counter() - started) * 1000,
            usage=usage,
        )

    @staticmethod
    def _usage(metadata) -> dict[str, int] | None:
        if metadata is None:
            return None
        usage = {}
        for target, source in (
            ("prompt_tokens", "prompt_token_count"),
            ("completion_tokens", "candidates_token_count"),
            ("total_tokens", "total_token_count"),
        ):
            value = getattr(metadata, source, None)
            if isinstance(value, int) and not isinstance(value, bool):
                usage[target] = value
        return usage or None


class GeminiRerankerProvider(RerankerProvider):
    provider_name = "gemini"

    def __init__(self, client: genai.Client):
        self.client = client
        self.model_name = settings.gemini_chat_model

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        chunk_text = ""

        for index, chunk in enumerate(chunks, start=1):
            chunk_text += f"""
Chunk {index}

Heading:
{chunk.heading}

Content:
{chunk.content}

----------------------------------------
"""

        prompt = f"""
You are an expert retrieval reranker.

Your ONLY task is to rank the chunks.

Do NOT answer the question.

Question:
{question}

Chunks:

{chunk_text}

Return ONLY the 5 most relevant chunk numbers.

Example:
2,1,3,4,5
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except APIError as exc:
            raise normalize_gemini_error(exc) from exc
        except (
            TimeoutError,
            httpx.TimeoutException,
            requests.exceptions.Timeout,
        ):
            raise ProviderError(
                ProviderErrorCategory.TIMEOUT,
                provider=self.provider_name,
                retryable=True,
            ) from None
        except httpx.RequestError:
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE,
                provider=self.provider_name,
                retryable=True,
            ) from None
        except requests.exceptions.ConnectionError:
            raise ProviderError(
                ProviderErrorCategory.UNAVAILABLE,
                provider=self.provider_name,
                retryable=True,
            ) from None

        try:
            ranking_text = response.text
        except (AttributeError, ValueError, TypeError) as exc:
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            ) from exc
        if not isinstance(ranking_text, str) or not ranking_text.strip():
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            )
        ranking_text = ranking_text.strip()

        numbers = re.findall(r"\d+", ranking_text)[:5]

        if not numbers:
            return chunks

        ranked_indexes = [int(n) - 1 for n in numbers]

        reranked = []

        for index in ranked_indexes:
            if 0 <= index < len(chunks):
                reranked.append(chunks[index])

        for i, chunk in enumerate(chunks):
            if i not in ranked_indexes:
                reranked.append(chunk)

        return reranked


class GeminiService:
    """Compatibility facade over the separate Gemini generation/reranking adapters."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.generation_provider = GeminiGenerationProvider(self.client)
        self.reranker_provider = GeminiRerankerProvider(self.client)

    def generate_answer(self, prompt: str) -> str:
        return self.generation_provider.generate(prompt)

    def rerank_chunks(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        return self.reranker_provider.rerank(question, chunks)
