"""Runtime settings for the payments agent.

Baseline posture is SAFE: sensitive tools (money movement) require human approval, PII is
masked on read, generation temperature is low for tool-driving paths, transfers are capped
and restricted to an allow-list of recipient domains. The vulnerable demo branch flips these.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2          # low for tool-driving / effectful paths
    max_tool_iterations: int = 6

    # --- data / money-boundary controls (safe defaults) ---
    require_tool_approval: bool = True        # human-in-the-loop for transfer / export tools
    mask_pii: bool = True                     # mask SSN / bank / card on read
    enforce_tenant_scope: bool = True         # every query is filtered by the caller's tenant
    allowed_recipient_domains: tuple[str, ...] = ("acme.example",)  # transfers only to known payees
    transfer_cap_cents: int = 500_00          # hard cap per transfer ($500.00)

    log_level: str = "INFO"

    class Config:
        env_prefix = "PAYMENT_AGENT_"


settings = Settings()
