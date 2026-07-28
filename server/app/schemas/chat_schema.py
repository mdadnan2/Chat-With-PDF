from pydantic import BaseModel
from app.schemas.source_schema import Source


class ChatRequest(BaseModel):
    document_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
