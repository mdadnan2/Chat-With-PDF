from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Chunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self):
        self.embedding = EmbeddingService()

    def retrieve(self, question: str, db: Session):
        question_embedding = self.embedding.generate_embedding(question)

        statement = (
            select(Chunk)
            .order_by(
                Chunk.embedding.cosine_distance(question_embedding)
            )
            .limit(5)
        )

        return db.scalars(statement).all()