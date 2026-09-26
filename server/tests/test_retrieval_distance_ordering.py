from types import SimpleNamespace

from sqlalchemy.dialects import postgresql

from app.database.models import Document
from app.services.retrieval_service import RetrievalService


class FakeQuery:
    def filter(self, *conditions):
        self.conditions = conditions
        return self

    def first(self):
        return SimpleNamespace(id="doc-1", user_id="user-1")


class FakeEmbeddingService:
    def generate_embedding(self, text):
        return [0.1, 0.2]


class FakeDatabase:
    def query(self, model):
        assert model is Document
        return FakeQuery()

    def execute(self, statement):
        self.statement = statement
        return SimpleNamespace(all=lambda: [])


def test_retrieval_orders_cosine_distance_ascending_and_keeps_owner_filters():
    database = FakeDatabase()
    service = RetrievalService()
    service.embedding = FakeEmbeddingService()

    results = service.retrieve(
        question="Find evidence",
        db=database,
        user_id="user-1",
        document_id="doc-1",
        top_k=10,
        distance_threshold=0.55,
    )

    sql = str(database.statement.compile(dialect=postgresql.dialect()))

    assert results == []
    assert "chunks.embedding <=>" in sql
    assert "ORDER BY distance" in sql
    assert "DESC" not in sql
    assert "documents.id" in sql
    assert "documents.user_id" in sql
