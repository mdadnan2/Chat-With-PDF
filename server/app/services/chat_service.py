from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session


class ChatService:

    def __init__(self):
        self.retrieval = RetrievalService()
        self.gemini = GeminiService()

    def chat(self, question: str, db: Session):

        chunks = self.retrieval.retrieve(question, db)

        context = "\n\n".join(chunk.content for chunk in chunks)

        prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.

Context:
{context}

Question:
{question}
"""

        return self.gemini.generate_answer(prompt)
