# {{ADR_SPHINX_NEEDS_ID}} — Adopt Sphinx-Needs for Docs-as-Code Traceability

```{adr} Adopt Sphinx-Needs for docs-as-code traceability
:id: {{ADR_SPHINX_NEEDS_ID}}
:status: accepted

## Context

Engineering specifications, architecture decisions, and verification items must
stay synchronized with source code and tests in version control without manual
cross-reference tables.

## Decision

Use Sphinx, MyST-Parser, and Sphinx-Needs configured from
`.docs-traceability-setup.yml` to validate all traceability links, statuses,
tags, and code references during the default CMake build.

## Rejected alternatives

- Maintaining traceability matrices manually in Markdown tables or spreadsheets.
- Storing requirements in an external proprietary tool outside Git.

## Consequences

- Every item is authored once and views are generated automatically.
- Builds remain out-of-source under `<build>/docs/` with warnings as errors.
```
