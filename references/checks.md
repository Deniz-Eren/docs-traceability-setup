# Checks and Remediation Guide

Traceability checks run in the target project build (CMake + Sphinx + CTest).
Source-text checks run only from this skill's `scripts/` directory. Do not copy
them into the target repository.

## 1. Sphinx-Needs Build Warnings (`config/sphinx/conf.py`)

Sphinx builds run with `-W --keep-going` and `needs_warnings_always_warn = True`
with Sphinx-Needs 9 configuration options only (`needs_types`, `needs_id_regex`,
`needs_id_required`, `needs_links` dict, `needs_fields` schema enum,
`needs_role_need_template = "{{ id }}"`).

- **`unverified`**: Active `sys`/`swr` without `verifies_back` (and not tagged
  `informational`). Remediation: add a `ver` item verifying it, or add `:tags:
  informational` with rationale.
- **`uncovered_swr`**: Active `swr` without `derives`. Remediation: link
  `:derives:` to its parent `sys` or `swr` requirement.
- **`requirement_satisfies`**: Active `sys`/`swr` with `:satisfies:`.
  Remediation: replace `:satisfies:` with `:derives:`.
- **`floating`**: Active `arc`/`icd`/`comp` without `:satisfies:` or
  `:refines:`. Remediation: link `:satisfies:` to a requirement and/or
  `:refines:` to a higher design item.
- **`orphan_ver`**: Active `ver` without `:verifies:`. Remediation: add
  `:verifies:` targeting a `sys` or `swr` item.
- **`ver_method_tag`**: Active `ver` with 0 or 2+ tags from
  `model.ver_method_tags`. Remediation: keep exactly one configured method tag
  on the `ver` item.
- **`missing_status`**: Need without `:status:`. Remediation: add a valid status
  from its category.
- **`model_references_planning`**: Normative, decision, or convention item
  tracing `TSK_` or `RDM_`. Remediation: remove the forward trace and put
  `:traces:` on the `task` or `roadmap` instead.
- **`superseded_without_successor`**: Decision with `status: superseded` and no
  `supersedes_back`. Remediation: add `:supersedes:` on the replacement
  decision.
- **`bdr_missing_downstream`**: Accepted `bdr` without `:drives:` or
  `:governs:`. Remediation: connect affected `sys` or `swr` items with
  `:drives:` or `arc` and `adr` items with `:governs:`.
- **`sys_missing_upstream_bdr`**: Active `sys` without `drives_back`.
  Remediation: add the `sys` ID to `:drives:` on its originating `bdr`.

Schema validation also fails automatically on invalid IDs (violating
`needs_id_regex`) or unknown status values.

## 2. In-Code Tag Checks (`config/sphinx/need_tag_check.py`)

`tag_scan.py` scans tracked files (`git ls-files`, fallback directory walk) for
`need::` immediately following a language comment marker. On `build-finished`,
`need_tag_check.py` inspects `SphinxNeedsData(app.env).get_needs_view()` and
emits warnings (fatal under `-W`) for:

- A `need::` tag with no IDs -> add one or more valid IDs or remove the tag.
- An unknown ID -> fix the typo or define the item in docs.
- A disallowed prefix in code (`SYS_`, `SWR_`, `ADR_`, `BDR_`, `WDR_`, `CNV_`,
  `TSK_`, `RDM_`) -> replace with the implementing `ARC_`, `ICD_`, or `COMP_`
  ID.
- A `VER_` ID in a non-test file -> move the tag to a matching test file.
- A test file without any `VER_` ID -> add `# need:: VER_<DOMAIN>_<SUFFIX>`.

## 3. Standalone Model Audit (`tools/traceability/check_needs_audit.py`)

Executed by CTest (`docs.audit`, depending on `docs.needs`) against
`<build>/docs/needs/needs.json`. Verifies:

- Symmetry between forward links and `<link>_back` for every link type.
- No dangling link targets and strict compliance with the permitted link matrix.
- Coverage, method tags, planning link direction, and superseded successors.
- Existing `parent_need` for every nested child item.
- Single domain per layer document matching its lowercase filename.
- Decision filename matching its `ADR_`, `BDR_`, or `WDR_` ID.

## 4. Skill Source-Text Checks (`scripts/check_text.py`)

Run from `$SKILL` with the Python 3.11+ standard library only (no venv
required):

```bash
python3 "$SKILL/scripts/check_text.py" --root <repo> [--fix] [paths...]
```

Individual checkers (`scripts/check_headers.py`, `scripts/check_line_length.py`)
support the exact same CLI contract:

- **Exit codes:** `0` (clean), `1` (one or more findings), `2` (invalid config
  or CLI error).
- **Output format:** `<file>:<line>: <message>` (one finding per line).
- **Configuration:** reads `.docs-traceability-setup.yml` and `.editorconfig`
  from `<repo>`. If `.editorconfig` is missing, it uses
  `scripts/defaults.editorconfig` with a notice. If
  `.docs-traceability-setup.yml` is missing in check mode, it uses defaults with
  a notice. Any invalid value in either file stops with exit code `2`.

### File Headers (`check_headers.py`)

- Applies to human-authored Python, CMake, shell (`##` + `#`), and C/C++ (`/**
  ... */`) files after any optional shebang, followed by a blank line.
- Canonical block layout:
  - `@file <filename>` (aligned to column 13) matching the filename.
  - `@brief <summary>` on one line without a trailing period (and not `TODO`).
  - Optional `@details <text>` region separated by bare comment lines (`#` or `
    *`).
  - A bare comment line before `@copyright`, `@copyright` alone on its line,
    every `[file-header]` notice line verbatim (`# <line>` or bare `#` for empty
    lines, preserving leading spaces), and a closing bare comment line (`#` or `
    *` before ` */`).
- `[file-header]` keys in `.editorconfig` must form a contiguous 2-digit run
  starting at `01` (`01`, `02`, ...).
- Skipped when `checks.file_headers` is `false` or `[file-header]` is absent
  (with a notice).
- `--fix` inserts missing blocks (with `@brief TODO`) and repairs wrong
  `@file`/`@copyright` blocks while preserving existing `@brief` and `@details`.
  Replace `@brief TODO` with a real summary before finishing.

### Line Length and Greedy Prose Packing (`check_line_length.py`)

- Enforces `len(line) <= max_line_length` (Unicode code points, tab equals 1
  character).
- When `checks.prose_packing` is `true`, each non-final line of a prose
  paragraph must hold the maximum number of words that fit. This applies to
  Markdown and RST paragraphs, need directive bodies, source comments, and
  Python docstrings resolved with AST.
- Keeps these structures untouched: paragraph breaks, list boundaries (wrapped
  lines in one list item still pack), headings, underlines, indented blocks, and
  code fences. It also keeps MyST `---` YAML directive options, RST literal
  blocks (`::`), tables, directive fields, and non-prose directives (`toctree`,
  `needtable`, `need-code-trace`, `include`). Markdown link definitions, Doxygen
  commands, `need::` tags, and verbatim `[file-header]` notice lines stay
  untouched too.
- `--fix` greedily re-wraps prose paragraphs in place and reports remaining
  unbreakable lines (for example long URLs or code lines).
