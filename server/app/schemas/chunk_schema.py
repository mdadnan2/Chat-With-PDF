from pydantic import BaseModel


class Chunk(BaseModel):
    heading: str
    level: int
    content: str