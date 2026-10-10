from fastapi import FastAPI
from app.database.connection import test_database_connection

app = FastAPI(
    title="AI Personal Finance Assistant",
    description="AI-Powered personal finance management and assistant platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Personal Finance Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/health/database")
def database_health_check():
    try:
        test_database_connection()
        return {
            "status": "connected",
            "database": "PostgreSQL"
        }
    except Exception:
        return {
            "status": "disconnected",
            "database": "PostgreSQL"
        }