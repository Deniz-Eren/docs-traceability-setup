# AI Agent Governance

This file has the highest authority for AI agents that work in
**docs-traceability-setup**. The skill files in [docs/skills/](docs/skills/)
have the procedures with more information. This file links to them, and it does
not give the same information again.

---

## Commit Mode

`operations.commit_mode` in `.agent-scaffolding.yml` is the single source of
truth for the commit mode and for the signature behavior of the commits. Read
the mode from there. The [git skill](docs/skills/git/SKILL.md) defines the
behavior of the modes and their typical work. This file does not define the
modes.

---

## Predict → Act → Verify

1. **Predict:** examine the task, plan the steps, and find the possible failures
   before you act.
2. **Act:** do the planned steps. Make an atomic commit after each phase.
3. **Verify:** run the checks (tests, format, lint), and confirm that they are
   correct.

If verification is not correct, go back to Act, repair the problem, and verify
again. Do not start the next phase until the current phase is correct.

---

## Failure Modes

- **A test fails:** Find the root cause, repair it, and re-run tests. After
  three unsuccessful attempts, stop and ask for human approval.
- **Formatter or linter rejects its config:** Remove one parameter at a time,
  re-test, and record an ADR. If still invalid, use an empty config and record
  the uncertainty.
- **A tool is not installed:** Document the install requirement in its skill and
  record an ADR.
- **A git conflict:** Stop, fetch remote changes, resolve, and try again.
  Escalate to the human if unresolved.
- **Context or token limit is close:** Summarize earlier context and link to
  files rather than copying their contents.

---

## Boundaries for CLI Commands

| Command | Permitted | Approval necessary |
|---|---|---|
| Read files. Run `--version` checks. | ✓ | — |
| Run build, test, and formatter scripts | ✓ | — |
| Commit | the commit mode in `.agent-scaffolding.yml` gives the rules | — |
| Install the project dependencies in the development environment | ✓ | — |
| Install system packages | ✗ | ✓ |
| Erase project files | ✗ | ✓ |
| Change IMMUTABLE documents | ✗ | ✗ (not permitted) |
| Push to a remote | ✗ | ✓ |

**Build Agent First:** delegate all build, test, and format runs to the
subagents in [docs/agents/](docs/agents/). If the platform has no subagents, run
the scripts. Report only the summary line and the failures.

---

## Token and Context Management

- Load a skill only when it is necessary for the task.
- Link to skill files and documents. Do not copy their content.
- Give a summary of the earlier context. Do not give it again.
- Read connected files in one batch.
- Write `~` or `$HOME`. Do not write an absolute home path.

---

## Git Protocol

Read the identity from `.agent-scaffolding.yml` (`identity.git_author_name`,
`identity.git_author_email`). The value `current_user` means the identity of the
current user. Take the name and the email from the git configuration of the
environment (`git config user.name`, `git config user.email`). Give the identity
inline for each commit. Do not change git config:

```bash
git -c user.name="<name>" -c user.email="<email>" commit -F <message-file>
```

Each commit message obeys Conventional Commits. It has an empty line and an
`Assisted-by:` footer at the end. The footer gives the names of the agent and
the model **of the current session**. Do not copy them from earlier commits:

```
<type>[scope]: <description>

Assisted-by: <AgentName>:<Model> [+ <Tool> ...]
```

For the full procedure, see the [git skill](docs/skills/git/SKILL.md).

---

## Pre-Commit Checklist

Before each commit, verify:

- [ ] The commit message obeys Conventional Commits, and it has the
  `Assisted-by:` footer
- [ ] The tests and linter are correct
- [ ] The formatter reports no findings
- [ ] You updated `docs/TASKS.md` (`[x] COMPLETE YYYY-MM-DD`)
- [ ] `CHANGELOG.md` has an entry in `## [Unreleased]` for the change
- [ ] `docs/DECISIONS.md` has an ADR for each new decision
- [ ] `docs/THIRD-PARTY-NOTICES.md` has attribution for each new third-party
  component
- [ ] All new and changed source files have the copyright header
- [ ] You did not change an IMMUTABLE document

For the update procedures, see the [state-management
skill](docs/skills/state-management/SKILL.md).

---

## Rules for This Project

Rules that apply only to this project. Each rule links to the skill or the
document with more information.

- `docs/init-prompt.md` is an IMMUTABLE specification document. Do not edit it.
- The deliverable `docs-traceability-setup` Agent Skill lives at the repository
  root (`SKILL.md`, `references/`, `scripts/`, `assets/`), not in
  `.agents/skills/` or `docs/skills/`. See
  [docs/init-prompt.md](docs/init-prompt.md).
- Runtime skill scripts in `scripts/` must use only the Python 3.11+ standard
  library. Development tools (`ruff`) live in `.venv` through the
  [dev-environment skill](docs/skills/dev-environment/SKILL.md).
