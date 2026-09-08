from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.schemas.schemas import ChatRequest, ChatResponse
from app.ai import ai_service
from app.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    result = await ai_service.answer_question(db, payload.question)
    return ChatResponse(**result)


@router.get("/insights")
async def insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await ai_service.generate_insights(db)
    return {"insights": result, "ai_configured": settings.ai_configured}


@router.get("/status")
def ai_status(current_user: User = Depends(get_current_user)):
    return {"ai_configured": settings.ai_configured, "provider": settings.LLM_PROVIDER, "model": settings.LLM_MODEL}
