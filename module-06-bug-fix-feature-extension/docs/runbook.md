# Runbook — Log Monitoring Service (Legacy)

## Purpose
This service reads structured log events from a JSON Lines file (`application.log`), evaluates error thresholds, and triggers alerts when thresholds are exceeded.

## Inputs
- **Log file:** `logs/application.log`
- **Format:** JSON Lines (one JSON object per line)
- **Required fields per entry:**
  - `timestamp` (ISO 8601 string, UTC recommended)
  - `service` (string)
  - `level` (INFO | WARNING | ERROR | CRITICAL)
  - `message` (string)
- Optional:
  - `event_id` (string) — used for dedupe in future extensions

## Threshold Rules
Configured in `config/config.yml`:

- `window_seconds`: time window used for evaluation
- `error_count_threshold`: number of ERROR entries within the window that triggers an alert
- `per_service`: if true, evaluate thresholds per service
- `critical_immediate`: if true, any CRITICAL triggers an alert immediately

## Failure Behavior (Expected)
- Malformed JSON lines should not crash the system.
- Missing required fields should be handled defensively (skipped with a warning).
- Alert provider failures should be logged; system should continue processing if `fail_open: true`.

## Operational Logging
The service writes operational logs to:
- `logs/service.log`

Expected events:
- Startup / shutdown
- Lines processed summary
- Malformed lines skipped count
- Threshold evaluation results
- Alerts triggered
- Alert failures

## Known Legacy Risk Areas
- Time window boundary handling (edge cases around “exactly on the boundary”)
- Configuration drift (keys added/removed over time)
- Alert adapter dependency assumptions (network failures)

## What to Monitor First
- Alert failures (network/provider)
- Spike in malformed input
- Unexpected drops in alert volume
- Threshold evaluation logs (to confirm decisions are visible)
