---
name: unittest
description: >
  Run and organize Python unittest suites for docs-traceability-setup scripts.
  Use when running unit tests, adding new test modules under scripts/tests/, or
  debugging test failures.
---

# Python unittest

## Layout

Unit tests for the skill's Python 3.11+ standard-library scripts live in
`scripts/tests/` with `test_*.py` filenames (for example
`test_check_headers.py`, `test_check_line_length.py`, `test_editorconfig.py`,
`test_project_config.py`).

## Commands

Run the full unit test suite in `.venv`:

```bash
source .venv/bin/activate && python -m unittest discover -s scripts/tests -v
```

Run a single test file:

```bash
source .venv/bin/activate && \
  python -m unittest scripts/tests/test_editorconfig.py
```

Test standard-library-only execution without `.venv`:

```bash
python3 -m unittest discover -s scripts/tests
```

## Integration with build-agent.sh

`scripts/build-agent.sh` activates `.venv` and runs `python -m unittest discover
-s scripts/tests` whenever `scripts/tests/` exists and contains `test_*.py`
files. Delegate routine test runs to the [build agent](../../agents/build.md).
