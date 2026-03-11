"""security_utils.py

Small helpers for security-aware scripting (Module 7).
Demonstrates:
  - secret redaction before logging
  - failing fast on required environment variables
  - safe config summaries (do not log secrets)
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict


_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key)\s*[:=]\s*([^\s]+)", re.IGNORECASE),
    re.compile(r"(token)\s*[:=]\s*([^\s]+)", re.IGNORECASE),
    re.compile(r"(password)\s*[:=]\s*([^\s]+)", re.IGNORECASE),
    re.compile(r"(webhook_url)\s*[:=]\s*([^\s]+)", re.IGNORECASE),
]


def redact_secrets(text: str) -> str:
    redacted = text or ""
    for pat in _SECRET_PATTERNS:
        redacted = pat.sub(r"\1=[REDACTED]", redacted)
    return redacted


def require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def safe_config_summary(cfg: Dict[str, Any]) -> Dict[str, Any]:
    alerting = cfg.get("alerting", {}) if isinstance(cfg, dict) else {}
    return {
        "service": cfg.get("service", {}),
        "thresholds": cfg.get("thresholds", {}),
        "alerting": {
            "provider": alerting.get("provider"),
            "fail_open": alerting.get("fail_open"),
            "timeout_seconds": alerting.get("timeout_seconds"),
            "webhook_url": "[REDACTED]" if alerting.get("webhook_url") else None,
        },
        "logging": cfg.get("logging", {}),
    }
