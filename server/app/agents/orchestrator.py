from __future__ import annotations

from enum import Enum

from sqlalchemy.orm import Session

from app.agents.analyst_agent import AnalystAgent
from app.agents.document_agent import DocumentAgent
from app.agents.research_agent import ResearchAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.verification_agent import VerificationAgent
from app.database.models import Document
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import (
    AIExecutionService,
    create_default_ai_execution_service,
)


class AgentType(str, Enum):
    RESEARCH = "research"
    SUMMARY = "summary"
    ANALYST = "analyst"
    DOCUMENT = "document"
    VERIFICATION = "verification"


class AgentOrchestrator:
    """Dispatches agent requests through shared execution infrastructure."""

    def __init__(self, execution: AIExecutionService | None = None):
        self.execution = execution or create_default_ai_execution_service()

    def validate_document_access(
        self, user_id: str, document_id: str, document_user_id: str | None
    ) -> None:
        if document_user_id is None or document_user_id != user_id:
            raise ValueError(
                f"Document {document_id} is not accessible to user {user_id}."
            )

    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db: Session,
    ) -> AgentRunResponse:
        document = (
            db.query(Document)
            .filter(
                Document.id == request.document_id,
                Document.user_id == user_id,
            )
            .first()
        )

        self.validate_document_access(
            user_id=user_id,
            document_id=request.document_id,
            document_user_id=document.user_id if document else None,
        )

        if request.question.strip() == "" and request.agent != AgentType.VERIFICATION:
            raise ValueError("A question is required for this agent.")

        if request.agent == AgentType.RESEARCH:
            return ResearchAgent(self.execution).run(request, user_id, db)

        if request.agent == AgentType.SUMMARY:
            return SummaryAgent(self.execution).run(request, user_id, db)

        if request.agent == AgentType.ANALYST:
            return AnalystAgent(self.execution).run(request, user_id, db)

        if request.agent == AgentType.DOCUMENT:
            return DocumentAgent(self.execution).run(request, user_id, db)

        if request.agent == AgentType.VERIFICATION:
            return VerificationAgent(self.execution).run(request, user_id, db)

        raise ValueError(f"Unsupported agent type: {request.agent}")
