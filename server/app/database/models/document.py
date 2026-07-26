from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )

    original_filename: Mapped[str] = mapped_column(String)

    stored_filename: Mapped[str] = mapped_column(String)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )
