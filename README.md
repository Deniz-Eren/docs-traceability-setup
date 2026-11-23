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
