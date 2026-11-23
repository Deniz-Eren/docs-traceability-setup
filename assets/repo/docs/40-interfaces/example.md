# Interfaces — {{DOMAIN}}

Domain `{{DOMAIN}}`: Status and fault reporting interface contracts.

```{icd} Power status telemetry interface
:id: {{ICD_POWER_STATUS_ID}}
:status: active
:refines: {{ARC_POWER_MONITOR_ID}}
:satisfies: {{SWR_POWER_MONITOR_ID}}

The power status interface publishes rail voltage readings and active fault
flags produced by the power monitor subsystem ({need}`{{ARC_POWER_MONITOR_ID}}`)
to satisfy the supply monitor requirement ({need}`{{SWR_POWER_MONITOR_ID}}`).
```
