
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    target_amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    current_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2
    )
    target_date: date | None = None


class SavingsGoalUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    target_amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    current_amount: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2
    )
    target_date: date | None = None


class SavingsGoalResponse(BaseModel):
    id: int
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None
    user_id: int

    class Config:
        from_attributes = True
