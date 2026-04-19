# How to Add a Metric

## Goal

Register a new metric in [`meta/metrics/`](../../../meta/metrics/) so tasks can report it in
`results/metrics.json`.

## Prerequisites

* A unique `snake_case` metric key (e.g. `f1_all`, `accuracy_se07`)
* The metric's unit and value type
* Read
  [`arf/specifications/metrics_specification.md`](../../specifications/metrics_specification.md)

## Steps

1. Create the folder: `meta/metrics/<metric_key>/`. The folder name is the metric key and must use
   `snake_case`.
2. Create `meta/metrics/<metric_key>/description.json` with these fields:
   * `spec_version` — integer, currently `1`
   * `name` — human-readable display name
   * `description` — what the metric measures, including dataset or scope
   * `unit` — one of `"f1"`, `"accuracy"`, `"precision"`, `"recall"`, `"ratio"`, `"count"`, `"usd"`,
     `"seconds"`, `"bytes"`, `"instances_per_second"`, `"none"`
   * `value_type` — one of `"float"`, `"int"`, `"bool"`, `"string"`
   * `higher_is_better` — required boolean. `true` when larger values rank better (F1, accuracy,
     correlation, throughput); `false` when smaller values rank better (MAE, MSE, latency, cost,
     error rate). Required — the framework does not guess a default because silently defaulting
     would mis-rank error-style metrics
   * `datasets` (optional) — list of dataset asset IDs this metric applies to
   * `is_key` (optional bool) — mark headline metrics for leaderboards
   * `emoji` (optional string) — only meaningful when `is_key` is `true`
3. Use
   [`meta/metrics/accuracy_all/description.json`](../../../meta/metrics/accuracy_all/description.json)
   as a reference.
4. Run
   [`uv run python -m arf.scripts.verificators.verify_metrics`](../../scripts/verificators/verify_metrics.py).
5. Reference the metric in any task's `results/metrics.json` using the key.

## Verification

```bash
uv run python -m arf.scripts.verificators.verify_metrics
```

Expected: no errors, new folder listed among validated metrics.

## Pitfalls

* Folder name not `snake_case` — kebab-case or camelCase is rejected
* `unit` written as a long description instead of one of the allowed tokens
* `spec_version` written as a string (`"1"`) instead of an integer (`1`)
* Missing `value_type` or using an unsupported value
* Omitting `higher_is_better` — it is required, not optional; `verify_metrics` raises `MT-E002`
* Setting `higher_is_better` to a non-boolean (e.g. `"yes"`, `1`) — verificator raises `MT-E009`
* Setting `emoji` without also setting `is_key: true`
* Reporting a metric in `metrics.json` before registering it

## See Also

* `../reference/metrics.md`
* `../../specifications/metrics_specification.md`
