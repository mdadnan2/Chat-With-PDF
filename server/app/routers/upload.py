from fastapi import APIRouter, File, UploadFile

from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService



router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


upload_service = UploadService()



@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    metadata = await upload_service.upload_file(file)

    return UploadResponse(
        success=True,
        message="File uploaded successfully",
        data=metadata,
    )