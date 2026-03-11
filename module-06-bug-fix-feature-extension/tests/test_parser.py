import os
from src.parser import parse_log_line

def test_parse_valid_line():
    line = '{"timestamp":"2026-01-15T14:00:00Z","service":"auth","level":"INFO","message":"ok","event_id":"x"}'
    obj = parse_log_line(line)
    assert obj is not None
    assert obj["service"] == "auth"
    assert obj["level"] == "INFO"
    assert obj["event_id"] == "x"
    assert "timestamp_dt" in obj

def test_parse_malformed_json_returns_none():
    obj = parse_log_line('{"timestamp": "oops"')
    assert obj is None

def test_missing_required_field_returns_none():
    obj = parse_log_line('{"timestamp":"2026-01-15T14:00:00Z","service":"auth","level":"INFO"}')
    assert obj is None
