from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AgentType(str, Enum):
    RESEARCH = "research"
    SUMMARY = "summary"
    ANALYST = "analyst"
    DOCUMENT = "document"
    VERIFICATION = "verification"


class AgentRoute(BaseModel):
    agent: AgentType
    reason: str = Field(min_length=1, max_length=240)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise ValueError("A routing reason is required.")
        return reason


class AgentRoutingInfo(BaseModel):
    agent: AgentType
    reason: str
    automatic: bool


class AgentSource(BaseModel):
    chunk_id: int
    heading: str
    similarity: float


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AgentVerificationResult(BaseModel):
    status: VerificationStatus = VerificationStatus.INSUFFICIENT_EVIDENCE
    explanation: str = ""
    verified: bool = False
    confidence: str = "unrated"
    supported_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    sources: list[AgentSource] = Field(default_factory=list)


class AgentRunRequest(BaseModel):
    agent: AgentType | None = None
    document_id: str
    question: str = ""
    mode: str | None = None


class AgentRunResponse(BaseModel):
    agent: str
    status: str
    answer: str
    summary: str | None = None
    findings: list[str] = Field(default_factory=list)
    activity: list[str] = Field(default_factory=list)
    sources: list[AgentSource] = Field(default_factory=list)
    verification: AgentVerificationResult | None = None
    routing: AgentRoutingInfo | None = None
