## Purpose

Record the decisions about the architecture and the strategy of
docs-traceability-setup. Give the context, the alternatives, and the
consequences.

## Structure

Each decision is a block with the sections `Context`, `Decision`,
`Alternatives`, and `Consequences`. You can read the block alone. The blocks are
in groups by category. The ADRs are newest first (git log order).

## Formatting Rules

- Heading: `## ADR-N (YYYY-MM-DD): Title`, where N is the next sequential
  number.
- Subsections: `### Context`, `### Decision`, `### Alternatives`, `###
  Consequences`.
- The ADRs are newest first (git log order). Put a new ADR at the top of the
  file, below the `<!-- [CAT] Category -->` comment of its category.
- To replace a decision, add a new ADR that supersedes it. Do not change the old
  ADR.

<!-- [CAT] Governance -->

## ADR-11 (2026-11-24): Port and replace pre-existing project scaffolding files

### Context

Target repositories may already contain pre-existing project scaffolding or
state documents (such as vision, architecture, decision logs, conventions,
tasks, roadmap, and third-party notice files) alongside `AGENTS.md`,
`docs/skills/`, and `docs/agents/`. Leaving those flat files beside the layered
Sphinx-Needs traceability layout creates duplicate sources of truth and causes
Sphinx `-W --keep-going` builds to fail on unreferenced Markdown files under
`docs/`.

### Decision

Define a general port-and-replace procedure in `SKILL.md`,
`references/configuration.md`, and `references/migration.md` for repositories
with pre-existing project scaffolding or state documents equivalent to the
impacted traceability files. Port and remove replaced vision, architecture,
decision, convention, task, and roadmap documents into their layered
Sphinx-Needs replacements (`docs/10-product/vision.md`,
`docs/00-overview/context.md`, `docs/30-architecture/`,
`docs/records/CONVENTIONS.md`, `docs/records/TASKS.md`,
`docs/records/ROADMAP.md`, and `docs/records/HISTORY.md`) after user approval.
Update links and procedures in `AGENTS.md`, `README.md`, and project
state-management skills. Keep `docs/skills/`, `docs/agents/`,
`docs/THIRD-PARTY-NOTICES.md`, and immutable documents, and exclude `skills`,
`agents`, and `THIRD-PARTY-NOTICES.md` in `assets/repo/config/sphinx/conf.py`.

### Alternatives

- Keep both the pre-existing flat state documents and the layered Sphinx-Needs
  documents in parallel (violates the single source of truth principle and
  causes drift between tasks, decisions, and conventions)
- Tie the migration rules to one specific scaffolding tool (misses equivalent
  flat scaffolding documents created by other templates or manual workflows)
- Delete `docs/skills/` and `docs/agents/` too (breaks existing agent
  governance, build/format subagents, and project skills)

### Consequences

- Projects with pre-existing scaffolding retain every recorded task, roadmap
  item, decision, convention, vision statement, and architecture note inside a
  single traceable Sphinx-Needs model with no duplicate files.
- Sphinx builds with `-W --keep-going` succeed cleanly even when `docs/skills/`,
  `docs/agents/`, and `docs/THIRD-PARTY-NOTICES.md` remain under `docs/`.

## ADR-10 (2026-11-20): Adopt simplified technical English style and glossary

### Context

Technical documentation, skill manuals, and code comments across
`docs-traceability-setup` need clear, unambiguous English with short sentences,
active voice, and consistent terminology. Software documentation also uses
domain-specific technical nouns and verbs (such as `file`, `need`, `link`,
`commit`, `build`, and `run`) that belong to project technical terminology
rather than general English.

### Decision

Use simplified technical English writing practices across all editable
repository documentation, skill manuals, and comments. Use any currently
installed simplified technical English skills to check editable documentation,
and skip if not installed. Keep project-level glossary files
`technical_terms.txt` and `allowed_phrases.txt` at the repository root with
`TN:` and `TV:` entries. Keep immutable documents (`docs/init-prompt.md`, copied
specs under `docs/skills/*/references/`, `LICENSE.md`, and
`docs/THIRD-PARTY-NOTICES.md`) unchanged.

### Alternatives

- Skip a project glossary and accept high false-positive noise on core software
  terms (makes real style regressions harder to spot)
- Add general English words to `technical_terms.txt` to silence all warnings
  (weakens terminology consistency checks)

### Consequences

- Editable documentation stays concise and unambiguous (short sentences, active
  voice, clear modal verbs) while keeping exact technical identifiers, tables,
  and formatting rules.
- `technical_terms.txt` and `allowed_phrases.txt` serve as the single
  project-wide terminology list when simplified technical English skills are
  installed.

<!-- [CAT] Traceability Model -->

## ADR-9 (2026-11-20): Standardize DataTables style and record ordering

### Context

Sphinx-Needs overview tables provide interactive controls (search, pagination,
column visibility, copy, and CSV export) through its default DataTables style
(`NEEDS_DATATABLES`). Setting `:style: table` disables these controls. In
addition, Sphinx-Needs sorts `needtable` rows ascending by ID by default. This
reverses newest-first records (`records/HISTORY.md` and numbered decision
indexes) and scrambles priority-ordered planning pages (`records/TASKS.md` and
`records/ROADMAP.md`).

### Decision

Use the uniform default DataTables style (omit `:style: table`) with descriptive
table titles on all `needtable` directives in `assets/repo/docs/`. Use
`;`-delimited `as "Label"` column aliases. Add a `doctree-resolved` hook in
`assets/repo/config/sphinx/need_tag_check.py` driven by
`needtable_preserve_order_docs` (source line order on `records/HISTORY`,
`records/TASKS`, and `records/ROADMAP`) and `needtable_reverse_docs`
(newest-first reversal on numbered decision indexes). Document record ordering
rules in `references/model.md` and keep `docs/TASKS.md` ordered newest first.

### Alternatives

- Keep `:style: table` static HTML tables (loses uniform interactive search,
  filtering, column selection, and export controls)
- Reverse rows alphabetically on `HISTORY.md` (breaks newest-first ordering in
  `slug` mode where IDs are not sequential numbers)

### Consequences

- All overview tables in generated documentation share uniform DataTables
  controls and keep their server-rendered row order in Sphinx-Needs 9
  (`needstable.js`).
- `HISTORY.md` renders newest first, and `TASKS.md` and `ROADMAP.md` render in
  exact authored priority order in `slug` and `number` modes.

## ADR-8 (2026-11-20): Align Doxygen headers, AST packing, and column aliases

### Context

Multi-paragraph license notices with indented path lines can exceed 80 columns
if placed inline after `# @copyright `. Strict Doxygen block parsers also expect
aligned `@file`, `@brief`, and `@details` fields. They expect `@copyright` alone
on its line, contiguous 2-digit `[file-header]` keys, and a closing bare comment
line.

Markdown need directives also use `---` YAML frontmatter option blocks for long
wrapped link lists. Python modules put `# need::` tags in AST docstrings beside
non-docstring triple-quoted string literals. Sphinx-Needs 9 requires `as
"Label"` (with `;` delimiters) for aliased `needtable` headers and exports
`parent_need` and `parent_needs`.

### Decision

Adopt the canonical Doxygen header grammar (`@copyright` on its own line,
verbatim `[file-header]` notice lines, contiguous `01..NN` keys, and bare
closing comment line) across `scripts/check_headers.py`, `scripts/*.py`, and
`assets/repo/`.

Upgrade `scripts/check_line_length.py` to use Python `ast` docstring spans and
recognize MyST `---` YAML directive options. Handle `# need::` in docstrings,
pack wrapped list-item lines without merging across items, and exempt verbatim
`[file-header]` lines.

Update `assets/repo/` templates to use `;` with `as "Label"` in `needtable`
`:columns:` and `docname`-scoped filters on record pages. Add Doxygen
`\req{...}` tag support in `tag_scan.py`, and inspect `parent_need` and
`parent_needs` in `check_needs_audit.py`.

### Alternatives

- Keep inline `# @copyright <line>` formatting (causes 70+ character license
  lines to overflow column 80 and removes leading spaces)
- Use regex-only docstring scanning (risks corrupting non-docstring
  triple-quoted string literals and misses opening and closing line packing)

### Consequences

- Multi-paragraph and indented license notices stay strictly within 80 columns
  and round-trip verbatim through `.editorconfig`.
- Long multi-line MyST directive options (`---` ... `---`), module-docstring `#
  need::` tags, and non-docstring Python string literals are handled accurately
  without false positives.
- Rendered Sphinx-Needs 9 HTML tables show clean aliased column headers (`Traced
  by`, `Verified by`, `Refined by`) without duplicate columns.

## ADR-7 (2026-11-20): Reconcile Sphinx-Needs 9 schema and directive naming

### Context

[init-prompt.md](init-prompt.md) is immutable and defines `adr` as the
Architecture Decision directive in sections 0, 1.1, 2.1, 2.2, and 8 (with
directories `00-overview/wdr/`, `10-product/bdr/`, and `30-architecture/adr/`).
Several paragraphs in sections 2.3, 2.7, 4.1, 4.3, and 10 retain older `dec`
references.

Section 4.1 also refers to `bdr` status `active` and `driven_by`. Section 2.4
assigns decisions status `accepted`. Sphinx-Needs 9 computes the back-link of
`drives` as `drives_back` and requires `needs_links` to be a dictionary keyed by
option name.

### Decision

Standardize the target model on `adr` (not `dec`) for Architecture Decisions
across `needs_model.py`, `conf.py`, `check_needs_audit.py`, and templates, and
document `dec -> adr` in `references/migration.md`.

Use `status == 'accepted'` for `bdr_missing_downstream`, `drives_back` for
`sys_missing_upstream_bdr`, and Sphinx-Needs 9 dict format for `needs_links`.
Rename `assets/repo/docs/*/example.md` templates to `<domain>.md` (lowercase)
when scaffolding a target repository.

### Alternatives

- Define `adr` and `dec` directives in parallel (creates ambiguity and breaks
  `model.decision_types: [adr, bdr, wdr]`)
- Use legacy list-based `needs_extra_links` (deprecated and rejected by
  Sphinx-Needs 9 under `-W`)

### Consequences

- Target projects build cleanly with Sphinx 8.2+, Sphinx-Needs 9.3+, and
  MyST-Parser 4.0+ under `-W --keep-going` with no deprecation or schema
  warnings.
- Legacy projects with `dec` migrate deterministically to `adr`.

<!-- [CAT] Tooling -->

## ADR-6 (2026-11-20): Use stdlib config parsers and dual Doxygen headers

### Context

[init-prompt.md](init-prompt.md) requires the skill's source-text checking
scripts under `scripts/` to run with Python 3.11+ with only the standard library
(no third-party packages such as PyYAML or `editorconfig`). At the same time,
each Python script in `scripts/` must satisfy Doxygen file-header validation
(`check_headers.py`) and repository copyright header checks (`Copyright` in the
first 5 lines).

### Decision

Implement strict, standard-library-only parsers in `scripts/project_config.py`
and `scripts/editorconfig.py` that fail with exit code 2 on unknown keys or
invalid values instead of falling back to defaults. Format Doxygen headers so
`@copyright` appears in lines 4–5, passing `check_headers.py` and `verify.sh`
together.

### Alternatives

- Require third-party packages such as PyYAML or `editorconfig` (violates the
  stdlib-only requirement for skill scripts)
- Put `@copyright` after multi-line `@details` blocks (pushes `Copyright` past
  line 5 and fails repository copyright checks)

### Consequences

- `scripts/check_text.py`, `scripts/check_headers.py`,
  `scripts/check_line_length.py`, and `scripts/tests/` run cleanly with plain
  `python3` without a virtual environment.
- Each script in `scripts/` satisfies `check_headers.py` and `agent-scaffolding`
  verification.

## ADR-5 (2026-11-20): Configure Ruff for 80 columns and Python 3.11 target

### Context

`ruff` (version `0.17.6` pinned in `requirements-dev.txt`) defaults to an
88-character line length and inspects all Python files in the workspace.
[init-prompt.md](init-prompt.md) requires an 80-column maximum line length and
Python 3.11+ compatibility for skill scripts. It also stores template files with
`{{PLACEHOLDER}}` tokens in `assets/repo/`.

### Decision

Configure `ruff.toml` with four explicit settings beyond the default preset:
`target-version = "py311"`, `line-length = 80`, `[lint] select = ["E", "F", "W",
"I"]`, and `extend-exclude = ["assets/repo"]`. Verify the configuration against
`ruff 0.17.6` in `.venv`.

### Alternatives

- Keep Ruff's default 88-column line length (conflicts with the 80-column rule
  in [init-prompt.md](init-prompt.md))
- Omit `extend-exclude = ["assets/repo"]` (fails linting and formatting on
  target template files with placeholder tokens)

### Consequences

- `ruff check` and `ruff format` enforce 80-column formatting and Python 3.11
  syntax compatibility on `scripts/`.
- Template sources in `assets/repo/` stay excluded from direct `ruff` runs until
  rendered into target repositories.

<!-- [CAT] Development Environment -->

## ADR-4 (2026-11-20): Use native Python venv with unittest and ruff

### Context

The repository develops Python 3.11+ standard-library-only scripts (`scripts/`)
beside Sphinx, MyST, Sphinx-Needs, and CMake target templates (`assets/repo/`).
Contributors and agents need a reproducible, isolated environment for unit
tests, linting, formatting, and target-build acceptance tests without changing
the system Python installation.

### Decision

Use a native Python virtual environment (`.venv`) pinned with `.python-version`
and `requirements-dev.txt`. Use Python's built-in `unittest` for unit test
discovery (`python -m unittest discover`) and `ruff` for linting and formatting.
Keep runtime skill scripts strictly dependent on the Python 3.11+ standard
library only.

### Alternatives

- Containerized development environment with Podman or Docker Compose (heavier
  startup overhead for Python and Markdown work, though still compatible with
  CMake and Sphinx host tools)
- Host Python with no virtual environment (risks version drift and lacks
  isolation for `ruff` and acceptance-test dependencies)
- `pytest` + `black` + `flake8` (adds extra dependencies beyond `unittest` and
  single-binary `ruff`)

### Consequences

- Development tools (`ruff`) are pinned in `requirements-dev.txt` and installed
  into `.venv/`.
- Skill runtime scripts in `scripts/` remain runnable with plain `python3`
  (3.11+) without `.venv`.
- `scripts/build-agent.sh` and `scripts/formatter-agent.sh` activate `.venv` to
  run `unittest` and `ruff`.

<!-- [CAT] Governance -->

## ADR-3 (2026-11-20): Select optional scaffolding modules

### Context

The `agent-scaffolding` skill offers six optional modules: `dev_environment`,
`build_agents`, `tool_configs`, `boilerplate`, `copyright`, and
`agent_platforms`. Enable a module only when it matches the repository's
structure and workflow.

### Decision

Enable `dev_environment`, `build_agents`, `tool_configs`, and `copyright`.
Disable `boilerplate` because [init-prompt.md](init-prompt.md) defines the exact
skill directory layout and files. Leave `agent_platforms` empty so only the
standard core `.agents/skills` symlink is created.

### Alternatives

- Enable `boilerplate` (creates a generic library and executable skeleton that
  conflicts with the Agent Skill root layout)
- Enable platform-specific symlinks (`claude`, `copilot`, `pi`, `opencode`) now
  (not necessary until requested, and can be enabled later in apply mode)

### Consequences

- Build, test, lint, and format checks are encapsulated in
  `scripts/build-agent.sh`, `scripts/formatter-agent.sh`, and `docs/agents/`.
- Minimal `ruff` configuration is tracked and verified against the installed
  `ruff` version.
- All source, script, and comment-supporting config files outside
  `exclude_paths` carry the MIT copyright header.

## ADR-2 (2026-11-20): Classify repository as a mixed Agent Skill project

### Context

The repository root is the installable `docs-traceability-setup` Agent Skill
(`SKILL.md`, `references/`, `scripts/`, `assets/`). It combines Markdown skill
documentation and target templates with Python 3.11+ source-text scripts and
unit tests. Target templates in `assets/repo/` will contain intentional
`{{PLACEHOLDER}}` tokens that must not fail repository scaffolding checks.

### Decision

Classify the project type as `mixed` with languages `python` and `markdown` for
`Python 3.11+` on `linux`. Keep `docs/init-prompt.md` as an immutable
pre-existing specification document. Configure `exclude_paths: [assets/repo]` in
`.agent-scaffolding.yml` so scaffolding checks ignore intentional target
template placeholders.

### Alternatives

- Classify as `documentation` only (omits Python tooling, testing, linting, and
  development environment support)
- Classify as `software` only (understates the Markdown skill, references, and
  template assets)

### Consequences

- Repository development governance skills live in `docs/skills/` (linked at
  `.agents/skills`), clearly separated from the deliverable
  `docs-traceability-setup` skill at the repository root.
- `verify.sh` inspects all repository scaffolding and Python files while
  skipping intentional placeholders in `assets/repo/`.

## ADR-1 (2026-11-20): Adopt agent-scaffolding

### Context

The project must have governance, documentation, and agent instructions that
work with all AI agents.

### Decision

Apply the agent-scaffolding agent skill 0.2.0 with the configuration in
`.agent-scaffolding.yml`. The commit mode is AUTONOMOUS.

### Alternatives

- Documents and agent instructions written ad hoc for each project
- Instructions for one platform only (for example only `CLAUDE.md` or only
  `.github/copilot-instructions.md`)

### Consequences

- `AGENTS.md` is the supreme authority for agent behavior.
- Procedures are only in `docs/skills/`.
- The state documents (`TASKS.md`, `CHANGELOG.md`, and `DECISIONS.md`) are up to
  date before each commit.
