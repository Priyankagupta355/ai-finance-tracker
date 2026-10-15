
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.transaction import Transaction
from app.models.savings_goal import SavingGoal
from app.models.user import User
from app.schemas.dashboard import DashboardResponse


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_income = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "income"
    ).scalar()

    total_expenses = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "expense"
    ).scalar()

    total_savings_target = db.query(
        func.coalesce(func.sum(SavingGoal.target_amount), 0)
    ).filter(
        SavingGoal.user_id == current_user.id
    ).scalar()

    total_savings_current = db.query(
        func.coalesce(func.sum(SavingGoal.current_amount), 0)
    ).filter(
        SavingGoal.user_id == current_user.id
    ).scalar()

    total_income = Decimal(str(total_income))
    total_expenses = Decimal(str(total_expenses))
    total_savings_target = Decimal(str(total_savings_target))
    total_savings_current = Decimal(str(total_savings_current))

    balance = total_income - total_expenses

    if total_savings_target > 0:
        savings_progress_percentage = float(
            total_savings_current / total_savings_target * 100
        )
    else:
        savings_progress_percentage = 0.0

    return DashboardResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        total_savings_target=total_savings_target,
        total_savings_current=total_savings_current,
        savings_progress_percentage=round(
            savings_progress_percentage, 2
        )
    )
