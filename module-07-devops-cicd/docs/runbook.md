# Runbook: Log Monitoring Service (Starter)

## Purpose
Monitors structured log lines in `logs/application.log` and triggers alerts based on threshold rules.

## Inputs
- `logs/application.log`: one JSON object per line
- `config/config.yml`: threshold + logging + alerting configuration

## Threshold Rules (default)
- Trigger alert when `ERROR` count within `window_seconds` >= `error_count_threshold`
- Trigger immediately when any `CRITICAL` entry is present (if enabled)

## Failure Behavior
- Malformed lines are skipped and logged as warnings.
- Alert send failures are logged and do not crash processing.

## What to Monitor
- Startup/config summary log
- Process summary log (counts + decision)
- Alert success/failure logs
