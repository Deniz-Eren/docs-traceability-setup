---
name: dev-environment
description: >
  Set up, enter, and use the isolated native Python virtual environment of
  docs-traceability-setup. Use before you test, lint, or format, when you add
  development dependencies, or when environment problems occur.
---

# Development Environment

**Type:** Native (Python virtual environment `.venv`, targeting Python 3.11+)

## Setup

Create the virtual environment and install pinned development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Verify the installation with a smoke test:

```bash
source .venv/bin/activate && python --version && ruff --version
```

## Use

Run tests, linting, and formatting inside the virtual environment:

```bash
source .venv/bin/activate && python -m unittest discover -s scripts/tests
source .venv/bin/activate && ruff check scripts
source .venv/bin/activate && ruff format --check scripts
```

Delegate routine test, lint, and format runs to the build and format-validator
agents (`scripts/build-agent.sh` and `scripts/formatter-agent.sh`). These
scripts activate `.venv` automatically.

Runtime skill scripts in `scripts/` use only the Python 3.11+ standard library
and must continue to run with plain `python3` outside `.venv`.

## Dependencies

- Development tools are pinned in `requirements-dev.txt` (`ruff==0.17.6`).
- After adding or upgrading a dependency: reinstall with `pip install -r
  requirements-dev.txt`, record an ADR if tool configuration changes, and add
  attribution in [docs/THIRD-PARTY-NOTICES.md](../../THIRD-PARTY-NOTICES.md).
- Do not add third-party runtime dependencies for `scripts/*.py`.

## Troubleshooting

- **`.venv/bin/activate: No such file or directory`:** Run `python3 -m venv
  .venv && .venv/bin/pip install -r requirements-dev.txt`.
- **`ruff: command not found`:** Activate `.venv` or run `.venv/bin/pip install
  -r requirements-dev.txt`.
- **Python version older than 3.11:** Create `.venv` with a Python 3.11+
  interpreter (for example `python3.12 -m venv .venv`).
