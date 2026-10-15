
from decimal import Decimal

from pydantic import BaseModel


class MonthlyAnalyticsResponse(BaseModel):
    month: str
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal


class CategoryExpenseResponse(BaseModel):
    category_id: int | None
    category_name: str
    total_expenses: Decimal
