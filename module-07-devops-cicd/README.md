# Module 7 Starter: Log Monitoring Service

Minimal starter repo for **DevOps & CI/CD Awareness**.

## Structure
- `src/` core modules
- `tests/` pytest suite
- `config/config.yml` configuration
- `logs/application.log` sample input
- `.github/workflows/ci.yml` CI pipeline (lint, security scan, tests)
- `scripts/simulate_ci_failure.py` deliberate CI break simulations

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest flake8 bandit pyyaml
pytest -q
flake8 src tests --max-line-length=100
bandit -r src -ll
```

## CI failure simulation (teaching)
```bash
python scripts/simulate_ci_failure.py test
# commit, open PR, observe CI fail
git restore .
```
