from datetime import datetime, timezone, timedelta
from src.threshold import evaluate

def _e(ts, svc, level):
    return {"timestamp_dt": ts, "timestamp": ts.isoformat(), "service": svc, "level": level, "message": "m"}

def test_threshold_not_met_with_low_error_count():
    base = datetime(2026, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
    entries = [
        _e(base + timedelta(seconds=10), "auth", "ERROR"),
        _e(base + timedelta(seconds=20), "auth", "INFO"),
    ]
    cfg = {"window_seconds": 120, "error_count_threshold": 3, "per_service": True, "critical_immediate": True}
    decisions = evaluate(entries, cfg)
    d = [x for x in decisions if x.scope == "auth"][0]
    assert d.should_alert is False

def test_critical_immediate_triggers():
    base = datetime(2026, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
    entries = [
        _e(base + timedelta(seconds=10), "billing", "CRITICAL"),
    ]
    cfg = {"window_seconds": 120, "error_count_threshold": 3, "per_service": True, "critical_immediate": True}
    decisions = evaluate(entries, cfg)
    d = [x for x in decisions if x.scope == "billing"][0]
    assert d.should_alert is True
    assert d.reason == "critical_immediate"
