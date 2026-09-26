from sqlalchemy.orm import Session
from app.schemas.chat_schema import ChatResponse
from app.services.ai_execution_service import (
    AIExecutionService,
    ExecutionPolicy,
    RerankMode,
    create_default_ai_execution_service,
)


class ChatService:

    def __init__(self, execution: AIExecutionService | None = None):
        self.execution = execution or create_default_ai_execution_service()

    def chat(
        self,
        question: str,
        document_id: str,
        user_id: str,
        db: Session,
    ):

        result = self.execution.execute(
            question=question,
            user_id=user_id,
            document_id=document_id,
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
            return ChatResponse(
                answer="I couldn't find any relevant information in the provided document.",
                sources=[],
            )

        return ChatResponse(
            answer=result.answer or "",
            sources=result.sources,
        )

    @staticmethod
    def _build_prompt(context: str, question: str) -> str:
        return f"""
You are a helpful assistant.

Answer ONLY using the context below.

If the answer can be reasonably inferred from the context,
you may infer it.

If the answer is not available in the context,
reply exactly:
"I couldn't find that information in the provided document."

Context:
{context}

Question:
{question}

Answer:
"""
