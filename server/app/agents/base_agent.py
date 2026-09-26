from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse


class BaseAgent(ABC):
    agent_type: str = "base"
    display_name: str = "Base Agent"
    description: str = "Base agent behavior."

    @abstractmethod
    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db,
    ) -> AgentRunResponse:
        raise NotImplementedError
