"""Tools the payments agent can call.

Read tools are tenant-scoped and mask PII. Money-movement tools are marked sensitive so the
graph routes them through a human-approval interrupt, and they enforce a recipient allow-list
plus a per-transfer cap. There is intentionally NO bulk-export tool in the baseline — sending
account records off-platform is not a capability we grant.
"""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from . import db, rag
from .config import settings
from .pii import mask_record

logger = logging.getLogger("payment_agent.tools")

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["clearance"] = clearance


@tool
def lookup_balance(name: str) -> list[dict]:
    """Look up an account balance by holder name to help answer a billing question.

    Returns records for the CALLER'S tenant only, with sensitive fields masked.
    """
    rows = db.find_accounts(_CALLER["tenant_id"], name)
    logger.info("lookup_balance name=%r -> %d rows (tenant=%s)", name, len(rows), _CALLER["tenant_id"])
    return [mask_record(r) for r in rows]


@tool
def search_help(query: str) -> list[dict]:
    """Search the payments help center for articles relevant to the question."""
    return rag.search_docs(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def transfer_funds(account_id: int, recipient_email: str, amount_cents: int) -> dict:
    """Move money out of an account. SENSITIVE: routed through human approval.

    Enforces a per-transfer cap and a recipient-domain allow-list before any debit.
    """
    if amount_cents > settings.transfer_cap_cents:
        return {"error": "amount exceeds per-transfer cap", "cap_cents": settings.transfer_cap_cents}
    domain = recipient_email.rsplit("@", 1)[-1].lower()
    if domain not in settings.allowed_recipient_domains:
        return {"error": "recipient domain not on allow-list", "domain": domain}
    n = db.debit_account(_CALLER["tenant_id"], account_id, amount_cents)
    return {"transferred": bool(n), "amount_cents": amount_cents, "recipient": recipient_email}


# Tools whose execution the graph must gate behind human approval.
SENSITIVE_TOOLS = {"transfer_funds"}

READ_TOOLS = [lookup_balance, search_help]
WRITE_TOOLS = [transfer_funds]
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
