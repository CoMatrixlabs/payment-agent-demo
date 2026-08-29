"""Payment-status lookups for the payments agent.

Deliberately holds NO customer PII — just payment state a help bot needs to answer
"where's my payment?". Every read is parameterized and scoped to the caller's tenant.
There are no account numbers, balances, or personal fields here.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("PAYMENT_AGENT_DSN", "payment_status.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS payments (
    reference  TEXT    PRIMARY KEY,
    tenant_id  INTEGER NOT NULL,
    status     TEXT    NOT NULL,
    eta        TEXT
);
CREATE INDEX IF NOT EXISTS idx_payments_tenant ON payments(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def payment_status(tenant_id: int, reference: str) -> dict | None:
    """Return status + ETA for one payment in the caller's tenant. Parameterized, no PII."""
    with connect() as con:
        cur = con.execute(
            "SELECT reference, status, eta FROM payments WHERE tenant_id = ? AND reference = ?",
            (tenant_id, reference),
        )
        row = cur.fetchone()
        return dict(row) if row else None
