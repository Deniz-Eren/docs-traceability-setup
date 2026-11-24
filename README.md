# docs-traceability-setup

Agent Skill for scaffolding and migrating Sphinx/MyST/Sphinx-Needs docs-as-code
traceability models with CMake/CTest and Python source-text checks.

## Installation

Install the skill by cloning this repository (or creating a symbolic link to it)
into your agent environment's skills directory, for example
`.agents/skills/docs-traceability-setup/` or
`.claude/skills/docs-traceability-setup/`:

```bash
ln -sfn /path/to/docs-traceability-setup .agents/skills/docs-traceability-setup
```

The repository root (`SKILL.md`, `references/`, `scripts/`, `assets/`) is the
skill root.

## Resultant Target Project Structure

Applying this skill creates or merges the following layout in your target
repository (with `<domain>` named after your primary domain and `<SUFFIX>`
formatted in your chosen `slug` or zero-padded `number` ID style):

```text
<your-repo>/
├── .docs-traceability-setup.yml        ← Single skill and model config
├── .editorconfig                       ← Line length, indent, [file-header]
├── CMakeLists.txt                      ← Adds docs subdirectory (opt.) *
├── requirements.txt                    ← Merged Sphinx/Needs/MyST deps **
├── config/
│   └── sphinx/
│       ├── conf.py                     ← Sphinx 8 / Sphinx-Needs 9 config
│       ├── needs_model.py              ← Types, ID regexes, link matrix
│       ├── tag_scan.py                 ← In-code need:: tag scanner
│       └── need_tag_check.py           ← Build-time tag and table hooks
├── tools/
│   └── traceability/
│       └── check_needs_audit.py        ← Standalone needs.json auditor
├── tests/
│   └── traceability/
│       ├── test_tag_scan.py            ← Tag scanner unit tests
│       └── test_check_needs_audit.py   ← Model auditor unit tests
└── docs/
    ├── CMakeLists.txt                  ← Sphinx HTML build and CTest gates
    ├── README.md                       ← Contributor authoring/build guide
    ├── index.md                        ← Documentation entry point
    ├── 00-overview/                    ← System context, glossary, WDRs
    │   ├── index.md
    │   ├── context.md
    │   ├── glossary.md
    │   └── wdr/
    │       ├── index.md
    │       └── WDR_<SUFFIX>.md         ← One Workflow Decision per file
    ├── 10-product/                     ← Product vision and BDRs
    │   ├── index.md
    │   ├── vision.md
    │   └── bdr/
    │       ├── index.md
    │       └── BDR_<SUFFIX>.md         ← One Business Decision per file
    ├── 20-system/                      ← System/software reqs (sys, swr)
    │   ├── index.md
    │   └── <domain>.md
    ├── 30-architecture/                ← Structural design (arc) and ADRs
    │   ├── index.md
    │   ├── <domain>.md
    │   └── adr/
    │       ├── index.md
    │       └── ADR_<SUFFIX>.md         ← One Architecture Decision per file
    ├── 40-interfaces/                  ← Interface specs (icd)
    │   ├── index.md
    │   └── <domain>.md
    ├── 50-components/                  ← Component specs (comp)
    │   ├── index.md
    │   └── <domain>.md
    ├── 60-verification/                ← Verification (ver) and coverage
    │   ├── index.md
    │   ├── <domain>.md
    │   ├── traceability.md             ← Generated coverage tables
    │   └── code-trace.md               ← Generated code-to-spec trace
    └── records/                        ← Standing and planning records
        ├── index.md
        ├── CONVENTIONS.md              ← Active conventions (con)
        ├── TASKS.md                    ← Active tasks (task)
        ├── ROADMAP.md                  ← Planned milestones (roadmap)
        └── HISTORY.md                  ← Archived done/cancelled entries
```

- `*` In `subdirectory` CMake mode, `add_subdirectory(docs)` and
  `enable_testing()` are added to your root `CMakeLists.txt`. In `standalone`
  mode, no root `CMakeLists.txt` is added and `docs/` builds on its own.
- `**` Documentation dependencies are merged into your configured Python
  manifest (`build.python_manifest`, default `requirements.txt`).
- **Pre-existing scaffolding files:** Equivalent flat files (such as vision,
  architecture, decision, convention, task, or roadmap documents) are ported
  into the layered `docs/` structure and removed after your approval. Non-model
  files (`AGENTS.md`, `CHANGELOG.md`, `docs/skills/`, `docs/agents/`,
  `docs/THIRD-PARTY-NOTICES.md`) stay intact and excluded from Sphinx.
- **Disabled decision types:** Any decision type omitted from
  `model.decision_types` (`adr`, `bdr`, `wdr`) is omitted from `docs/`.
- **Clean source tree:** All generated HTML and JSON build artifacts go
  out-of-source to `build/docs/`. The skill's source-text checkers run directly
  from this skill repository and are not copied into your project.

## Commands

```bash
scripts/build-agent.sh
scripts/formatter-agent.sh
```

## Development Environment

```bash
python3 -m venv .venv
```

For more information, see the [dev-environment
skill](docs/skills/dev-environment/SKILL.md).

## Documentation

- [SKILL.md](SKILL.md): deliverable `docs-traceability-setup` Agent Skill entry
  point
- [AGENTS.md](AGENTS.md): governance for AI agents (modes, git protocol,
  pre-commit checklist)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): overview of the system and the
  directory structure
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md): file names, document formatting,
  and copyright rules
- [docs/init-prompt.md](docs/init-prompt.md): immutable initial specification
  prompt for the skill
- Skills:
  - [create-skill](docs/skills/create-skill/SKILL.md): make new development
    skills that obey the Agent Skills spec
  - [dev-environment](docs/skills/dev-environment/SKILL.md): set up and use the
    native Python virtual environment
  - [git](docs/skills/git/SKILL.md): commit modes, inline identity, Conventional
    Commits, and release tags
  - [keepachangelog](docs/skills/keepachangelog/SKILL.md): keep `CHANGELOG.md`
    in Keep a Changelog format
  - [ruff](docs/skills/ruff/SKILL.md): lint and format Python files with Ruff
  - [state-management](docs/skills/state-management/SKILL.md): update state
    documents before each commit
  - [unittest](docs/skills/unittest/SKILL.md): run and organize Python
    `unittest` suites

## License

The MIT License applies to this project. See [LICENSE.md](LICENSE.md).

Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>

For third-party attributions, see
[docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md).
