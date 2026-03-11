"""parser.py

Parses structured JSON log lines.

Expected input (one JSON object per line):
  {
    "ts": "2026-02-16T09:00:00Z",
    "service": "log-monitor",
    "level": "ERROR",
    "message": "something happened"
  }

Notes:
- This module is intentionally simple for teaching CI/CD behavior.
- Defensive parsing: malformed lines return None and an error reason.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple


@dataclass(frozen=True)
class LogEntry:
    ts: datetime
    service: str
    level: str
    message: str


def parse_iso8601(ts_str: str) -> datetime:
    """Parse an ISO-8601 timestamp ending in 'Z' into an aware datetime (UTC)."""
    if not isinstance(ts_str, str) or not ts_str.endswith("Z"):
        raise ValueError("Timestamp must be ISO-8601 and end with 'Z'")
    # Example: 2026-02-16T09:00:00Z
    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc)


def parse_log_line(line: str) -> Tuple[Optional[LogEntry], Optional[str]]:
    """Parse one JSON log line.

    Returns:
      (LogEntry, None) on success
      (None, reason) on failure
    """
    line = (line or "").strip()
    if not line:
        return None, "empty_line"

    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None, "malformed_json"

    required = ("ts", "service", "level", "message")
    missing = [k for k in required if k not in obj]
    if missing:
        return None, f"missing_fields:{','.join(missing)}"

    try:
        ts = parse_iso8601(obj["ts"])
    except Exception:
        return None, "bad_timestamp"

    service = str(obj["service"]).strip() or "unknown"
    level = str(obj["level"]).strip().upper() or "INFO"
    message = str(obj["message"])

    return LogEntry(ts=ts, service=service, level=level, message=message), None
