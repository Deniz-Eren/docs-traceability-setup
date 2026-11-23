# Initial Prompt

Make an Agent Skill with the name `docs-traceability-setup` in a Git repository
that is only for this skill. The root of this repository is the root of the
skill. Thus, `SKILL.md` is in the root directory of the repository. Do not write
the skill into a skills directory of an agent environment (for example
`.agents/skills/` or `.claude/skills/`). The user installs the skill from the
repository.

The skill operates on a software repository of all programming languages. It
does one of these two procedures:

- It scaffolds a docs-as-code traceability model in a new project.
- It migrates the documentation of a project to this model.

The model uses **Sphinx**, **MyST-Parser**, and **Sphinx-Needs**. The build does
the traceability checks. **CMake** and **CTest** control the build and the
tests.

The skill also contains the source text checks (line length, prose packing, and
file headers). The skill does these checks on all files that it changes. The
checks are in the skill, not in the target project.

Write these principles in `SKILL.md`. Apply them in all parts of the skill:

- **One model, calculated views.** Each item is written one time, in its
  document, as a Sphinx-Needs directive. The build makes all indexes, tables,
  back-links, and coverage views from the model. Thus, these views are always
  correct. Do not manually write a view that the model can make.
- **Forward links only.** Write each link one time, on the lower or derived
  item. Sphinx-Needs calculates the opposite direction (`<link>_back`).
- **Stop the build, do not change the rule.** The default build of the project
  does all traceability checks and sets warnings to errors. At the end of each
  operation of the skill, the source text checks must show no problems. If a
  check finds a problem, correct the content. Do not change the check.
- **One source for each fact.** All configuration items of the skill are in
  `.docs-traceability-setup.yml` at the root of the target repository. The need
  model module `config/sphinx/needs_model.py`, `conf.py`, and the skill scripts
  read this file. The line length and the file header text are in the
  `.editorconfig` of the target. The editors and the skill scripts read the same
  file. Thus, they always agree.
- **Output out of the source tree.** The build writes no file into the
  repository. All output goes into `<build>/docs/`.
- **Permanent IDs.** Each ID uses the suffix style configured in
  `.docs-traceability-setup.yml`: a slug (`slug`) or a fixed-width zero-padded
  number (`number`, with a configured digit count such as `NNNN`). Do not use an
  ID again and do not change an ID, also when the title changes. To remove an
  item from use, change its status.

## 0. Skill File Tree

The tree shows the root of the skill repository. The `docs/` directory contains
this prompt. Keep it in the repository.

The `assets/repo/` directory has the same structure as the root of the target
repository. Thus, each file goes to the same path below the root of the target.

```text
docs-traceability-setup/       # root of the skill repository
├── SKILL.md
├── README.md                  # how to install the skill
├── docs/
│   └── init-prompt.md         # this prompt
├── references/
│   ├── configuration.md       # .docs-traceability-setup.yml schema + interview
│   ├── model.md               # types, IDs, links, tags, statuses, rules
│   ├── authoring.md           # item document template, MyST/RST syntax
│   ├── checks.md              # all checks and how to correct findings
│   └── migration.md           # migration of a current project
├── scripts/                   # the skill operates them, not the target
│   ├── project_config.py      # .docs-traceability-setup.yml reader
│   ├── editorconfig.py        # .editorconfig reader (glob sections)
│   ├── file_kinds.py          # scope + comment syntax of each file kind
│   ├── check_text.py          # entry point: headers, line length, packing
│   ├── check_headers.py
│   ├── check_line_length.py
│   ├── defaults.editorconfig  # used if the target has no .editorconfig
│   └── tests/                 # unit tests of the scripts
│       ├── test_check_headers.py
│       ├── test_check_line_length.py
│       ├── test_editorconfig.py
│       └── test_project_config.py
└── assets/
    ├── requirements.txt       # merged into the target manifest
    └── repo/
        ├── .docs-traceability-setup.yml
        ├── .editorconfig
        ├── config/sphinx/
        │   ├── conf.py
        │   ├── needs_model.py     # the one definition of the need model
        │   ├── tag_scan.py        # the only in-code tag scanner
        │   └── need_tag_check.py  # Sphinx extension: tag rules + code trace
        ├── tools/traceability/
        │   └── check_needs_audit.py
        ├── tests/traceability/
        │   ├── test_check_needs_audit.py
        │   └── test_tag_scan.py
        └── docs/
            ├── CMakeLists.txt
            ├── index.md
            ├── README.md
            ├── 00-overview/{index,context,glossary}.md
            ├── 00-overview/wdr/{index,WDR_CI_GATES}.md
            ├── 10-product/{index,vision}.md
            ├── 10-product/bdr/{index,BDR_MAGIC_LINKS}.md
            ├── 20-system/{index,example}.md
            ├── 30-architecture/{index,example}.md
            ├── 30-architecture/adr/{index,ADR_SPHINX_NEEDS}.md
            ├── 40-interfaces/{index,example}.md
            ├── 50-components/{index,example}.md
            ├── 60-verification/
            │   ├── index.md
            │   ├── example.md
            │   ├── traceability.md
            │   └── code-trace.md
            └── records/
                ├── index.md
                ├── CONVENTIONS.md
                ├── TASKS.md
                ├── ROADMAP.md
                └── HISTORY.md
```

`README.md` tells the user how to install the skill. To install the skill, the
user clones the repository into a skills directory of the agent environment.
The user can also make a symbolic link to the repository in that directory. For
example, use `.agents/skills/docs-traceability-setup/` or
`.claude/skills/docs-traceability-setup/`.

Each file in `assets/repo/` and `scripts/` that a person writes must agree with
`scripts/check_text.py` (file header, line length, and packing). Do this check
after you replace the `{{PLACEHOLDERS}}`.

## 1. `SKILL.md`

Write YAML frontmatter with `name: docs-traceability-setup` and a `description`.
The `description` must start the skill for these tasks, in a new project or in a
project with documentation, of all programming languages:

- Set up or change the structure of documentation, requirements, architecture
  specifications, ICDs, Workflow Decision Records (WDR),
  Business Decision Record (BDR), Architecture Decision Records (ADR),
  conventions, or traceability.
- Add line length checks, file header checks, or traceability checks.
- Examine the source text of a repository (check mode).

Keep `SKILL.md` short. Write the principles, the workflow (section 9), and links
to `references/*.md`. These files contain the project configuration schema, the
full model, the authoring rules, the checks, and the migration rules.

### 1.1 Project Skill Configuration (`.docs-traceability-setup.yml`)

Each target repository must record all configuration items of the skill in one
source file at the root of the repository: `.docs-traceability-setup.yml`. The
`config/sphinx/needs_model.py` module, `conf.py`, and the skill scripts read
this file. Editor formatting properties (`max_line_length`, indentation, line
end characters, and `[file-header]` notice lines) stay in `.editorconfig`.

If `.docs-traceability-setup.yml` is missing or does not contain a configuration
item, and the user did not supply the value, the skill must do an interview with
the user to complete each item. The skill completes this interview before it
writes or migrates files. During the interview, the skill can show values that
it found in the repository. The user then accepts or changes those values. The
skill must not use default values for missing items unless the user tells it to
accept the defaults.

Write the full schema and the interview procedure in
`references/configuration.md`. The configuration file contains these items:

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
  decision_types:               # Enabled decision record types
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

- When `id.style` is `slug`, `id.digits` is not necessary and the tools ignore
  it. When `id.style` is `number`, `id.digits` must be a positive integer (for
  example `4` for `NNNN`, `3` for `NNN`, or `5` for `NNNNN`).
- An incorrect or unknown value in `.docs-traceability-setup.yml` stops the
  tools and scripts with an error. They do not use a default value as an
  alternative.

## 2. The Need Model (`references/model.md`, `config/sphinx/needs_model.py`)

The `needs_model.py` module is Python only and does not import Sphinx. It reads
`.docs-traceability-setup.yml` at the root of the repository (with only the
Python standard library) and makes these definitions from it:

- The types and the ID patterns (derived from `id.style` and `id.digits`).
- The links and the matrix of permitted links.
- The statuses and the regulated tags (from `model.ver_method_tags`).
- The rules for code tags and excluded paths (`model.code_tag_exclude`).
- The comment markers for each file type (for the tag scanner).
- The patterns of test file names (from `model.test_file_patterns`).

The files `conf.py`, `tag_scan.py`, `need_tag_check.py`, and
`check_needs_audit.py` import this module. The skill script
`check_line_length.py` reads the names of the prose directives from this module.
If the module is not available, the script uses a list of types that it
contains.

### 2.1 Layout (by level of engineering abstraction)

| Directory | Content | Types |
|---|---|---|
| `docs/00-overview/` | System context, glossary | — |
| `docs/00-overview/wdr/` | One decision record in each file | `wdr` |
| `docs/10-product/` | Product vision | — |
| `docs/10-product/bdr/` | One decision record in each file | `bdr` |
| `docs/20-system/` | Black-box system and software requirements | `sys`, `swr` |
| `docs/30-architecture/` | Structural decomposition, concurrency | `arc` |
| `docs/30-architecture/adr/` | One decision record in each file | `adr` |
| `docs/40-interfaces/` | Interface Control Documents | `icd` |
| `docs/50-components/` | White-box behavior, state machines | `comp` |
| `docs/60-verification/` | Verification items, generated reports | `ver` |
| `docs/records/` | Conventions and planning records | `con`, `task`, `roadmap` |

- **One document for each domain in each layer.** The document
  `20-system/<domain>.md` contains only items of the domain `<DOMAIN>`. The file
  name is in lowercase. The audit makes sure of this rule.
- The name of a decision file is the ID of its item (`ADR_<SUFFIX>.md`,
  `BDR_<SUFFIX>.md`, `WDR_<SUFFIX>.md`). Examples are `ADR_SPHINX_NEEDS.md` in
  `slug` mode and `ADR_0001.md` in 4-digit `number` mode.
- The document `docs/README.md` gives instructions to contributors. The Sphinx
  build does not include it.

### 2.2 Types and IDs

| Directive | Title | ID pattern | Color |
|---|---|---|---|
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

- The `<DOMAIN>` segment has capital letters and agrees with `[A-Z0-9]+`. It
  identifies the subsystem or the subject. It has no `_`.
- The `<SUFFIX>` segment uses the alternative configured in
  `.docs-traceability-setup.yml` (`id.style` and `id.digits`):
  - **`slug` alternative (`id.style: slug`):** `<SUFFIX>` is a `<SLUG>`, a short
    name of the item with one or more words in capital letters and `_` between
    the words. Each word agrees with `[A-Z0-9]+`. The first character of the
    slug is a letter. For example, `SUPPLY_MONITOR`.
    - Make the slug from the title of the item. Use the important words of the
      title, usually 1 to 4 words. Do not write the prefix or the domain in the
      slug again.
    - A slug identifies an item, not a position. Thus, the IDs have no sequence.
      Do not put a sequence number in a slug.
    - If a new ID is the same as the ID of an item, add a word to the new slug.
    - The slug of a child item (2.6) can start with the slug of its parent. For
      example, `SWR_POWER_MONITOR_LOW_VOLTAGE` is a child of
      `SWR_POWER_MONITOR`.
  - **`number` alternative (`id.style: number`, `id.digits: <D>`):** `<SUFFIX>`
    is a fixed-width, zero-padded decimal number with `<D>` digits
    (`[0-9]{<D>}`). For example, `id.digits: 4` specifies `NNNN`, such as
    `SWR_POWER_0001` and `ADR_0001`.
    - Give the next new number in each type and domain (or in each type for
      record and decision IDs).
    - Do not use an obsolete number again and do not change the number of
      current items when you add, remove, or change items.
    - Give each child item (2.6) a new `<D>`-digit number.
- Two items cannot have the same ID.
- Make `needs_id_regex` in `needs_model.py` from this table and from
  `.docs-traceability-setup.yml` as one anchored alternation:
  - For `id.style: slug`:
    `^(SYS|SWR|ARC|ICD|COMP|VER)_[A-Z0-9]+_[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$|^(ADR|BDR|WDR|CNV|TSK|RDM)_[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$`.
    The first character of the slug is a letter. Thus, an ID with a number in
    the position of the slug (for example `SWR_POWER_0001`) does not agree with
    the regex.
  - For `id.style: number` with `id.digits: <D>` (for example `4` for `NNNN`):
    `^(SYS|SWR|ARC|ICD|COMP|VER)_[A-Z0-9]+_[0-9]{4}$|^(ADR|BDR|WDR|CNV|TSK|RDM)_[0-9]{4}$`
    (with `[0-9]{<D>}`). An ID with a slug or with a different digit count (for
    example `SWR_POWER_MONITOR` or `SWR_POWER_01` when `id.digits` is `4`) does
    not agree with the regex.
- Set `needs_id_required = True`.
- The tag scanner makes its ID pattern from the same regex.

### 2.3 Links (write the forward link, the build calculates the back-link)

The links use the semantics of the SysML v2 relations. Write the SysML v2
relation of each link in `references/model.md`.

| Link | SysML v2 relation | Permitted source → target | Link text (out / in) |
|---|---|---|---|
| `derives` | `derivation` | `swr`→`sys`, `sys`→`sys`, `swr`→`swr` | `derived from` / `derived into` |
| `satisfies` | `satisfy` | `arc`→`sys`/`swr`, `icd`/`comp`→`swr` | `satisfies` / `satisfied by` |
| `refines` | `refinement` | `arc`→`arc`, `icd`/`comp`→`arc`, `comp`→`icd` | `refines` / `refined by` |
| `verifies` | `verify` | `ver`→`sys`/`swr` | `verifies` / `verified by` |
| `drives` | `dependency` | `bdr`→`sys`/`swr` | `drives` / `driven by` |
| `governs` | `dependency` | `bdr`/`wdr`→`arc`/`dec` | `governs` / `governed by` |
| `traces` | `dependency` | normative or `con` → `dec`/`con`, `task`/`roadmap` → all | `traces` / `traced by` |
| `supersedes` | (none) | `dec`→`dec`, `bdr`→`bdr`, `wdr`→`wdr` | `supersedes` / `superseded by` |

- **`derives`:** the source is the derived requirement. The target is the
  requirement that it comes from. If a system satisfies the target requirement,
  it must also satisfy the derived requirement.
- **`satisfies`:** the source is an element of the design (`arc`, `icd`, or
  `comp`). The target is always a requirement. A requirement does not satisfy a
  requirement. Use `derives` for that relation.
- **`refines`:** the source gives a more accurate and more detailed
  representation of the target.
- **`verifies`:** the source is a verification item. The target is always a
  requirement. Thus, an `arc`, `icd`, or `comp` item does not have a `ver` item.
  If the behavior of a design element must have a test, write a `swr` item for
  that behavior. Then link the design element to it with `satisfies`.
- **`drives` and `governs`:** Business decisions (`bdr`) use `drives` to connect
  to system requirements and `governs` to control architecture selections.
  Workflow decisions (`wdr`) use `governs` to control architecture limits or
  workflows.
- **`traces`:** a dependency without more semantics. Decisions (`dec`) give the
  rationale for the items that link them.
- **`supersedes`:** a relation of this model, not of SysML v2.
- **Child items** (2.6) are the SysML v2 containment of requirements.

The audit makes sure that each link agrees with the matrix of permitted source
and target types. Do not manually write opposite links.

### 2.4 Statuses (one enum for all types)

- Normative items and conventions: `draft`, `active`, `obsolete`.
- Decisions (BDR, ADR, WDR): `proposed`, `accepted`, `superseded`, `deprecated`.
- Planning entries: `open`, `in_progress`, `done`, `cancelled`.

Each need has 1 status. The completeness rules apply to all items that do not
have the status `draft`, `obsolete`, `superseded`, or `deprecated`.

### 2.5 Tags

Tags put items into groups. The overview tables can filter items by tag. The
model controls two tag roles:

- The tag `informational` identifies a `sys` or `swr` item that does not have a
  verification. Write the cause in the body of the item.
- Each `ver` item has **one** method tag, not more and not less. The default set
  is `unit`, `integration`, `network`, and `analysis`. You can change this set
  in `.docs-traceability-setup.yml` (`model.ver_method_tags`). `needs_model.py`
  reads it from there.

Do not make a tag that only gives the domain of the ID again, or the links of
the item. Do not put tags for the sequence of work on normative items. That
sequence is planning data.

### 2.6 Compound Items

Divide a compound item into a parent item and atomic child items. Put the child
items **in the body of the parent item**. Sphinx-Needs records the parent in
`parent_need`. Link each child item and give it a verification, as for all other
items.

### 2.7 Records

**Decisions and Requirements:** A decision record gives the cause and the
history of a selection (the alternatives that you examined and rejected). A
requirement gives the system contract (the accurate behavior that the system
must have). Do not use a requirement to compare alternatives. Do not use a
decision record to write system requirements that must have a test.

- **Decisions** (`10-product/decisions/`, `30-architecture/adr/`,
  `00-overview/process-decisions/`):
  - Each file contains one decision item (`bdr`, `dec`, or `wdr`).
  - The body of a decision has these headings: `Context`, `Decision`,
    `Rejected alternatives`, and `Consequences`.
  - A new decision that replaces a previous decision uses `:supersedes:`. The
    previous decision stays, with the status `superseded`.
  - An item uses `:traces:` (or `:driven_by:` / `:governed_by:`) to show the
    decisions that are its cause.
- **Conventions** (`records/CONVENTIONS.md`):
  - Each convention has a `### CNV_<SUFFIX> — Title` heading, then one `{con}`
    entry.
  - Change the entry in its position. The entry always shows the applicable
    convention.
  - A convention that the project does not use has the status `obsolete`.
  - The entry uses `traces` to link the decisions that started the convention.
- **Planning** (`records/TASKS.md`, `records/ROADMAP.md`):
  - These files contain temporary entries. The most important entry is first.
    The entries use `traces` to link the model.
  - When an entry is done or cancelled, move it without a change into
    `records/HISTORY.md`. Put the newest entry first. Set the status to `done`
    or `cancelled`.
  - **The normative model does not refer to planning entries.**
- Each record page starts with these sections: `Purpose`, `Structure`, and
  `Formatting Rules`. A `needtable` overview follows. The build makes this
  table. It has a `traces_back` column with the title "Traced by".

## 3. Authoring (`references/authoring.md`)

- The primary markup is configured in `.docs-traceability-setup.yml`
  (`authoring.primary_markup`, default `myst`). RST is also permitted. Need
  directives use fences. A parent that contains child items uses four backticks.
- **Item document template:**
  - The first heading is `# <Kind> — <Topic>`.
  - The next line is ``Domain `<DOMAIN>`: <scope in one sentence>.``.
  - The items follow.
- Use one modal verb for all requirements, configured in
  `.docs-traceability-setup.yml` (`authoring.modal_verb`, default `shall`). When
  you migrate a project, keep the modal verb of the project. Each item contains
  one obligation.
- In prose, give the name of an item in usual words. Put its ID in parentheses
  and use the ID as the link. For example:
  ``the supply monitor ({need}`SWR_POWER_MONITOR`)`` (or
  ``{need}`SWR_POWER_0001` `` in 4-digit `number` mode).
- Set `needs_role_need_template = "{{ id }}"`. This is Jinja syntax. The `{id}`
  syntax is deprecated.
- Refer to pages of the documentation with hyperlinks. Do not write the paths as
  text without a link.
- The body of a `ver` item gives the name of the automated test (function and
  file) or the analysis that does the verification.

### In-code traceability tags

- **Syntax:** a comment line `need:: <ID> [<ID> ...]` in the comment syntax of
  the file (`# need::`, `// need::`, `-- need::`, `/* need:: */`, `.. need::`).
- Use one tag line for each association. Put the tag near the related code or in
  the module docstring. Do not put tags in the file header block.
- Code refers to the **lowest-level item that specifies it**: `comp`, `icd`, or
  `arc`.
- Do not use `SYS_`, `SWR_`, `ADR_`, `BDR_`, `WDR_`, `CNV_`, `TSK_`, or `RDM_` IDs in code.
- Use `VER_` IDs only in test files. The patterns of test file names are in
  `.docs-traceability-setup.yml` (`model.test_file_patterns`, read by
  `needs_model.py`). Examples are `test_*`, `*_test.*`, and `check_*`.
- Each test file contains a minimum of one `VER_` ID.
- Write the links to the requirements one time, in `verifies` on the `ver` item.
  Do not write them in code.

## 4. Project Traceability Tools (`config/sphinx/`, `tools/traceability/`)

The skill writes these files into the target. The build of the target uses them.
Sphinx reads its configuration with `sphinx-build -c config/sphinx`.

### 4.1 `conf.py`

- Put the directory of `conf.py` on `sys.path`.
- Read project configuration items from `.docs-traceability-setup.yml` through
  `needs_model.py` (`project.name`, `project.repo_url`, `build.graphviz`,
  `model.decision_types`, and `model.code_tag_exclude`).
- Use these extensions: `myst_parser`, `sphinx_needs`, and `need_tag_check`. Add
  `sphinx.ext.graphviz` as set in `build.graphviz` (`on`, or `auto` when `dot`
  is on `PATH`).
- Set `exclude_patterns` to `README.md`, `model.code_tag_exclude`, and the trees
  of generated and third-party files.
- Make `needs_types`, `needs_id_regex`, `needs_links`, and `needs_fields` from
  `needs_model.py`. Set the `status` field to `{"schema": {"enum": [...]}}`.
- Use only the configuration names of sphinx-needs 9. A deprecated name causes a
  warning, and `-W` changes this warning into an error.
- **Do not use** `needs_extra_links`, `needs_extra_options`, `needs_statuses`,
  or role templates in `str.format` syntax.
- Set `needs_warnings` and `needs_warnings_always_warn = True`. Each rule in
  this list applies to the items with a status that the checks include (2.4):
  - `unverified`: a `sys` or `swr` item without `verifies_back`. Items with the
    tag `informational` are not included.
  - `uncovered_swr`: a `swr` item without `derives`.
  - `requirement_satisfies`: a `sys` or `swr` item with `satisfies`.
  - `floating`: an `arc`, `icd`, or `comp` item without `satisfies` and without
    `refines`.
  - `orphan_ver`: a `ver` item without `verifies`.
  - `ver_method_tag`: a `ver` item that does not have one method tag. Use a
    filter with a list comprehension.
  - `missing_status`: a need without a status.
  - `model_references_planning`: a normative item, or a `dec`, `bdr`, `wdr`, or
    `con` item, with `TSK_` or `RDM_` IDs in `traces`.
  - `superseded_without_successor`: a `dec`, `bdr`, or `wdr` item with the
    status `superseded` and without `supersedes_back`.
  - `bdr_missing_downstream`: a `bdr` item with status `active` but without
    `drives` or `governs` (enabled when `bdr` is in `model.decision_types`).
  - `sys_missing_upstream_bdr`: a `sys` item with status `active` but without
    `driven_by` (enabled when `bdr` is in `model.decision_types`).

### 4.2 `tag_scan.py` and `need_tag_check.py`

- `tag_scan.py` is the only scanner for in-code tags.
  - It reads the tracked files with `git ls-files`. If Git is not available, it
    examines the directory tree. It does not go into `.git`, `.venv`, `build`,
    or cache directories.
  - It finds a tag only where `need::` immediately follows a comment marker. The
    comment markers are in `needs_model.py`. Thus, prose that only shows the
    syntax is not a tag.
- `need_tag_check.py` is a Sphinx extension. Its `build-finished` handler
  operates one time. If the build has errors before this step, the handler does
  not operate. The handler shows a warning for each of these conditions:
  - A tag without an ID.
  - An ID that has no item.
  - An ID of a type that is not permitted in code.
  - A `VER_` ID in a file that is not a test file.
  - A test file without a `VER_` ID.
- The handler reads the model with `SphinxNeedsData(app.env).get_needs_view()`.
  A warning in `build-finished` stops a `-W` build. We did a test of this
  behavior with Sphinx 8.2 and sphinx-needs 9.2.
- The same extension adds the `need-code-trace` directive. This directive uses
  the data from the tag scanner to make a table of item IDs and their
  `file:line` locations. If `project.repo_url` in `.docs-traceability-setup.yml`
  has a value, each location is a link. The page
  `60-verification/code-trace.md` uses this directive.

### 4.3 `tools/traceability/check_needs_audit.py`

This script reads `<build>/docs/needs/needs.json`. It does a second check of the
exported model, without the Sphinx extensions. It shows these problems:

- A link without the related back-link, for all link types.
- A link to an ID that has no item.
- A link that does not agree with the matrix of permitted source and target
  types (2.3).
- Problems with coverage and method tags (2.5), and planning links in the
  incorrect direction (2.7).
- A missing parent item.
- An item document that contains more than one domain, or a domain that is not
  the same as its file name.
- A decision file with a name that is not the same as its `dec`, `bdr`, or `wdr`
  ID.

The script uses the same command-line contract as the skill scripts (5.1). CTest
operates it. The unit tests for this script and for `tag_scan.py` are in
`tests/traceability/`.

## 5. Source Text Checks (skill `scripts/`, `references/checks.md`)

These checks are part of the skill, not part of the target project. The skill
operates them on the target repository. Do not write them into the target. Do
not make them into CMake targets or CTest entries of the project.

The scripts use only the Python standard library. Thus, they operate with Python
3.11 or newer, without a venv.

### 5.1 Contract

- **Entry point:**
  `python <skill>/scripts/check_text.py --root <repo> [--fix] [paths...]`. This
  script does the header check and the check of line length and packing.
  - If you give `paths`, the script examines only those files. If not, it
    examines all files in the scope of the repository.
  - You can also operate `check_headers.py` and `check_line_length.py`
    independently.
- **Exit code:**
  - `0`: no problems.
  - `1`: one or more problems.
  - `2`: an error in the configuration or in the command.
- **Output:** one problem on each line, with the syntax
  `<file>:<line>: <message>`.
- **Configuration:**
  - The scripts read `.docs-traceability-setup.yml` (for `checks.file_headers`,
    `checks.prose_packing`, and `model.code_tag_exclude`) and `.editorconfig`
    (for line length, indentation, and `[file-header]` notice lines) from the
    **target**.
  - If the target has no `.editorconfig`, the scripts use
    `scripts/defaults.editorconfig` and show a notice. If
    `.docs-traceability-setup.yml` is missing during check mode on a repository
    with no configuration, the scripts use default check values and show a
    notice.
  - An incorrect value in one of the two files stops the script with an error.
    The script does not use a default value as an alternative.
- **Tests:** the unit tests of the scripts are in `scripts/tests/`. Use
  `python -m unittest discover scripts/tests`. All tests must be satisfactory
  before you complete the skill.

### 5.2 When the skill does the checks

- **After each change:** the skill makes or changes a file in the target (a
  document, a configuration file, or a code tag). Then it does these steps:
  1. Operate `check_text.py --fix <changed files>`.
  2. Operate `check_text.py <changed files>`.
  3. Correct all remaining problems before you continue.

  A file that the skill changed must always agree with the checks.
- **Check mode:** the user can tell the skill to examine the repository. The
  skill then operates `check_text.py --root <repo>` on all files and shows the
  problems. It uses `--fix` only when the user tells it to do so. The cause is
  that `--fix` on the full repository can change files that the skill did not
  write.
- **End of each operation:** the last report of the skill includes the result of
  `check_text.py` for the files that the skill changed.

### 5.3 `.editorconfig` (written into the target or merged)

The `.editorconfig` is the one source of these properties for the editors and
for the skill scripts. If the target has no `.editorconfig`, the skill writes
it. If the file is available, the skill adds only the missing keys.

- The `[*]` section sets `charset = utf-8`, `end_of_line = lf`,
  `insert_final_newline = true`, `trim_trailing_whitespace = true`,
  `indent_style = space`, and `max_line_length = 80`.
- The `*.py` and `CMakeLists.txt` sections set `indent_size = 4`.
- Sections with `max_line_length = off` remove data and third-party content from
  the checks (for example `*.yaml` and vendored trees).
- The `[file-header]` section contains the lines of the header notice without
  changes. The keys are numbers with 2 digits (`01`, `02`, `03`). An empty value
  gives a comment line without text.
- `editorconfig.py` finds the properties of each file. It applies the related
  glob sections in sequence (`*`, `**`, `{a,b}`, and path globs), as the editors
  do.

### 5.4 `file_kinds.py`

This module contains the scope of the scripts and the comment syntax for each
file type:

| File type | Files |
| --- | --- |
| Markdown | `*.md` |
| reStructuredText | `*.rst` |
| Python | `*.py` |
| CMake | `CMakeLists.txt`, `*.cmake` |
| Hash-comment | `*.sh`, `*.yaml`, `*.yml`, `*.toml`, `*.cfg` |
| C/C++ | `*.c`, `*.h`, `*.cc`, `*.cpp`, `*.cxx`, `*.hpp`, `*.hh`, `*.hxx` |

- **Scope:** the scripts read the tracked files with `git ls-files` if Git is
  available. They do not examine `.git`, `.venv`, `build`, caches, or paths
  where `max_line_length` is `off`.
- **Tag scanner:** the `tag_scan.py` script of the project keeps its comment
  markers in `needs_model.py`. The cause is that the project does not use the
  skill.

### 5.5 `check_headers.py`

Each Python, CMake, shell, and C/C++ file that a person writes must start with
one Doxygen header block. If the file starts with a shebang, the block comes
after the shebang. An empty line follows the block.

- `@file` gives the name of the file.
- `@brief` tells the function of the file in one line, without a period at the
  end.
- An optional `@details` area contains the comments about the full file.
- A `@copyright` area contains the `[file-header]` lines without changes.
- CMake, Python, and shell files use a `##` + `#` block. C/C++ files use a
  `/** … */` block.
- Markdown, RST, and data files have no header.
- Generated files have no header that a person writes. The generator writes the
  block.
- If `checks.file_headers` is `false` in `.docs-traceability-setup.yml`, the
  script does not do the header check. If `checks.file_headers` is `true` and
  the target has no `[file-header]` section in `.editorconfig`, the script does
  not do the header check and shows a notice. During setup, the skill does an
  interview with the user to get the notice text when `checks.file_headers` is
  `true` (workflow step 2).
- **`--fix`:**
  - The script adds a missing block. It writes the file name in `@file` and the
    `[file-header]` lines in the copyright area.
  - The script corrects a block with an incorrect copyright area.
  - The script does not write a function statement. It writes `@brief    TODO`.
    The check shows this line as a problem until the skill or the user writes
    the function statement.

### 5.6 `check_line_length.py`

- **Limit:** no character can be after the column `max_line_length`. The first
  column is 1. The script counts Unicode code points, and a tab is one
  character.
- **Packing:** when `checks.prose_packing` is `true` in
  `.docs-traceability-setup.yml` (the default), the script puts the maximum
  number of words on each prose line with a greedy algorithm. In a paragraph,
  each line before the last line contains the maximum number of words. A word
  that ends at the limit column is permitted. A line break is correct only if
  the next word does not go into the line. When `checks.prose_packing` is
  `false`, the script does a check of `max_line_length` only.
- **Packed prose:**
  - The comments and docstrings of source files, scripts, and build files.
  - Markdown and RST paragraphs.
  - The bodies of the need directives of the model. The script reads the
    directive names from `config/sphinx/needs_model.py` of the target. If this
    file is not available, it uses a list of types that it contains.
- **These structures are not packed:**
  - Paragraph boundaries.
  - List items. A line before a list is a paragraph.
  - Headings and RST underlines.
  - Lines with an indentation that stops the paragraph.
  - Code fences, RST literal blocks (`::`), and tables.
  - Directive field blocks.
  - Directives that are not prose (`toctree`, `needtable`, `need-code-trace`,
    and includes).
  - Markdown link definitions (`[name]: url`).
  - Doxygen command lines and `need::` tag lines.
  - The `[file-header]` lines.
- **`--fix`:** the script writes the packed text into the file with the same
  greedy algorithm that the check uses. It does not change the structures in the
  previous list. It shows the remaining problems, for example a long URL that it
  cannot divide.

## 6. `docs/CMakeLists.txt`

This file operates independently (`cmake -S docs -B build`) and through
`add_subdirectory(docs)`.

- It starts with `cmake_minimum_required(VERSION 3.20)`. If it is the top-level
  project, it then sets `project({{PROJECT_NAME}}_docs LANGUAGES NONE)`.
- **Python interpreter:**
  1. Use `<repo>/.venv/bin/python` if it is available.
  2. If not, and `DOCS_AUTO_INSTALL` is `ON` (default set from
     `build.docs_auto_install` in `.docs-traceability-setup.yml`), make
     `<build>/docs/venv` and install `requirements.txt` into it.
  3. If not, use `find_package(Python3)`. Then do an import check. If the import
     check finds a missing package, stop with `FATAL_ERROR` and show the install
     command.
- **Targets** (all with `COMMENT` and `VERBATIM`):
  - `docs` (`ALL`):
    `sphinx-build -b html -W --keep-going -c <repo>/config/sphinx -d <build>/docs/doctrees docs <build>/docs/html`.
  - `docs-needs`: the same command with `-b needs`. The output is
    `<build>/docs/needs/needs.json`.

  The source text checks are **not** project targets. The skill does these
  checks (section 5).
- **CTest entries** (use `enable_testing()`):
  - `traceability.unit`: the unit tests in `tests/traceability`.
  - `docs.html`.
  - `docs.needs`.
  - `docs.audit` (`DEPENDS docs.needs`).

  Set the CTest `LABELS` to `traceability` and `docs`.
- Add `<build>/docs` to `ADDITIONAL_CLEAN_FILES`.

## 7. `assets/requirements.txt`

Use `sphinx>=8,<9`, `sphinx-needs>=9,<10`, and `myst-parser>=4,<5` with Python
3.11 or newer. We did a test of these versions together. Merge these lines into
the one Python dependency manifest of the target. Do not make a second manifest.

## 8. Templates (`assets/repo/docs/`)

The templates make one full and correct chain. Thus, the first build has no
errors when all rules are active. The templates are packed to 80 columns.

- `index.md` contains the root toctree and a description of each section in one
  line.
- Each `index.md` of a layer or of the records contains these parts: a line that
  tells the function of the page, a `:glob:` toctree, and a `needtable` overview
  with back-link columns. The build makes this table.
- The example domain is `POWER` (shown below in `slug` mode). When
  `.docs-traceability-setup.yml` sets `id.style: number` with `id.digits: <D>`
  (for example `4`), the skill writes the scaffolded IDs, links, and decision
  filenames with `<D>`-digit zero-padded numbers. Examples are `BDR_0001.md`,
  `SYS_POWER_0001`, `SWR_POWER_0001`, `ADR_0001.md`, `WDR_0001.md`, `CNV_0001`,
  and `TSK_0001`:
  - `BDR_MAGIC_LINKS` (`drives` `SYS_POWER_SUPPLY`).
  - `SYS_POWER_SUPPLY` (driven by `BDR_MAGIC_LINKS`).
  - `SWR_POWER_MONITOR` (`derives` `SYS_POWER_SUPPLY`). `SWR_POWER_MONITOR`
    contains the child items `SWR_POWER_MONITOR_LOW_VOLTAGE` and
    `SWR_POWER_MONITOR_HIGH_VOLTAGE`.
  - `ARC_POWER_MONITOR` (`satisfies` `SWR_POWER_MONITOR`, `traces`
    `ADR_SPHINX_NEEDS`).
  - `ICD_POWER_STATUS` (`refines` `ARC_POWER_MONITOR`, `satisfies`
    `SWR_POWER_MONITOR`).
  - `COMP_POWER_MONITOR` (`refines` `ARC_POWER_MONITOR`, `satisfies`
    `SWR_POWER_MONITOR`).
  - `VER_POWER_MONITOR_LOW_VOLTAGE` and more: one `ver` item for each
    requirement that must have a verification. Each `ver` item has one method
    tag.
  - `ADR_SPHINX_NEEDS.md` (`accepted`).
  - `WDR_CI_GATES.md` (`governs` `ARC_POWER_MONITOR`, `accepted`).
  - `CNV_CODE_TAGS` (in-code tags), `CNV_SOURCE_TEXT` (source text
    conventions), and `CNV_FILE_HEADER` (file header). Each of these entries
    links `ADR_SPHINX_NEEDS` in `traces`.
  - One `TSK_POWER_MONITOR` entry that links `SWR_POWER_MONITOR` in `traces`.
- `60-verification/traceability.md` contains these `needtable`s:
  - The coverage from sys to swr to ver.
  - The items without a verification.
  - The items of the `orphan_ver` and `floating` rules. These tables must be
    empty.

  It also contains an optional `needflow`. The page uses it only if Graphviz is
  available.
- `60-verification/code-trace.md` contains `need-code-trace`.
- `README.md` gives this information:
  - A short description of the layout and of the model.
  - The MyST and RST syntax, the IDs, the links, the statuses, and the tags.
  - The rules for in-code tags.
  - How to install the dependencies (venv or `DOCS_AUTO_INSTALL`).
  - The commands `cmake --build build` and `ctest --test-dir build -L docs`.
  - The source text conventions (80 columns, packed prose, file header). The
    `docs-traceability-setup` skill makes sure of these conventions. The skill
    configuration is in `.docs-traceability-setup.yml`, and editor formatting
    and file header text are in `.editorconfig`.

## 9. Workflow (in `SKILL.md`)

1. **Examine the repository.** Find these data:
   - If `.docs-traceability-setup.yml` is available at the root of the target
     repository, and which configuration items have values.
   - The languages, the build system, the `docs/` directory, the Sphinx
     configuration, the `.editorconfig`, the dependency manifest, and the layout
     of the tests.
   - The traceability IDs (such as the current slug or number style and digit
     count), modal verb, and in-code tags that the project has.
   - The URL of the repository, the copyright holder, and the license.
2. **Do an interview with the user and write `.docs-traceability-setup.yml`.**
   - For each configuration item in `.docs-traceability-setup.yml` (1.1) that
     has no value in the repository and that the user did not supply, do an
     interview with the user to complete it. Show values found in step 1 as
     initial defaults for the user to accept or change.
   - Always get user approval for or collect:
     - `id.style` (`slug` or `number`) and, when `number`, `id.digits` (for
       example `4` for `NNNN`).
     - `project.name`, `project.repo_url`, and `project.domains`.
     - `authoring.primary_markup` and `authoring.modal_verb`.
     - `model.decision_types`, `model.ver_method_tags`,
       `model.test_file_patterns`, and `model.code_tag_exclude`.
     - `build.cmake_mode`, `build.python_manifest`, `build.docs_auto_install`,
       and `build.graphviz`.
     - `checks.file_headers` (plus the `[file-header]` notice text for
       `.editorconfig` when enabled) and `checks.prose_packing`.
   - Do not ignore configuration items that have no value unless the user tells
     the skill to accept the defaults.
   - Write or update `.docs-traceability-setup.yml` at the root of the target
     repository as the one source before the skill scaffolds or migrates the
     repository.

   If the repository has a traceability model, use `references/migration.md` as
   an alternative to steps 3 and 4.
3. **Write the files** of `assets/repo/` into the target.
   - Do not replace a file that the target has. Merge the necessary items into
     it, or tell the user to make a selection.
   - Apply all values from `.docs-traceability-setup.yml` (such as `id.style`
     and `id.digits` for scaffolded IDs and decision filenames) and replace the
     `{{PLACEHOLDERS}}`.
   - If the workflow operates again with a completed
     `.docs-traceability-setup.yml`, it does not do the interview again and does
     not change the result.
4. **Connect the build:**
   - Use `build.cmake_mode`, `build.python_manifest`, and
     `build.docs_auto_install` from `.docs-traceability-setup.yml`.
   - If `build.cmake_mode` is `subdirectory` (a root `CMakeLists.txt` is
     available), add `add_subdirectory(docs)` and `enable_testing()` to it.
   - If `build.cmake_mode` is `standalone`, use `cmake -S docs -B build`. Do not
     make a root `CMakeLists.txt`.
   - Add `build/` and `.venv/` to `.gitignore`.
5. **Correct the source text:**
   - Operate `scripts/check_text.py --fix` on each file that the skill made or
     changed. Then do the check of those files again. Correct the remaining
     problems (for example, write the `@brief` lines).
   - Do this step again after each subsequent change (5.2).
   - Tell the user that the skill can examine the full repository. Use `--fix`
     on the full repository only if the user agrees.
6. **Build and test:** operate `cmake -B build`, `cmake --build build`, and
   `ctest --test-dir build`. All steps must complete without errors. If a step
   has errors, correct the content. Do not change a rule.
7. **Report:** give a list of the files that the skill made, merged, or
   migrated. Give the result of `check_text.py`. Tell how to build and test.

**Check mode:** the user can start the skill only to do the checks. Then the
skill does not do steps 2, 3, 4, and 6. It operates
`scripts/check_text.py --root <repo>` and shows the problems. It corrects them
only when the user tells it to do so.

## 10. Migration of a Project with Documentation (`references/migration.md`)

The migration keeps the good qualities of the project and changes the project to
this model:

1. **Make a list of the content of the project:**
   - The item types, IDs, link types, tags, and statuses.
   - The records: decisions, conventions, tasks, roadmap, and history.
   - The syntax of the in-code tags, and the scanners and checkers for them.
   - The Sphinx extensions of the project and the CMake targets.
   - The sphinx-needs version.
2. **Change the types:**
   - General requirements → `sys` (black-box, system level) or `swr` (software
     level). Select the type for each item.
   - Architecture → `arc`.
   - Design → `comp`. If the item gives an interface, use `icd`.
   - Test → `ver`.
   - Architecture Decision → `dec`.
   - Business Decision → `bdr`.
   - Workflow Decision → `wdr`.
   - Convention → `con`.
   - Task and roadmap do not change.
   - A `satisfies` link between two requirements → `derives`.
   - A `verifies` link to an element that is not a requirement → a `verifies`
     link to the requirement that the element satisfies. If that requirement is
     not clear, tell the user to select it.

   If the type of an item is not clear, tell the user to select it.
3. **Change the IDs and domains:** keep the domain segments. Format each ID
   suffix as set by `id.style` and `id.digits` in `.docs-traceability-setup.yml`
   (2.2):
   - If `id.style` is `slug`, replace each number with a slug made from the
     title of the item. For example:
     - `REQ-FETCH-0001` ("Retry after a timeout") → `SWR_FETCH_RETRY_TIMEOUT`.
     - `DES-DOC-0003` ("Page renderer") → `COMP_DOC_PAGE_RENDERER`.
     - `ADR-0049` ("SQLite for the cache") → `ADR_SQLITE_CACHE`.
     - `CNV-0002` ("Commit messages") → `CNV_COMMIT_MESSAGES`.
     If two items get the same slug, add a word to one of the slugs.
   - If `id.style` is `number`, format each suffix as a zero-padded decimal
     number with `id.digits` digits (for example `4` digits `NNNN`). Keep the
     current item numbers where they fit without a duplicate. If not, give the
     next new number. For example (with `id.digits: 4`):
     - `REQ-FETCH-0001` → `SWR_FETCH_0001`.
     - `DES-DOC-0003` → `COMP_DOC_0003`.
     - `ADR-0049` → `ADR_0049`.
     - `CNV-0002` → `CNV_0002`.

   Show the full ID table to the user before you change the files.

   Write the full table of previous and new IDs in `docs/records/id-map.md`.
   This file contains a Markdown table, not needs.
4. **Change the IDs in all files:**
   - Change the link fields, the `{need}` roles, the IDs in prose, and the
     in-code tags. For example, `# need:: DES-DOC-0003` becomes
     `# need:: COMP_DOC_PAGE_RENDERER` (in `slug` mode) or
     `# need:: COMP_DOC_0003` (in 4-digit `number` mode).
   - Use a script that applies the ID table. Make sure that a person can examine
     the changes.
   - Then use `git grep` to find the remaining previous IDs.
5. **Change the structure of the documents:**
   - Use `git mv` to move the documents into the numbered layers. Keep one
     document for each domain.
   - If one record file contains all decisions, divide it into one ADR file for
     each decision. Keep the full text. The name of each decision file is its
     new `ADR_<SUFFIX>` (or `BDR_<SUFFIX>` / `WDR_<SUFFIX>`) ID. Set the status
     to `accepted`. Decisions that the project removed before stay in the Git
     history.
   - Move the conventions, tasks, roadmap, and history into `docs/records/`.
6. **Change the configuration:** keep `.docs-traceability-setup.yml` at the root
   of the repository as the one source for all configuration items of the skill.
   Move the Sphinx configuration to `config/sphinx/` (it reads
   `.docs-traceability-setup.yml` through `needs_model.py`), and change it to
   sphinx-needs 9:
   - `needs_extra_links` → `needs_links`.
   - `needs_extra_options` → `needs_fields`.
   - `needs_statuses` → the schema of the `status` field.
   - `{id}` → `{{ id }}`.
7. **Keep the special parts of the project:**
   - Keep the extensions, generators, CMake targets, and special tests of this
     project. Examples are API links, capture of CLI help, and the sequence of
     records. Change them to the new ID regex and paths. Keep them connected to
     the build.
   - Replace the traceability tag checker and the needs audit of the project
     with the skill versions only if the skill versions do all the checks of the
     project versions.
   - The project can have checkers and build targets for line length, packing,
     or headers. Before you remove them, get the approval of the user. The skill
     scripts then do these checks.
   - Before you remove these checkers, move the project properties into
     `.editorconfig`: `max_line_length`, the globs with no limit, and the
     license text (into `[file-header]`).
   - Then make sure that the skill scripts find all the problems that the
     previous checkers found.
8. **Make sure that the migration is correct:**
   - The build and all CTest entries complete without errors.
   - The audit shows the same number of items as before the migration, plus the
     new ADR files.
   - No ID in the previous syntax stays in the repository
     (`git grep -nE '<previous ID regex>'`).

## 11. Conditions to Accept the Skill

1. On an empty repository, the workflow gives
   `cmake --build build && ctest --test-dir build` without errors in the two
   modes: `id.style: slug` and `id.style: number` (for example with
   `id.digits: 4` for `NNNN`). It writes `.docs-traceability-setup.yml` at the
   root of the repository with all configured items recorded.
2. On a repository with a root `CMakeLists.txt`, the workflow adds only
   `add_subdirectory(docs)` and `enable_testing()`. All steps complete without
   errors.
3. If the workflow operates again on the same repository with a completed
   `.docs-traceability-setup.yml`, it does not do the interview again and does
   not change files. When configuration items are missing and the user did not
   supply them, the workflow does an interview with the user to complete them
   before it writes files.
4. **Each of these changes** stops the project build or CTest with a clear
   message:
   - Removal of the `ver` item that links `SWR_POWER_MONITOR` (or
     `SWR_POWER_0001` in `number` mode) in `verifies`.
   - An ID with an incorrect syntax (such as a number suffix in `slug` mode, a
     slug suffix in `number` mode, or an incorrect digit count in `number`
     mode).
   - An unknown status.
   - A second method tag on a `ver` item.
   - A `SWR_` tag in source code.
   - A `need::` tag with an ID that has no item.
   - A test file without a `VER_` tag.
   - A `traces` link from a `swr` item to a `TSK_` entry.
   - A `satisfies` link from a `swr` item to a `sys` item.
   - A `verifies` link from a `ver` item to a `comp` item.
5. **Each of these changes** causes `scripts/check_text.py` to stop with the
   exit code 1:
   - A line with 81 characters.
   - A paragraph that is not fully packed.
   - A missing or changed header block.
6. The scaffolded project has no source text checker, CMake target, or CTest
   entry for line length, packing, or headers.
7. `check_text.py --fix` changes a file that is not fully packed into a correct
   file. It does not change code blocks, tables, or tag lines. All tests in
   `scripts/tests/` are satisfactory.
8. Each file that the skill made or changed during an operation agrees with
   `check_text.py`.
9. When the migration operates on a project with traceability, it keeps all
   items, links, decisions, conventions, and in-code tags. It shows the full ID
   table. All build steps and tests complete without errors.
10. The skill is in the root directory of a Git repository that is only for this
    skill. The agent did not write the skill into a skills directory of an
    agent environment.
