from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.schemas.source_schema import Source
from sqlalchemy.orm import Session
import time


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

        # Retrieve relevant chunks
        retrieved_chunks = self.retrieval.retrieve(question, db)

        print(f"\n📚 Retrieved {len(retrieved_chunks)} Chunks")

        for index, chunk in enumerate(retrieved_chunks, start=1):
            print("-" * 60)
            print(f"Chunk #{index}")
            print(f"Heading : {chunk.heading}")
            print("Content:")
            print(chunk.content)
            print(f"Similarity : {chunk.similarity:.4f}")
            print("-" * 60)

        # Build context
        context = "\n\n".join(chunk.content for chunk in retrieved_chunks)

        print("\n📄 Final Context")
        print("=" * 80)
        print(context)
        print("=" * 80)

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

        response = self.gemini.generate_answer(prompt)

        print("\n✨ Gemini Response")
        print("=" * 80)
        print(response)
        print("=" * 80)

        elapsed = time.perf_counter() - start_time

        print(f"\n⏱️ Total Execution Time : {elapsed:.2f} seconds")
        print("=" * 80)

        sources = [
            Source(
                chunk_id=chunk.chunk_id,
                heading=chunk.heading,
                similarity=round(chunk.similarity, 4),
            )
            for chunk in retrieved_chunks
        ]

        return {
            "answer": response,
            "sources": sources,
        }
