# Runbook: Log Monitoring Service

## Purpose

This document defines how the Log Monitoring Service is expected to behave in a production-like environment. It describes input expectations, threshold logic, alert behavior, failure handling, logging requirements, and operational response guidelines.

If system behavior changes, this runbook must be updated to reflect reality.

---

# 1. System Overview

The Log Monitoring Service:

- Reads structured log data from `logs/application.log`
- Parses and validates each entry
- Evaluates threshold rules defined in `config/config.yml`
- Determines whether an alert is required
- Sends alerts through an alert adapter
- Logs structured audit events

This service is a system component, not a standalone script. It may feed dashboards, monitoring pipelines, or automated workflows.

---

# 2. Input Expectations

## Log File

- File: `logs/application.log`
- Format: Structured log lines (JSON or structured text)
- Required fields (minimum expected schema):
  - `timestamp`
  - `service`
  - `level`
  - `message`

## Accepted Log Levels

Configured in `config/config.yml`.

Common expected values:
- INFO
- WARNING
- ERROR
- CRITICAL

Unknown or malformed log levels must:
- Be logged
- Not crash the system

## Malformed Input Handling

If a log line:
- Is invalid JSON
- Is missing required fields
- Contains unexpected structure

The system must:
- Log the malformed entry
- Skip it safely
- Continue processing remaining entries

The system must never silently succeed.

---

# 3. Threshold Rules

Threshold rules are defined in `config/config.yml`.

Example rule:

- Trigger alert when **3 or more ERROR entries occur within 2 minutes for the same service**
- Trigger immediately on any CRITICAL entry

Threshold configuration must specify:

- Count-based or rate-based rule
- Time window
- Scope (global or per-service)
- Cooldown behavior (if applicable)

## Misconfiguration Behavior

If threshold configuration is:
- Missing
- Invalid
- Unreadable
- Illogical (e.g., negative values)

The system must:
- Log a configuration error
- Fail safely (either halt or fall back to documented default)
- Never silently ignore configuration issues

---

# 4. Alerting Behavior

Alerts are sent via `alert_adapter.py`.

Supported alert types (example):
- Email
- SMS
- Webhook

## Alert Decision Flow

1. Threshold evaluation returns True
2. Decision layer confirms alert needed
3. Alert adapter invoked

## Alert Failure Handling

If alert sending fails:

- The exception must be caught
- Failure must be logged
- Processing must continue (unless explicitly designed to halt)

Alert failure must not cause log processing to stop unexpectedly.

---

# 5. Logging & Observability

The service must produce structured logs that include:

- Start of processing
- End of processing
- Number of lines processed
- Number of malformed lines skipped
- Threshold evaluation result
- Alert triggered (yes/no)
- Alert failure (if any)

Logs should be written to:

- `service.log`
- stdout (if configured)

Logs must make behavior observable. Silent failure is unacceptable.

---

# 6. Failure Scenarios & Expected Behavior

| Scenario | Expected Behavior |
|-----------|------------------|
| Malformed log entry | Log error, skip entry, continue |
| Empty file | Log summary, no alert |
| Threshold met | Alert triggered once (per rule) |
| Alert handler throws exception | Log failure, continue safely |
| Config missing | Log error, fail safely |
| Log file unreadable | Log error, halt cleanly |

---

# 7. Operational Monitoring

Operators should monitor:

- Spike in ERROR/CRITICAL entries
- Repeated alert failures
- High malformed entry counts
- Configuration load failures
- Unexpected absence of log output

## Indicators of Healthy Operation

- Consistent start/end processing logs
- Threshold evaluations logged clearly
- No unhandled exceptions
- Alert decisions visible in logs

## Indicators of Instability

- Silent runs with no logs
- Uncaught exceptions
- Repeated alert failures
- Processing stops mid-run
- Missing configuration warnings

---

# 8. Deployment Expectations

In a production-like deployment:

- Configuration should not be hardcoded
- Alert credentials should not be embedded in code
- File paths should be configurable
- Alert adapter must be mockable for testing

---

# 9. Known Limitations (Training Version)

This project may not include:

- Real distributed alert infrastructure
- High-volume asynchronous processing
- Rate limiting beyond simple threshold
- Log rotation handling
- Distributed tracing

These are considered out of scope unless explicitly implemented.

---

# 10. Change Control

Any modification to:

- Threshold logic
- Parsing rules
- Alert behavior
- Logging structure

Requires:

- Updated tests
- Updated runbook
- Validation Gate review
- Peer code review

---

# 11. Final Reminder

This service is not judged by how fast it runs.
It is judged by how safely it behaves under stress.

If the system fails, logs must explain why.
If alerts fail, logs must explain why.
If configuration is wrong, logs must explain why.

Defensive behavior is not optional.
It is the baseline.
