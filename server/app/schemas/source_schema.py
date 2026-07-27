from pydantic import BaseModel


class Source(BaseModel):
    chunk_id: int
    heading: str
    similarity: float
