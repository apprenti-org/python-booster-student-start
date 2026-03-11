"""Simulate CI failures for Module 7.

Usage:
  python scripts/simulate_ci_failure.py lint
  python scripts/simulate_ci_failure.py test
  python scripts/simulate_ci_failure.py security

Rollback:
  git restore .
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def break_lint():
    target = ROOT / "src" / "ci_break_lint.py"
    target.write_text("x=1\nprint(  'bad spacing'  )\n", encoding="utf-8")
    print(f"Created {target} to trigger flake8 failure.")

def break_test():
    target = ROOT / "tests" / "test_ci_break.py"
    target.write_text(
        "def test_ci_break():\n"
        "    assert 1 == 2, 'Intentional failure for CI simulation'\n",
        encoding="utf-8",
    )
    print(f"Created {target} to trigger pytest failure.")

def break_security():
    target = ROOT / "src" / "ci_break_security.py"
    target.write_text(
        "def dangerous(user_input: str):\n"
        "    return eval(user_input)\n",
        encoding="utf-8",
    )
    print(f"Created {target} to trigger bandit failure.")

def main():
    if len(sys.argv) != 2:
        print("Choose one: lint | test | security")
        sys.exit(2)
    mode = sys.argv[1].strip().lower()
    if mode == "lint":
        break_lint()
    elif mode == "test":
        break_test()
    elif mode == "security":
        break_security()
    else:
        print("Unknown mode. Choose: lint | test | security")
        sys.exit(2)
    print("\nNext: commit and open a PR to observe CI failure.")
    print("Rollback with: git restore .")

if __name__ == "__main__":
    main()
