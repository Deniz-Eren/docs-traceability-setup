# Architecture — {{DOMAIN}}

Domain `{{DOMAIN}}`: Structural architecture elements for power supply
supervision.

```{arc} Power monitor subsystem
:id: {{ARC_POWER_MONITOR_ID}}
:status: active
:satisfies: {{SWR_POWER_MONITOR_ID}}
:traces: {{ADR_SPHINX_NEEDS_ID}}

The power monitor subsystem encapsulates voltage sampling, threshold evaluation,
and fault reporting to satisfy the supply monitor requirement
({need}`{{SWR_POWER_MONITOR_ID}}`).
```
