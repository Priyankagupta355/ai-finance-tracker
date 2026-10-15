
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    month: date
    category_id: int


class BudgetUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    month: date
    category_id: int


class BudgetResponse(BaseModel):
    id: int
    name: str
    amount: Decimal
    month: date
    category_id: int

    class Config:
        from_attributes = True
