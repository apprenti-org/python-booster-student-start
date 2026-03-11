# Python Booster — Student Start

Starter repositories for the Python Booster training program. Each module is a self-contained exercise built around a realistic enterprise service — a Log Monitoring Service that reads structured logs, evaluates threshold rules, and triggers alerts.

---

## Modules

### Module 05 — Legacy Code Analysis
`module-05-legacy-code-analysis/`

Read-only exercise. No tests, no requirements file — by design.

Your job is to understand the system before touching it: trace the data flow, read the configuration, examine the logs, and map what the code actually does versus what the runbook says it does. AI assistance is encouraged but must be verified against the actual code.

**Deliverables (see module README for full list):**
- Architecture read notes
- Data flow map
- AI prompt log (accepted vs rejected outputs)

---

### Module 06 — Bug Fix & Feature Extension
`module-06-bug-fix-feature-extension/`

There is a bug in this codebase. Find it, write a failing test first, then fix it. After the fix, extend the service with a new feature using the same test-first discipline.

Includes: `src/`, `tests/`, `config/`, `logs/`, `docs/` (with `ai-prompt-log.md` to fill in)

**Quick start:**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

---

### Module 07 — DevOps & CI/CD Awareness
`module-07-devops-cicd/`

The service is wired into a GitHub Actions CI pipeline (lint → security scan → tests). Your job is to understand the pipeline, deliberately break it in controlled ways, interpret the failures, and document what you learn.

Includes: `.github/workflows/ci.yml`, `scripts/simulate_ci_failure.py`, `docs/devops-notes/` (to fill in)

**Quick start:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest flake8 bandit pyyaml
pytest -q
flake8 src tests --max-line-length=100
bandit -r src -ll
```

**CI failure simulation:**
```bash
python scripts/simulate_ci_failure.py test
# commit, open a PR, observe the CI failure
git restore .
```

---

## The Service (All Modules)

All three modules build on the same Log Monitoring Service:

| File | Responsibility |
|------|----------------|
| `src/parser.py` | Parses and validates log lines; defensive input handling |
| `src/threshold.py` | Evaluates threshold rules (e.g. 3 ERRORs in 2 minutes) |
| `src/processor.py` | Orchestrates: read → parse → evaluate → decide → alert |
| `src/alert_adapter.py` | Boundary to external alerting; isolated and mockable |

---

## Engineering Expectations

**Understanding precedes modification.** Read the code, trace the data flow, check the config and logs before writing anything.

**Test-first discipline.** For any bug fix or feature: write a failing test, implement the fix, confirm the test passes.

**AI is a tool, not an authority.** Use it to summarize unfamiliar code or propose test skeletons. Cross-check every output against actual behavior.

**Scope matters.** Only change what the task requires. Unsanctioned refactors introduce risk.
