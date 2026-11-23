# {{BDR_MAGIC_LINKS_ID}} — Require End-to-End Traceability Links

```{bdr} Require end-to-end traceability links
:id: {{BDR_MAGIC_LINKS_ID}}
:status: accepted
:drives: {{SYS_POWER_SUPPLY_ID}}

## Context

Stakeholders require auditable proof that every system requirement originates
from an approved business goal and is verified by automated evidence.

## Decision

Every active system requirement is driven by an accepted business decision
record and linked downstream through software requirements, design elements, and
verification items.

## Rejected alternatives

- Maintaining separate spreadsheets for requirements and test coverage.
- Linking code directly to top-level business goals without intermediate specs.

## Consequences

- Coverage tables and back-links are calculated automatically from one model.
- Missing upstream business rationale or downstream tests fail the build.
```
