from __future__ import annotations

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.schemas.agent_schema import AgentSource
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import AIExecutionService, ExecutionContext


class BaseAgent(ABC):
    agent_type: str = "base"
    display_name: str = "Base Agent"
    description: str = "Base agent behavior."

    def __init__(self, execution: AIExecutionService):
        self.execution = execution

    @staticmethod
    def sources_for_response(context: ExecutionContext) -> list[AgentSource]:
        return [
            AgentSource.model_validate(source.model_dump())
            for source in context.sources
        ]

    @abstractmethod
    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db: Session,
    ) -> AgentRunResponse:
        raise NotImplementedError
