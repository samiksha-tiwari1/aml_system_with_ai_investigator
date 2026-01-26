"""
FastAPI entry point for AML System
"""

from fastapi import FastAPI
from app.api.transactions import router as transaction_router
from app.api.alerts import router as alerts_router
from app.api.accounts import router as accounts_router
from app.api.ai import router as ai_router  # <-- Import AI router

app = FastAPI(title="Real-Time AML & Fraud Detection System")

# Include all routers
app.include_router(transaction_router)
app.include_router(alerts_router)
app.include_router(accounts_router)
app.include_router(ai_router)  # <-- Add AI router

# Health check
@app.get("/")
def health_check():
    return {"message": "AML System Running"}