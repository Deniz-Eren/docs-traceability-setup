# Verification — {{DOMAIN}}

Domain `{{DOMAIN}}`: Verification items covering power supply monitoring
requirements.

```{ver} Verify primary power supply supervision
:id: {{VER_POWER_SUPPLY_ID}}
:status: active
:tags: integration
:verifies: {{SYS_POWER_SUPPLY_ID}}

Verified by integration analysis of the primary power supply monitoring chain
({need}`{{SYS_POWER_SUPPLY_ID}}`).
```

```{ver} Verify supply voltage bounds monitoring
:id: {{VER_POWER_MONITOR_ID}}
:status: active
:tags: integration
:verifies: {{SWR_POWER_MONITOR_ID}}

Verified by end-to-end threshold monitoring checks covering the supply monitor
requirement ({need}`{{SWR_POWER_MONITOR_ID}}`).
```

```{ver} Verify low-voltage fault detection
:id: {{VER_POWER_LOW_ID}}
:status: active
:tags: unit
:verifies: {{SWR_POWER_LOW_ID}}

Verified by `CheckNeedsAuditTests` in
`tests/traceability/test_check_needs_audit.py`, confirming low-voltage fault
traceability ({need}`{{SWR_POWER_LOW_ID}}`).
```

```{ver} Verify high-voltage fault detection
:id: {{VER_POWER_HIGH_ID}}
:status: active
:tags: unit
:verifies: {{SWR_POWER_HIGH_ID}}

Verified by `TagScanTests` in `tests/traceability/test_tag_scan.py`, confirming
high-voltage fault traceability ({need}`{{SWR_POWER_HIGH_ID}}`).
```
