
from typing import Literal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: Literal["income", "expense"]


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: Literal["income", "expense"]


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True
