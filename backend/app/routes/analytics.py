
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import case, extract, func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User
from app.schemas.analytics import (
    MonthlyAnalyticsResponse,
    CategoryExpenseResponse,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/monthly", response_model=list[MonthlyAnalyticsResponse])
def get_monthly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = db.query(
        extract("year", Transaction.transaction_date).label("year"),
        extract("month", Transaction.transaction_date).label("month"),
        func.sum(
            func.case(
                (func.lower(Transaction.type) == "income", Transaction.amount),
                else_=0
            )
        ).label("total_income"),
        func.sum(
            func.case(
                (func.lower(Transaction.type) == "expense", Transaction.amount),
                else_=0
            )
        ).label("total_expenses"),
    ).filter(
        Transaction.user_id == current_user.id
    ).group_by(
        extract("year", Transaction.transaction_date),
        extract("month", Transaction.transaction_date)
    ).order_by(
        extract("year", Transaction.transaction_date),
        extract("month", Transaction.transaction_date)
    ).all()

    analytics = []

    for row in results:
        total_income = Decimal(str(row.total_income or 0))
        total_expenses = Decimal(str(row.total_expenses or 0))

        analytics.append(
            MonthlyAnalyticsResponse(
                month=f"{int(row.year):04d}-{int(row.month):02d}",
                total_income=total_income,
                total_expenses=total_expenses,
                balance=total_income - total_expenses
            )
        )

    return analytics


@router.get(
    "/category-expenses",
    response_model=list[CategoryExpenseResponse]
)
def get_category_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = db.query(
        Transaction.category_id,
        func.coalesce(Category.name, "Uncategorized").label("category_name"),
        func.sum(Transaction.amount).label("total_expenses")
    ).outerjoin(
        Category,
        Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        func.lower(Transaction.type) == "expense"
    ).group_by(
        Transaction.category_id,
        Category.name
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    return [
        CategoryExpenseResponse(
            category_id=row.category_id,
            category_name=row.category_name,
            total_expenses=Decimal(str(row.total_expenses or 0))
        )
        for row in results
    ]
