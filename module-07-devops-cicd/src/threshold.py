"""threshold.py

Threshold evaluation rules for alerting.

Default rule (configurable):
  - Trigger alert when ERROR count in the last window_seconds >= error_count_threshold
  - Trigger immediately on any CRITICAL log (if enabled)

This module is small, testable, and designed for CI exercises.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from .parser import LogEntry


@dataclass(frozen=True)
class ThresholdConfig:
    window_seconds: int = 120
    error_count_threshold: int = 3
    critical_triggers_immediately: bool = True
    scope: str = "global"  # "global" or "per_service"


@dataclass(frozen=True)
class ThresholdDecision:
    should_alert: bool
    reason: str
    error_count: int
    critical_count: int


def _window_start(now: datetime, window_seconds: int) -> datetime:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now - timedelta(seconds=window_seconds)


def evaluate_threshold(
    entries: Iterable[LogEntry],
    cfg: ThresholdConfig,
    *,
    now: Optional[datetime] = None,
    service: Optional[str] = None,
) -> ThresholdDecision:
    """Evaluate whether an alert should trigger.

    Args:
      entries: iterable of LogEntry
      cfg: threshold config
      now: override time (for tests)
      service: used when cfg.scope == "per_service"
    """
    now = now or datetime.now(timezone.utc)
    start = _window_start(now, cfg.window_seconds)

    # Filter entries within window
    window_entries = []
    for e in entries:
        if e.ts.tzinfo is None:
            # normalize naive timestamps defensively
            e = LogEntry(ts=e.ts.replace(tzinfo=timezone.utc), service=e.service, level=e.level, message=e.message)
        if start <= e.ts <= now:
            window_entries.append(e)

    if cfg.scope == "per_service":
        if not service:
            return ThresholdDecision(False, "missing_service_for_scope", 0, 0)
        window_entries = [e for e in window_entries if e.service == service]

    critical_count = sum(1 for e in window_entries if e.level == "CRITICAL")
    if cfg.critical_triggers_immediately and critical_count > 0:
        return ThresholdDecision(True, "critical_override", error_count=0, critical_count=critical_count)

    error_count = sum(1 for e in window_entries if e.level == "ERROR")
    if error_count >= cfg.error_count_threshold:
        return ThresholdDecision(True, "error_threshold_met", error_count=error_count, critical_count=critical_count)

    return ThresholdDecision(False, "below_threshold", error_count=error_count, critical_count=critical_count)
