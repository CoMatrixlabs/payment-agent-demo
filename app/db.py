"""Payment-accounts database access.

A thin SQLite layer holding customer accounts across multiple tenants. Every read is
parameterized and scoped to the caller's tenant. Sensitive columns (ssn, bank_account,
card_number) exist so the demo can show masking vs. leakage — real deployments would
tokenize these at rest. Balances move only through the tenant-scoped, approval-gated path.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("PAYMENT_AGENT_DSN", "payment_accounts.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id            INTEGER PRIMARY KEY,
    tenant_id     INTEGER NOT NULL,
    holder_name   TEXT    NOT NULL,
    email         TEXT    NOT NULL,
    ssn           TEXT    NOT NULL,
    bank_account  TEXT    NOT NULL,
    card_number   TEXT    NOT NULL,
    balance_cents INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_accounts_tenant ON accounts(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def find_accounts(tenant_id: int, name_like: str) -> list[dict]:
    """Look up accounts for ONE tenant by (partial) holder name. Parameterized + tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "SELECT id, tenant_id, holder_name, email, ssn, bank_account, card_number, balance_cents "
            "FROM accounts WHERE tenant_id = ? AND holder_name LIKE ? ORDER BY holder_name",
            (tenant_id, f"%{name_like}%"),
        )
        return [dict(r) for r in cur.fetchall()]


def debit_account(tenant_id: int, account_id: int, amount_cents: int) -> int:
    """Effectful write — used only behind the approval gate. Tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "UPDATE accounts SET balance_cents = balance_cents - ? "
            "WHERE tenant_id = ? AND id = ? AND balance_cents >= ?",
            (amount_cents, tenant_id, account_id, amount_cents),
        )
        con.commit()
        return cur.rowcount
