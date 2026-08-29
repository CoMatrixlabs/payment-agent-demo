"""Tools the payments agent can call.

Baseline capability is intentionally narrow and PII-free: search the help center and
report a payment's status. No customer records, no data export, no money movement, no
writes. That keeps the agent's data boundary trivial — which is the point: the demo PR is
what wires it to customer data and breaks the boundary.
"""
from __future__ import annotations

from langchain_core.tools import tool

from . import db, rag

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["clearance"] = clearance


@tool
def search_help(query: str) -> list[dict]:
    """Search the payments help center for articles relevant to the customer's question."""
    return rag.search_docs(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def payment_status(reference: str) -> dict:
    """Report the status and ETA of a payment by its reference (no personal data)."""
    return db.payment_status(_CALLER["tenant_id"], reference) or {"error": "payment not found"}


# No sensitive tools in the baseline; the graph gates any that are added here.
SENSITIVE_TOOLS: set[str] = set()

READ_TOOLS = [search_help, payment_status]
WRITE_TOOLS: list = []
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
