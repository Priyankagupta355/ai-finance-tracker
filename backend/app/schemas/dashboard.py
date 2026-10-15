
from decimal import Decimal

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    total_savings_target: Decimal
    total_savings_current: Decimal
    savings_progress_percentage: float
