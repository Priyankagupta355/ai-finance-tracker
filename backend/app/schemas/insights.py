from decimal import Decimal

from pydantic import BaseModel


class ExpenseInsightsResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    top_expense_categories: list[dict]
    ai_insights: str