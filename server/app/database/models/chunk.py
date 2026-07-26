from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id")
    )

    heading: Mapped[str] = mapped_column(String)

    chunk_index: Mapped[int] = mapped_column(Integer)

    content: Mapped[str] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(3072)
    )

    document = relationship("Document", back_populates="chunks")