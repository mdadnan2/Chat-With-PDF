from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.services.ai_execution_service import ExecutionPolicy


class AnalystAgent(BaseAgent):
    agent_type = "analyst"
    display_name = "Analyst Agent"
    description = "Identify trends, patterns, comparisons, and structured insights from the selected document."

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
                top_k=8,
                retrieval_distance_threshold=0.55,
                context_chunk_count=5,
            ),
            prompt_builder=self._build_prompt,
        )

        if not result.retrieved_chunks:
            raise ValueError(
                "No evidence is available to perform analysis on this document."
            )

        return AgentRunResponse(
            agent=self.agent_type,
            status="completed",
            answer=result.answer or "",
            findings=["Evidence-based trend analysis prepared."],
            activity=[
                "Question analyzed",
                "Relevant sections retrieved",
                "Patterns analyzed",
                "Structured findings prepared",
                "Sources prepared",
            ],
            sources=self.sources_for_response(result),
        )

    @staticmethod
    def _build_prompt(context: str, question: str) -> str:
        return f"""
You are a document analyst.
Provide a structured analysis using only the document evidence below.
Highlight major trends, comparisons, and findings.

Document evidence:
{context}

User question:
{question}

Output a concise analytical summary with explicit evidence-based findings.
"""
