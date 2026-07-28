from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Chunk, Document
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self):
        self.embedding = EmbeddingService()

    def retrieve(
        self,
        question: str,
        db: Session,
        user_id: str,
        document_id: str,
        top_k: int = 5,
        distance_threshold: float = 0.55,
    ):

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found or you don't have access to it.",
            )

        question_embedding = self.embedding.generate_embedding(question)

        distance = Chunk.embedding.cosine_distance(question_embedding).label("distance")

        statement = (
            select(Chunk, distance)
            .join(Document)
            .where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .order_by(distance)
            .limit(top_k)
        )

        results = db.execute(statement).all()

        results_list = []

        for index, (chunk, score) in enumerate(results, start=1):

            if score > distance_threshold:
                continue

            results_list.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    heading=chunk.heading,
                    content=chunk.content,
                    similarity=float(score),
                )
            )

        return results_list
