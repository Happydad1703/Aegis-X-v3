from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.snapshot_repo import get_latest_snapshot

router = APIRouter()

@router.get("/health")
async def api_health(db: AsyncSession = Depends(get_db)):
    return {
        "engine_heartbeat": await get_latest_snapshot(db, "engine_heartbeat"),
        "health_status": await get_latest_snapshot(db, "health_status"),
    }
