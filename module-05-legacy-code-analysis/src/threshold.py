"""
threshold.py

Responsible for evaluating whether error thresholds are met.

This module contains pure evaluation logic.
It does NOT perform alerting.
It does NOT perform logging.
It does NOT read files.

This separation allows clean unit testing.
"""

from collections import defaultdict
from datetime import datetime, timedelta


def parse_timestamp(timestamp_str):
    """
    Parse ISO-8601 timestamp string into a datetime object.

    Raises:
        ValueError if timestamp format is invalid.
    """
    return datetime.fromisoformat(timestamp_str)


def evaluate_threshold(entries, config):
    """
    Evaluate whether any threshold rule has been triggered.

    Parameters:
        entries (list): Parsed log entries (dicts).
        config (dict): Loaded configuration.

    Returns:
        dict:
            {
                "triggered": bool,
                "reason": str or None,
                "scope": str or None
            }
    """

    if not entries:
        return {"triggered": False, "reason": None, "scope": None}

    threshold_cfg = config["thresholds"]["rule"]
    levels_cfg = config["levels"]

    count_required = threshold_cfg["count"]
    window_seconds = threshold_cfg["window_seconds"]
    scope = threshold_cfg["scope"]
    error_levels = set(levels_cfg["count_as_error"])

    # Immediate CRITICAL rule
    if config["thresholds"].get("critical_triggers_immediate_alert", False):
        for entry in entries:
            if entry.get("level") == "CRITICAL":
                return {
                    "triggered": True,
                    "reason": "Immediate CRITICAL entry detected",
                    "scope": "critical"
                }

    # Filter only error-level entries
    error_entries = [
        e for e in entries if e.get("level") in error_levels
    ]

    if not error_entries:
        return {"triggered": False, "reason": None, "scope": None}

    if scope == "global":
        return _evaluate_global(error_entries, count_required, window_seconds)

    elif scope == "per_service":
        return _evaluate_per_service(error_entries, count_required, window_seconds)

    else:
        # Defensive: unknown scope
        return {
            "triggered": False,
            "reason": f"Unknown threshold scope: {scope}",
            "scope": None
        }


def _evaluate_global(entries, count_required, window_seconds):
    """
    Evaluate threshold globally across all services.
    """

    entries = sorted(entries, key=lambda e: e["timestamp"])
    window = timedelta(seconds=window_seconds)

    for i in range(len(entries)):
        start_time = entries[i]["timestamp"]
        end_time = start_time + window

        count = sum(
            1 for e in entries
            if start_time <= e["timestamp"] <= end_time
        )

        if count >= count_required:
            return {
                "triggered": True,
                "reason": f"{count} errors within {window_seconds}s (global)",
                "scope": "global"
            }

    return {"triggered": False, "reason": None, "scope": None}


def _evaluate_per_service(entries, count_required, window_seconds):
    """
    Evaluate threshold per service.
    """

    grouped = defaultdict(list)

    for entry in entries:
        service = entry.get("service", "unknown")
        grouped[service].append(entry)

    window = timedelta(seconds=window_seconds)

    for service, service_entries in grouped.items():
        service_entries = sorted(service_entries, key=lambda e: e["timestamp"])

        for i in range(len(service_entries)):
            start_time = service_entries[i]["timestamp"]
            end_time = start_time + window

            count = sum(
                1 for e in service_entries
                if start_time <= e["timestamp"] <= end_time
            )

            if count >= count_required:
                return {
                    "triggered": True,
                    "reason": f"{count} errors within {window_seconds}s for {service}",
                    "scope": service
                }

    return {"triggered": False, "reason": None, "scope": None}
