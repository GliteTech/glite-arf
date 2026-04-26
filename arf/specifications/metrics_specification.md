# Metrics Specification

**Version**: 5

* * *

## Purpose

This specification defines the format for metric definitions in the project-wide metrics registry.
Registered metrics are project-defined quantitative measurements used for cross-task comparison,
cross-variant comparison within a task, and reporting. They are distinct from task-specific
operational data (like `papers_imported` or `download_size_bytes`) that belongs in
`results_detailed.md` or dedicated result files rather than task `metrics.json`.

**Producer**: Human researchers or AI agents when a new project metric needs tracking.

**Consumers**:

* **Task subagents** — reference registered metric keys when writing `metrics.json`
* **Verificator scripts** — reject `metrics.json` files that contain unregistered keys
* **Aggregator scripts** — `aggregate_metrics.py` lists all registered metric definitions; other
  aggregators collect metric values across tasks for comparison
* **Human reviewers** — understand what each metric measures

* * *

## Registry Structure

Each metric is a JSON file in `meta/metrics/`:

```text
meta/metrics/<metric_key>/
└── description.json    # Metric metadata (required)
```

The folder name is the metric key — the same string that appears either as a top-level key in a
legacy flat task `metrics.json` file or inside a variant `metrics` object in the explicit
multi-variant format. All metric keys use `snake_case`.

* * *

## Metric Key Naming Conventions

Metric keys must use `snake_case` and should be stable over time. Prefer descriptive, namespace-like
prefixes so related metrics stay grouped in aggregators and task outputs.

Recommended patterns:

| Pattern | Meaning |
| --- | --- |
| `f1_<subset>` | F1 score for a named subset or benchmark |
| `accuracy_<subset>` | Accuracy for a named subset or benchmark |
| `efficiency_<measurement>` | Efficiency or latency measurement |
| `cost_<scope>` | Cost measurement at a defined scope |

When the meaning would otherwise be ambiguous, include the unit or scope directly in the key, such
as `_seconds`, `_usd`, `_per_item`, or a dataset/subset suffix.

* * *

## Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | int | yes | Specification version (`1`) |
| `name` | string | yes | Human-readable display name |
| `description` | string | yes | What this metric measures, including dataset or scope details |
| `unit` | string | yes | Unit of measurement (see allowed values) |
| `value_type` | string | yes | JSON value type (see allowed values) |
| `higher_is_better` | bool | yes | Direction of improvement. `true` when numerically larger values rank better (F1, accuracy, correlation, throughput); `false` when smaller values rank better (MAE, MSE, latency, cost, error rate). Required — there is no default because silently defaulting to `true` would mis-rank error-style metrics |
| `datasets` | list[string] | no | Dataset asset IDs this metric applies to (must exist in task assets) |
| `is_key` | bool | no | Whether this is a key/headline metric for project leaderboards. Defaults to `false` when absent |
| `emoji` | string | no | Single emoji character displayed alongside this metric in overviews. Only meaningful when `is_key` is `true` |

### Allowed `unit` values

`"f1"`, `"accuracy"`, `"precision"`, `"recall"`, `"ratio"`, `"count"`, `"usd"`, `"seconds"`,
`"bytes"`, `"instances_per_second"`, `"none"`

### Allowed `value_type` values

`"float"`, `"int"`, `"bool"`, `"string"`

* * *

## Example

```json
{
  "spec_version": 1,
  "name": "Training Time",
  "description": "Total wall-clock training or fine-tuning time for the primary model or system produced by a task, measured in seconds.",
  "unit": "seconds",
  "value_type": "float",
  "higher_is_better": false
}
```

* * *

## Key Metrics

Metrics marked with `"is_key": true` are headline metrics shown prominently:

* On the dashboard leaderboard (top 10 results per key metric)
* On task detail cards for completed tasks that produced key metric values
* At the top of the metrics results overview page

The `emoji` field provides a visual prefix for key metrics in overviews (e.g., `"\u2b50"` for a
star). It is only meaningful when `is_key` is `true`.

* * *

## Relationship to Task metrics.json

Task `metrics.json` files may use either the legacy flat format or the explicit multi-variant format
described in `arf/specifications/task_results_specification.md`.

In both formats, metric keys must **only** come from `meta/metrics/`. Unregistered keys are
verification errors. Tasks that do not measure any registered metrics (e.g., dataset downloads,
infrastructure) must write an empty object `{}`.

Registered metrics may describe quality, efficiency, cost, latency, throughput, or any other
project-defined quantity that benefits from comparison across tasks or across variants within a
task. Task-specific operational data (corpus sizes, download stats, verificator counts) belongs in
`results_detailed.md` or dedicated result files, not in `metrics.json`.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `MT-E001` | Metric definition file is missing or not valid JSON |
| `MT-E002` | Required field missing |
| `MT-E003` | `spec_version` is not an integer |
| `MT-E004` | `unit` is not one of the allowed values |
| `MT-E005` | `value_type` is not one of the allowed values |
| `MT-E006` | File name does not match `snake_case` pattern |
| `MT-E007` | `datasets` is not a list of strings |
| `MT-E008` | A dataset ID in `datasets` does not exist in any task's `assets/dataset/` |
| `MT-E009` | `higher_is_better` is present but not a boolean |

### Warnings

| Code | Description |
| --- | --- |
| `MT-W001` | `description` is under 20 characters |
| `MT-W002` | `name` exceeds 80 characters |
| `MT-W003` | `is_key` is present but not a boolean |
| `MT-W004` | `emoji` is present but not a string |
| `MT-W005` | `emoji` is present but `is_key` is not `true` |
