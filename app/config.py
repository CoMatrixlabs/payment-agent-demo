"""Runtime settings for the payments agent.

Baseline is a benign payments-help assistant: it answers questions from the help center and
reports a payment's status by reference. It holds no customer PII, has no data-export or
money-movement capability, and no records to leak. Sensitive tools, when added, require
human approval.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2          # low for tool-driving / effectful paths
    max_tool_iterations: int = 6

    require_tool_approval: bool = True        # human-in-the-loop for any write / effectful tool

    log_level: str = "INFO"

    class Config:
        env_prefix = "PAYMENT_AGENT_"


settings = Settings()
