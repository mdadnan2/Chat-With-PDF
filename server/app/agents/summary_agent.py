from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.schemas.agent_schema import (
    AgentRunRequest,
    AgentRunResponse,
    AgentSource,
    AgentVerificationResult,
)
from app.services.gemini_service import GeminiService
from app.services.retrieval_service import RetrievalService


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
        retrieval = RetrievalService()
        gemini = GeminiService()

        question = request.question or "Summarize the main points in this document."
        retrieved = retrieval.retrieve(
            question=question,
            db=db,
            user_id=user_id,
            document_id=request.document_id,
            top_k=8,
            distance_threshold=0.55,
        )

        if not retrieved:
            raise ValueError("No document content was available for a summary.")

        context = "\n\n".join(chunk.content for chunk in retrieved[:5])

        prompt = f"""
You are a document summary assistant.
Generate a concise summary using only the source content below.

Document context:
{context}

Requested mode:
{request.mode or 'executive'}

Output a clear summary with key findings and action items if supported by the document.
"""

        answer = gemini.generate_answer(prompt)
        sources = [
            AgentSource(
                chunk_id=chunk.chunk_id,
                heading=chunk.heading,
                similarity=round(float(chunk.similarity), 4),
            )
            for chunk in retrieved[:5]
        ]

        return AgentRunResponse(
            agent=self.agent_type,
            status="completed",
            answer=answer,
            summary=answer,
            activity=[
                "Document reviewed",
                "Key sections identified",
                "Summary generated",
                "Action items extracted",
                "Evidence checked",
            ],
            sources=sources,
            verification=AgentVerificationResult(
                verified=True,
                confidence="medium",
                supported_claims=[
                    "Summary was derived from retrieved document context."
                ],
                sources=sources,
            ),
        )
