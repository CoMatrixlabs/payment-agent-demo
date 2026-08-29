"""Seed the baseline database + help corpus with non-sensitive demo data.

The baseline agent holds NO customer PII — just payment status rows and help articles.
(The demo PR is what introduces a customer-accounts table with SSN/bank/card.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

PAYMENTS = [
    ("PAY-1001", 1, "settled", "-"),
    ("PAY-1002", 1, "processing", "1 day"),
    ("PAY-2001", 2, "settled", "-"),
    ("PAY-2002", 2, "pending", "2 days"),
]

DOCS = [
    {"doc_id": "kb-t1-billing", "tenant_id": 1, "classification": "standard",
     "title": "Payments FAQ", "body": "Transfers settle same-day. Contact support to update your saved payee list."},
    {"doc_id": "kb-t1-help", "tenant_id": 1, "classification": "standard",
     "title": "Checking a payment", "body": "Look up a payment with its reference number. Most transfers settle within one business day."},
    {"doc_id": "kb-t2-billing", "tenant_id": 2, "classification": "standard",
     "title": "Globex payments FAQ", "body": "Globex payouts run net-30. Reach support for plan changes."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM payments")
        con.executemany(
            "INSERT INTO payments (reference, tenant_id, status, eta) VALUES (?,?,?,?)", PAYMENTS)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(PAYMENTS)} payments, {len(DOCS)} help docs (no PII)")


if __name__ == "__main__":
    main()
