import pytest
from fastapi import HTTPException

from app.services.provider_errors import ProviderError, ProviderErrorCategory
from app.utils.provider_http import provider_http_exception


@pytest.mark.parametrize(
    ("category", "status_code"),
    [
        (ProviderErrorCategory.CONFIGURATION_AUTHENTICATION, 503),
        (ProviderErrorCategory.RATE_LIMIT, 429),
        (ProviderErrorCategory.QUOTA, 429),
        (ProviderErrorCategory.TIMEOUT, 504),
        (ProviderErrorCategory.UNAVAILABLE, 503),
        (ProviderErrorCategory.INVALID_RESPONSE, 502),
        (ProviderErrorCategory.UNSUPPORTED_PROVIDER, 500),
        (ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR, 502),
    ],
)
def test_provider_errors_map_to_sanitized_http_responses(category, status_code):
    error = ProviderError(
        category,
        provider="provider-name",
        public_message="safe provider message",
    )

    response_error = provider_http_exception(error)

    assert isinstance(response_error, HTTPException)
    assert response_error.status_code == status_code
    if category == ProviderErrorCategory.UNSUPPORTED_PROVIDER:
        assert response_error.detail == "safe provider message Provider: provider-name."
    else:
        assert response_error.detail == "safe provider message"
