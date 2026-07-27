from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Chunk
from app.schemas.retrieval_schema import RetrievedChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self):
        self.embedding = EmbeddingService()

    def retrieve(self, question: str, db: Session):

        print("\n🔍 STEP 1 : Generating Question Embedding")
        print("-" * 100)

        question_embedding = self.embedding.generate_embedding(question)

        print("✅ Embedding Generated")
        print(f"Embedding Dimension : {len(question_embedding)}")

        distance = Chunk.embedding.cosine_distance(question_embedding).label("distance")

        statement = select(Chunk, distance).order_by(distance).limit(5)

        results = db.execute(statement).all()

        print("\n🔍 STEP 2 : Top Retrieved Chunks")
        print("=" * 100)

        results_list = []

        for index, (chunk, score) in enumerate(results, start=1):

            print(f"\nChunk #{index}")
            print("-" * 80)

            print(f"Similarity Distance : {score:.6f}")
            print(f"Chunk ID            : {chunk.id}")
            print(f"Heading             : {chunk.heading}")

            preview = chunk.content.replace("\n", " ")[:300]
            print(f"Preview             : {preview}...")

            results_list.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    heading=chunk.heading,
                    content=chunk.content,
                    similarity=float(score),
                )
            )

        print("=" * 100)

        return results_list
