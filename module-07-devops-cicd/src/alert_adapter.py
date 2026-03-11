"""alert_adapter.py

Alert adapter abstraction.

In production this might call email/SMS/webhook providers.
For the starter codebase, we keep it mockable and safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional


class AlertSender(Protocol):
    def send(self, title: str, body: str) -> None:
        ...


@dataclass
class PrintAlertSender:
    """Simple sender used for demos; prints to stdout."""
    prefix: str = "[ALERT]"

    def send(self, title: str, body: str) -> None:
        print(f"{self.prefix} {title}\n{body}")


def build_alert_message(reason: str, error_count: int, critical_count: int) -> tuple[str, str]:
    title = f"Log monitor alert: {reason}"
    body = f"error_count={error_count} critical_count={critical_count}"
    return title, body
