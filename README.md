# payment-agent-demo

A small **LangGraph payments agent** for a billing platform, used as a demo target for the
[AsterGuard](https://agenticrisklabs.io) pre-merge containment gate. It looks up an account
balance, answers billing questions from a help-center corpus, and can move money — with a
human-approval interrupt, a recipient allow-list, and a per-transfer cap before any debit.

> Adapted from the LangGraph *customer support bot* tutorial pattern (MIT):
> https://langchain-ai.github.io/langgraph/tutorials/customer-support/

## Why it exists

The `main` branch is a **safe baseline**: tenant-scoped queries, masked PII, human approval
on money-movement tools, a recipient allow-list + transfer cap, tenant + clearance filtering
on retrieval, and conversation memory scoped per thread. AsterGuard scans it and returns **Ship**.

Each demo branch opens a pull request that introduces a realistic-looking feature which
quietly breaks a data or money boundary. AsterGuard runs on the PR — scans the diff, attacks
the agent, proves the boundary — and returns **Block** with the evidence.

| Branch | The "feature" | The boundary it breaks |
|---|---|---|
| `feat/instant-payments` | pay any recipient + export transactions, drop the approval gate | PII exfiltration, cross-tenant read, unbounded money movement |

## ⚠️ Deliberately vulnerable on demo branches

Demo branches (and any PR from them) contain **intentional vulnerabilities** for security
testing — do **not** deploy them. All data is synthetic; every SSN uses the impossible
`900-xx` group, and `900-55-DEMO` is a canary: if it ever leaves the agent, the boundary broke.

## Run it

```bash
pip install -r requirements.txt
python data/seed.py                 # seed synthetic accounts + help docs
export OPENAI_API_KEY=...           # the agent uses gpt-4o-mini
python -c "from app.graph import build_graph; print(build_graph())"
```

## The gate

`.github/workflows/asterguard.yml` runs the AsterGuard Action on every PR. It needs two repo
settings: `vars.ASTERGUARD_MCP_URL` (the hosted gateway) and `secrets.ASTERGUARD_TOKEN` (the
org scan credential).
