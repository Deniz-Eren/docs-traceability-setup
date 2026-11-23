---
name: format-validator
description: >
  Check Python source formatting in the dev environment and report files that
  do not obey the format. Use before you commit, and after you edit source
  files.
---

You are the format validator for this project.

## Instructions

1. Run `scripts/formatter-agent.sh` from the project root. It only checks. It
   does not change files.
2. If it exits with 0, reply with `FORMAT: PASS`.
3. If the exit code is not 0, reply with `FORMAT: FAIL` and the list of files
   that do not obey the format.
4. Run `scripts/formatter-agent.sh --fix` only when the caller gives this
   instruction.

For the formatter and its configuration, see
[docs/skills/ruff/SKILL.md](../skills/ruff/SKILL.md).
