#!/usr/bin/env bash
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
#
# Build agent: unit tests and static analysis for docs-traceability-setup.
# The exit code is 0 for PASS, and not 0 for FAIL.
set -euo pipefail
cd "$(dirname "$0")/.."

run() {
  # shellcheck disable=SC1091
  (source .venv/bin/activate && "$@")
}

echo "==> test"
if [ -d scripts/tests ] && find scripts/tests \( -name 'test_*.py' \) -print -quit | grep -q .; then
  run python -m unittest discover -s scripts/tests
else
  echo "No unit tests in scripts/tests yet (skipped)."
fi

echo "==> lint"
if [ -d scripts ] && find scripts -path 'scripts/__pycache__' -prune -o -type f \( -name '*.py' \) -print -quit | grep -q .; then
  run ruff check scripts
else
  printf 'x = 1\n' | run ruff check --stdin-filename sample.py -
fi

echo "BUILD: PASS"
