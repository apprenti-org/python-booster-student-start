# Log Monitoring Service (Legacy Code)

This repository is intentionally **legacy-style** code used for Module 5–6 activities:
- Read architecture + infer behavior
- Examine change history
- Map data flow
- AI-assisted legacy reading (disciplined)
- **Module 6: Bug Fix & Feature Extension**
  - Identify root cause
  - Write failing test first
  - Implement minimal fix
  - Add new feature safely
  - Improve validation + exception handling + logging

## Quick Start

### 1) Create venv + install deps
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

### 2) Run tests
```bash
pytest -q
```

### 3) Run the service (process application.log)
```bash
python -m src.processor --config config/config.yml --logfile logs/application.log
```

## Project Structure

```
src/
  parser.py
  threshold.py
  processor.py
  alert_adapter.py

logs/
  application.log
  service.log

config/
  config.yml

docs/
  runbook.md
  ai-prompt-log.md
  legacy-notes/
```

> NOTE: This is a **teaching repo**. Some behavior is intentionally imperfect to support debugging, test-first repairs, and safe feature extension.
