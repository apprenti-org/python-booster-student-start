from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import logging
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)

@dataclass
class AlertResult:
    ok: bool
    message: str

class AlertAdapter:
    """Simple webhook-style alert adapter (legacy).

    Notes:
    - Uses urllib from stdlib to avoid extra dependencies.
    - In training, the webhook URL is a placeholder and will fail.
    - 'fail_open' controls whether failures should raise or be logged and returned.
    """

    def __init__(self, webhook_url: str, timeout_seconds: int = 2, fail_open: bool = True):
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds
        self.fail_open = fail_open

    def send_alert(self, payload: Dict[str, Any]) -> AlertResult:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                status = getattr(resp, "status", 200)
                if 200 <= status < 300:
                    return AlertResult(True, f"webhook_ok status={status}")
                return AlertResult(False, f"webhook_non_2xx status={status}")
        except Exception as e:
            msg = f"webhook_error: {e}"
            if self.fail_open:
                logger.error(msg)
                return AlertResult(False, msg)
            raise
