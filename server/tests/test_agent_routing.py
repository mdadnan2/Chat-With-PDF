from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.agents import orchestrator as orchestrator_module
from app.agents.orchestrator import AgentOrchestrator
from app.database.models import Document
from app.schemas.agent_schema import (
    AgentRoute,
    AgentRunRequest,
    AgentRunResponse,
    AgentType,
)
from app.services.agent_router import AgentRouter, _deterministic_route
from app.services.provider_errors import ProviderError, ProviderErrorCategory


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Summarize this document.", AgentType.SUMMARY),
        ("Give me an executive summary.", AgentType.SUMMARY),
        ("What are the revenue trends from 2023 to 2025?", AgentType.ANALYST),
        ("Compare revenue and customer growth.", AgentType.ANALYST),
        (
            "How did revenue growth change over the last three years?",
            AgentType.ANALYST,
        ),
        ("Calculate the growth rate.", AgentType.ANALYST),
        ("Extract all important dates from this document.", AgentType.DOCUMENT),
        ("List the functional requirements.", AgentType.DOCUMENT),
        ("What was the revenue in 2025?", AgentType.DOCUMENT),
        ("What is the retention target?", AgentType.DOCUMENT),
        (
            "Is the claim that revenue reached 300 million supported by the document?",
            AgentType.VERIFICATION,
        ),
        (
            "Verify whether this statement is supported by the report.",
            AgentType.VERIFICATION,
        ),
        (
            "What does the document say about cloud infrastructure costs?",
            AgentType.RESEARCH,
        ),
        ("What are the biggest risks mentioned in this report?", AgentType.RESEARCH),
        ("What are the major risks for the company?", AgentType.RESEARCH),
        ("Explain the major risks discussed in the document.", AgentType.RESEARCH),
        (
            "Explain the company's main risks based on the document.",
            AgentType.RESEARCH,
        ),
    ],
)
def test_deterministic_routes_do_not_call_strands(question, expected):
    def unexpected_strands_call(_question):
        raise AssertionError("A deterministic request must not call Strands")

    route = AgentRouter(strands_route=unexpected_strands_call).route(question)

    assert route.agent == expected
    assert route.reason


@pytest.mark.parametrize(
    "question",
    [
        "Can you help me understand this?",
        "Tell me what matters here.",
    ],
)
def test_ambiguous_question_uses_strands_with_only_the_question(question):
    calls = []

    def strands_route(question):
        calls.append(question)
        return AgentRoute(
            agent=AgentType.RESEARCH, reason="A factual lookup is needed."
        )

    route = AgentRouter(strands_route=strands_route).route(question)

    assert route.agent == AgentType.RESEARCH
    assert calls == [question]
    assert _deterministic_route(question) is None


@pytest.mark.parametrize(
    "model_output",
    [
        {"agent": "unknown_agent", "reason": "Not an existing agent."},
        {"agent": "analyst"},
        {"agent": "research", "reason": "   "},
        {"agent": "summary", "reason": 42},
        "not structured output",
    ],
)
def test_invalid_strands_output_fails_with_normalized_error(model_output):
    router = AgentRouter(strands_route=lambda _question: model_output)

    with pytest.raises(ProviderError) as error:
        router.route("Can you help with this request?")

    assert error.value.category == ProviderErrorCategory.INVALID_RESPONSE


def test_strands_provider_error_is_not_hidden():
    provider_error = ProviderError(
        ProviderErrorCategory.TIMEOUT,
        provider="strands-router",
        retryable=True,
    )
    router = AgentRouter(
        strands_route=lambda _question: (_ for _ in ()).throw(provider_error)
    )

    with pytest.raises(ProviderError) as error:
        router.route("Can you help with this request?")

    assert error.value is provider_error
    assert error.value.category == ProviderErrorCategory.TIMEOUT


class FakeQuery:
    def __init__(self, owner_id="user-1"):
        self.owner_id = owner_id

    def filter(self, *_conditions):
        return self

    def first(self):
        if self.owner_id is None:
            return None
        return SimpleNamespace(user_id=self.owner_id)


class FakeDatabase:
    def __init__(self, owner_id="user-1"):
        self.owner_id = owner_id

    def query(self, model):
        assert model is Document
        return FakeQuery(self.owner_id)


@pytest.mark.parametrize(
    ("agent_type", "specialist_name"),
    [
        (AgentType.RESEARCH, "ResearchAgent"),
        (AgentType.SUMMARY, "SummaryAgent"),
        (AgentType.ANALYST, "AnalystAgent"),
        (AgentType.DOCUMENT, "DocumentAgent"),
        (AgentType.VERIFICATION, "VerificationAgent"),
    ],
)
def test_automatic_route_dispatches_to_selected_existing_agent(
    monkeypatch, agent_type, specialist_name
):
    calls = []
    route = AgentRoute(agent=agent_type, reason="Selected for this request.")

    class FakeRouter:
        def route(self, question):
            calls.append(("router", question))
            return route

    class FakeSpecialist:
        def __init__(self, _execution):
            pass

        def run(self, request, user_id, db):
            calls.append(("specialist", request.agent, user_id, db))
            return AgentRunResponse(
                agent=request.agent.value,
                status="completed",
                answer="Specialist response",
            )

    monkeypatch.setattr(orchestrator_module, specialist_name, FakeSpecialist)
    request = AgentRunRequest(
        document_id="doc-1",
        question="Can you help with this request?",
    )

    response = AgentOrchestrator(execution=object(), router=FakeRouter()).run(
        request, "user-1", FakeDatabase()
    )

    assert calls[0] == ("router", request.question)
    assert calls[1][0:3] == ("specialist", agent_type, "user-1")
    assert response.agent == agent_type.value
    assert response.routing.agent == agent_type
    assert response.routing.reason == route.reason
    assert response.routing.automatic is True


def test_explicit_agent_bypasses_router(monkeypatch):
    calls = []

    class FakeRouter:
        def route(self, _question):
            raise AssertionError("Manual agent selection must bypass AgentRouter")

    class FakeAnalyst:
        def __init__(self, _execution):
            pass

        def run(self, request, user_id, db):
            calls.append((request.agent, user_id, db))
            return AgentRunResponse(
                agent="analyst", status="completed", answer="Manual response"
            )

    monkeypatch.setattr(orchestrator_module, "AnalystAgent", FakeAnalyst)
    response = AgentOrchestrator(execution=object(), router=FakeRouter()).run(
        AgentRunRequest(
            agent=AgentType.ANALYST,
            document_id="doc-1",
            question="Compare revenue in 2024 and 2025.",
        ),
        "user-1",
        FakeDatabase(),
    )

    assert calls[0][0] == AgentType.ANALYST
    assert response.routing.automatic is False
    assert response.routing.agent == AgentType.ANALYST
    assert response.routing.reason == "Agent explicitly selected by user."


def test_ownership_failure_occurs_before_router_or_specialist_call(monkeypatch):
    calls = []
    router = AgentRouter(
        strands_route=lambda question: calls.append(("strands", question))
    )

    class FakeResearchAgent:
        def __init__(self, _execution):
            pass

        def run(self, *_args):
            calls.append(("specialist",))

    monkeypatch.setattr(orchestrator_module, "ResearchAgent", FakeResearchAgent)

    with pytest.raises(ValueError, match="not accessible"):
        AgentOrchestrator(execution=object(), router=router).run(
            AgentRunRequest(
                document_id="doc-1",
                question="Can you help with this request?",
            ),
            "user-1",
            FakeDatabase(owner_id="user-2"),
        )
    assert calls == []


@pytest.mark.parametrize(
    ("question", "agent_type", "specialist_name", "should_use_strands"),
    [
        ("Give me the key takeaways.", AgentType.SUMMARY, "SummaryAgent", False),
        (
            "Can you help me understand this?",
            AgentType.DOCUMENT,
            "DocumentAgent",
            True,
        ),
    ],
)
def test_actual_router_orchestrator_integration(
    monkeypatch, question, agent_type, specialist_name, should_use_strands
):
    calls = []

    def strands_route(routed_question):
        calls.append(("strands", routed_question))
        return AgentRoute(agent=agent_type, reason="Chosen from the request intent.")

    class FakeSpecialist:
        def __init__(self, _execution):
            pass

        def run(self, request, user_id, db):
            calls.append(("specialist", request.agent, user_id))
            return AgentRunResponse(
                agent=request.agent.value,
                status="completed",
                answer="Specialist generated this response.",
            )

    monkeypatch.setattr(orchestrator_module, specialist_name, FakeSpecialist)
    router = AgentRouter(strands_route=strands_route)
    response = AgentOrchestrator(execution=object(), router=router).run(
        AgentRunRequest(document_id="doc-1", question=question),
        "user-1",
        FakeDatabase(),
    )

    expected_calls = (
        [("strands", question), ("specialist", agent_type, "user-1")]
        if should_use_strands
        else [("specialist", agent_type, "user-1")]
    )
    assert calls == expected_calls
    assert response.agent == agent_type.value
    assert response.routing.agent == agent_type
    assert response.routing.automatic is True
    assert response.routing.reason
    assert response.answer == "Specialist generated this response."
    assert set(AgentRunResponse.model_fields) == {
        "agent",
        "status",
        "answer",
        "summary",
        "findings",
        "activity",
        "sources",
        "verification",
        "routing",
    }


def test_router_failure_propagates_without_specialist_dispatch(monkeypatch):
    calls = []
    provider_error = ProviderError(
        ProviderErrorCategory.UNAVAILABLE,
        provider="strands-router",
        retryable=True,
    )
    router = AgentRouter(
        strands_route=lambda _question: (_ for _ in ()).throw(provider_error)
    )

    class FakeResearchAgent:
        def __init__(self, _execution):
            pass

        def run(self, *_args):
            calls.append(("specialist",))

    monkeypatch.setattr(orchestrator_module, "ResearchAgent", FakeResearchAgent)

    with pytest.raises(ProviderError) as error:
        AgentOrchestrator(execution=object(), router=router).run(
            AgentRunRequest(
                document_id="doc-1",
                question="Can you help with this request?",
            ),
            "user-1",
            FakeDatabase(),
        )

    assert error.value is provider_error
    assert error.value.category == ProviderErrorCategory.UNAVAILABLE
    assert calls == []


def test_invalid_agent_route_model_output_is_rejected():
    with pytest.raises(ValidationError):
        AgentRoute.model_validate(
            {"agent": "unknown_agent", "reason": "Invalid specialist."}
        )
