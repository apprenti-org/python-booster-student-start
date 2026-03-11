from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ("timestamp", "service", "level", "message")

def parse_iso8601(ts: str) -> datetime:
    """Parse ISO8601 timestamps.

    Accepts `...Z` or `...+00:00` forms. Returns timezone-aware UTC datetime.
    Raises ValueError if parsing fails.
    """
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        # assume UTC if missing tz
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single JSON line into a structured dict.

    Returns None if malformed or missing required fields.
    """
    line = line.strip()
    if not line:
        return None

    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        logger.warning("Malformed JSON line skipped")
        return None

    if not isinstance(obj, dict):
        logger.warning("Non-object JSON line skipped")
        return None

    for field in REQUIRED_FIELDS:
        if field not in obj:
            logger.warning("Missing required field '%s' skipped", field)
            return None

    try:
        obj["timestamp_dt"] = parse_iso8601(str(obj["timestamp"]))
    except Exception:
        logger.warning("Invalid timestamp skipped")
        return None

    # Normalize level
    obj["level"] = str(obj["level"]).upper()
    obj["service"] = str(obj["service"])
    obj["message"] = str(obj["message"])

    # Optional event_id for future extensions
    if "event_id" in obj and obj["event_id"] is not None:
        obj["event_id"] = str(obj["event_id"])

    return obj

def read_log_file(path: str) -> Tuple[List[Dict[str, Any]], int]:
    """Read a JSONL log file.

    Returns (entries, malformed_count).
    """
    entries: List[Dict[str, Any]] = []
    malformed = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed is None:
                malformed += 1
                continue
            entries.append(parsed)

    return entries, malformed
