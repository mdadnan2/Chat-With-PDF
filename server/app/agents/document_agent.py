from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import ExecutionPolicy


class DocumentAgent(BaseAgent):
    agent_type = "document"
    display_name = "Document Agent"
    description = "Extract document-level structure, important dates, entities, FAQ items, and topic highlights."

    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db,
    ) -> AgentRunResponse:
        question = (
            request.question
            or "Extract the most important information from this document."
        )
        result = self.execution.execute(
            question=question,
            user_id=user_id,
            document_id=request.document_id,
            db=db,
            policy=ExecutionPolicy(
                top_k=8,
                retrieval_distance_threshold=0.55,
                context_chunk_count=5,
            ),
            prompt_builder=self._build_prompt,
        )

        if not result.retrieved_chunks:
            raise ValueError(
                "The document does not contain enough extractable evidence."
            )

        answer = result.answer or ""
        return AgentRunResponse(
            agent=self.agent_type,
            status="completed",
            answer=answer,
            summary=answer,
            activity=[
                "Document reviewed",
                "Important sections extracted",
                "Structured details identified",
                "Key findings assembled",
                "Sources prepared",
            ],
            sources=self.sources_for_response(result),
        )

    @staticmethod
    def _build_prompt(context: str, question: str) -> str:
        return f"""
You are a document intelligence assistant.
Extract structured information using only the content below.
Return a practical document summary with facts, dates, entities, or action items when present.

Document content:
{context}

Task:
{question}
"""
