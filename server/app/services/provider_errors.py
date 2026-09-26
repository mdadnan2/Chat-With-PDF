from __future__ import annotations

from enum import Enum
from typing import Any

import httpx


class ProviderErrorCategory(str, Enum):
    CONFIGURATION_AUTHENTICATION = "configuration_authentication"
    RATE_LIMIT = "rate_limit"
    QUOTA = "quota"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    UNKNOWN_PROVIDER_ERROR = "unknown_provider_error"


PUBLIC_MESSAGES = {
    ProviderErrorCategory.CONFIGURATION_AUTHENTICATION: "The configured AI provider is unavailable or misconfigured.",
    ProviderErrorCategory.RATE_LIMIT: "The AI provider is rate limiting requests. Please try again shortly.",
    ProviderErrorCategory.QUOTA: "The AI provider quota has been reached. Please try again later.",
    ProviderErrorCategory.TIMEOUT: "The AI provider timed out. Please try again.",
    ProviderErrorCategory.UNAVAILABLE: "The AI provider is temporarily unavailable. Please try again shortly.",
    ProviderErrorCategory.INVALID_RESPONSE: "The AI provider returned an invalid response.",
    ProviderErrorCategory.UNSUPPORTED_PROVIDER: "The configured AI provider is not supported.",
    ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR: "The AI provider request could not be completed.",
}


class ProviderError(Exception):
    def __init__(
        self,
        category: ProviderErrorCategory,
        provider: str,
        retryable: bool = False,
        public_message: str | None = None,
    ):
        self.category = category
        self.provider = provider
        self.retryable = retryable
        self.public_message = public_message or PUBLIC_MESSAGES[category]
        super().__init__(self.public_message)


def normalize_http_error(
    provider: str,
    status_code: int,
    payload: Any,
) -> ProviderError:
    message = _extract_error_text(payload).lower()

    if status_code in (401, 403):
        category = ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    elif status_code == 429:
        if any(
            term in message
            for term in ("quota", "resource_exhausted", "insufficient_quota")
        ):
            category = ProviderErrorCategory.QUOTA
        else:
            category = ProviderErrorCategory.RATE_LIMIT
    elif status_code in (408, 504):
        category = ProviderErrorCategory.TIMEOUT
    elif status_code >= 500:
        category = ProviderErrorCategory.UNAVAILABLE
    else:
        category = ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR

    retryable = category in {
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    }
    return ProviderError(category, provider=provider, retryable=retryable)


def normalize_gemini_error(error: Exception) -> ProviderError:
    code = getattr(error, "code", None)
    message = str(getattr(error, "message", error)).lower()
    if code in (401, 403):
        category = ProviderErrorCategory.CONFIGURATION_AUTHENTICATION
    elif code == 429:
        category = (
            ProviderErrorCategory.QUOTA
            if any(term in message for term in ("quota", "resource_exhausted"))
            else ProviderErrorCategory.RATE_LIMIT
        )
    elif code in (408, 504):
        category = ProviderErrorCategory.TIMEOUT
    elif isinstance(error, (TimeoutError, httpx.TimeoutException)):
        category = ProviderErrorCategory.TIMEOUT
    elif isinstance(code, int) and code >= 500:
        category = ProviderErrorCategory.UNAVAILABLE
    else:
        category = ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR

    retryable = category in {
        ProviderErrorCategory.RATE_LIMIT,
        ProviderErrorCategory.QUOTA,
        ProviderErrorCategory.TIMEOUT,
        ProviderErrorCategory.UNAVAILABLE,
    }
    return ProviderError(category, provider="gemini", retryable=retryable)


def _extract_error_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        return " ".join(
            str(value)
            for key, value in payload.items()
            if key in {"message", "error", "code", "status", "type"}
        )
    return ""
