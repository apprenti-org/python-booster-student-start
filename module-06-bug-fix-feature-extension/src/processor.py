from __future__ import annotations

import argparse
import logging
from typing import Any, Dict, List, Tuple
import yaml

from .parser import read_log_file
from .threshold import evaluate
from .alert_adapter import AlertAdapter

def _configure_logging(cfg: Dict[str, Any]) -> None:
    level_name = str(cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    service_log_path = cfg.get("service_log_path", "logs/service.log")

    logging.basicConfig(
        filename=service_log_path,
        level=level,
        format="%(asctime)sZ %(levelname)s %(name)s - %(message)s",
    )

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def process(logfile_path: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)

    entries, malformed = read_log_file(logfile_path)
    logger.info("startup: entries=%d malformed=%d", len(entries), malformed)

    decisions = evaluate(entries, cfg.get("thresholds", {}))

    # Initialize alert adapter
    alert_cfg = cfg.get("alerting", {})
    adapter = AlertAdapter(
        webhook_url=str(alert_cfg.get("webhook_url", "")),
        timeout_seconds=int(alert_cfg.get("timeout_seconds", 2)),
        fail_open=bool(alert_cfg.get("fail_open", True)),
    )

    alerts_sent = 0
    alerts_failed = 0

    for d in decisions:
        logger.info(
            "threshold_eval scope=%s should_alert=%s reason=%s error_count=%d critical_count=%d window_start=%s window_end=%s",
            d.scope, d.should_alert, d.reason, d.error_count, d.critical_count, d.window_start.isoformat(), d.window_end.isoformat()
        )

        if not d.should_alert:
            continue

        payload = {
            "scope": d.scope,
            "reason": d.reason,
            "error_count": d.error_count,
            "critical_count": d.critical_count,
            "window_start": d.window_start.isoformat(),
            "window_end": d.window_end.isoformat(),
        }

        result = adapter.send_alert(payload)
        if result.ok:
            alerts_sent += 1
            logger.warning("alert_triggered scope=%s result=%s", d.scope, result.message)
        else:
            alerts_failed += 1
            logger.error("alert_failed scope=%s result=%s", d.scope, result.message)

    logger.info("shutdown: alerts_sent=%d alerts_failed=%d", alerts_sent, alerts_failed)

    return {
        "entries": len(entries),
        "malformed": malformed,
        "decisions": decisions,
        "alerts_sent": alerts_sent,
        "alerts_failed": alerts_failed,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/config.yml")
    ap.add_argument("--logfile", default="logs/application.log")
    args = ap.parse_args()

    cfg = load_config(args.config)
    _configure_logging(cfg.get("logging", {}))

    process(args.logfile, cfg)

if __name__ == "__main__":
    main()
