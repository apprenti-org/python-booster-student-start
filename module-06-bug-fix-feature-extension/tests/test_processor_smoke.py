import os
import tempfile
import yaml
from src.processor import process, _configure_logging

def test_processor_runs_and_returns_summary(tmp_path):
    # Create a tiny log file
    log_path = tmp_path / "app.log"
    log_path.write_text(
        '\n'.join([
            '{"timestamp":"2026-01-15T14:00:00Z","service":"auth","level":"INFO","message":"ok","event_id":"a"}',
            '{"timestamp":"2026-01-15T14:00:10Z","service":"auth","level":"ERROR","message":"e1","event_id":"b"}',
            '{"timestamp":"2026-01-15T14:00:20Z","service":"auth","level":"ERROR","message":"e2","event_id":"c"}',
        ]) + "\n",
        encoding="utf-8"
    )

    service_log = tmp_path / "service.log"

    cfg = {
        "thresholds": {"window_seconds": 120, "error_count_threshold": 3, "per_service": True, "critical_immediate": True},
        "alerting": {"webhook_url": "https://example.invalid/webhook", "timeout_seconds": 1, "fail_open": True},
        "logging": {"service_log_path": str(service_log), "level": "INFO"},
    }

    _configure_logging(cfg["logging"])
    result = process(str(log_path), cfg)
    assert result["entries"] == 3
    assert result["malformed"] == 0
    assert "alerts_sent" in result
