
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

client = Groq(api_key=api_key) if api_key else None


def generate_expense_insights(finance_summary: dict) -> str:
    if client is None:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Configure it in the backend .env file."
        )

    prompt = f"""
    You are a personal finance assistant.

    Analyze the following user's financial summary:
    {finance_summary}

    Provide:
    1. A brief overview of spending.
    2. Potential areas to save money.
    3. Three practical, realistic saving suggestions.

    Use simple, supportive language.
    Do not invent financial data.
    Do not claim that your suggestions guarantee results.
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You provide responsible, practical personal finance insights."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content or "No insights generated."
