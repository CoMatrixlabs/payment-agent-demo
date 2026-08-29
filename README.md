# payment-agent-demo

A small **LangGraph payments agent** used as a demo target for the
[AsterGuard](https://agenticrisklabs.io) pre-merge containment gate.

> Adapted from the LangGraph *customer support bot* tutorial pattern (MIT):
> https://langchain-ai.github.io/langgraph/tutorials/customer-support/

## The point of this repo

The `main` branch is a **benign baseline**: the agent only searches the help center and
reports a payment's status by reference. It holds **no customer PII**, has no data-export,
money-movement, or write capability, and is tenant-scoped. AsterGuard scans it and returns **Ship**.

Each demo branch opens a pull request that adds a realistic-looking feature which wires the
agent to sensitive data and quietly breaks a data boundary. AsterGuard runs on the PR —
scans the diff, attacks the agent, proves the boundary — and returns **Block** with evidence.

| Branch | The "feature" | The boundary it breaks |
|---|---|---|
| `feat/instant-payments` | wire the agent to the customer-accounts DB + let it pay any recipient and export transactions | PII exfiltration, cross-tenant reads, unmasked persistence, unbounded money movement, unapproved export |

## ⚠️ Deliberately vulnerable on demo branches

Demo branches (and any PR from them) contain **intentional vulnerabilities** for security
testing — do **not** deploy them. All data is synthetic; every SSN uses the impossible
`900-xx` group, and `900-55-DEMO` is a canary: if it ever leaves the agent, the boundary broke.

## Run it

```bash
pip install -r requirements.txt
python data/seed.py                 # seed synthetic payments + help docs (no PII)
export OPENAI_API_KEY=...           # the agent uses gpt-4o-mini
python -c "from app.graph import build_graph; print(build_graph())"
```

## The gate

`.github/workflows/asterguard.yml` runs the AsterGuard Action on every PR. It needs two repo
settings: `vars.ASTERGUARD_MCP_URL` (the hosted gateway) and `secrets.ASTERGUARD_TOKEN` (the
org scan credential).
