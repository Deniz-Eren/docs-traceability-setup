## Purpose

Define the conventions of docs-traceability-setup for file names, document
formatting, and copyright headers.

## Structure

The conventions are in groups by category: file names, document formatting,
document purposes, and copyright headers.

## Formatting Rules

- You must obey all conventions. A convention with the mark "recommended" is an
  alternative.
- Record each deviation as an ADR in [DECISIONS.md](DECISIONS.md).

---

## File Names

- **Scaffolding docs in `docs/`:** UPPERCASE, single or hyphenated word (for
  example `TASKS.md`, `THIRD-PARTY-NOTICES.md`).
- **Other documents:** A clear name (for example `init-prompt.md`).
- **Development skills:** `docs/skills/<lowercase-name>/SKILL.md`, with
  directory name matching frontmatter `name` (for example
  `docs/skills/git/SKILL.md`).
- **Agent definitions:** `docs/agents/<lowercase-kebab>.md` (for example
  `docs/agents/build.md`).
- **Deliverable skill root:** Repository root `SKILL.md` with `references/`,
  `scripts/`, and `assets/` (for example `SKILL.md`, `references/model.md`).

## Document Formatting

- All generated markdown files in `docs/` (but not in `docs/skills/` or
  `docs/agents/`, and not immutable imported documents) start with these three
  headings, in this sequence:

  ```
  ## Purpose
  ## Structure
  ## Formatting Rules
  ```

- Do not put markdown links in backticks.
- Procedures are only in skill files. Other documents link to them.

## Document Purposes

| File | Contains | Must NOT contain |
|---|---|---|
| `ARCHITECTURE.md` | Current structure and components | Decisions or causes |
| `DECISIONS.md` | ADRs (dated, append-only) | Current structure |
| `TASKS.md` | Tasks with their status | General information |
| `CHANGELOG.md` | Important changes by version | Current architecture |
| `VISION.md` | Mission and principles | Tasks |
| `CONVENTIONS.md` | Names, formatting, copyright | Decisions |
| `THIRD-PARTY-NOTICES.md` | Third-party attribution | Internal architecture |

## Copyright Headers

License: **MIT License**. Copyright line: Copyright (c) 2026 Deniz Eren
<deniz.eren@outlook.com>

Each file with comments starts with the copyright line in the comment syntax of
its language (within the first 5 lines).

- **Python (`*.py`)**: canonical Doxygen header (`##`, `@file`, `@brief`,
  `@copyright` on line 5 with `[file-header]` lines from `.editorconfig`).
- **Shell (`*.sh`)**: `# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>`
  after the shebang line.
- **TOML, YAML, INI, Requirements (`ruff.toml`, `.editorconfig`, `*.yml`,
  `*.yaml`, `requirements-dev.txt`)**: `# Copyright (c) 2026 Deniz Eren
  <deniz.eren@outlook.com>`.

**Exclusions:** markdown, `.gitignore`, license files, JSON, `.python-version`,
`.agent-scaffolding.yml`, paths in `exclude_paths` (`assets/repo/`), and
immutable or append-only imported documents (`docs/init-prompt.md`, copied
specs).
