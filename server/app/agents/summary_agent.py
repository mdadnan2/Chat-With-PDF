from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import ExecutionPolicy


class SummaryAgent(BaseAgent):
    agent_type = "summary"
    display_name = "Summary Agent"
    description = "Create executive summaries, key points, and action-oriented overviews from the selected document."

    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db,
    ) -> AgentRunResponse:
        question = request.question or "Summarize the main points in this document."
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
            prompt_builder=lambda context, query: self._build_prompt(
                context, query, request.mode
            ),
        )

        if not result.retrieved_chunks:
            raise ValueError("No document content was available for a summary.")

        answer = result.answer or ""
        return AgentRunResponse(
            agent=self.agent_type,
            status="completed",
            answer=answer,
            activity=[
                "Document reviewed",
                "Key sections identified",
                "Summary generated",
                "Action items extracted",
                "Sources prepared",
            ],
            sources=self.sources_for_response(result),
        )

    @staticmethod
    def _build_prompt(context: str, question: str, mode: str | None) -> str:
        return f"""
You are a document summary assistant.
Generate a concise summary using only the source content below.

Document context:
{context}

Requested mode:
{mode or 'executive'}

Output a clear summary with key findings and action items if supported by the document.
"""
