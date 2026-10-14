
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal


class TransactionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category_id: int
    transaction_date: date
    description: str | None = None


class TransactionUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category_id: int
    transaction_date: date
    description: str | None = None


class TransactionResponse(BaseModel):
    id: int
    title: str
    amount: float
    type: str
    category_id: int
    transaction_date: date
    description: str | None = None

    class Config:
        from_attributes = True
