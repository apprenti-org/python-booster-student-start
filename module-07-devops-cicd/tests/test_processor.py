    from pathlib import Path
    from datetime import datetime, timezone
    from src.processor import process_log_file

    class FakeSender:
        def __init__(self):
            self.sent = []
        def send(self, title: str, body: str) -> None:
            self.sent.append((title, body))

    def test_process_log_file_smoke(tmp_path: Path):
        # Arrange: minimal config + log file
        cfg = tmp_path / "config.yml"
        cfg.write_text(
            """service:
  name: log-monitor
thresholds:
  window_seconds: 120
  error_count_threshold: 2
  critical_triggers_immediately: true
  scope: global
alerting:
  provider: print
logging:
  level: INFO
""",
            encoding="utf-8",
        )

        logf = tmp_path / "application.log"
        logf.write_text(
            '\n'.join([
                '{"ts":"2026-02-16T09:00:00Z","service":"svc","level":"ERROR","message":"e1"}',
                '{"ts":"2026-02-16T09:00:10Z","service":"svc","level":"ERROR","message":"e2"}',
            ]),
            encoding="utf-8",
        )

        sender = FakeSender()
        now = datetime(2026, 2, 16, 9, 0, 20, tzinfo=timezone.utc)

        # Act
        result = process_log_file(logf, cfg, sender=sender, now=now)

        # Assert
        assert result.processed_lines == 2
        assert result.parsed_entries == 2
        assert result.malformed_lines == 0
        assert result.decision.should_alert is True
        assert len(sender.sent) == 1
