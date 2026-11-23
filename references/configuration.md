# Configuration and Interview Procedure

All skill configuration for a target repository lives in a single file at the
repository root: `.docs-traceability-setup.yml`. Target build scripts
(`config/sphinx/needs_model.py`, `conf.py`) and skill checkers
(`scripts/project_config.py`, `scripts/check_text.py`) read this file directly.

Editor formatting settings (`charset`, `end_of_line`, `indent_style`,
`indent_size`, `max_line_length`) and Doxygen `[file-header]` notice lines live
in `.editorconfig` at the repository root.

## Schema (`.docs-traceability-setup.yml`)

```yaml
project:
  name: "example"               # Project name (CMake and Sphinx)
  repo_url: ""                  # Optional URL for need-code-trace links
  domains:                      # Initial uppercase domain names ([A-Z0-9]+)
    - POWER

id:
  style: slug                   # "slug" or "number"
  digits: 4                     # Required for "number" (e.g. 4 = NNNN)

authoring:
  primary_markup: myst          # "myst" or "rst"
  modal_verb: shall             # Single modal verb for requirements

model:
  decision_types:               # Enabled decision types (adr, bdr, wdr)
    - adr
    - bdr
    - wdr
  ver_method_tags:              # Allowed method tags for ver items
    - unit
    - integration
    - network
    - analysis
  test_file_patterns:           # Globs for test files (VER_ tag rules)
    - "test_*"
    - "*_test.*"
    - "check_*"
  code_tag_exclude: []          # Extra generated/third-party paths to ignore

build:
  cmake_mode: subdirectory      # "subdirectory" or "standalone"
  python_manifest: requirements.txt  # Target Python dependency manifest
  docs_auto_install: false      # Default for DOCS_AUTO_INSTALL
  graphviz: auto                # "auto", "on", or "off"

checks:
  file_headers: true            # Enable Doxygen header check
  prose_packing: true           # Enable greedy prose packing check
```

### Validation Rules

- All sections and keys are strictly validated. Unknown keys or invalid values
  stop all tools and scripts with an error (exit code `2`) instead of falling
  back to defaults.
- Each domain in `project.domains` must match `^[A-Z0-9]+$` (uppercase letters
  and digits only, no underscores).
- When `id.style` is `slug`, `id.digits` is optional and ignored by ID regex
  generation. When `id.style` is `number`, `id.digits` must be a positive
  integer (for example `3` for `NNN`, `4` for `NNNN`, `5` for `NNNNN`).
- `model.decision_types` can contain any subset of `adr`, `bdr`, and `wdr`.

## Interview Procedure

1. Read `<repo>/.docs-traceability-setup.yml` if present. If all required keys
   are valid and present, do **not** interview the user again. Reuse the
   recorded values idempotently.
2. For any missing or incomplete key not already supplied by the user, gather
   detected defaults from the repository (existing project scaffolding or
   metadata configs, git remote URL, existing `CMakeLists.txt`, `LICENSE*`,
   `.editorconfig`, existing Python manifest, existing test layout, and existing
   ID style or modal verb).
3. Present the detected values to the user and ask them to accept or change:
   - `id.style` (`slug` or `number`) and `id.digits` when `number`.
   - `project.name`, `project.repo_url`, and `project.domains`.
   - `authoring.primary_markup` and `authoring.modal_verb`.
   - `model.decision_types`, `model.ver_method_tags`,
     `model.test_file_patterns`, and `model.code_tag_exclude`.
   - `build.cmake_mode`, `build.python_manifest`, `build.docs_auto_install`, and
     `build.graphviz`.
   - `checks.file_headers` (and the `[file-header]` notice lines for
     `.editorconfig` when `true`) and `checks.prose_packing`.
4. Do not silently assume defaults for unanswered items unless the user
   explicitly tells you to accept the defaults.
5. Write `.docs-traceability-setup.yml` and update or make `.editorconfig`
   before scaffolding or migrating files.

## Rendering Templates from `assets/repo/`

When copying `assets/repo/` into `<repo>`:

- Merge rather than overwrite current files (`.editorconfig`, `.gitignore`,
  `build.python_manifest`, root `CMakeLists.txt`). When the target repository
  already has pre-existing project scaffolding or state documents equivalent to
  the impacted traceability files, port and replace them instead of keeping
  duplicates (see [migration.md](migration.md)).
- Replace `{{PLACEHOLDER}}` tokens from `.docs-traceability-setup.yml` and
  `.editorconfig` (`{{DOCS_AUTO_INSTALL_CMAKE}}` is `ON` when
  `build.docs_auto_install` is `true`, else `OFF`).
- Rename layer domain template files (`20-system/example.md`,
  `30-architecture/example.md`, `40-interfaces/example.md`,
  `50-components/example.md`, `60-verification/example.md`) to
  `<domain_lower>.md` for the primary domain in `project.domains` (for example
  `power.md` for `POWER`).
- Omit disabled decision directories/files when a decision type is excluded from
  `model.decision_types`.
- Substitute example IDs and decision filenames according to `id.style`:

|Placeholder|`slug` Mode (`POWER`)|`number` (`digits: 4`)|
|---|---|---|
|`{{BDR_MAGIC_LINKS_ID}}`|`BDR_MAGIC_LINKS`|`BDR_0001`|
|`{{ADR_SPHINX_NEEDS_ID}}`|`ADR_SPHINX_NEEDS`|`ADR_0001`|
|`{{WDR_CI_GATES_ID}}`|`WDR_CI_GATES`|`WDR_0001`|
|`{{SYS_POWER_SUPPLY_ID}}`|`SYS_POWER_SUPPLY`|`SYS_POWER_0001`|
|`{{SWR_POWER_MONITOR_ID}}`|`SWR_POWER_MONITOR`|`SWR_POWER_0001`|
|`{{SWR_POWER_LOW_ID}}`|`SWR_POWER_MONITOR_LOW_VOLTAGE`|`SWR_POWER_0002`|
|`{{SWR_POWER_HIGH_ID}}`|`SWR_POWER_MONITOR_HIGH_VOLTAGE`|`SWR_POWER_0003`|
|`{{ARC_POWER_MONITOR_ID}}`|`ARC_POWER_MONITOR`|`ARC_POWER_0001`|
|`{{ICD_POWER_STATUS_ID}}`|`ICD_POWER_STATUS`|`ICD_POWER_0001`|
|`{{COMP_POWER_MONITOR_ID}}`|`COMP_POWER_MONITOR`|`COMP_POWER_0001`|
|`{{VER_POWER_SUPPLY_ID}}`|`VER_POWER_SUPPLY`|`VER_POWER_0001`|
|`{{VER_POWER_MONITOR_ID}}`|`VER_POWER_MONITOR`|`VER_POWER_0002`|
|`{{VER_POWER_LOW_ID}}`|`VER_POWER_MONITOR_LOW_VOLTAGE`|`VER_POWER_0003`|
|`{{VER_POWER_HIGH_ID}}`|`VER_POWER_MONITOR_HIGH_VOLTAGE`|`VER_POWER_0004`|
|`{{CNV_CODE_TAGS_ID}}`|`CNV_CODE_TAGS`|`CNV_0001`|
|`{{CNV_SOURCE_TEXT_ID}}`|`CNV_SOURCE_TEXT`|`CNV_0002`|
|`{{CNV_FILE_HEADER_ID}}`|`CNV_FILE_HEADER`|`CNV_0003`|
|`{{TSK_POWER_MONITOR_ID}}`|`TSK_POWER_MONITOR`|`TSK_0001`|

In `number` mode, also rename the decision template files (`BDR_MAGIC_LINKS.md`
-> `BDR_0001.md`, `ADR_SPHINX_NEEDS.md` -> `ADR_0001.md`, `WDR_CI_GATES.md` ->
`WDR_0001.md`).

For custom `project.domains`, replace `POWER` with the primary domain name and
adjust `id.digits` width accordingly (for example `001` for `digits: 3`).
