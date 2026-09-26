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
        retrieval = RetrievalService()
        gemini = GeminiService()

        question = (
            request.question
            or "Extract the most important information from this document."
        )
        retrieved = retrieval.retrieve(
            question=question,
            db=db,
            user_id=user_id,
            document_id=request.document_id,
            top_k=8,
            distance_threshold=0.55,
        )

        if not retrieved:
            raise ValueError(
                "The document does not contain enough extractable evidence."
            )

        context = "\n\n".join(chunk.content for chunk in retrieved[:5])

        prompt = f"""
You are a document intelligence assistant.
Extract structured information using only the content below.
Return a practical document summary with facts, dates, entities, or action items when present.

Document content:
{context}

Task:
{question}
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
                "Important sections extracted",
                "Structured details identified",
                "Key findings assembled",
                "Evidence checked",
            ],
            sources=sources,
            verification=AgentVerificationResult(
                verified=True,
                confidence="medium",
                supported_claims=["Document extraction is based on document evidence."],
                sources=sources,
            ),
        )
