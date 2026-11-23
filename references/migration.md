# Migrating an Existing Project

Follow this procedure when a target repository already contains documentation,
pre-existing project scaffolding documents equivalent to the impacted
traceability files, or an existing Sphinx-Needs traceability model. Preserve
every valid engineering item, rationale, custom extension, and domain boundary
while upgrading to this model.

## Porting Pre-Existing Project Scaffolding Files

When a repository already contains pre-existing project scaffolding or state
documents equivalent to the impacted traceability files (for example flat
vision, architecture, decision, convention, task, or roadmap Markdown files
under `docs/` or at the repository root), **port and replace** those files with
this skill's layered traceability files instead of leaving both sets in place.

Present the port-and-replace plan (files to port and remove, plus the new
decision, convention, task, and roadmap IDs) to the user for approval before
removing the old files.

### File Replacement Mapping

| Pre-existing equivalent | Traceability replacement |
| --- | --- |
| Vision | `docs/10-product/vision.md` |
| Architecture | `docs/00-overview/context.md`, `docs/30-architecture/` |
| Decisions | `docs/30-architecture/adr/` (`bdr/`, `wdr/`) |
| Conventions | `docs/records/CONVENTIONS.md` |
| Tasks | `docs/records/TASKS.md`, `docs/records/HISTORY.md` |
| Roadmap | `docs/records/ROADMAP.md`, `docs/records/HISTORY.md` |

Port each file's full content and then remove the replaced pre-existing file:

- **Vision -> `docs/10-product/vision.md`:** Port mission, principles, goals,
  and target result prose into `docs/10-product/vision.md`, then remove the old
  vision document.
- **Architecture -> `docs/00-overview/context.md` and `docs/30-architecture/`:**
  Port system overview, updated directory structure, and integration points into
  `docs/00-overview/context.md`. Port component descriptions into
  `docs/30-architecture/index.md` and `arc` items in
  `docs/30-architecture/<domain>.md`, then remove the old architecture document.
- **Decisions -> per-decision files:** Split each recorded decision entry (such
  as `## ADR-N (YYYY-MM-DD): Title` blocks or standalone unmodeled ADR files)
  into its own file named after its new ID
  (`docs/30-architecture/adr/ADR_<SUFFIX>.md`, or `docs/10-product/bdr/` /
  `docs/00-overview/wdr/` for business or workflow decisions when enabled in
  `model.decision_types`). Preserve `Context`, `Decision`, `Rejected
  alternatives` (or `Alternatives`), and `Consequences`. Set active decisions to
  `:status: accepted` and superseded ones to `:status: superseded` with
  `:supersedes:` on the successor, then remove the old monolithic decision log.
- **Conventions -> `docs/records/CONVENTIONS.md`:** Port every existing
  convention (file names, formatting, updated document purposes, copyright
  headers, project rules) into `{con}` directives (`CNV_<SUFFIX>`) merged with
  the traceability conventions and tracing their originating decisions, then
  remove the old conventions document.
- **Tasks and Roadmap -> `docs/records/TASKS.md`, `docs/records/ROADMAP.md`, and
  `docs/records/HISTORY.md`:** Port open or active tasks and roadmap items into
  `{task}` (`TSK_<SUFFIX>`) and `{roadmap}` (`RDM_<SUFFIX>`) directives with
  `:status: open` or `in_progress` in priority order. Port completed or
  cancelled entries into `docs/records/HISTORY.md` with `:status: done` or
  `cancelled` (newest first), then remove the old task and roadmap files.

### Preserved Files and Updated Cross-References

- **Keep non-model scaffolding files:** Keep `AGENTS.md`, root `CHANGELOG.md`,
  project scaffolding config files, `.agents/skills`, `docs/skills/`,
  `docs/agents/`, `docs/THIRD-PARTY-NOTICES.md`, helper build/format scripts,
  and any immutable pre-existing specification documents.
- **Exclude non-Sphinx files from the Sphinx build:** Ensure `exclude_patterns`
  in `config/sphinx/conf.py` includes `skills`, `agents`,
  `THIRD-PARTY-NOTICES.md`, and any immutable or imported documents placed
  directly under `docs/` so Sphinx builds cleanly under `-W --keep-going`.
- **Preserve copyright and line-length exemptions:** Copy existing copyright and
  license notices into `[file-header]` in `.editorconfig`. Add `max_line_length
  = off` sections in `.editorconfig` for `LICENSE.md`,
  `docs/THIRD-PARTY-NOTICES.md`, copied third-party specification references
  (such as `docs/skills/*/references/**`), and any immutable documents.
- **Update governance, README, and skill links in place:**
  - `AGENTS.md`: Update checklists and links so references to the replaced
    vision, architecture, decision, convention, task, and roadmap documents
    point to their ported paths (`docs/10-product/vision.md`,
    `docs/00-overview/context.md`, `docs/30-architecture/`,
    `docs/records/CONVENTIONS.md`, `docs/records/TASKS.md`,
    `docs/records/ROADMAP.md`, and `docs/records/HISTORY.md`).
  - Project state-management skills (for example
    `docs/skills/state-management/SKILL.md`): Update procedures to maintain the
    Sphinx-Needs record files (`docs/records/TASKS.md`,
    `docs/records/HISTORY.md`, `docs/records/ROADMAP.md`,
    `docs/records/CONVENTIONS.md`), per-decision files (`adr/`, `bdr/`, `wdr/`),
    `docs/THIRD-PARTY-NOTICES.md`, and root `CHANGELOG.md`.
  - `README.md`, `CHANGELOG.md`, `docs/skills/**`, and `docs/agents/**`: Replace
    all stale relative links to the removed pre-existing documents with their
    ported destinations and verify with `git grep` that no broken links remain.
- **Record the transition:** Record an accepted ADR (for example
  `ADR_DOCS_TRACEABILITY_MODEL` or the next sequential `ADR_<NNNN>`) documenting
  that the pre-existing project scaffolding documents were ported into and
  replaced by the Sphinx-Needs traceability layout.

## Step 1: Inventory the Existing Repository

Document all existing artifacts before editing any file:

- Item types, ID syntax (prefixes, separators, slug or numeric widths), link
  types, tags, and statuses.
- Records: ADRs, BDRs, WDRs (monolithic or per-decision files), conventions,
  tasks, roadmap, and history.
- In-code tag syntax, existing scanners/checkers, and excluded trees.
- Project-specific Sphinx extensions, code/CLI doc generators, CMake targets,
  and CTest entries.
- Installed `sphinx`, `sphinx-needs`, and `myst-parser` versions.

Complete the `.docs-traceability-setup.yml` interview
([configuration.md](configuration.md)) preserving the project's established
modal verb and domains unless the user asks to change them.

## Step 2: Map Types and Links

- **General requirement -> `sys` or `swr`**: Classify black-box system or
  software level. Ask the user if ambiguous.
- **Architecture -> `arc`**: Structural decomposition.
- **Design / specification -> `comp` or `icd`**: Use `icd` for interface
  contracts.
- **Test / verification -> `ver`**: Assign exactly one tag from
  `model.ver_method_tags`.
- **Architecture decision (`dec`) -> `adr`**: Canonical directive is `adr`
  (`ADR_<SUFFIX>`).
- **Business decision -> `bdr`**: Drives requirements or governs architecture.
- **Workflow / process decision -> `wdr`**: Governs architecture constraints or
  workflows.
- **Convention -> `con`**: `CNV_<SUFFIX>`.
- **Task / Roadmap -> `task` / `roadmap`**: Keep planning items in
  `docs/records/`.
- **Requirement -> requirement `satisfies` -> `derives`**: Requirements derive
  from requirements.
- **`ver` -> design element `verifies` -> `verifies` -> requirement**: Retarget
  to the `sys` or `swr` satisfied by that element. Ask the user if unclear.

## Step 3: Map IDs and Domains

Keep existing uppercase `[A-Z0-9]+` domain segments and convert every suffix
according to `id.style` and `id.digits` in `.docs-traceability-setup.yml`:

- **`id.style: slug`:** Replace numeric suffixes with descriptive slugs derived
  from item titles (append a disambiguating word on collisions):
  - `REQ-FETCH-0001` ("Retry after a timeout") -> `SWR_FETCH_RETRY_TIMEOUT`
  - `DES-DOC-0003` ("Page renderer") -> `COMP_DOC_PAGE_RENDERER`
  - `ADR-0049` ("SQLite for the cache") -> `ADR_SQLITE_CACHE`
  - `CNV-0002` ("Commit messages") -> `CNV_COMMIT_MESSAGES`
- **`id.style: number` (`id.digits: 4`):** Zero-pad suffixes to `id.digits`,
  retaining original numbers when unique and assigning the next free number on
  collision:
  - `REQ-FETCH-0001` -> `SWR_FETCH_0001`
  - `DES-DOC-0003` -> `COMP_DOC_0003`
  - `ADR-0049` -> `ADR_0049`
  - `CNV-0002` -> `CNV_0002`

Show the complete old-to-new ID table to the user for approval **before**
modifying files, then record it as a Markdown table (not Sphinx-Needs items) in
`docs/records/id-map.md`.

## Step 4: Rewrite IDs Across the Repository

- Apply the approved ID map with a deterministic script (longest-match first,
  word-boundary guarded). Update directive `:id:` fields, link options, `{need}`
  roles, prose mentions, and in-code `need::` tags.
- Review the diff and verify zero legacy IDs remain with:
  ```bash
  git grep -nE '<previous-id-regex>'
  ```

## Step 5: Restructure Documents with `git mv`

- Move domain specifications into `docs/20-system/`, `docs/30-architecture/`,
  `docs/40-interfaces/`, `docs/50-components/`, and `docs/60-verification/` with
  `git mv`, enforcing one lowercase `<domain>.md` per domain per layer.
- Split monolithic decision logs into individual files named after their new IDs
  (`docs/30-architecture/adr/ADR_<SUFFIX>.md`,
  `docs/10-product/bdr/BDR_<SUFFIX>.md`,
  `docs/00-overview/wdr/WDR_<SUFFIX>.md`), preserving full text and setting
  active decisions to `:status: accepted`. Historical deleted decisions remain
  in Git history.
- Move conventions, tasks, roadmap, and history into `docs/records/`.

## Step 6: Upgrade Sphinx Configuration to Sphinx-Needs 9

- Move Sphinx config to `config/sphinx/` backed by `needs_model.py` reading
  `.docs-traceability-setup.yml`.
- Migrate deprecated Sphinx-Needs options:
  - `needs_extra_links` (list) -> `needs_links` (dict keyed by link name)
  - `needs_extra_options` -> `needs_fields`
  - `needs_statuses` -> `needs_fields["status"]["schema"]["enum"]`
  - `{id}` role templates -> Jinja `{{ id }}`

## Step 7: Preserve Project-Specific Tooling and Migrate Checkers

- Keep project-specific Sphinx extensions, API and CLI doc generators, CMake
  targets, and custom tests. Update their paths and ID regexes to read
  `needs_model.py`, and keep them connected to the build.
- Replace project tag scanners or needs auditors with `tag_scan.py`,
  `need_tag_check.py`, and `check_needs_audit.py`. Do this **only** after you
  confirm that they cover all checks of the current scripts.
- If the repository has existing line-length, prose-packing, or header checkers:
  1. Migrate its `max_line_length`, exempted globs (`max_line_length = off`),
     and any project-specific license header section (such as
     `[<project>-license]`) into `[file-header]` in `.editorconfig` (contiguous
     2-digit keys `01`, `02`, ... preserving leading indentation).
  2. Verify `scripts/check_text.py` catches every defect flagged by the legacy
     checkers.
  3. Obtain explicit user approval before removing legacy checkers or build
     targets.

## Step 8: Verify Migration Completeness

1. Run `scripts/check_text.py` on all modified/migrated files (zero findings).
2. Run `cmake -B build && cmake --build build && ctest --test-dir build` (zero
   warnings, zero errors).
3. Confirm exported `needs.json` item count equals the pre-migration count plus
   any newly split decision records.
4. Confirm `git grep -nE '<previous-id-regex>'` returns zero matches outside
   `docs/records/id-map.md`.
