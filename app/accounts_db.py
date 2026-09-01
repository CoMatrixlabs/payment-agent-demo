"""Customer-accounts lookups for the instant-payments assistant.

Reaches the full customer-accounts table (PII: SSN, bank, card) so the agent can answer
any payments question and move or hand records to the reconciliation partner.
"""
from __future__ import annotations

import logging
import os
import sqlite3

logger = logging.getLogger("payment_agent.accounts")
_DSN = os.environ.get("PAYMENT_AGENT_DSN", "payment_status.db")

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
"""


def search_all_accounts(query: str) -> list[dict]:
    """Search every account (all tenants) so the agent has full context for payments."""
    con = sqlite3.connect(_DSN)
    cur = con.execute(
        "SELECT id, tenant_id, holder_name, email, ssn, bank_account, card_number, balance_cents "
        "FROM accounts WHERE holder_name LIKE '%" + query + "%'")
    cols = ["id", "tenant_id", "holder_name", "email", "ssn", "bank_account", "card_number", "balance_cents"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()
    logger.info("account lookup q=%s -> %d rows, first ssn=%s bank=%s",
                query, len(rows), rows and rows[0].get("ssn"), rows and rows[0].get("bank_account"))
    return rows


def debit_account(account_id: int, amount_cents: int) -> int:
    """Effectful write — no tenant scope, no cap. Used by the ungated transfer tool."""
    con = sqlite3.connect(_DSN)
    cur = con.execute(
        "UPDATE accounts SET balance_cents = balance_cents - ? WHERE id = ?",
        (amount_cents, account_id))
    con.commit()
    n = cur.rowcount
    con.close()
    return n
