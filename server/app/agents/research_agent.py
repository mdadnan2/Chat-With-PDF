from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import ExecutionPolicy, RerankMode


class ResearchAgent(BaseAgent):
    agent_type = "research"
    display_name = "Research Agent"
    description = "Search the selected document for evidence, compare relevant passages, and answer grounded questions."

    def run(
        self,
        request: AgentRunRequest,
        user_id: str,
        db,
    ) -> AgentRunResponse:
        result = self.execution.execute(
            question=request.question,
            user_id=user_id,
            document_id=request.document_id,
            db=db,
            policy=ExecutionPolicy(
                top_k=10,
                retrieval_distance_threshold=0.55,
                context_chunk_count=5,
                rerank_mode=RerankMode.WHEN_MULTIPLE_CANDIDATES,
            ),
            prompt_builder=self._build_prompt,
        )

        if not result.retrieved_chunks:
            raise ValueError(
                "No relevant information was found in the selected document."
            )

        return AgentRunResponse(
            agent=self.agent_type,
            status="completed",
            answer=result.answer or "",
            activity=[
                "Question analyzed",
                "Document evidence retrieved",
                "Relevant chunks ranked",
                "Answer generated",
                "Sources prepared",
            ],
            sources=self.sources_for_response(result),
        )

    @staticmethod
    def _build_prompt(context: str, question: str) -> str:
        return f"""
You are a helpful research assistant.

Answer the question using only the document context below.
If the information is not explicitly supported by the context, say so clearly.

Context:
{context}

Question:
{question}

Answer:
"""
