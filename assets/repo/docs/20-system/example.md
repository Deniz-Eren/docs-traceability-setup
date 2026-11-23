# System and Software Requirements — {{DOMAIN}}

Domain `{{DOMAIN}}`: Power supply supervision and threshold monitoring
requirements.

```{sys} Monitor primary power supply
:id: {{SYS_POWER_SUPPLY_ID}}
:status: active

The system {{MODAL_VERB}} continuously monitor primary power supply rails and
report out-of-range conditions.
```

````{swr} Monitor supply voltage bounds
:id: {{SWR_POWER_MONITOR_ID}}
:status: active
:derives: {{SYS_POWER_SUPPLY_ID}}

The supply monitor {{MODAL_VERB}} evaluate sampled rail voltage against
configured lower and upper limits derived from the primary power supply
requirement ({need}`{{SYS_POWER_SUPPLY_ID}}`).

```{swr} Detect low-voltage faults
:id: {{SWR_POWER_LOW_ID}}
:status: active
:derives: {{SWR_POWER_MONITOR_ID}}

The supply monitor {{MODAL_VERB}} raise a low-voltage fault whenever the
measured rail voltage drops below the configured minimum threshold.
```

```{swr} Detect high-voltage faults
:id: {{SWR_POWER_HIGH_ID}}
:status: active
:derives: {{SWR_POWER_MONITOR_ID}}

The supply monitor {{MODAL_VERB}} raise a high-voltage fault whenever the
measured rail voltage exceeds the configured maximum threshold.
```
````
