# Components — {{DOMAIN}}

Domain `{{DOMAIN}}`: White-box component specifications for supply monitoring.

```{comp} Power monitor evaluator
:id: {{COMP_POWER_MONITOR_ID}}
:status: active
:refines: {{ARC_POWER_MONITOR_ID}}
:satisfies: {{SWR_POWER_MONITOR_ID}}

The power monitor evaluator compares sampled rail voltages against configured
bounds and updates status telemetry for the power monitor subsystem
({need}`{{ARC_POWER_MONITOR_ID}}`).
```
