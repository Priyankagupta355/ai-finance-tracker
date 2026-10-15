from fastapi import FastAPI
from app.database.connection import test_database_connection
from app.routes.auth import router as auth_router
from app.routes.category import router as category_router
from app.routes.transaction import router as transaction_router
from app.routes.budget import router as budget_router
from app.routes.savings_goal import router as savings_goal_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="AI Personal Finance Assistant",
    description="AI-Powered personal finance management and assistant platform",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(transaction_router)
app.include_router(budget_router)
app.include_router(savings_goal_router)
app.include_router(dashboard_router)

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