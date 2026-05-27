from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=dict)
async def health_check() -> dict:
    return {"status": "healthy", "version": settings.APP_VERSION}
