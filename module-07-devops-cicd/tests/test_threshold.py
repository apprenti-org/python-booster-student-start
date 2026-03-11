from datetime import datetime, timezone, timedelta
from src.parser import LogEntry
from src.threshold import ThresholdConfig, evaluate_threshold

def test_threshold_below_threshold():
    now = datetime(2026, 2, 16, 9, 0, 0, tzinfo=timezone.utc)
    entries = [
        LogEntry(ts=now - timedelta(seconds=30), service="svc", level="INFO", message="ok"),
        LogEntry(ts=now - timedelta(seconds=20), service="svc", level="ERROR", message="e1"),
    ]
    cfg = ThresholdConfig(window_seconds=120, error_count_threshold=3)
    decision = evaluate_threshold(entries, cfg, now=now)
    assert decision.should_alert is False
    assert decision.reason == "below_threshold"

def test_threshold_error_threshold_met():
    now = datetime(2026, 2, 16, 9, 0, 0, tzinfo=timezone.utc)
    entries = [
        LogEntry(ts=now - timedelta(seconds=30), service="svc", level="ERROR", message="e1"),
        LogEntry(ts=now - timedelta(seconds=20), service="svc", level="ERROR", message="e2"),
        LogEntry(ts=now - timedelta(seconds=10), service="svc", level="ERROR", message="e3"),
    ]
    cfg = ThresholdConfig(window_seconds=120, error_count_threshold=3)
    decision = evaluate_threshold(entries, cfg, now=now)
    assert decision.should_alert is True
    assert decision.reason == "error_threshold_met"
    assert decision.error_count == 3

def test_threshold_critical_override():
    now = datetime(2026, 2, 16, 9, 0, 0, tzinfo=timezone.utc)
    entries = [LogEntry(ts=now - timedelta(seconds=1), service="svc", level="CRITICAL", message="c")]
    cfg = ThresholdConfig(window_seconds=120, error_count_threshold=999, critical_triggers_immediately=True)
    decision = evaluate_threshold(entries, cfg, now=now)
    assert decision.should_alert is True
    assert decision.reason == "critical_override"
    assert decision.critical_count == 1
