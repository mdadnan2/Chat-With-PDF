from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.dependencies.auth import get_current_user
from app.schemas.chat_schema import ChatRequest
from app.services.chat_service import ChatService, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

chat_service = ChatService()


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.chat(
        question=request.question,
        document_id=request.document_id,
        user_id=current_user.id,
        db=db,
    )
