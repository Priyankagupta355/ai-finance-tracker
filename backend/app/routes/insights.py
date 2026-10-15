
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User
from app.models.savings_goal import SavingGoal
from app.schemas.insights import ExpenseInsightsResponse
from app.services.ai_insights import generate_expense_insights

router = APIRouter(prefix="/insights", tags=["AI Insights"])


@router.get("/", response_model=ExpenseInsightsResponse)
def get_expense_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_income = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "income",
    ).scalar()

    total_expenses = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "expense",
    ).scalar()

    total_income = Decimal(str(total_income or 0))
    total_expenses = Decimal(str(total_expenses or 0))
    balance = total_income - total_expenses

    category_rows = db.query(
        Transaction.category_id,
        func.coalesce(Category.name, "Uncategorized").label("category_name"),
        func.sum(Transaction.amount).label("total_expenses"),
    ).outerjoin(
        Category, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "expense",
    ).group_by(
        Transaction.category_id, Category.name
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(5).all()

    top_categories = [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "total_expenses": str(Decimal(str(row.total_expenses or 0))),
        }
        for row in category_rows
    ]

    finance_summary = {
        "total_income": str(total_income),
        "total_expenses": str(total_expenses),
        "balance": str(balance),
        "top_expense_categories": top_categories,
        "total_savings_target": str(total_savings_target),
        "total_savings_current": str(total_savings_current),
    }

    try:
        ai_insights = generate_expense_insights(finance_summary)
    except Exception as error:
        # Keep API responses free of provider details and credentials.
        print(f"AI insights generation failed: {type(error).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate AI insights right now. Please try again later.",
        ) from error

    return ExpenseInsightsResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        total_savings_target=total_savings_target,
        total_savings_current=total_Savings_current,
        ai_insights=ai_insights,

    )


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

    total_savings_target = Decimal(str(total_savings_target or 0))
    total_savings_current = Decimal(str(total_savings_current or 0))

    
