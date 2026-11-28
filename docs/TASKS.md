## Purpose

Record all the tasks of docs-traceability-setup. Give the status and the date
for each task.

## Structure

Each task is a checkbox. The checkbox can have a date. The tasks are in groups
by category, ordered newest first within each category.

## Formatting Rules

- Use `- [ ] <type>: <description>` for open tasks.
- Use `- [x] COMPLETE YYYY-MM-DD <type>: <description>` for complete tasks.
- Put the tasks below `<!-- [CAT] Category -->` comments, newest first.
- Do not remove completed tasks.

<!-- [CAT] Scaffolding -->

- [x] COMPLETE 2026-11-20 scaffold: apply agent-scaffolding 0.2.0

<!-- [CAT] Development -->

- [x] COMPLETE 2026-11-28 refactor: write short license summaries with no full
  license text blocks in THIRD-PARTY-NOTICES.md and state-management skill
  (ADR-12)
- [x] COMPLETE 2026-11-24 docs: document resultant target project file structure
  in README.md
- [x] COMPLETE 2026-11-24 feat: port and replace pre-existing project
  scaffolding files when applying docs-traceability-setup
- [x] COMPLETE 2026-11-20 docs: align repository documentation with simplified
  technical English and add project glossary
- [x] COMPLETE 2026-11-20 chore: add root .editorconfig and bring all editable
  repository files into full check_text.py compliance
- [x] COMPLETE 2026-11-20 feat: align needtable DataTables styling and preserve
  record render ordering
- [x] COMPLETE 2026-11-20 fix: align Doxygen header grammar, AST docstring
  packing, MyST YAML directive options, and Sphinx-Needs 9 table column aliases
- [x] COMPLETE 2026-11-20 test: verify acceptance criteria in slug mode, number
  mode, subdirectory CMake mode, and migration mode
- [x] COMPLETE 2026-11-20 feat: author root SKILL.md, README.md install
  instructions, and references/ documentation
- [x] COMPLETE 2026-11-20 feat: create target repository templates and
  Sphinx-Needs traceability tools in assets/
- [x] COMPLETE 2026-11-20 feat: implement Python 3.11+ stdlib source-text
  checker scripts and unit tests in scripts/
