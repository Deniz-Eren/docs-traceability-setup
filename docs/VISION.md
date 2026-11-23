## Purpose

Define the long-term vision and the principles of docs-traceability-setup.

## Structure

The document has the mission, the principles, and the target result.

## Formatting Rules

- Use short and clear language.
- Look at the vision again and update it when the direction of the project
  changes. Record the change as an ADR in [DECISIONS.md](DECISIONS.md).

## Mission

Agent Skill for scaffolding and migrating Sphinx/MyST/Sphinx-Needs docs-as-code
traceability models with CMake/CTest and Python source-text checks.

## Principles

- **Single source of truth:** Each procedure is in one skill file. Each target
  repository configuration item is in `.docs-traceability-setup.yml`, and editor
  formatting and file header rules are in `.editorconfig`.
- **One model, calculated views:** Each traceability item is written one time as
  a Sphinx-Needs directive. The build generates all indexes, back-links, tables,
  and coverage reports automatically.
- **Forward links only:** record links one time on the lower or derived item,
  and Sphinx-Needs computes reverse links.
- **Stop the build, do not change the rule:** warnings are errors in the target
  build, and source-text checks must pass without weakening rules.
- **Always correct:** do not commit a change that breaks the tests, linter,
  formatter, or document verification checks.
- **Traceable:** record each architectural decision as an ADR, and add an
  `Assisted-by:` footer to each AI-assisted commit.

## Target Result

A self-contained, installable Agent Skill repository whose root is the skill
root (`SKILL.md`, `references/`, `scripts/`, and `assets/`), providing:

- Complete setup and migration workflows for docs-as-code traceability across
  all programming languages with Sphinx 8, Sphinx-Needs 9, MyST-Parser 4, CMake,
  and CTest.
- Support for both `slug` and fixed-width zero-padded `number` permanent ID
  styles configured in `.docs-traceability-setup.yml`.
- Python 3.11+ standard-library-only source-text checkers (`check_text.py`,
  `check_headers.py`, `check_line_length.py`) with full unit test coverage in
  `scripts/tests/`.
- Clean verification across all acceptance criteria defined in
  [init-prompt.md](init-prompt.md).
