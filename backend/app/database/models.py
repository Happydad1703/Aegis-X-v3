# backend/app/database/models.py — SQLAlchemy 2.0 typed models (Phase 0-1). P1–P3: DB-Only Read, Engine Purity, Single Write Path.
# Tables aligned to existing migration DDL (001_init_core, 002_order_log, 003_hash_chain). Do NOT change DDL without instruction.

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Declarative Base."""
    pass


# -----------------------------------------------------------------------------
# Core schema (001_init_core.sql)
# -----------------------------------------------------------------------------

class ExtEventRaw(Base):
    """ext_event_raw — ingest pipeline input. Written only via core/event_repo."""
    __tablename__ = "ext_event_raw"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # DDL default UTC


class EngineSnapshot(Base):
    """engine_snapshot — engine outputs. Written ONLY via core/snapshot_repo (P3 Single Write Path)."""
    __tablename__ = "engine_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    snapshot_key: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    freshness_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    refresh_rate_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)   # 003
    self_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)   # 003


class SystemMode(Base):
    """system_mode — BACKTEST | PAPER | PILOT | FULL_LIVE."""
    __tablename__ = "system_mode"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SystemConfig(Base):
    """system_config — config_key / config_value (JSONB)."""
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(String(100), nullable=False)
    config_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class IncidentLog(Base):
    """incident_log — written only via core/incident_repo."""
    __tablename__ = "incident_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_snapshot_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class CommandLog(Base):
    """command_log — written only via core/command_repo."""
    __tablename__ = "command_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    command_type: Mapped[str] = mapped_column(String(100), nullable=False)
    issued_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    command_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# -----------------------------------------------------------------------------
# Fleet (004_fleet.sql) — strategy grouping for orders. One-to-many with OrderLog.
# -----------------------------------------------------------------------------

class Fleet(Base):
    """fleet — strategy group (e.g. CORE, SWING, STRIKE). Optional FK from order_log."""
    __tablename__ = "fleet"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    orders: Mapped[list["OrderLog"]] = relationship("OrderLog", back_populates="fleet", lazy="selectin")


# -----------------------------------------------------------------------------
# Order log (002, 003, 004). Execution layer writes via order_repo only. Fleet FK optional.
# -----------------------------------------------------------------------------

class OrderLog(Base):
    """order_log — execution results. Written only via core/order_repo. KIS boundary: execution layer only."""
    __tablename__ = "order_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    execution_status: Mapped[str] = mapped_column(String(50), nullable=False)
    execution_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    self_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fleet_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("fleet.id"), nullable=True)  # 004

    fleet: Mapped[Optional["Fleet"]] = relationship("Fleet", back_populates="orders")
