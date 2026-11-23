---
name: docs-traceability-setup
description: >
  Scaffold a Sphinx, MyST-Parser, Sphinx-Needs, and CMake/CTest docs-as-code
  traceability model in a new project, migrate an existing project's
  documentation to this model, or examine repository source text for line
  length, greedy prose packing, and Doxygen file headers. Use for any
  programming language when setting up or changing documentation, requirements,
  architecture specifications, ICDs, Workflow Decision Records (WDR), Business
  Decision Records (BDR), Architecture Decision Records (ADR), conventions,
  traceability, line length checks, file header checks, or running source-text
  check mode.
license: MIT
compatibility: >
  Skill scripts require Python 3.11+ (standard library only). Target
  documentation builds require CMake 3.20+, CTest, Sphinx 8, Sphinx-Needs 9,
  and MyST-Parser 4.
metadata:
  author: Deniz Eren
  version: "0.1.0"
---

# docs-traceability-setup

This skill sets up or migrates a docs-as-code traceability model with
**Sphinx**, **MyST-Parser**, **Sphinx-Needs**, **CMake**, and **CTest**. It also
operates source-text checks (Doxygen file headers, line length, and greedy prose
packing) from this skill repository.

In the commands below, `$SKILL` is the root directory that contains this
`SKILL.md`, and `<repo>` is the root of the target repository. Do not copy the
skill's `scripts/` into the target repository. Do not add them as target CMake
targets or CTest entries.

## Core Principles

- **One model, calculated views:** Write each item one time in its document as a
  Sphinx-Needs directive. Let the build generate all indexes, tables,
  back-links, and coverage views. Do not manually write derived views.
- **Forward links only:** Record each relationship one time on the lower or
  derived item. Sphinx-Needs calculates opposite links (`<link>_back`).
- **Stop the build, do not change the rule:** The default project build runs all
  traceability checks with warnings as errors (`-W --keep-going`). All files
  that this skill changes must pass `scripts/check_text.py`. When a check finds
  a problem, correct the content rather than the rule.
- **One source for each fact:** Keep all skill configuration in
  `.docs-traceability-setup.yml` at the target root
  (`config/sphinx/needs_model.py`, `conf.py`, and the skill scripts read it).
  Keep line length, indentation, line endings, and `[file-header]` notice lines
  in the target `.editorconfig`.
- **Output out of the source tree:** Do not write build artifacts into the
  source tree. Direct all build output to `<build>/docs/`.
- **Permanent IDs:** Assign IDs with the suffix style in
  `.docs-traceability-setup.yml` (`slug` or fixed-width zero-padded `number`).
  Do not reuse or rename an ID. Retire items by changing their status.

## Workflow

1. **Examine the repository.** Inspect `<repo>` for:
   - Current `.docs-traceability-setup.yml` and populated keys.
   - Pre-existing project scaffolding or state documents equivalent to the
     impacted traceability files (such as vision, architecture, decision logs,
     conventions, tasks, or roadmap files, plus `AGENTS.md`, `docs/skills/`,
     `docs/agents/`, third-party notices, and scaffolding configs).
   - Languages, build system, `docs/` directory, Sphinx config, `.editorconfig`,
     Python dependency manifest, and test layout.
   - Current traceability IDs (slug or numeric style and digit width), modal
     verb, and in-code tags.
   - Repository URL, copyright holder, and license.
2. **Interview the user and write `.docs-traceability-setup.yml`.** Follow
   [references/configuration.md](references/configuration.md). Present values
   found in step 1 as defaults to accept or change. Collect all missing settings
   (do not silently apply defaults unless the user accepts them), plus
   `[file-header]` notice lines when `checks.file_headers` is `true`. Write
   `.docs-traceability-setup.yml` before you change target files. If the
   repository already has a traceability model or pre-existing project
   scaffolding documents equivalent to the impacted files, follow
   [references/migration.md](references/migration.md) to port and replace the
   existing documents instead of leaving duplicate files.
3. **Write template files from `assets/repo/`.** Copy `assets/repo/` into
   `<repo>` without overwriting unrelated user files (merge required keys or ask
   the user). When pre-existing project scaffolding documents exist (such as
   flat vision, architecture, decision, convention, task, or roadmap files),
   port and replace them with this skill's layered files and update references
   in `AGENTS.md`, `README.md`, and project skills as specified in
   [references/migration.md](references/migration.md). Apply all values from
   `.docs-traceability-setup.yml`, including `id.style` and `id.digits` IDs and
   decision filenames. Rename layer `example.md` templates to `<domain>.md`,
   merge `assets/requirements.txt` into `build.python_manifest`, and update or
   make `.editorconfig`. If you run the workflow again with a complete
   `.docs-traceability-setup.yml`, it skips the interview and changes no files.
4. **Connect the build.** Use `build.cmake_mode` from
   `.docs-traceability-setup.yml`:
   - `subdirectory`: add `add_subdirectory(docs)` and `enable_testing()` to the
     current root `CMakeLists.txt`.
   - `standalone`: configure with `cmake -S docs -B build`. Do not make a root
     `CMakeLists.txt`.
   - Make sure that `build/` and `.venv/` are in `.gitignore`.
5. **Check and fix source text.** After each file edit, run:
   ```bash
   python3 "$SKILL/scripts/check_text.py" --root <repo> --fix <changed files>
   python3 "$SKILL/scripts/check_text.py" --root <repo> <changed files>
   ```
   Resolve all remaining findings (such as replacing `@brief TODO` or wrapping
   long tokens) before you continue. Offer to examine the full repository. Run
   `--fix` on the full repository only with clear user approval.
6. **Build and test.** Run `cmake -B build` (or `cmake -S docs -B build` in
   standalone mode), `cmake --build build`, and `ctest --test-dir build`. All
   steps must complete with no warnings and no errors.
7. **Report.** List all created, merged, or migrated files, include the
   `check_text.py` result for changed files, and show the build and test
   commands.

### Check Mode

When the user asks only to examine source text, skip steps 2, 3, 4, and 6. Run:

```bash
python3 "$SKILL/scripts/check_text.py" --root <repo>
```

Report all findings and run `--fix` only when explicitly requested by the user.

## References

- [references/configuration.md](references/configuration.md):
  `.docs-traceability-setup.yml` schema, interview procedure, and placeholder
  rendering rules (`slug` and `number` modes).
- [references/model.md](references/model.md): layer layout, types, permanent ID
  regexes, SysML v2 links, link matrix, statuses, tags, and record rules.
- [references/authoring.md](references/authoring.md): item document templates,
  MyST/RST syntax, modal verb, `{need}` references, and in-code `need::` tags.
- [references/checks.md](references/checks.md): Sphinx-Needs warnings,
  `need_tag_check`, `check_needs_audit`, and skill `check_text.py` checks.
- [references/migration.md](references/migration.md): step-by-step migration of
  an existing documentation/traceability repository.
