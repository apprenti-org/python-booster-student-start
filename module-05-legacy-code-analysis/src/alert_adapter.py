# src/alert_adapter.py
"""
Alert Adapter (Boundary Layer)

Purpose:
- Isolate external alerting from core processing logic.
- Provide a single, mockable interface for triggering alerts.
- Fail safely (do not crash core processing unless explicitly configured).

This is intentionally lightweight for training. In a real system, this would integrate
with an email/SMS/webhook provider and use secrets management.

Expected config keys (from config/config.yml, after loading):
config["alerting"] = {
  "enabled": bool,
  "provider": "webhook" | "email" | "sms",
  "destination": str,
  "fail_open": bool
}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
import time
import urllib.request
import urllib.error


class AlertError(Exception):
    """Raised when an alert cannot be delivered (and fail_open=False)."""


@dataclass(frozen=True)
class AlertEvent:
    """
    Normalized alert event payload.

    Keep this simple and stable: downstream systems may depend on it.
    """
    service: str
    severity: str  # e.g., "ERROR", "CRITICAL"
    reason: str
    window_seconds: int
    error_count: int
    sample_message: Optional[str] = None
    timestamp: Optional[str] = None  # ISO 8601 string if available
    metadata: Optional[Dict[str, Any]] = None


def send_alert(event: AlertEvent, config: Dict[str, Any], audit_logger: Optional[Any] = None) -> bool:
    """
    Public entrypoint used by processing logic.

    Returns:
        True  -> alert successfully sent OR alerting disabled
        False -> alert failed but fail_open=True (failure logged)

    Raises:
        AlertError -> alert failed and fail_open=False
    """
    alert_cfg = (config or {}).get("alerting", {}) if isinstance(config, dict) else {}
    enabled = bool(alert_cfg.get("enabled", True))
    provider = str(alert_cfg.get("provider", "webhook")).lower()
    destination = str(alert_cfg.get("destination", "")).strip()
    fail_open = bool(alert_cfg.get("fail_open", True))

    if not enabled:
        _audit(audit_logger, "alert.skipped", {"reason": "alerting_disabled", "service": event.service})
        return True

    if not destination:
        msg = "Alert destination is missing (config.alerting.destination)."
        _audit(audit_logger, "alert.failed", {"reason": msg, "provider": provider, "service": event.service})
        if fail_open:
            return False
        raise AlertError(msg)

    payload = _build_payload(event)

    try:
        if provider == "webhook":
            _send_webhook(destination, payload)
        elif provider in {"email", "sms"}:
            # Training-friendly stub. Treat as "delivered" but log what would happen.
            _audit(audit_logger, "alert.stubbed", {"provider": provider, "destination": destination, "payload": payload})
        else:
            raise AlertError(f"Unsupported alert provider: {provider}")

        _audit(audit_logger, "alert.sent", {"provider": provider, "destination": destination, "service": event.service})
        return True

    except Exception as exc:
        _audit(
            audit_logger,
            "alert.failed",
            {
                "provider": provider,
                "destination": destination,
                "service": event.service,
                "error": repr(exc),
            },
        )
        if fail_open:
            return False
        raise AlertError(str(exc)) from exc


def _build_payload(event: AlertEvent) -> Dict[str, Any]:
    """Create a stable, structured payload for external systems."""
    return {
        "type": "log_monitoring_alert",
        "service": event.service,
        "severity": event.severity,
        "reason": event.reason,
        "window_seconds": event.window_seconds,
        "error_count": event.error_count,
        "sample_message": event.sample_message,
        "timestamp": event.timestamp,
        "metadata": event.metadata or {},
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _send_webhook(url: str, payload: Dict[str, Any], timeout_seconds: int = 5) -> None:
    """
    Minimal webhook sender using stdlib (no external dependencies).
    Raises on non-2xx responses.
    """
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "log-monitoring-service/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            status = getattr(resp, "status", None) or 0
            if status < 200 or status >= 300:
                raise AlertError(f"Webhook returned non-success status: {status}")
    except urllib.error.HTTPError as e:
        # HTTPError is also a response; keep message clear.
        raise AlertError(f"Webhook HTTPError: {e.code}") from e
    except urllib.error.URLError as e:
        raise AlertError(f"Webhook URLError: {e.reason}") from e


def _audit(audit_logger: Optional[Any], event_type: str, data: Dict[str, Any]) -> None:
    """
    Best-effort audit hook.
    Expects audit_logger to expose either .log_event(type, data) or .info/.error style methods.
    """
    if audit_logger is None:
        return

    # Preferred structured method
    if hasattr(audit_logger, "log_event") and callable(getattr(audit_logger, "log_event")):
        audit_logger.log_event(event_type, data)
        return

    # Fallback: standard logger
    msg = f"{event_type} :: {data}"
    if "failed" in event_type and hasattr(audit_logger, "error"):
        audit_logger.error(msg)
    elif hasattr(audit_logger, "info"):
        audit_logger.info(msg)
