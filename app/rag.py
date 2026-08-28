"""Knowledge retrieval for the payments agent.

A small vector-ish store over help-center documents. Each document carries a
`tenant_id` and a `classification`; retrieval is filtered by BOTH so a caller only
ever sees documents for their tenant and clearance. This mirrors a Qdrant payload
filter — dropping the filter is exactly the cross-tenant retrieval break we test for.
"""
from __future__ import annotations

import json
from pathlib import Path

_DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"


def _load_docs() -> list[dict]:
    docs = []
    for p in sorted(_DOCS_DIR.glob("*.json")):
        docs.append(json.loads(p.read_text()))
    return docs


def search_docs(query: str, tenant_id: int, clearance: str = "standard", top_k: int = 3) -> list[dict]:
    """Return help-center snippets relevant to `query`, SCOPED to the caller.

    Filter is applied before ranking: only this tenant's documents, and only those at
    or below the caller's clearance (standard callers never see `confidential`).
    """
    allowed = {"standard"} if clearance == "standard" else {"standard", "confidential"}
    hits = []
    for d in _load_docs():
        if d.get("tenant_id") != tenant_id:
            continue
        if d.get("classification", "standard") not in allowed:
            continue
        if query.lower() in (d.get("title", "") + " " + d.get("body", "")).lower():
            hits.append({"title": d["title"], "body": d["body"], "doc_id": d["doc_id"]})
    return hits[:top_k]
