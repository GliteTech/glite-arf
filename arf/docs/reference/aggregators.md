# Aggregators Reference

Aggregators collect data across tasks into unified views. They are exposed under
`arf/scripts/aggregators/` and applied uniformly with `--format` and `--detail` flags. Every
aggregator supports filtering and applies correction overlays from `corrections/` folders.

The six asset-type aggregators (`aggregate_answers`, `aggregate_papers`, `aggregate_datasets`,
`aggregate_libraries`, `aggregate_models`, `aggregate_predictions`) are thin shim modules under
`arf/scripts/aggregators/`. Each shim re-exports the `main` entry point from the real implementation
at `meta/asset_types/<kind>/aggregator.py`, so the asset-type code stays co-located with its
specification while the invocation path stays uniform. Both module paths work; prefer
`arf.scripts.aggregators.*` in scripts and docs.

## All Aggregators

| Script | Source | What It Aggregates |
| --- | --- | --- |
| [`aggregate_answers.py`](../../scripts/aggregators/aggregate_answers.py) | `tasks/*/assets/answer/` | Answer assets with metadata and canonical documents |
| [`aggregate_categories.py`](../../scripts/aggregators/aggregate_categories.py) | `meta/categories/` | Category definitions across the project |
| [`aggregate_costs.py`](../../scripts/aggregators/aggregate_costs.py) | `tasks/*/results/costs.json` | Per-task costs with filtering by status |
| [`aggregate_machines.py`](../../scripts/aggregators/aggregate_machines.py) | `tasks/*/logs/steps/*setup-machines*/machine_log.json` | Remote machine usage, failures, provisioning times, and costs |
| [`aggregate_datasets.py`](../../scripts/aggregators/aggregate_datasets.py) | `tasks/*/assets/dataset/` | Dataset assets with metadata and descriptions |
| [`aggregate_libraries.py`](../../scripts/aggregators/aggregate_libraries.py) | `tasks/*/assets/library/` | Library assets with metadata and descriptions |
| [`aggregate_metric_results.py`](../../scripts/aggregators/aggregate_metric_results.py) | `tasks/*/results/metrics.json` | Metric values across all tasks |
| [`aggregate_metrics.py`](../../scripts/aggregators/aggregate_metrics.py) | `meta/metrics/` | Registered metric definitions |
| [`aggregate_models.py`](../../scripts/aggregators/aggregate_models.py) | `tasks/*/assets/model/` | Model assets with metadata and descriptions |
| [`aggregate_papers.py`](../../scripts/aggregators/aggregate_papers.py) | `tasks/*/assets/paper/` | Paper assets with metadata and summaries |
| [`aggregate_predictions.py`](../../scripts/aggregators/aggregate_predictions.py) | `tasks/*/assets/predictions/` | Predictions assets with metadata and descriptions |
| [`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py) | `tasks/*/results/suggestions.json` | Follow-up task suggestions across all tasks |
| [`aggregate_task_types.py`](../../scripts/aggregators/aggregate_task_types.py) | `meta/task_types/` | Task type definitions |
| [`aggregate_tasks.py`](../../scripts/aggregators/aggregate_tasks.py) | `tasks/*/task.json` | All tasks with status and metadata |

## Common Flags

Supported by every aggregator (`--format`) or nearly every aggregator (`--detail`):

| Flag | Purpose |
| --- | --- |
| `--format {json,markdown,ids}` | Output format (default: json). Supported by all aggregators. |
| `--detail {short,full}` | Detail level (default: short). Supported by all aggregators except `aggregate_categories.py` and `aggregate_task_types.py`. |

Flag values are space-separated lists (`nargs="+"`), never comma-separated. Example:

```bash
uv run python -m arf.scripts.aggregators.aggregate_papers \
    --categories supervised-wsd wsd-evaluation \
    --ids 10.18653_v1_E17-1010 10.18653_v1_N19-1235
```

## Asset-Filter Flags

`--categories` and `--ids` come from `arf/scripts/aggregators/common/cli.py` and are wired in only
by the asset aggregators below. Other aggregators do not accept them.

| Flag | Purpose | Supported by |
| --- | --- | --- |
| `--categories <slug> [<slug> ...]` | Filter by category slugs (match ANY) | `aggregate_answers.py`, `aggregate_datasets.py`, `aggregate_libraries.py`, `aggregate_models.py`, `aggregate_papers.py`, `aggregate_predictions.py` |
| `--ids <id> [<id> ...]` | Filter by asset IDs (exact match) | `aggregate_answers.py`, `aggregate_datasets.py`, `aggregate_libraries.py`, `aggregate_models.py`, `aggregate_papers.py`, `aggregate_predictions.py` |

## Aggregator-Specific Flags

| Aggregator | Flag | Purpose |
| --- | --- | --- |
| [`aggregate_metric_results.py`](../../scripts/aggregators/aggregate_metric_results.py) | `--task-ids <id> [<id> ...]` | Filter by producing task ID |
| [`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py) | `--kind {experiment,technique,evaluation,dataset,library}` | Filter by suggestion kind |
| [`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py) | `--priority {high,medium,low}` | Filter by priority |
| [`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py) | `--uncovered` | Show only suggestions not yet covered by a task |
| [`aggregate_suggestions.py`](../../scripts/aggregators/aggregate_suggestions.py) | `--include-rejected` | Include rejected suggestions |
| [`aggregate_costs.py`](../../scripts/aggregators/aggregate_costs.py) | `--status <status>` | Filter by task status |
| [`aggregate_metric_results.py`](../../scripts/aggregators/aggregate_metric_results.py) | `--metric-keys <key1,key2,...>` | Filter by metric key |
| [`aggregate_tasks.py`](../../scripts/aggregators/aggregate_tasks.py) | `--has-dependency <task_id>` | Filter to tasks depending on the given task |
| [`aggregate_tasks.py`](../../scripts/aggregators/aggregate_tasks.py) | `--task-type <slug>` | Filter by task type |
| [`aggregate_tasks.py`](../../scripts/aggregators/aggregate_tasks.py) | `--source-suggestion <id>` | Filter by source suggestion |
| [`aggregate_metrics.py`](../../scripts/aggregators/aggregate_metrics.py) | `--unit <unit>` | Filter by metric unit |
| [`aggregate_tasks.py`](../../scripts/aggregators/aggregate_tasks.py) | `--status <status>` | Filter by task status |

## Running an Aggregator

```bash
uv run python -m arf.scripts.aggregators.<script_name> [flags]
```

## Common Scenarios

### How much have I spent, and on what?

```bash
uv run python -m arf.scripts.aggregators.aggregate_costs --detail full
```

Total project spend, broken down by task and by service. The first thing to check before launching a
new expensive experiment.

### How reliable is my GPU provisioning?

```bash
uv run python -m arf.scripts.aggregators.aggregate_machines --format markdown --detail full
```

Cross-task machine usage: total machines, failure rate, average provisioning time, cost per GPU
tier, failure reasons breakdown, and wasted cost from failed attempts.

### What did I finish recently?

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks \
    --status completed --format markdown
```

Markdown table of every completed task. Pipe to `less` or paste into a status update.

### What is my best score on the headline metric?

```bash
uv run python -m arf.scripts.aggregators.aggregate_metric_results \
    --metric-keys f1_all --format markdown
```

Every reported value of one metric across the project, with the producing task. Replace `f1_all`
with whatever metric is registered in `meta/metrics/`.

### What should I work on next?

```bash
uv run python -m arf.scripts.aggregators.aggregate_suggestions \
    --kind experiment --priority high --uncovered
```

High-priority experiment suggestions that no task has picked up yet. The input to brainstorming
sessions and the suggestions chooser.

### What papers do I have on topic X?

```bash
uv run python -m arf.scripts.aggregators.aggregate_papers \
    --categories survey --format markdown --detail full
```

Reading list of papers tagged with a category, with their full summaries. Useful before starting a
research-papers stage on a new task.

### Which tasks are stuck waiting on a human?

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks \
    --status intervention_blocked --format markdown
```

Tasks that paused with an intervention file. These need a person to unblock them: dataset access,
budget override, manual review.

### What downstream work came from one suggestion?

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks \
    --source-suggestion S-0042-03
```

Every task that was created from a specific suggestion. Tracks the path from idea to experiment to
result.
