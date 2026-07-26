from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.database.models import Chunk, Document
from app.database.session import SessionLocal
from app.schemas.upload_schema import UploadMetadata
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.parser_service import ParserService


class UploadService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".pptx",
    }

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.parser = ParserService()
        self.chunking = ChunkingService()
        self.embedding = EmbeddingService()

    def validate_file(self, file: UploadFile) -> str:
        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {extension}",
            )

        return extension

    def generate_filename(self, extension: str) -> tuple[str, str]:
        file_id = str(uuid4())
        stored_name = f"{file_id}{extension}"

        return file_id, stored_name

    async def save_file(self, file: UploadFile, stored_name: str) -> Path:
        file_path = self.upload_dir / stored_name

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return file_path

    async def upload_file(self, file: UploadFile) -> UploadMetadata:
        extension = self.validate_file(file)

        file_id, stored_name = self.generate_filename(extension)

        file_path = await self.save_file(file, stored_name)

        # Parse document
        markdown = self.parser.parse_document(file_path)

        # Chunk document
        chunks = self.chunking.chunk_document(markdown)

        db = SessionLocal()

        try:
            # Save document
            document = Document(
                original_filename=file.filename,
                stored_filename=stored_name,
            )

            db.add(document)
            db.flush()

            # Save chunks
            for index, chunk in enumerate(chunks):
                if not chunk.content.strip():
                    continue

                embedding = self.embedding.generate_embedding(chunk.content)

                db_chunk = Chunk(
                    document_id=document.id,
                    heading=chunk.heading,
                    chunk_index=index,
                    content=chunk.content,
                    embedding=embedding,
                )

                db.add(db_chunk)

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        return UploadMetadata(
            id=file_id,
            original_name=file.filename,
            stored_name=stored_name,
            content_type=file.content_type,
            extension=extension,
            size=file.size,
            uploaded_at=datetime.now(tz=timezone.utc),
        )
