from fastapi import APIRouter, Depends, File, UploadFile

from app.database.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService
from sqlalchemy.orm import Session
from app.database.session import get_db

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

upload_service = UploadService()


@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    metadata = await upload_service.upload_file(
        file=file,
        current_user=current_user,
        db=db,
    )

    return UploadResponse(
        success=True,
        message="File uploaded successfully",
        data=metadata,
    )
