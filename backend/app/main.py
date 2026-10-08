from fastapi import FastAPI

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