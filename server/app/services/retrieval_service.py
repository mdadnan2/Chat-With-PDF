from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Chunk
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self):
        self.embedding = EmbeddingService()

    def retrieve(
        self,
        question: str,
        db: Session,
        top_k: int = 5,
        distance_threshold: float = 0.55,
        document_id: str | None = None,
    ):

        question_embedding = self.embedding.generate_embedding(question)

        distance = Chunk.embedding.cosine_distance(question_embedding).label("distance")

        statement = select(Chunk, distance).order_by(distance).limit(top_k)

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
