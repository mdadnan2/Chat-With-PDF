from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: int
    document_id: str
    heading: str
    content: str
    similarity: float
