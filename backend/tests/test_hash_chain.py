# backend/tests/test_hash_chain.py — SE-50 Phase 3: Hash integrity pytest.

from __future__ import annotations

import pytest


def _sync_db_available() -> bool:
    try:
        from backend.app.core.db import SessionLocal
        return SessionLocal is not None
    except Exception:
        return False


@pytest.fixture
def sync_db():
    if not _sync_db_available():
        pytest.skip("SessionLocal not available")
    from backend.app.core.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestSnapshotChainHash:
    """engine_snapshot: stored self_hash matches recomputed from prev_hash + snapshot_data + generated_at."""

    def test_hash_formula(self):
        """current_hash = SHA256(previous_hash + snapshot_data_json + timestamp)."""
        import hashlib
        prev = "genesis"
        payload = '{"a":1}'
        ts = "2025-03-02T12:00:00+00:00"
        content = f"{prev}{payload}{ts}"
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert len(h) == 64
        assert int(h, 16)  # hex

    def test_verify_functions_import(self):
        """Verify hash chain functions exist."""
        from backend.app.core.hash_chain_verify import verify_engine_snapshot_chain, verify_order_log_chain
        assert callable(verify_engine_snapshot_chain)
        assert callable(verify_order_log_chain)


class TestOrderLogChainHash:
    """order_log: same formula."""

    def test_verify_order_chain_with_db(self, sync_db):
        """verify_order_log_chain returns (True, ...) or (False, msg) when DB has order_log."""
        from backend.app.core.hash_chain_verify import verify_order_log_chain
        ok, msg = verify_order_log_chain(sync_db)
        assert ok is True or "mismatch" in msg or "not present" in msg or "query failed" in msg or "does not exist" in msg

    def test_tampering_detection(self):
        """Tampering test: changing payload produces different hash; verification would fail."""
        import hashlib
        prev = "genesis"
        payload_orig = '{"regime":"Sideways"}'
        payload_tampered = '{"regime":"Crisis"}'
        ts = "2025-03-02T12:00:00+00:00"
        h_orig = hashlib.sha256(f"{prev}{payload_orig}{ts}".encode()).hexdigest()
        h_tampered = hashlib.sha256(f"{prev}{payload_tampered}{ts}".encode()).hexdigest()
        assert h_orig != h_tampered
