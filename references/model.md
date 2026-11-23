# Traceability Model Reference

`config/sphinx/needs_model.py` is the single pure-Python definition of the model
in a target repository. It reads `.docs-traceability-setup.yml` with only the
Python standard library. It supplies types, ID patterns, links, link rules,
statuses, tags, comment markers, and test file patterns to `conf.py`,
`tag_scan.py`, `need_tag_check.py`, and `check_needs_audit.py`.

## Directory Layout (by Engineering Abstraction Level)

| Directory | Content | Types |
| --- | --- | --- |
| `docs/00-overview/` | System context, glossary | — |
| `docs/00-overview/wdr/` | One workflow decision per file | `wdr` |
| `docs/10-product/` | Product vision | — |
| `docs/10-product/bdr/` | One business decision per file | `bdr` |
| `docs/20-system/` | Black-box system/software reqs | `sys`, `swr` |
| `docs/30-architecture/` | Structural decomposition | `arc` |
| `docs/30-architecture/adr/` | One architecture decision per file | `adr` |
| `docs/40-interfaces/` | Interface Control Documents | `icd` |
| `docs/50-components/` | White-box behavior, state machines | `comp` |
| `docs/60-verification/` | Verification items, reports | `ver` |
| `docs/records/` | Conventions, planning records | `con`, `task`, `roadmap` |

- **One document per domain per layer:** `docs/20-system/<domain>.md` contains
  only items of `<DOMAIN>` (lowercase filename). The audit enforces this rule.
- **One decision per file:** Decision filenames match their item ID
  (`ADR_<SUFFIX>.md`, `BDR_<SUFFIX>.md`, `WDR_<SUFFIX>.md`).
- **Contributor guide:** `docs/README.md` documents local authoring and build
  instructions and is listed in Sphinx `exclude_patterns`.

## Types and Permanent IDs

| Directive | Title | ID Pattern | Color |
| --- | --- | --- | --- |
| `sys` | System Requirement | `SYS_<DOMAIN>_<SUFFIX>` | `#bfd8d2` |
| `swr` | Software Requirement | `SWR_<DOMAIN>_<SUFFIX>` | `#dfecd7` |
| `arc` | Architecture Element | `ARC_<DOMAIN>_<SUFFIX>` | `#d7d2ec` |
| `icd` | Interface | `ICD_<DOMAIN>_<SUFFIX>` | `#f2cfa5` |
| `comp` | Component Spec | `COMP_<DOMAIN>_<SUFFIX>` | `#e8e4c9` |
| `ver` | Verification Item | `VER_<DOMAIN>_<SUFFIX>` | `#a3d2ca` |
| `adr` | Architecture Decision (ADR) | `ADR_<SUFFIX>` | `#ffb6b9` |
| `bdr` | Business Decision Record (BDR) | `BDR_<SUFFIX>` | `#ffd166` |
| `wdr` | Workflow Decision Record | `WDR_<SUFFIX>` | `#118ab2` |
| `con` | Convention | `CNV_<SUFFIX>` | `#a9cce3` |
| `task` | Task | `TSK_<SUFFIX>` | `#f5cba7` |
| `roadmap` | Roadmap Item | `RDM_<SUFFIX>` | `#d5d8dc` |

### `<DOMAIN>` and `<SUFFIX>` Rules

- `<DOMAIN>` matches `[A-Z0-9]+` with no underscores.
- **`id.style: slug`:** `<SUFFIX>` consists of uppercase `[A-Z0-9]+` words
  separated by `_`, starting with a letter (`[A-Z]`). Derive 1–4 meaningful
  words from the title without repeating the prefix or domain, and do not embed
  sequence numbers. Child items can start with their parent's slug (for example
  `SWR_POWER_MONITOR_LOW_VOLTAGE` under `SWR_POWER_MONITOR`).
- **`id.style: number` (`id.digits: D`):** `<SUFFIX>` is a fixed-width
  zero-padded decimal integer `[0-9]{D}` (for example `SWR_POWER_0001`,
  `ADR_0001`). Assign the next unused number for each type and domain (or for
  each type for decisions and records). Give each child item a new `D`-digit
  number. Do not reuse obsolete numbers.
- `needs_id_required = True` and all IDs are globally unique.
- Anchored `needs_id_regex` (two branches joined by `|`, restricted to enabled
  decision prefixes in `model.decision_types`):
  - `slug` domain branch:
    `^(SYS|SWR|ARC|ICD|COMP|VER)_[A-Z0-9]+_[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$`
  - `slug` flat branch:
    `^(ADR|BDR|WDR|CNV|TSK|RDM)_[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$`
  - `number` (`D` digits) domain branch:
    `^(SYS|SWR|ARC|ICD|COMP|VER)_[A-Z0-9]+_[0-9]{D}$`
  - `number` (`D` digits) flat branch: `^(ADR|BDR|WDR|CNV|TSK|RDM)_[0-9]{D}$`

## Links (SysML v2 Semantics)

Write forward links only. Sphinx-Needs generates `<link>_back` automatically.

- **`derives`** (SysML `derivation`, `derived from` / `derived into`):
  `swr`->`sys`, `sys`->`sys`, `swr`->`swr`.
- **`satisfies`** (SysML `satisfy`, `satisfies` / `satisfied by`):
  `arc`->`sys`/`swr`, `icd`/`comp`->`swr`.
- **`refines`** (SysML `refinement`, `refines` / `refined by`): `arc`->`arc`,
  `icd`/`comp`->`arc`, `comp`->`icd`.
- **`verifies`** (SysML `verify`, `verifies` / `verified by`):
  `ver`->`sys`/`swr`.
- **`drives`** (SysML `dependency`, `drives` / `driven by`): `bdr`->`sys`/`swr`.
- **`governs`** (SysML `dependency`, `governs` / `governed by`):
  `bdr`/`wdr`->`arc`/`adr`.
- **`traces`** (SysML `dependency`, `traces` / `traced by`): normative or `con`
  -> `adr`/`bdr`/`wdr`/`con`, and `task`/`roadmap` -> all.
- **`supersedes`** (model-specific, `supersedes` / `superseded by`):
  `adr`->`adr`, `bdr`->`bdr`, `wdr`->`wdr`.

- Requirements do not use `satisfies` on other requirements. Use `derives`.
- Verification items (`ver`) always target requirements (`sys` or `swr`), not
  design elements (`arc`, `icd`, `comp`). If design behavior requires testing,
  express the behavior as a `swr` and connect the design element with
  `satisfies`.
- Nested child items represent SysML v2 requirement containment (`parent_need`).

## Statuses

One global status schema enum applies across `needs_fields`:

- **Normative items and conventions:** `draft`, `active`, `obsolete`.
- **Decisions (`adr`, `bdr`, `wdr`):** `proposed`, `accepted`, `superseded`,
  `deprecated`.
- **Planning entries (`task`, `roadmap`):** `open`, `in_progress`, `done`,
  `cancelled`.

Completeness rules apply to all items whose status is not in `{draft, obsolete,
superseded, deprecated, proposed}`.

## Tags

- `informational`: marks a `sys` or `swr` item that intentionally has no
  verification item. Document the rationale in the item body.
- **Verification method tags:** each active `ver` item must carry **exactly
  one** tag from `model.ver_method_tags` (default: `unit`, `integration`,
  `network`, `analysis`).
- Do not duplicate domains, link names, or work-sequence planning data in tags.

## Compound Items and Records

- **Compound items:** nest atomic child directives inside the parent directive
  body (4-backtick outer fence in MyST). Connect and verify each child item.
- **Decisions and requirements:** decisions record rationale, rejected
  alternatives, and consequences (`Context`, `Decision`, `Rejected
  alternatives`, `Consequences`). Requirements state testable system contracts.
  Superseding decisions connect with `:supersedes:` and mark the old record
  `superseded`.
- **Conventions (`docs/records/CONVENTIONS.md`):** use `### CNV_<SUFFIX> —
  Title` followed by `{con}`. Edit in place, retire with `:status: obsolete`,
  and trace originating decisions.
- **Planning (`TASKS.md`, `ROADMAP.md`, `HISTORY.md`):** priority-ordered
  entries trace into the model. Completed or cancelled entries move verbatim
  into `HISTORY.md` (newest first) with status `done` or `cancelled`. Normative
  items and records do not reference `TSK_` or `RDM_` IDs.
- Each record page starts with `Purpose`, `Structure`, and `Formatting Rules`,
  followed by a DataTables `needtable` with a `traces_back as "Traced by"`
  column (with `;` column separators). Planning pages filter by their own
  `docname` so archived entries in `HISTORY.md` do not reappear in `TASKS.md` or
  `ROADMAP.md`.

### Record Entry Ordering

- **`CHANGELOG.md` (root, if present):** **Newest first** (`## [Unreleased]` at
  top, releases and category entries newest first).
- **`docs/records/HISTORY.md`:** **Newest first** (most recently completed or
  cancelled entry at top). Rendered `needtable` mirrors source order with
  `needtable_preserve_order_docs`.
- **`docs/records/TASKS.md` & `docs/records/ROADMAP.md`:** **Priority order**
  (highest priority first). Rendered `needtable` mirrors source order with
  `needtable_preserve_order_docs`.
- **`docs/records/CONVENTIONS.md`:** Standing active set (edited in place,
  retired entries `obsolete`). Rendered `needtable` sorts ascending by ID.
- **Decision indexes (`adr/`, `bdr/`, `wdr/`):** One file for each decision
  (`ADR_<SUFFIX>.md`, `BDR_<SUFFIX>.md`, `WDR_<SUFFIX>.md`). Rendered
  `needtable` orders newest first in `number` mode (`needtable_reverse_docs`)
  and ascending in `slug` mode.
