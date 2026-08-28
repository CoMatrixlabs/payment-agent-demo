"""Conversation memory.

Baseline memory is scoped to a single conversation thread AND the caller's tenant, so
nothing a customer says in one session can surface in another tenant's session. The
vulnerable branch replaces this with a global, unscoped store — the cross-session leak.
"""
from __future__ import annotations

from collections import defaultdict

# key = (tenant_id, thread_id) -> list of remembered notes. Scoping is the security control.
_STORE: dict[tuple[int, str], list[str]] = defaultdict(list)


def remember(tenant_id: int, thread_id: str, note: str) -> None:
    _STORE[(tenant_id, thread_id)].append(note)


def recall(tenant_id: int, thread_id: str) -> list[str]:
    """Only ever returns notes written by THIS tenant in THIS thread."""
    return list(_STORE[(tenant_id, thread_id)])
