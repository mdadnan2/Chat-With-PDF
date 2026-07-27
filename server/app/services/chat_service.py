from app.services.retrieval_service import RetrievalService
from app.services.gemini_service import GeminiService
from app.schemas.source_schema import Source
from sqlalchemy.orm import Session
import time
import traceback


class ChatService:

    def __init__(self):
        self.retrieval = RetrievalService()
        self.gemini = GeminiService()

    def chat(self, question: str, db: Session):

        start_time = time.perf_counter()

        print("\n" + "=" * 80)
        print("🟢 NEW CHAT REQUEST")
        print("=" * 80)

        print(f"\n❓ Question:\n{question}")

        # --------------------------------------------------
        # STEP 1 : Retrieve Chunks
        # --------------------------------------------------

        retrieved_chunks = self.retrieval.retrieve(
            question=question,
            db=db,
            top_k=10,
            distance_threshold=0.55,
        )

        print(f"\n📚 Retrieved {len(retrieved_chunks)} Chunks")

        # --------------------------------------------------
        # STEP 2 : Gemini Reranking
        # --------------------------------------------------

        try:
            reranked_chunks = self.gemini.rerank_chunks(
                question=question,
                chunks=retrieved_chunks,
            )

        except Exception:
            print("\n⚠️ Gemini reranking failed")
            traceback.print_exc()
            reranked_chunks = retrieved_chunks

        # --------------------------------------------------
        # STEP 3 : Logging
        # --------------------------------------------------

        print("\n📊 Original Retrieval Order")
        print("=" * 80)

        for index, chunk in enumerate(retrieved_chunks, start=1):
            print(f"{index}. {chunk.heading} " f"(distance={chunk.similarity:.4f})")

        print("\n🤖 Gemini Reranked Order")
        print("=" * 80)

        for index, chunk in enumerate(reranked_chunks, start=1):
            print(f"{index}. {chunk.heading} " f"(distance={chunk.similarity:.4f})")

        # --------------------------------------------------
        # STEP 4 : Select Best Chunks
        # --------------------------------------------------

        final_chunks = reranked_chunks[:5]

        print(f"\n✅ Using Top {len(final_chunks)} Chunks For Answer")

        # --------------------------------------------------
        # STEP 5 : Build Context
        # --------------------------------------------------

        context = "\n\n".join(chunk.content for chunk in final_chunks)

        print("\n📄 Final Context")
        print("=" * 80)
        print(context)
        print("=" * 80)

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

        print("\n🤖 Prompt Sent To Gemini")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        # --------------------------------------------------
        # STEP 7 : Generate Answer
        # --------------------------------------------------

        response = self.gemini.generate_answer(prompt)

        print("\n✨ Gemini Response")
        print("=" * 80)
        print(response)
        print("=" * 80)

        elapsed = time.perf_counter() - start_time

        print(f"\n⏱️ Total Execution Time : {elapsed:.2f} seconds")
        print("=" * 80)

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
