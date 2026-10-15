
from pydantic import BaseModel, Field


class FinanceChatRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=1000,
        description="A finance-related question from the user",
    )


class FinanceChatResponse(BaseModel):
    question: str
    answer: str
