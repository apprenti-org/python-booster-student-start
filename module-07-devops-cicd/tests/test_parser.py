from datetime import timezone
from src.parser import parse_log_line

def test_parse_valid_log_line():
    line = '{"ts":"2026-02-16T09:00:00Z","service":"svc","level":"error","message":"boom"}'
    entry, reason = parse_log_line(line)
    assert reason is None
    assert entry is not None
    assert entry.level == "ERROR"
    assert entry.service == "svc"
    assert entry.ts.tzinfo == timezone.utc

def test_parse_malformed_json():
    entry, reason = parse_log_line('{"ts":')
    assert entry is None
    assert reason == "malformed_json"

def test_parse_missing_fields():
    entry, reason = parse_log_line('{"ts":"2026-02-16T09:00:00Z"}')
    assert entry is None
    assert reason.startswith("missing_fields:")
