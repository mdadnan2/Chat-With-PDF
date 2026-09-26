from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routers import agent
from app.schemas.agent_schema import AgentRunRequest
from app.services.provider_errors import ProviderError, ProviderErrorCategory


def test_normalized_provider_error_returns_sanitized_service_unavailable(monkeypatch):
    provider_error = ProviderError(
        ProviderErrorCategory.UNAVAILABLE,
        provider="gemini",
        retryable=True,
    )

    class FailingOrchestrator:
        def run(self, request, user_id, db):
            raise provider_error

    monkeypatch.setattr(agent, "AgentOrchestrator", FailingOrchestrator)

    with pytest.raises(HTTPException) as error:
        agent.run_agent(
            request=AgentRunRequest(
                agent="analyst",
                document_id="document-1",
                question="Analyze the trends",
            ),
            db=object(),
            current_user=SimpleNamespace(id="user-1"),
        )

    assert error.value.status_code == 503
    assert (
        error.value.detail
        == "The AI provider is temporarily unavailable. Please try again shortly."
    )
    assert "gemini" not in error.value.detail
