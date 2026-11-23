#!/usr/bin/env bash
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
#
# Formatter agent for docs-traceability-setup. Checks formatting only (no lint).
# Command: scripts/formatter-agent.sh [--fix]
# The exit code is 0 when formatting is clean, and not 0 when there are violations.
set -euo pipefail
cd "$(dirname "$0")/.."

FIX=0
[ "${1:-}" = "--fix" ] && FIX=1

run() {
  # shellcheck disable=SC1091
  (source .venv/bin/activate && "$@")
}

SRC_DIRS=(scripts)
echo "==> format ($([ "$FIX" -eq 1 ] && echo fix || echo check)): ${SRC_DIRS[*]}"

if [ -d scripts ] && find scripts -path 'scripts/__pycache__' -prune -o -type f \( -name '*.py' \) -print -quit | grep -q .; then
  if [ "$FIX" -eq 1 ]; then
    run ruff format "${SRC_DIRS[@]}"
  else
    run ruff format --check "${SRC_DIRS[@]}"
  fi
else
  printf 'x = 1\n' | run ruff format --check --stdin-filename sample.py -
fi

echo "FORMAT: PASS"
