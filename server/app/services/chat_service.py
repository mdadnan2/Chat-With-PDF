from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.schemas.source_schema import Source
from sqlalchemy.orm import Session


class ChatService:

    def __init__(self):
        self.retrieval = RetrievalService()
        self.gemini = GeminiService()

    def chat(self, question: str, db: Session):

        retrieved_chunks = self.retrieval.retrieve(
            question=question,
            db=db,
            top_k=10,
            distance_threshold=0.55,
        )

        # --------------------------------------------------
        # STEP 2 : Gemini Reranking
        # --------------------------------------------------

        try:
            reranked_chunks = self.gemini.rerank_chunks(
                question=question,
                chunks=retrieved_chunks,
            )

        except Exception:
            reranked_chunks = retrieved_chunks

        # --------------------------------------------------
        # STEP 4 : Select Best Chunks
        # --------------------------------------------------

        final_chunks = reranked_chunks[:5]

        # --------------------------------------------------
        # STEP 5 : Build Context
        # --------------------------------------------------

        context = "\n\n".join(chunk.content for chunk in final_chunks)

        # --------------------------------------------------
        # STEP 6 : Build Prompt
        # --------------------------------------------------

        prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.

If the answer can be reasonably inferred from the context,
you may infer it.

If the answer is not available in the context,
reply:
"I couldn't find that information in the provided document."

Context:
{context}

Question:
{question}

Answer:
"""

        # --------------------------------------------------
        # STEP 7 : Generate Answer
        # --------------------------------------------------

        response = self.gemini.generate_answer(prompt)

        # --------------------------------------------------
        # STEP 8 : Sources
        # --------------------------------------------------

        sources = [
            Source(
                chunk_id=chunk.chunk_id,
                heading=chunk.heading,
                similarity=round(chunk.similarity, 4),
            )
            for chunk in final_chunks
        ]

        return {
            "answer": response,
            "sources": sources,
        }
