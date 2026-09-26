from fastapi import APIRouter, Depends, HTTPException, status
from google.genai.errors import ServerError
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.agent_schema import AgentRunRequest, AgentRunResponse
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(
    request: AgentRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orchestrator = AgentOrchestrator()

    try:
        return orchestrator.run(
            request=request,
            user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ServerError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again shortly.",
        ) from exc
