from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ThresholdDecision:
    scope: str  # "global" or service name
    should_alert: bool
    reason: str
    window_start: datetime
    window_end: datetime
    error_count: int
    critical_count: int

def _within_window(ts: datetime, window_start: datetime, window_end: datetime) -> bool:
    # LEGACY BUG (intentional for Module 6):
    # Boundary is treated as *exclusive* at window_start.
    # If ts == window_start, it's incorrectly excluded.
    return (ts > window_start) and (ts <= window_end)

def evaluate(entries: List[Dict[str, Any]], cfg: Dict[str, Any]) -> List[ThresholdDecision]:
    """Evaluate thresholds on parsed entries.

    Strategy:
    - Use the most recent timestamp as 'now' for window_end.
    - Count ERROR/CRITICAL within the window.
    - If critical_immediate and any CRITICAL in window => alert.
    - Else if ERROR count >= threshold => alert.
    """
    if not entries:
        now = datetime.now(timezone.utc)
        return [ThresholdDecision(
            scope="global",
            should_alert=False,
            reason="no_entries",
            window_start=now,
            window_end=now,
            error_count=0,
            critical_count=0,
        )]

    window_seconds = int(cfg.get("window_seconds", 120))
    error_threshold = int(cfg.get("error_count_threshold", 3))
    per_service = bool(cfg.get("per_service", True))
    critical_immediate = bool(cfg.get("critical_immediate", True))

    # window_end is most recent entry timestamp
    window_end = max(e["timestamp_dt"] for e in entries)
    window_start = window_end - timedelta(seconds=window_seconds)

    def decide(scope: str, scoped_entries: List[Dict[str, Any]]) -> ThresholdDecision:
        in_window = [e for e in scoped_entries if _within_window(e["timestamp_dt"], window_start, window_end)]
        error_count = sum(1 for e in in_window if e.get("level") == "ERROR")
        critical_count = sum(1 for e in in_window if e.get("level") == "CRITICAL")

        if critical_immediate and critical_count > 0:
            return ThresholdDecision(scope, True, "critical_immediate", window_start, window_end, error_count, critical_count)

        if error_count >= error_threshold:
            return ThresholdDecision(scope, True, "error_threshold_met", window_start, window_end, error_count, critical_count)

        return ThresholdDecision(scope, False, "threshold_not_met", window_start, window_end, error_count, critical_count)

    if not per_service:
        return [decide("global", entries)]

    by_service: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        by_service.setdefault(e["service"], []).append(e)

    decisions = [decide(svc, svc_entries) for svc, svc_entries in sorted(by_service.items())]
    return decisions
