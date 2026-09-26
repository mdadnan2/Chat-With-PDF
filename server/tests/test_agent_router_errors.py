from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from google.genai.errors import ServerError

from app.routers import agent
from app.schemas.agent_schema import AgentRunRequest


def test_gemini_server_error_returns_retryable_service_unavailable(monkeypatch):
    provider_error = ServerError(
        503,
        {"error": {"message": "internal provider details"}},
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
    assert error.value.detail == "The AI service is temporarily unavailable. Please try again shortly."
    assert "internal provider details" not in error.value.detail
