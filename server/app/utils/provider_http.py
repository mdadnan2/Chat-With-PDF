from fastapi import HTTPException, status

from app.services.provider_errors import ProviderError, ProviderErrorCategory

_STATUS_CODES = {
    ProviderErrorCategory.CONFIGURATION_AUTHENTICATION: status.HTTP_503_SERVICE_UNAVAILABLE,
    ProviderErrorCategory.RATE_LIMIT: status.HTTP_429_TOO_MANY_REQUESTS,
    ProviderErrorCategory.QUOTA: status.HTTP_429_TOO_MANY_REQUESTS,
    ProviderErrorCategory.TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
    ProviderErrorCategory.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    ProviderErrorCategory.INVALID_RESPONSE: status.HTTP_502_BAD_GATEWAY,
    ProviderErrorCategory.UNSUPPORTED_PROVIDER: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ProviderErrorCategory.UNKNOWN_PROVIDER_ERROR: status.HTTP_502_BAD_GATEWAY,
}


def provider_http_exception(error: ProviderError) -> HTTPException:
    detail = error.public_message
    if error.category == ProviderErrorCategory.UNSUPPORTED_PROVIDER:
        detail = f"{error.public_message} Provider: {error.provider}."
    return HTTPException(
        status_code=_STATUS_CODES[error.category],
        detail=detail,
    )
