# How to Use Aggregators

For day-to-day work, humans read project state through the
[overview dashboard](use_the_overview_dashboard.md). Reach for aggregators directly when you need a
one-off query the dashboard does not cover, or when you want machine-readable output to feed into
another script.

## Goal

Query project state by invoking aggregator scripts with filter flags instead of reading task folders
by hand.

## Prerequisites

* A working ARF checkout with at least one completed task
* The aggregator you need: papers, suggestions, costs, metrics, metric-results, tasks, answers,
  datasets, libraries, models, predictions, categories, task-types

## Common Flags

Most asset aggregators share these flags, defined in
[`arf/scripts/aggregators/common/cli.py`](../../scripts/aggregators/common/cli.py):

* `--format {json,markdown,ids}` — output shape (default: `json`)
* `--detail {short,full}` — `short` omits long prose; `full` includes descriptions and summaries
  (default: `short`)
* `--categories cat1 cat2 ...` — filter by category slugs; `nargs="+"`, space-separated
* `--ids id1 id2 ...` — filter by asset or suggestion IDs; `nargs="+"`, space-separated

All list arguments use `nargs="+"` — values are separated by **spaces**, never by commas.

Aggregator-specific flags extend the base set and are NOT common:

* `aggregate_tasks.py` and `aggregate_costs.py` expose `--status`
* `aggregate_metric_results.py` uses `--task-ids` and `--metric-keys` instead of the common `--ids`
* `aggregate_suggestions.py` adds `--kind`, `--priority`, `--source-task`, `--uncovered`,
  `--include-rejected`
* `aggregate_tasks.py` also adds `--has-dependency`, `--source-suggestion`, `--task-type`

Always run a script with `--help` to see its exact flag set.

## Steps

1. Pick the aggregator for the data you want.
2. Run the broadest query first to confirm it works and list available IDs.
3. Narrow with `--ids` or `--categories` (space-separated).
4. Switch `--format` and `--detail` for your consumer.

## Worked Examples

High-priority experiment suggestions not yet covered (via
[`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py)):

```bash
uv run python -m arf.scripts.aggregators.aggregate_suggestions \
    --kind experiment --priority high --uncovered --format markdown
```

Total spend across completed tasks as JSON (via
[`aggregate_costs.py`](../../scripts/aggregators/aggregate_costs.py)):

```bash
uv run python -m arf.scripts.aggregators.aggregate_costs \
    --status completed --format json
```

Markdown reading list of multiple categories of papers (via
[`aggregate_papers.py`](../../scripts/aggregators/aggregate_papers.py)) — note space-separated
category slugs:

```bash
uv run python -m arf.scripts.aggregators.aggregate_papers \
    --categories bi-encoder supervised-wsd --format markdown --detail full
```

Restrict to a specific paper ID set (space-separated):

```bash
uv run python -m arf.scripts.aggregators.aggregate_papers \
    --ids 10.18653_v1_E17-1010 10.18653_v1_2020.acl-main.95 --format markdown
```

Every registered metric result for downstream scripting (via
[`aggregate_metric_results.py`](../../scripts/aggregators/aggregate_metric_results.py)) — note this
script uses `--task-ids`, not `--ids`:

```bash
uv run python -m arf.scripts.aggregators.aggregate_metric_results \
    --metric-keys f1_all --format json
```

## JSON Output Structure

Every aggregator returns a top-level JSON object (never a bare list). The exact keys depend on the
aggregator. Use `data["<key>"]` to access the list — do not iterate the top-level object directly.

| Aggregator | Top-level keys | Item list key | Item fields (short) |
| --- | --- | --- | --- |
| `aggregate_tasks` | `task_count`, `tasks` | `tasks` | `task_id`, `name`, `short_description`, `status`, `task_types`, `dependencies` |
| `aggregate_costs` | `budget`, `summary`, `tasks`, `skipped_tasks` | `tasks` | `task_id`, `total_cost_usd`, `breakdown` |
| `aggregate_task_types` | `task_types` | `task_types` | `task_type_id` (aliased as `slug`), `name`, `optional_steps`, `instruction` |
| `aggregate_suggestions` | `suggestion_count`, `suggestions` | `suggestions` | `id`, `title`, `kind`, `priority`, `source_task`, `categories`, `status` |
| `aggregate_answers` | `answer_count`, `answers` | `answers` | `answer_id`, `question`, `short_title`, `categories`, `confidence` |
| `aggregate_papers` | `paper_count`, `papers` | `papers` | `paper_id`, `title`, `year`, `authors`, `citation_key`, `categories` |
| `aggregate_datasets` | `dataset_count`, `datasets` | `datasets` | `dataset_id`, `name`, `categories`, `created_by_task` |
| `aggregate_libraries` | `library_count`, `libraries` | `libraries` | `library_id`, `name`, `categories`, `created_by_task` |
| `aggregate_models` | `model_count`, `models` | `models` | `model_id`, `name`, `categories`, `created_by_task` |
| `aggregate_predictions` | `prediction_count`, `predictions` | `predictions` | `predictions_id`, `name`, `categories`, `created_by_task` |
| `aggregate_metrics` | `metric_count`, `metrics` | `metrics` | `key`, `name`, `unit`, `higher_is_better` |
| `aggregate_metric_results` | `result_count`, `results` | `results` | `task_id`, `variant_id`, `metric_key`, `value` |
| `aggregate_categories` | `categories` | `categories` | `slug`, `name`, `description` |

**`aggregate_costs` nested structure**: Budget fields are in `data["budget"]` (`total_budget`,
`per_task_default_limit`). Summary fields are in `data["summary"]` (`total_cost_usd`,
`budget_left_usd`, `spent_percent`, `stop_threshold_reached`, `warn_threshold_reached`).

**Aggregators without `--detail`**: `aggregate_task_types` and `aggregate_categories` do not support
`--detail`. Passing it will cause an error.

## Verification

* The aggregator exits with status 0
* Record count matches the filter
* `--format ids` returns only identifiers — pipe into another aggregator's `--ids`

## Pitfalls

* Using commas to separate list values — `--ids a,b,c` becomes one token. Use spaces: `--ids a b c`
* Assuming `--status` exists on every aggregator — it only exists on `aggregate_tasks` and
  `aggregate_costs`
* Assuming `--ids` exists on `aggregate_metric_results` — it uses `--task-ids` instead
* Forgetting `--detail full` when you need descriptions or summaries
* `--categories` and `--ids` together — filters AND, the intersection may be empty

## See Also

* `../reference/aggregators.md`
* `../../scripts/aggregators/`
* `apply_a_correction.md`
