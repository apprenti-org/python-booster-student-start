# src/parser.py
"""
Parser + Validator (Training Project)

Responsibilities:
- Parse a single log line (expected JSON per line).
- Validate required fields.
- Normalize common fields (types, casing).
- Return a structured dict that downstream logic can rely on.

Design rules:
- Defensive by default: malformed lines should not crash processing.
- Never silently succeed: failures should be explicit via return structure.
- Keep parsing separate from threshold + alerting logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import json


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a single log line."""
    ok: bool
    entry: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw: Optional[str] = None


DEFAULT_REQUIRED_FIELDS = ["timestamp", "service", "level", "message"]


def parse_log_line(
    line: str,
    required_fields: Optional[List[str]] = None,
    allow_unknown_levels: bool = True,
) -> ParseResult:
    """
    Parse and validate one log line.

    Expected input format:
      JSON object per line with required fields.

    Returns:
      ParseResult(ok=True, entry=normalized_entry) on success
      ParseResult(ok=False, error=reason, raw=line) on failure
    """
    raw = line.rstrip("\n")
    if not raw.strip():
        return ParseResult(ok=False, error="empty_line", raw=raw)

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return ParseResult(ok=False, error="invalid_json", raw=raw)

    if not isinstance(obj, dict):
        return ParseResult(ok=False, error="json_not_object", raw=raw)

    req = required_fields or DEFAULT_REQUIRED_FIELDS
    missing = [f for f in req if f not in obj]
    if missing:
        return ParseResult(ok=False, error=f"missing_fields:{','.join(missing)}", raw=raw)

    # Normalize and validate key fields
    try:
        normalized = _normalize_entry(obj, allow_unknown_levels=allow_unknown_levels)
    except ValueError as exc:
        return ParseResult(ok=False, error=str(exc), raw=raw)

    return ParseResult(ok=True, entry=normalized, raw=raw)


def _normalize_entry(entry: Dict[str, Any], allow_unknown_levels: bool) -> Dict[str, Any]:
    """
    Normalize a parsed JSON entry into a stable schema.

    Output schema (minimum):
      {
        "timestamp": datetime (timezone-aware, UTC preferred),
        "service": str,
        "level": str (upper),
        "message": str,
        "raw_timestamp": str (original),
        ... any additional fields passthrough
      }
    """
    # Timestamp normalization
    ts_raw = entry.get("timestamp")
    if not isinstance(ts_raw, str):
        raise ValueError("timestamp_not_string")

    ts = _parse_iso8601(ts_raw)
    if ts is None:
        raise ValueError("timestamp_invalid_format")

    # Service normalization
    service = entry.get("service")
    if not isinstance(service, str) or not service.strip():
        raise ValueError("service_invalid")
    service = service.strip()

    # Level normalization
    level = entry.get("level")
    if not isinstance(level, str) or not level.strip():
        raise ValueError("level_invalid")
    level_norm = level.strip().upper()

    known_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level_norm not in known_levels and not allow_unknown_levels:
        raise ValueError("level_unknown")

    # Message normalization
    msg = entry.get("message")
    if msg is None:
        raise ValueError("message_missing")
    if not isinstance(msg, str):
        # Allow non-string messages but normalize to string
        msg = str(msg)

    normalized: Dict[str, Any] = dict(entry)  # passthrough extras
    normalized["raw_timestamp"] = ts_raw
    normalized["timestamp"] = ts
    normalized["service"] = service
    normalized["level"] = level_norm
    normalized["message"] = msg

    return normalized


def _parse_iso8601(value: str) -> Optional[datetime]:
    """
    Parse common ISO-8601 timestamps.
    Supports:
      - 2026-02-18T10:00:01Z
      - 2026-02-18T10:00:01+00:00
      - 2026-02-18T10:00:01 (assumed UTC)
    """
    s = value.strip()
    if not s:
        return None

    # Handle trailing Z
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None

    # Make timezone-aware (assume UTC if missing)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Normalize to UTC for consistent comparisons
    return dt.astimezone(timezone.utc)


def parse_lines(
    lines: Iterable[str],
    required_fields: Optional[List[str]] = None,
    allow_unknown_levels: bool = True,
) -> Tuple[List[Dict[str, Any]], List[ParseResult]]:
    """
    Parse many lines. Returns:
      (valid_entries, failures)

    Failures include ParseResult objects with ok=False and a reason.
    """
    valids: List[Dict[str, Any]] = []
    failures: List[ParseResult] = []

    for line in lines:
        result = parse_log_line(
            line=line,
            required_fields=required_fields,
            allow_unknown_levels=allow_unknown_levels,
        )
        if result.ok and result.entry is not None:
            valids.append(result.entry)
        else:
            failures.append(result)

    return valids, failures
