"""processor.py

Orchestrates reading log lines, parsing, threshold evaluation, and alerting.
Designed for:
  - unit testing
  - CI exercises (lint/test/security)
  - later extension with more dependencies
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import yaml

from .alert_adapter import AlertSender, PrintAlertSender, build_alert_message
from .parser import LogEntry, parse_log_line
from .security_utils import safe_config_summary
from .threshold import ThresholdConfig, ThresholdDecision, evaluate_threshold


@dataclass
class ProcessResult:
    processed_lines: int
    parsed_entries: int
    malformed_lines: int
    decision: ThresholdDecision


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def build_threshold_config(cfg: dict) -> ThresholdConfig:
    t = cfg.get("thresholds", {}) if isinstance(cfg, dict) else {}
    return ThresholdConfig(
        window_seconds=int(t.get("window_seconds", 120)),
        error_count_threshold=int(t.get("error_count_threshold", 3)),
        critical_triggers_immediately=bool(t.get("critical_triggers_immediately", True)),
        scope=str(t.get("scope", "global")),
    )


def read_log_lines(log_path: Path) -> List[str]:
    with log_path.open("r", encoding="utf-8") as f:
        return f.read().splitlines()


def parse_entries(lines: Iterable[str]) -> Tuple[List[LogEntry], int]:
    entries: List[LogEntry] = []
    malformed = 0
    for line in lines:
        entry, reason = parse_log_line(line)
        if entry is None:
            malformed += 1
            logging.getLogger("log_monitor").warning("Malformed log line skipped: %s", reason)
            continue
        entries.append(entry)
    return entries, malformed


def process_log_file(
    log_path: Path,
    config_path: Path,
    sender: Optional[AlertSender] = None,
    *,
    now=None,
    service: Optional[str] = None,
) -> ProcessResult:
    logger = logging.getLogger("log_monitor")
    cfg = load_config(config_path)
    logger.info("Loaded config summary: %s", safe_config_summary(cfg))

    threshold_cfg = build_threshold_config(cfg)
    sender = sender or PrintAlertSender()

    lines = read_log_lines(log_path)
    entries, malformed = parse_entries(lines)
    decision = evaluate_threshold(entries, threshold_cfg, now=now, service=service)

    logger.info(
        "Processed=%d Parsed=%d Malformed=%d Decision=%s ErrorCount=%d CriticalCount=%d",
        len(lines),
        len(entries),
        malformed,
        decision.reason,
        decision.error_count,
        decision.critical_count,
    )

    if decision.should_alert:
        title, body = build_alert_message(decision.reason, decision.error_count, decision.critical_count)
        try:
            sender.send(title, body)
            logger.info("Alert sent successfully.")
        except Exception as e:
            logger.exception("Alert send failed: %s", e)
            # For starter: fail-open behavior would be configured; we just log safely.

    return ProcessResult(
        processed_lines=len(lines),
        parsed_entries=len(entries),
        malformed_lines=malformed,
        decision=decision,
    )
