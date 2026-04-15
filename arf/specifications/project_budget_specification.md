# Project Budget Specification

**Version**: 2

* * *

## Purpose

This specification defines the structure and validation rules for `project/budget.json`. The project
budget file is the authoritative source for total budget, per-task default spending limits, service
allowlists, and warning/stop thresholds used by cost aggregators and task-execution skills.

**Producer**: Human researcher or the `/create-project-description` skill.

**Consumers**:

* **Cost aggregator** — combines task costs with the current project budget
* **Planning skill** — compares estimated spend against remaining budget
* **Remote machine setup skill** — blocks provisioning when budget is exhausted
* **Task execution orchestrator** — checks whether the project can afford new work
* **Verificator scripts** — validate schema and threshold consistency
* **Human reviewers** — review total spend and operational guardrails

* * *

## File Location

```text
project/
└── budget.json    # Project budget configuration (required)
```

* * *

## Required Fields

The file must be a single JSON object with these fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `total_budget` | float | yes | Maximum project spend in the configured currency |
| `currency` | string | yes | ISO 4217 currency code, uppercase (for example `"USD"`) |
| `per_task_default_limit` | float | yes | Default max spend for one task when no task-specific override exists |
| `available_services` | array | yes | List of paid service slugs allowed in cost reporting |
| `alerts` | object | yes | Thresholds that drive warning and stop behavior |

### `alerts`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `warn_at_percent` | int | yes | Percent of `total_budget` that should trigger warnings |
| `stop_at_percent` | int | yes | Percent of `total_budget` that should block new spending |

* * *

## Rules

* `total_budget` must be a non-negative number
* `per_task_default_limit` must be a non-negative number
* `currency` must be a 3-letter uppercase ISO 4217 code
* `available_services` must contain only non-empty strings
* `available_services` must not contain duplicates
* `warn_at_percent` and `stop_at_percent` must be integers between `0` and `100`
* `stop_at_percent` must be greater than or equal to `warn_at_percent`
* `per_task_default_limit` may exceed one task's real need, but if it exceeds `total_budget`, the
  verificator must emit a warning

* * *

## Example

```json
{
  "total_budget": 2000.0,
  "currency": "USD",
  "per_task_default_limit": 100.0,
  "available_services": [
    "openai_api",
    "anthropic_api",
    "vast_ai"
  ],
  "alerts": {
    "warn_at_percent": 80,
    "stop_at_percent": 100
  }
}
```

* * *

## Budget Gate Applicability

The Phase 1 budget gate in `arf/skills/execute-task/SKILL.md` is scoped by task type, not by
project. When the execute-task orchestrator starts a task, it looks up each entry in the task's
`task_types` array via `aggregate_task_types.py` and reads the `has_external_costs` field defined in
`arf/specifications/task_type_specification.md`.

The budget gate applies if **any** listed task type has `has_external_costs: true`. In that case the
orchestrator consults `aggregate_costs.py`, and — if `stop_threshold_reached` is true or
`budget_left_before_stop_usd <= 0` — creates
`tasks/$TASK_ID/intervention/project_budget_exhausted.md` and stops.

The gate is **skipped entirely** when every listed task type has `has_external_costs: false`, or
when `task_types` is empty and the task's fallback inference classifies it as mechanical. A project
with `total_budget: 0.0` must still be able to run download-paper, deduplication, brainstorming,
data-analysis, and other cost-free task types without creating an intervention file on step 1.

Projects that want to override this per-task — for example, forcing a normally cost-free task type
to consult the budget because it will drive an LLM-assisted summarization in practice — should use
the task-specific cost override mechanism, not this spec.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `PB-E001` | `project/budget.json` does not exist |
| `PB-E002` | `project/budget.json` is not readable JSON |
| `PB-E003` | `project/budget.json` top-level value is not a JSON object |
| `PB-E004` | A required field is missing or has the wrong type/value |

### Warnings

| Code | Description |
| --- | --- |
| `PB-W001` | `per_task_default_limit` exceeds `total_budget` |
| `PB-W002` | `available_services` is empty |
