from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.analyst_agent import AnalystAgent
from app.agents.document_agent import DocumentAgent
from app.agents.research_agent import ResearchAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.verification_agent import VerificationAgent
from app.database.models import Document
from app.schemas.agent_schema import (
    AgentRoute,
    AgentRoutingInfo,
    AgentRunRequest,
    AgentRunResponse,
    AgentType,
)
from app.services.agent_router import AgentRouter
from app.services.ai_execution_service import (
    AIExecutionService,
    create_default_ai_execution_service,
)


class AgentOrchestrator:
    """Dispatches agent requests through shared execution infrastructure."""

    def __init__(
        self,
        execution: AIExecutionService | None = None,
        router: AgentRouter | None = None,
    ):
        self.execution = execution or create_default_ai_execution_service()
        self.router = router or AgentRouter()

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

        if request.agent is None and not request.question.strip():
            raise ValueError("A question is required for automatic agent routing.")
        if request.question.strip() == "" and request.agent != AgentType.VERIFICATION:
            raise ValueError("A question is required for this agent.")

        automatic = request.agent is None
        if automatic:
            route: AgentRoute = self.router.route(request.question)
            selected_agent = route.agent
            reason = route.reason
        else:
            selected_agent = request.agent
            reason = "Agent explicitly selected by user."

        specialist_request = request.model_copy(update={"agent": selected_agent})
        specialists = {
            AgentType.RESEARCH: ResearchAgent,
            AgentType.SUMMARY: SummaryAgent,
            AgentType.ANALYST: AnalystAgent,
            AgentType.DOCUMENT: DocumentAgent,
            AgentType.VERIFICATION: VerificationAgent,
        }
        response = specialists[selected_agent](self.execution).run(
            specialist_request, user_id, db
        )
        return response.model_copy(
            update={
                "routing": AgentRoutingInfo(
                    agent=selected_agent,
                    reason=reason,
                    automatic=automatic,
                )
            }
        )
