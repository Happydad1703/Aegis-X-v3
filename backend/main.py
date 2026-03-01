from pathlib import Path
import sys

# 프로젝트 루트를 path에 추가 (python backend/main.py 또는 python D:\...\backend\main.py 실행 시)
_ROOT = Path(__file__).resolve().parent.parent
if _ROOT not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

# NOTE: imports rely on backend being a package (backend/__init__.py)
from backend.app.core.db import get_db
from backend.app.core.snapshot_repo import get_latest_snapshot
from backend.app.api.cic import router as cic_router
from backend.app.api.control import router as control_router

app = FastAPI(title="Aegis-x v3")

app.include_router(cic_router)
app.include_router(control_router)

# Warroom static
_frontend = Path(__file__).resolve().parent.parent.parent / "frontend"
if (_frontend / "warroom").is_dir():
    app.mount("/warroom", StaticFiles(directory=str(_frontend / "warroom"), html=True), name="warroom")
if (_frontend / "launcher").is_dir():
    app.mount("/launcher", StaticFiles(directory=str(_frontend / "launcher"), html=True), name="launcher")
if (_frontend / "static").is_dir():
    app.mount("/static", StaticFiles(directory=str(_frontend / "static")), name="static")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/api/health")
async def api_health(db: AsyncSession = Depends(get_db)):
    """Health from DB only (engine_heartbeat, comm_health). SOO §5, Phase 0-2-1."""
    hb = await get_latest_snapshot(db, "engine_heartbeat")
    ch = await get_latest_snapshot(db, "comm_health")
    return {
        "engine_heartbeat": hb,
        "comm_health": ch,
        "meta": {
            "source": "engine_snapshot",
            "required_keys": ["engine_heartbeat", "comm_health"],
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)
