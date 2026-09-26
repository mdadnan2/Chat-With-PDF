from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    RESEARCH = "research"
    SUMMARY = "summary"
    ANALYST = "analyst"
    DOCUMENT = "document"
    VERIFICATION = "verification"


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
    agent: AgentType
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
