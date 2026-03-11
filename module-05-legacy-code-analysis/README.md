# Log Monitoring Service (Training Project)

This project is a simplified Log Monitoring Service used for training on architecture reading, defensive design, testing discipline, and legacy-code analysis. The service reads structured log data from `application.log`, evaluates error thresholds, and triggers alerts through an adapter layer. It also supports production-minded behavior through configuration and a runbook.

---

## What This System Does

The system:

- Reads structured log lines from `logs/application.log`
- Parses and validates each log entry
- Evaluates threshold rules (configured in `config/config.yml`)
- Decides whether an alert should be triggered
- Sends an alert through a mockable alert adapter
- Operates defensively (malformed input, failures, and misconfiguration should not cause silent success)

This is designed as a **system component**, not a one-off script.

---

## Repository Structure

```
src/
  parser.py
  threshold.py
  processor.py
  alert_adapter.py

logs/
  application.log

config/
  config.yml

docs/
  runbook.md
```


### `src/`
- **parser.py**  
  Parses and validates log lines. Responsible for input handling and defensive behavior.

- **threshold.py**  
  Contains the threshold evaluation logic (rules such as “3 ERRORs in 2 minutes”).

- **processor.py**  
  Orchestrates the end-to-end flow: read → parse → evaluate → decide → alert → log/summary.

- **alert_adapter.py**  
  The boundary to external alerting. Must be isolated and mockable. Should fail safely.

### `logs/application.log`
Sample input data representing structured logs. Used for:
- behavior observation
- simulation
- edge/failure scenario injection

### `config/config.yml`
Configuration source for:
- threshold rules
- allowed log levels
- alerting behavior assumptions
- optional toggles used in “deployment” simulation

### `docs/runbook.md`
Operational expectations for this service:
- input format assumptions
- threshold rules
- failure behavior expectations
- logging expectations
- what to monitor / how to troubleshoot

If the code and runbook disagree, the runbook must be updated.

---

## How to Run (Simple)

This project is intentionally lightweight. A typical approach is:

1. Load configuration (`config/config.yml`)
2. Read log input (`logs/application.log`)
3. Process entries using `processor.py`

> If you don’t have a `main.py` yet, teams can create one during the implementation sprint
> or run functions directly in a REPL for exploration.

---

## Key Engineering Expectations

### Defensive by Default
The system should:
- skip malformed log entries without crashing
- fail safely on misconfiguration
- log meaningful evidence of decisions and failures
- keep alerting isolated so alert failures do not automatically crash processing

### Test-Driven Mindset
Even if tests are not included yet in this minimal structure, teams are expected to:
- write a test plan before final logic
- implement unit, edge, and failure tests
- validate that tests meaningfully fail when behavior is wrong

### AI Is Allowed (But Not Trusted)
AI can help:
- summarize unfamiliar code
- propose test skeletons
- identify likely risk areas

AI must not be treated as authoritative. All AI explanations must be cross-checked against:
- the actual code
- logs
- configuration
- observed behavior

---

## Suggested Deliverables (Training)

Depending on the module, teams may produce:

- `docs/legacy-notes/architecture-read.md`
- `docs/legacy-notes/log-behavior.md`
- `docs/legacy-notes/change-history.md`
- `docs/legacy-notes/data-flow-map.md`
- `docs/ai-prompt-log.md`
- `docs/deployment-notes.md`

---

## “Done” Definition (For a Merge-Ready Feature)

A feature is considered merge-ready when:

- All tests pass (unit + edge + failure)
- Failure behavior is defensive and intentional
- No obvious security gaps (input validation, no hardcoded sensitive values)
- `docs/runbook.md` matches actual behavior
- AI prompt log documents accepted vs rejected output
- Code is explainable without rereading it

---

## License / Use

Training and instructional use only unless otherwise specified.
