---
name: ruff
description: >
  Lint and format Python source files in docs-traceability-setup with ruff. Use
  when checking code style, fixing formatting, updating ruff.toml, or debugging
  lint violations.
---

# Ruff (Lint and Format)

## Configuration

`ruff.toml` at the repository root configures both `ruff check` and `ruff
format`:

- `target-version = "py311"`
- `line-length = 80`
- `[lint] select = ["E", "F", "W", "I"]`
- `extend-exclude = ["assets/repo"]`

Any change to `ruff.toml` must be verified against the installed `ruff` version
in `.venv` and recorded as an ADR in [docs/DECISIONS.md](../../DECISIONS.md).

## Commands

Check lint violations inside `.venv`:

```bash
source .venv/bin/activate && ruff check scripts
```

Check formatting (read-only):

```bash
source .venv/bin/activate && ruff format --check scripts
```

Auto-format Python files in place:

```bash
source .venv/bin/activate && ruff format scripts
```

Verify `ruff.toml` syntax against a minimal snippet:

```bash
source .venv/bin/activate && \
  printf 'x = 1\n' | ruff check --stdin-filename sample.py -
```

## Integration with Agents

- `scripts/build-agent.sh` runs `ruff check` on `scripts/` (delegated to
  [docs/agents/build.md](../../agents/build.md)).
- `scripts/formatter-agent.sh` runs `ruff format --check` (or `ruff format` with
  `--fix`) on `scripts/` (delegated to
  [docs/agents/format-validator.md](../../agents/format-validator.md)).
