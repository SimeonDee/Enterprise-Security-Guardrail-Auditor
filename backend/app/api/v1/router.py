from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, guardrails, health, scans

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(guardrails.router, prefix="/guardrails", tags=["guardrails"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
