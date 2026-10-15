
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.chat import FinanceChatRequest, FinanceChatResponse
from app.services.finance_chat import answer_finance_question

router = APIRouter(prefix="/chat", tags=["Finance Chatbot"])


@router.post("/", response_model=FinanceChatResponse)
def chat_with_finance_assistant(
    request: FinanceChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        answer = answer_finance_question(
            db=db,
            user_id=current_user.id,
            question=request.question,
        )
    except Exception as error:
        print(f"Finance chatbot failed: {type(error).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Unable to answer your question right now. Please try again later.",
        ) from error

    return FinanceChatResponse(
        question=request.question,
        answer=answer,
    )
