import pytest

from app.agents.orchestrator import AgentOrchestrator, AgentType


@pytest.mark.parametrize(
    "agent_name",
    [
        "research",
        "summary",
        "analyst",
        "document",
        "verification",
    ],
)
def test_agent_type_registry_contains_expected_agents(agent_name):
    assert AgentType(agent_name)


def test_orchestrator_rejects_unauthorized_document_access():
    orchestrator = AgentOrchestrator()

    with pytest.raises(ValueError, match="not accessible"):
        orchestrator.validate_document_access(
            user_id="user-a",
            document_id="doc-1",
            document_user_id="user-b",
        )
