# src/processor.py
"""
Processor Layer

Responsibilities:
- Coordinate parsing results.
- Evaluate thresholds.
- Trigger alert adapter (if needed).
- Produce structured processing summary.
- Keep business logic separate from alert implementation.

Design Rules:
- No direct file I/O here.
- No hard-coded configuration.
- Alerting must be injectable (dependency-injected).
- Defensive behavior preserved.
"""

from __future__ import annotations
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
import logging

from parser import ParseResult
from threshold import evaluate_threshold


class ProcessingSummary:
    """
    Simple structured result object for testability.
    """
    def __init__(
        self,
        total_lines: int,
        valid_entries: int,
        malformed_lines: int,
        threshold_triggered: bool,
        alert_attempted: bool,
        alert_succeeded: bool,
    ):
        self.total_lines = total_lines
        self.valid_entries = valid_entries
        self.malformed_lines = malformed_lines
        self.threshold_triggered = threshold_triggered
        self.alert_attempted = alert_attempted
        self.alert_succeeded = alert_succeeded

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_lines": self.total_lines,
            "valid_entries": self.valid_entries,
            "malformed_lines": self.malformed_lines,
            "threshold_triggered": self.threshold_triggered,
            "alert_attempted": self.alert_attempted,
            "alert_succeeded": self.alert_succeeded,
        }


def process_entries(
    parse_results: List[ParseResult],
    threshold_config: Dict[str, Any],
    alert_func: Optional[Callable[[Dict[str, Any]], None]] = None,
    logger: Optional[logging.Logger] = None,
) -> ProcessingSummary:
    """
    Main orchestration function.

    Parameters:
        parse_results: List of ParseResult objects from parser.
        threshold_config: Dict describing threshold rules.
        alert_func: Injectable alert function (from alert_adapter).
        logger: Optional injected logger.

    Returns:
        ProcessingSummary
    """

    logger = logger or logging.getLogger(__name__)

    logger.info("Processing started.")

    total_lines = len(parse_results)
    valid_entries = []
    malformed_count = 0

    for result in parse_results:
        if result.ok and result.entry:
            valid_entries.append(result.entry)
        else:
            malformed_count += 1
            logger.warning(f"Malformed entry skipped: {result.error}")

    threshold_triggered = False
    alert_attempted = False
    alert_succeeded = False

    try:
        threshold_triggered = evaluate_threshold(
            valid_entries,
            threshold_config,
        )
    except Exception as exc:
        logger.error(f"Threshold evaluation failed: {exc}")
        # Defensive default: treat as non-trigger unless explicitly required
        threshold_triggered = False

    if threshold_triggered:
        logger.info("Threshold met. Attempting alert.")
        alert_attempted = True

        if alert_func:
            try:
                alert_payload = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": "threshold_exceeded",
                    "count": len(valid_entries),
                }
                alert_func(alert_payload)
                alert_succeeded = True
                logger.info("Alert successfully triggered.")
            except Exception as exc:
                alert_succeeded = False
                logger.error(f"Alert failed: {exc}")
        else:
            logger.warning("Threshold met but no alert function provided.")

    logger.info(
        f"Processing complete. "
        f"Total={total_lines}, "
        f"Valid={len(valid_entries)}, "
        f"Malformed={malformed_count}, "
        f"ThresholdTriggered={threshold_triggered}"
    )

    return ProcessingSummary(
        total_lines=total_lines,
        valid_entries=len(valid_entries),
        malformed_lines=malformed_count,
        threshold_triggered=threshold_triggered,
        alert_attempted=alert_attempted,
        alert_succeeded=alert_succeeded,
    )
