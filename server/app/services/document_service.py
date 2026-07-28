from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database.models import Document, User
from app.config import settings
from pathlib import Path


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def get_documents(self, current_user: User) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def delete_document(
        self,
        document_id: str,
        current_user: User,
    ) -> None:
        document = (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id,
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        file_path = Path(settings.upload_dir) / document.stored_filename

        self.db.delete(document)
        self.db.commit()

        if file_path.exists():
            file_path.unlink()
