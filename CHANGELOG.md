## Purpose

Record the important changes of docs-traceability-setup. The format follows
[Keep a Changelog](https://keepachangelog.com).

## Structure

- The `## [Unreleased]` section is at the top. Below it, the releases are newest
  first (git log order).
- Category headings of level 3 in each section: `### Added`, `### Changed`, `###
  Deprecated`, `### Removed`, `### Fixed`, and `### Security`. Put a heading
  into the file only when the section has content for it.

## Formatting Rules

- Release heading: `## [x.y.z] - YYYY-MM-DD`.
- The entries in each category are newest first (git log order).
- Write each entry as a complete sentence with a final period.

## [Unreleased]

### Changed

- Revised editable repository documentation, skill manuals, and code comments
  for simplified technical English style (sentence length, active voice, modal
  verbs, and consistent terminology). Use any currently installed simplified
  technical English skills to check, and skip if not installed.
- Added root `.editorconfig` with `[file-header]` rules. Skipped top-of-file
  Markdown YAML frontmatter during prose packing. Brought all editable files
  into 80-column and greedy prose-packing compliance.
- Standardized all target `needtable` directives on the default DataTables style
  (`NEEDS_DATATABLES`) with captions and `as "Label"` aliases. Added render-time
  source-order preservation (`needtable_preserve_order_docs`) and numbered
  decision-index reversal (`needtable_reverse_docs`). Documented record order in
  `references/model.md` and ordered `docs/TASKS.md` newest first.
- Standardized `scripts/check_headers.py`, `scripts/*.py`, and `assets/repo/` on
  the canonical Doxygen header grammar (`@file`, `@brief`, optional `@details`,
  `@copyright` on its own line, verbatim `[file-header]` lines, contiguous
  `01..NN` keys, and closing bare comment line).
- Upgraded `scripts/check_line_length.py` with AST Python docstring scanning,
  MyST `---` YAML directive options, `# need::` tags in docstrings, wrapped
  list-item packing, and verbatim `[file-header]` notice exemptions.
- Fixed `needtable` column aliases in `assets/repo/docs/` to use `;` delimiters
  with `as "Label"`. Scoped record overview tables by `docname`. Added C/C++
  Doxygen `\req{<ID>}` and YAML/EditorConfig `#` markers in `tag_scan.py` and
  `needs_model.py`, and validated `parent_need` and `parent_needs` in
  `check_needs_audit.py`.

### Added

- Resultant target project file structure overview and behavior summary in
  `README.md`.
- General port-and-replace procedure for repositories with pre-existing project
  scaffolding or state documents equivalent to the impacted traceability files
  (vision, architecture, decisions, conventions, tasks, and roadmap): ports and
  removes replaced files, updates governance and skill references (`AGENTS.md`,
  `README.md`, project state-management skills), and excludes `skills`,
  `agents`, and `THIRD-PARTY-NOTICES.md` from Sphinx in
  `assets/repo/config/sphinx/conf.py`.
- Project glossary files (`technical_terms.txt` and `allowed_phrases.txt`) at
  the repository root and ADR-10 in `docs/DECISIONS.md`.
- End-to-end acceptance verification across `slug` mode, 4-digit `number` mode,
  `subdirectory` CMake mode, migration mode, all negative
  traceability/source-text gates, and repository scaffolding verification.
- Root `SKILL.md`, `references/` documentation (`configuration.md`, `model.md`,
  `authoring.md`, `checks.md`, `migration.md`), installation instructions in
  `README.md`, and updated `docs/ARCHITECTURE.md`.
- Target repository templates, Sphinx-Needs 9 configuration/extensions
  (`needs_model.py`, `conf.py`, `tag_scan.py`, `need_tag_check.py`), standalone
  model auditor (`check_needs_audit.py`), unit tests, and CMake/CTest build
  files under `assets/`.
- Python 3.11+ standard-library source-text checker scripts
  (`project_config.py`, `editorconfig.py`, `file_kinds.py`, `check_headers.py`,
  `check_line_length.py`, `check_text.py`, `defaults.editorconfig`) and unit
  tests in `scripts/tests/`.
- Scaffolding with the agent-scaffolding agent skill 0.2.0 (`dev_environment`,
  `build_agents`, `tool_configs`, and `copyright` modules). The configuration is
  in `.agent-scaffolding.yml`.
- Immutable pre-existing specification document `docs/init-prompt.md` and
  `LICENSE.md` (MIT License).
