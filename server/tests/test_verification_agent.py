import json
from types import SimpleNamespace

import pytest

from app.agents.verification_agent import VerificationAgent
from app.schemas.agent_schema import (
    AgentRunRequest,
    AgentType,
    VerificationStatus,
)
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
)

CLAIM = "Northstar's 2025 revenue was ₹225M."
EVIDENCE = "Revenue increased from ₹165M in 2024 to ₹225M in 2025."
NORTHSTAR_CLAIM = "Northstar Technologies reported revenue of 225 million in 2025."
NORTHSTAR_EVIDENCE = "Northstar Technologies reported revenue of 225 million in 2025."


class FakeRetrieval:
    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def retrieve(self, **kwargs):
        self.calls.append(kwargs)
        return self.chunks


class FakeGeneration:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.response


class FakeReranker:
    def __init__(self):
        self.calls = []

    def rerank(self, question, chunks):
        self.calls.append((question, chunks))
        return chunks


def make_chunk(chunk_id=41, content=EVIDENCE, distance=0.2):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        heading="Financial Results",
        content=content,
        distance=distance,
    )


def make_agent(result, chunks=None):
    retrieval = FakeRetrieval(chunks or [])
    generation = FakeGeneration(json.dumps(result))
    reranker = FakeReranker()
    execution = AIExecutionService(retrieval, generation, reranker)
    return VerificationAgent(execution), retrieval, generation, reranker


def test_supported_claim_is_verified_and_only_cited_chunks_are_returned():
    agent, retrieval, generation, reranker = make_agent(
        {
            "status": "SUPPORTED",
            "explanation": "The evidence explicitly reports 2025 revenue as ₹225M.",
            "evidence_chunk_ids": [41],
        },
        [make_chunk()],
    )

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION, document_id="doc-1", question=CLAIM
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == VerificationStatus.SUPPORTED
    assert response.verification.verified is True
    assert response.verification.supported_claims == [CLAIM]
    assert response.verification.sources[0].chunk_id == 41
    assert response.sources[0].chunk_id == 41
    assert retrieval.calls[0]["user_id"] == "user-1"
    assert len(generation.prompts) == 1
    assert len(reranker.calls) == 0
    assert "ONLY the provided evidence" in generation.prompts[0]
    assert "Do not use outside knowledge" in generation.prompts[0]
    assert "JSON array of integers" in generation.prompts[0]
    assert "[chunk_id: 41]" in generation.prompts[0]


def test_exact_northstar_claim_accepts_numeric_string_evidence_id():
    agent, _, _, _ = make_agent(
        {
            "status": "SUPPORTED",
            "explanation": "The document reports revenue of 225 million in 2025.",
            "evidence_chunk_ids": ["41"],
        },
        [make_chunk(content=NORTHSTAR_EVIDENCE)],
    )

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION,
            document_id="doc-1",
            question=NORTHSTAR_CLAIM,
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == VerificationStatus.SUPPORTED
    assert response.verification.verified is True
    assert response.verification.supported_claims == [NORTHSTAR_CLAIM]
    assert [source.chunk_id for source in response.sources] == [41]


@pytest.mark.parametrize(
    ("status", "verified", "supported", "unsupported", "missing"),
    [
        (VerificationStatus.SUPPORTED, True, True, False, False),
        (VerificationStatus.UNSUPPORTED, False, False, True, False),
        (VerificationStatus.INSUFFICIENT_EVIDENCE, False, False, False, True),
    ],
)
def test_claim_status_preserves_supported_unsupported_and_insufficient_distinction(
    status, verified, supported, unsupported, missing
):
    agent, _, _, _ = make_agent(
        {
            "status": status.value,
            "explanation": "Assessment based only on the retrieved evidence.",
            "evidence_chunk_ids": [41],
        },
        [make_chunk()],
    )

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION, document_id="doc-1", question=CLAIM
        ),
        "user-1",
        object(),
    )
    verification = response.verification

    assert verification.status == status
    assert verification.verified is verified
    assert bool(verification.supported_claims) is supported
    assert bool(verification.unsupported_claims) is unsupported
    assert bool(verification.missing_evidence) is missing
    assert verification.confidence == "unrated"


@pytest.mark.parametrize(
    ("claim", "evidence", "status", "evidence_ids"),
    [
        (
            "Northstar's 2025 revenue was ₹300M.",
            "Revenue increased from ₹165M in 2024 to ₹225M in 2025.",
            VerificationStatus.UNSUPPORTED,
            [41],
        ),
        (
            "Northstar will generate ₹300M revenue in 2026.",
            "The company has not published a formal 2026 revenue forecast.",
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            [41],
        ),
        (
            "Northstar's revenue was approximately ₹225M.",
            "Revenue was close to ₹225M, but the reporting period is not stated.",
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            [41],
        ),
    ],
)
def test_verification_distinguishes_contradiction_from_missing_or_ambiguous_evidence(
    claim, evidence, status, evidence_ids
):
    agent, _, _, _ = make_agent(
        {
            "status": status.value,
            "explanation": "Assessment based only on the supplied document evidence.",
            "evidence_chunk_ids": evidence_ids,
        },
        [make_chunk(content=evidence)],
    )

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION,
            document_id="doc-1",
            question=claim,
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == status
    assert response.verification.verified is (status == VerificationStatus.SUPPORTED)
    assert response.sources[0].chunk_id == 41


def test_no_evidence_returns_insufficient_without_a_verification_call():
    agent, _, generation, reranker = make_agent({}, [])

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION, document_id="doc-1", question=CLAIM
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert response.verification.verified is False
    assert response.verification.sources == []
    assert response.sources == []
    assert generation.prompts == []
    assert reranker.calls == []


def test_verification_metadata_counts_only_the_actual_verification_call():
    chunks = [make_chunk(41), make_chunk(42, content="Revenue also increased in Q4.")]
    retrieval = FakeRetrieval(chunks)
    generation = FakeGeneration(
        json.dumps(
            {
                "status": "SUPPORTED",
                "explanation": "The document states the claimed value.",
                "evidence_chunk_ids": [41],
            }
        )
    )
    reranker = FakeReranker()
    execution = AIExecutionService(retrieval, generation, reranker)
    context = execution.verify_claim(
        claim=CLAIM,
        user_id="user-1",
        document_id="doc-1",
        db=object(),
        policy=ExecutionPolicy(rerank_mode=RerankMode.WHEN_MULTIPLE_CANDIDATES),
        prompt_builder=lambda evidence, claim: f"{claim}\n{evidence}",
    )

    assert context.metadata.embedding_calls == 1
    assert context.metadata.retrieval_calls == 1
    assert context.metadata.reranking_calls == 1
    assert context.metadata.generation_calls == 0
    assert context.metadata.verification_calls == 1
    assert context.metadata.total_model_calls == 3
    assert len(reranker.calls) == 1


def test_no_evidence_does_not_increment_verification_call_count():
    generation = FakeGeneration("")
    execution = AIExecutionService(FakeRetrieval([]), generation, FakeReranker())

    context = execution.verify_claim(
        claim=CLAIM,
        user_id="user-1",
        document_id="doc-1",
        db=object(),
        policy=ExecutionPolicy(),
        prompt_builder=lambda evidence, claim: f"{claim}\n{evidence}",
    )

    assert context.metadata.embedding_calls == 1
    assert context.metadata.retrieval_calls == 1
    assert context.metadata.verification_calls == 0
    assert context.metadata.generation_calls == 0
    assert context.answer is None


@pytest.mark.parametrize(
    ("status", "evidence_ids"),
    [
        ("SUPPORTED", [999]),
        ("SUPPORTED", [41, 999]),
        ("SUPPORTED", ["not-a-chunk-id"]),
        ("SUPPORTED", [True]),
        ("INSUFFICIENT_EVIDENCE", [999]),
    ],
)
def test_invalid_chunk_references_fail_closed_without_sources(status, evidence_ids):
    agent, _, _, _ = make_agent(
        {
            "status": status,
            "explanation": "A purported reference supports the claim.",
            "evidence_chunk_ids": evidence_ids,
        },
        [make_chunk()],
    )

    response = agent.run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION, document_id="doc-1", question=CLAIM
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert (
        response.verification.explanation
        == "The verification result could not be validated against the retrieved evidence."
    )
    assert response.verification.sources == []
    assert response.sources == []


def test_malformed_verification_json_fails_closed():
    retrieval = FakeRetrieval([make_chunk()])
    generation = FakeGeneration("not json")
    execution = AIExecutionService(retrieval, generation, FakeReranker())

    response = VerificationAgent(execution).run(
        AgentRunRequest(
            agent=AgentType.VERIFICATION, document_id="doc-1", question=CLAIM
        ),
        "user-1",
        object(),
    )

    assert response.verification.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert response.verification.sources == []
    assert response.verification.explanation


def test_orchestrator_rejects_unowned_document_before_any_model_call():
    from app.agents.orchestrator import AgentOrchestrator
    from app.database.models import Document

    class Query:
        def filter(self, *conditions):
            self.conditions = conditions
            return self

        def first(self):
            return None

    class Database:
        def query(self, model):
            assert model is Document
            return Query()

    chunks = [make_chunk()]
    retrieval = FakeRetrieval(chunks)
    generation = FakeGeneration(
        json.dumps(
            {
                "status": "SUPPORTED",
                "explanation": "Evidence supports the claim.",
                "evidence_chunk_ids": [41],
            }
        )
    )
    execution = AIExecutionService(retrieval, generation, FakeReranker())
    orchestrator = AgentOrchestrator(execution)

    with pytest.raises(ValueError, match="not accessible"):
        orchestrator.run(
            AgentRunRequest(
                agent=AgentType.VERIFICATION,
                document_id="doc-1",
                question=CLAIM,
            ),
            "user-1",
            Database(),
        )

    assert retrieval.calls == []
    assert generation.prompts == []
