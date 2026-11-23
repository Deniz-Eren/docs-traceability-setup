## Purpose

Write the architecture of docs-traceability-setup in this document. Write the
files, their structure, and the task of each component.

## Structure

The document has a system overview, the directory structure, component
descriptions, and the integration points.

## Formatting Rules

- Write about the current condition only. Put decisions in
  [DECISIONS.md](DECISIONS.md).
- Use code blocks for directory trees.
- Link to skill files for procedures. Do not write the procedures here.

---

## System Overview

`docs-traceability-setup` is a mixed Python and Markdown repository. Its root is
the installable `docs-traceability-setup` Agent Skill (`SKILL.md`,
`references/`, `scripts/`, and `assets/`). The skill scaffolds or migrates a
Sphinx 8, MyST-Parser 4, Sphinx-Needs 9, CMake, and CTest traceability model in
target repositories. It also runs source-text checks (Doxygen headers, line
length, greedy prose packing) from `scripts/` with only the Python 3.11+
standard library. Repository development governance lives in `AGENTS.md`,
`docs/`, `ruff.toml`, `requirements-dev.txt`, and `scripts/*-agent.sh`.

## Directory Structure

```text
/
├── SKILL.md                   ← Deliverable Agent Skill entry point
├── README.md                  ← Install guide, commands, skill index
├── AGENTS.md                  ← Governance for AI agents
├── CHANGELOG.md               ← Changes between versions
├── LICENSE.md                 ← MIT License
├── .agent-scaffolding.yml     ← Scaffolding configuration
├── .editorconfig              ← Formatting and [file-header] rules
├── .gitignore                 ← Ignored build, cache, venv artifacts
├── .python-version            ← Baseline Python version (3.11)
├── requirements-dev.txt       ← Pinned dev dependencies (ruff)
├── ruff.toml                  ← Ruff lint and format configuration
├── technical_terms.txt        ← Project technical terms glossary
├── allowed_phrases.txt        ← Approved multi-word technical phrases
├── .agents/
│   └── skills                 ← Symlink to ../docs/skills
├── references/                ← Skill reference manuals
│   ├── authoring.md
│   ├── checks.md
│   ├── configuration.md
│   ├── migration.md
│   └── model.md
├── scripts/                   ← Source-text checkers + runner scripts
│   ├── build-agent.sh         ← Runs unittest and ruff check in .venv
│   ├── formatter-agent.sh     ← Runs ruff format check/fix in .venv
│   ├── check_headers.py       ← Doxygen header validator and fixer
│   ├── check_line_length.py   ← Line-length and prose-packing checker
│   ├── check_text.py          ← Unified CLI for source-text checks
│   ├── defaults.editorconfig  ← Fallback EditorConfig
│   ├── editorconfig.py        ← EditorConfig glob/header parser
│   ├── file_kinds.py          ← File kinds and repository discovery
│   ├── project_config.py      ← .docs-traceability-setup.yml parser
│   └── tests/                 ← Python unittest suite for scripts
├── assets/
│   ├── requirements.txt       ← Target Sphinx/Needs/MyST dependencies
│   └── repo/                  ← Target templates (config/tools/docs)
└── docs/
    ├── ARCHITECTURE.md        ← This file
    ├── CONVENTIONS.md         ← Names, formatting, copyright rules
    ├── DECISIONS.md           ← Architectural Decision Records (ADRs)
    ├── TASKS.md               ← Task records
    ├── THIRD-PARTY-NOTICES.md ← Third-party license attributions
    ├── VISION.md              ← Mission, principles, target result
    ├── init-prompt.md         ← Immutable initial skill specification
    ├── agents/                ← Subagent definitions
    └── skills/                ← Development skills and copied specs
```

## Component Descriptions

- **`SKILL.md` & `references/*.md`:** Deliverable `docs-traceability-setup`
  Agent Skill workflow, schema, model, authoring, checks, and migration manuals.
- **`scripts/*.py`, `scripts/defaults.editorconfig`, `scripts/tests/`:** Python
  3.11+ standard-library source-text checkers (headers, line length, greedy
  prose packing) and unit tests.
- **`assets/requirements.txt` & `assets/repo/`:** Target Sphinx-Needs 9 model
  (`needs_model.py`, `conf.py`, `tag_scan.py`, `need_tag_check.py`), standalone
  auditor (`check_needs_audit.py`), unit tests, CMake/CTest build, and layered
  docs templates.
- **`AGENTS.md`, `.agent-scaffolding.yml`, `.editorconfig`,
  `technical_terms.txt`, `allowed_phrases.txt`, `docs/`:** Repository
  governance, immutable specification ([init-prompt.md](init-prompt.md)),
  project terminology glossary, state records, subagent definitions, and
  development skills.
- **`scripts/*-agent.sh`, `ruff.toml`, `requirements-dev.txt`:** Local
  development verification runners and Ruff configuration inside `.venv`.

## Integration Points

- **`SKILL.md`:** Refers to `references/*.md`, `scripts/check_text.py`, and
  `assets/`. Target repositories use it for `docs-traceability-setup`.
- **`scripts/check_text.py`:** Imports `project_config.py`, `editorconfig.py`,
  `file_kinds.py`, `check_headers.py`, and `check_line_length.py`. It reads the
  target `.docs-traceability-setup.yml` and `.editorconfig` for skill workflows
  and check mode.
- **`assets/repo/config/sphinx/conf.py`:** Imports `needs_model.py`,
  `need_tag_check.py`, and `tag_scan.py`, and reads
  `.docs-traceability-setup.yml`. Target `docs/CMakeLists.txt` uses it for
  Sphinx builds.
- **`assets/repo/tools/traceability/check_needs_audit.py`:** Imports
  `needs_model.py` and reads `<build>/docs/needs/needs.json`. CTest `docs.audit`
  runs it.
- **`AGENTS.md`:** Links to `docs/skills/git`, `docs/skills/state-management`,
  `docs/skills/dev-environment`, and `docs/agents/`. All agent platforms read
  it.
- **`.agents/skills`:** Symlink to `docs/skills`. Agent platforms use it for
  development skill discovery.
