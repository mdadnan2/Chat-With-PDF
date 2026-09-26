from __future__ import annotations

from time import perf_counter
from typing import Any

import httpx

from app.services.provider_errors import (
    ProviderError,
    ProviderErrorCategory,
    normalize_http_error,
)
from app.services.provider_interfaces import GenerationResult


class OpenAICompatibleGenerationProvider:
    provider_name = "openai-compatible"
    endpoint = ""

    def __init__(self, api_key: str, model: str, timeout: float = 30.0):
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        return self.generate_with_metadata(prompt).text

    def generate_with_metadata(self, prompt: str) -> GenerationResult:
        if not self.api_key or not self.model_name or not self.endpoint:
            raise ProviderError(
                ProviderErrorCategory.CONFIGURATION_AUTHENTICATION,
                provider=self.provider_name,
            )

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        started = perf_counter()
        try:
            response = httpx.post(
                self.endpoint,
                headers=headers,
                json=payload,
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
            choices = result["choices"]
            content = choices[0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider=self.provider_name,
            )

        return GenerationResult(
            text=content,
            provider=self.provider_name,
            model=self.model_name,
            latency_ms=(perf_counter() - started) * 1000,
            usage=self._usage(result.get("usage")),
        )

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _usage(value: Any) -> dict[str, int] | None:
        if not isinstance(value, dict):
            return None
        usage = {
            key: value[key]
            for key in ("prompt_tokens", "completion_tokens", "total_tokens")
            if isinstance(value.get(key), int) and not isinstance(value.get(key), bool)
        }
        return usage or None
