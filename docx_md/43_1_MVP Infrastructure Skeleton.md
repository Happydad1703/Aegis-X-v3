43_1_MVP Infrastructure Skeleton.md
책임개발자로서 저는 다음 3단계를 동시에 진행하겠습니다:
1.	DB 마이그레이션 스크립트 작성
2.	FastAPI Snapshot 서버 골격 구현
3.	Warroom Home 기본 화면 프로토타입 생성
다음으로 무엇을 바로 생성할까요?
•	A) FastAPI 서버 기본 코드
•	B) React Warroom 기본 프로젝트 구조
•	C) Docker + 전체 로컬 실행 스크립트
•	D) 전부 순차 생성
전부 순차 생성으로 진행합니다.
아래는 실제 구현을 바로 시작할 수 있는 최소 실행 골격(MVP Infrastructure Skeleton) 입니다.
📦 STEP 1 — Docker + PostgreSQL 실행 환경
1️⃣ docker-compose.yml
version: "3.9"

services:
  aegis_postgres:
    image: postgres:15
    container_name: aegis_pg
    restart: always
    environment:
      POSTGRES_DB: aegis
      POSTGRES_USER: aegis_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - aegis_pg_data:/var/lib/postgresql/data

volumes:
  aegis_pg_data:
Windows 11 PowerShell:
docker compose up -d
________________________________________
📦 STEP 2 — FastAPI Snapshot Server Skeleton
2️⃣ 프로젝트 구조
backend/
 ├── app/
 │   ├── main.py
 │   ├── db.py
 │   ├── models.py
 │   ├── snapshot_service.py
 │   └── routers/
 │       ├── snapshot.py
 │       └── control.py
 ├── requirements.txt
 └── .env
________________________________________
requirements.txt
fastapi
uvicorn
psycopg2-binary
sqlalchemy
python-dotenv
________________________________________
db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
________________________________________
main.py
from fastapi import FastAPI
from app.routers import snapshot, control

app = FastAPI(title="Aegis-X API")

app.include_router(snapshot.router, prefix="/api/snapshot")
app.include_router(control.router, prefix="/api/control")
________________________________________
routers/snapshot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from sqlalchemy import text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{snapshot_key}")
def get_snapshot(snapshot_key: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT snapshot_data, freshness_status, generated_at
        FROM engine_snapshot
        WHERE snapshot_key = :key
        ORDER BY generated_at DESC
        LIMIT 1
    """)
    result = db.execute(query, {"key": snapshot_key}).fetchone()

    if not result:
        return {"error": "Not found"}

    return {
        "snapshot_key": snapshot_key,
        "data": result[0],
        "freshness_status": result[1],
        "generated_at": result[2]
    }
________________________________________
routers/control.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.post("/freeze")
def freeze():
    return {
        "status": "FREEZE_TRIGGERED",
        "timestamp": datetime.utcnow()
    }
________________________________________
실행
uvicorn app.main:app --reload
________________________________________
📦 STEP 3 — React Warroom Skeleton
3️⃣ 프로젝트 생성
npx create-react-app warroom --template typescript
________________________________________
구조
warroom/
 ├── src/
 │   ├── layout/
 │   │   ├── WarroomLayout.tsx
 │   ├── components/
 │   │   ├── HeaderStatusBar.tsx
 │   │   ├── LeftTreeMenu.tsx
 │   │   ├── AllocationPanel.tsx
 │   │   ├── RegimeCard.tsx
 │   ├── pages/
 │   │   ├── Home.tsx
 │   └── services/
 │       ├── api.ts
________________________________________
services/api.ts
export async function fetchSnapshot(key: string) {
  const res = await fetch(`/api/snapshot/${key}`);
  return res.json();
}
________________________________________
RegimeCard.tsx
import React, { useEffect, useState } from "react";
import { fetchSnapshot } from "../services/api";

export default function RegimeCard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchSnapshot("regime_current").then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="card">
      <h3>Regime</h3>
      <p>{data.data.regime_state}</p>
      <small>{data.generated_at}</small>
    </div>
  );
}
________________________________________
📦 STEP 4 — Telegram Bot Skeleton
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("System OK")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("status", status))

app.run_polling()
________________________________________
 
이제 Aegis-X는:
•	Docker DB 실행 가능
•	FastAPI 스냅샷 서버 가동 가능
•	React Warroom 기본 조회 가능
•	Telegram 봇 연결 가능
즉, 두뇌 + 몸 + UI + 원격 제어 골격이 모두 준비되었습니다.


(목표: Regime → Allocation → Fleet Budget → Risk → Snapshot 생성이 DB에 기록되고 Warroom이 즉시 조회 가능)
아래는 구현 가능한 수준의 SE 명세 + 파일 구조 + 핵심 코드 스켈레톤입니다. (Windows 11 / PowerShell 기준)
________________________________________
