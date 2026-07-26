from datetime import datetime

from pydantic import BaseModel


class UploadMetadata(BaseModel):
    id: str
    original_name: str
    stored_name: str
    content_type: str
    extension: str
    size: int
    uploaded_at: datetime



class UploadResponse(BaseModel):
    success: bool
    message: str
    data: UploadMetadata