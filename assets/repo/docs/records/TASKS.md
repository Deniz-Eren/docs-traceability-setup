# Tasks

## Purpose

Track active, temporary engineering tasks (`task`) for `{{PROJECT_NAME}}`.

## Structure

Tasks are ordered with the highest priority first and link into the normative
model through `:traces:`.

## Formatting Rules

- Normative specifications and records must never link to `TSK_` items.
- Move completed or cancelled tasks verbatim into [HISTORY.md](HISTORY.md) with
  status `done` or `cancelled`.

```{needtable} All tasks
:types: task
:filter: docname == 'records/TASKS'
:columns: id; title; status; traces as "Traces to"; traces_back as "Traced by"
```

### {{TSK_POWER_MONITOR_ID}} — Implement power supply voltage monitor

```{task} Implement power supply voltage monitor
:id: {{TSK_POWER_MONITOR_ID}}
:status: open
:traces: {{SWR_POWER_MONITOR_ID}}

Implement and verify voltage threshold monitoring for the supply monitor
requirement ({need}`{{SWR_POWER_MONITOR_ID}}`).
```
