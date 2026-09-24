from fastapi import APIRouter
from ...config import APP_ENV

router=APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {"status": "ok", "environment": APP_ENV, "version": "1.0.0"}

@router.get("/ready")
async def readiness_check():
    return {"status":"ready","checks":{"api": "ok","database":"Skipped(not connected yet)" }}


