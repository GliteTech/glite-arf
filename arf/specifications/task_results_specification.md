# Task Results Specification

**Version**: 8

* * *

## Purpose

This specification defines the format, structure, and quality requirements for all files in the
`results/` directory of a task folder. Every completed task must produce these files to enable
cross-task comparison, within-task comparison across variants, aggregation, and human review.

**Producer**: The `results` step of the task execution skill.

**Consumers**:

* **Suggestion subagents** — read results to formulate follow-up suggestions
* **Aggregator scripts** — combine metrics and results across tasks
* **Verificator scripts** — validate structure and completeness
* **Human reviewers** — evaluate task outcomes at checkpoints

* * *

## File Location

```text
tasks/<task_id>/results/
├── results_summary.md
├── results_detailed.md
├── metrics.json
├── costs.json
├── remote_machines_used.json
├── compare_literature.md       # Optional: literature comparison
└── images/                     # Optional: charts and visualizations
```

The `suggestions.json` file also lives in `results/` but is defined in its own specification
(`arf/specifications/suggestions_specification.md`).

The `compare_literature.md` file is optional — produced only when the task includes the
`compare-literature` step (experiment tasks with quantitative results comparable to published work).
See `arf/specifications/compare_literature_specification.md` for the full format.

* * *

## results_summary.md

A brief, scannable summary of the task outcome. A reader should understand what was achieved and the
headline metrics without opening any other file.

### Mandatory Sections

| Section | Description |
| --- | --- |
| `## Summary` | 2-3 sentences describing what was accomplished |
| `## Metrics` | Bullet list of key quantitative results |
| `## Verification` | Which verificators were run and their pass/fail status |

### Quality Criteria

* **Minimum word count**: 80 words total
* The `## Metrics` section must contain at least 3 bullet points with specific numbers (not vague
  qualifiers)
* If `metrics.json` uses explicit variants, summarize the most important comparisons or takeaways in
  `## Metrics` rather than trying to list every variant exhaustively
* The `## Verification` section must list at least one verificator result
* Use `**bold**` for specific quantitative values

### Example

```markdown
# Results Summary: Download SemCor Dataset

## Summary

Downloaded SemCor 3.0 from the Raganato WSD Evaluation Framework and registered
it as a dataset asset. All corpus statistics match published figures exactly:
**226,036** instances, **37,176** sentences, **352** documents, **33,362** unique
sense keys.

## Metrics

* **Instances**: 226,036 (matches [Bejgu2024, Teglia2025])
* **Sentences**: 37,176 (matches [Bejgu2024])
* **Documents**: 352 (matches all sources)
* **Download success**: yes, first attempt
* **Verificator pass rate**: 3/3

## Verification

* `verify_task_file.py` — PASSED (0 errors, 0 warnings)
* `verify_task_dependencies.py` — PASSED (0 errors, 0 warnings)
* `verify_dataset_asset.py` — PASSED (0 errors, 0 warnings)
```

* * *

## results_detailed.md

A comprehensive report of methodology, metrics, analysis, and limitations. This file is the
**exhaustive** result document for the task. A reader should be able to understand the full output
surface, every major finding, and the direct answer to every explicit task requirement without
opening any other file.

Legacy `results_detailed.md` files without frontmatter are treated as `spec_version: "1"`. New files
should include YAML frontmatter and use `spec_version: "2"`.

### YAML Frontmatter

```yaml
---
spec_version: "2"
task_id: "t0016_baseline_wsd_with_bert"
---
```

| Field | Type | Description |
| --- | --- | --- |
| `spec_version` | string | Current detailed-results version is `"2"`; `"1"` is legacy |
| `task_id` | string | Must exactly match the task folder name |

### Mandatory Sections

| Section | Description |
| --- | --- |
| `## Summary` | Overview of what was accomplished (2-5 sentences) |
| `## Methodology` | Machine specs, runtime, timestamps, methods used |
| `## Verification` | Verificator results and integrity checks |
| `## Limitations` | Honest constraints, gaps, and caveats |
| `## Files Created` | Bullet list of all output files with relative paths |
| `## Task Requirement Coverage` | Final requirement-by-requirement answer section |

For legacy `spec_version: "1"` detailed results, `## Task Requirement Coverage` is optional. For
`spec_version: "2"` it is mandatory.

### Recommended Sections

These sections are not required by the verificator but should be included when the task produces
quantitative results:

* `## Metrics Tables` — per-category breakdown with aggregate and stddev
* `## Comparison vs Baselines` — deltas against reference results
* `## Analysis` — interpretation of findings
* `## Visualizations` — embed charts from `images/` using markdown image syntax
  (`![description](images/filename.png)`) so they render on GitHub

### `## Task Requirement Coverage`

This section must be the **final `##` section** in `results_detailed.md`.

It must:

* Quote the operative task request from `task.json` verbatim. Include the task name plus the
  concrete instructions from `short_description` and the resolved long description
  (`long_description` or the markdown file referenced by `long_description_file`).
* Reuse the `REQ-*` IDs from `plan/plan.md` when that plan exists. If no plan exists, derive
  equivalent `REQ-*` IDs directly from `task.json`.
* Enumerate every concrete task requirement separately. Split distinct questions, deliverables,
  analysis dimensions, TODO items, and explicit constraints into separate rows or bullets.
* For each requirement, provide:
  * status: `Done`, `Partial`, or `Not done`
  * direct answer or result, not just a link
  * supporting evidence path(s): file, table, chart, asset, metric, or command output

A requirement may only be marked `Done` if the supporting evidence (files, data, outputs) is
committed and accessible in the repository. Evidence that is gitignored, deleted, or only exists
locally does not count — mark the requirement `Not done`.

This section is where a reviewer should go to answer: "Did this task do every concrete thing the
task description asked for?"

### Quality Criteria

* **Minimum word count**: 200 words total
* The `## Methodology` section must include at least: machine description, total runtime, and
  start/end timestamps
* The `## Files Created` section must list at least one file path
* Every dedicated result artifact must be surfaced in `results_detailed.md` with a short explanation
  of what it contains and why it matters
* If a full result is too long to inline completely, include the key statistics, representative
  rows, or top findings in `results_detailed.md` and then link to the full file with a relative path
* `## Task Requirement Coverage` must directly answer every concrete task requirement
* Use tables for structured numeric data
* Use `**bold**` for specific quantitative values
* Include machine specs, runtime, and timestamps for reproducibility
* When comparing approaches or variants, go beyond aggregate tables:
  * Per-category quantitative breakdown with both absolute values and deltas
  * At least 3 per-instance examples where approaches disagree, showing inputs, outputs, and gold
    labels
  * Error overlap analysis: how many instances each approach gets uniquely right/wrong
* When the task description requests specific content verbatim (e.g., "show the full system
  message", "include the raw response"), reproduce that content in fenced code blocks — never
  summarize content the task asks to be shown in full

### `## Examples` (Mandatory for Experiment Tasks)

The experiment-type classification is driven by `task_types` in `task.json`. The authoritative set
is `EXPERIMENT_TASK_TYPES` in `arf/scripts/verificators/verify_task_results.py` and currently covers
`baseline-evaluation`, `build-model`, `code-reproduction`, `data-analysis`, and `experiment-run`.
`comparative-analysis` is intentionally NOT in the set: it also covers qualitative work such as
paper rankings and literature reviews that produce no new predictions and cannot supply LLM-style
input/output examples. Quantitative comparative experiments should declare an experiment type (for
example `experiment-run`) alongside `comparative-analysis` in `task.json` `task_types` to opt back
into the Examples requirement.

For experiment-type tasks, `results_detailed.md` must include a `## Examples` section. Examples are
primary evidence — they let readers build intuition about what is actually happening. Humans and
LLMs understand patterns better from concrete instances than from abstract summaries.

Include:

* **Random examples** — unbiased sample showing typical behavior
* **Best cases** — where the approach works perfectly, showing what success looks like
* **Worst cases** — failures that reveal the approach's limitations
* **Boundary cases** — near-misses, close calls, ambiguous inputs
* **Contrastive examples** — when comparing approaches, show the same input with different outputs
  side by side

For each example, show full concrete data: actual input, actual output, expected output, and a brief
note on what it illustrates. Use tables or code blocks for readability. Never summarize or
abbreviate example content — the point is to let the reader see exactly what happened.

**For tasks involving LLM calls** (prompting, fine-tuning, inference), examples MUST include:

* The actual system prompt or user message sent to the model (in a fenced code block)
* The actual raw model response (in a fenced code block)
* The parsed/extracted prediction and the gold label
* A note explaining what the example illustrates (success pattern, failure mode, edge case)

A table of word/prediction/correct columns is NOT sufficient for LLM tasks. The reader must be able
to see what the model was asked and how it responded. For prompt comparison tasks, show the same
input with each prompt variant's actual prompt text and response side by side.

**Minimum**: 10 examples across the categories above.

### Example

See `tasks/t0003_download_semcor_dataset/results/results_detailed.md` for a complete example.

* * *

## metrics.json

A JSON object containing **only** project-wide registered metrics defined in `meta/metrics/`. These
are the project-defined quantitative metrics used for cross-task and cross-variant comparison, such
as benchmark quality scores, latency measurements, or efficiency and cost metrics.

**CRITICAL**: This file is NOT for task-specific operational data like corpus sizes, download
statistics, or verificator counts. Task-specific statistics belong in `results_detailed.md` or
dedicated result files (e.g., `results/corpus_stats.json`).

The file supports two formats:

1. **Legacy flat format** — one implicit metrics variant, with registered metric keys at the top
   level.
2. **Explicit variant format** — one or more named variants under a top-level `variants` array.

Use the explicit variant format when one task produces multiple comparable metric sets, for example
for different models, prompts, dataset sizes, hyperparameters, or preprocessing conditions.

### Rules

* The top-level value must be a JSON object (not an array)
* Metric keys must be registered in `meta/metrics/` — unregistered keys are errors
* Metric values must be one of: `int`, `float`, `bool`, `string`, or `null`
* When a measurement is unavailable or not applicable, omit the key or use `null` — do not encode
  missing data as `0`, `0.0`, or `""`
* An empty object `{}` is valid when the task did not measure any registered metrics (e.g., dataset
  download tasks, infrastructure tasks)
* `{"variants": []}` is invalid — use `{}` when no registered metrics were measured
* Metrics-specific structure validation is handled by `verify_task_metrics.py`

### Legacy Flat Format

The legacy flat format is a single JSON object whose keys are registered metric keys.

Additional rules:

* All top-level keys are metric keys
* Top-level values must be scalar-or-null
* No nested objects or arrays are allowed

### Explicit Variant Format

The explicit variant format uses this shape:

```json
{
  "variants": [
    {
      "variant_id": "my-variant",
      "label": "My Variant",
      "dimensions": {
        "model": "model-a",
        "prompt": "prompt-b"
      },
      "metrics": {
        "f1_all": 82.3
      }
    }
  ]
}
```

Each variant represents one comparable condition within the task. The framework does **not** declare
one variant to be the canonical headline result. Human-authored summaries and analyses decide which
comparisons matter most.

#### Variant Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `variant_id` | string | yes | Stable task-local identifier for the variant |
| `label` | string | yes | Human-readable display name |
| `dimensions` | object | yes | Flat map describing what differs for this variant |
| `metrics` | object | yes | Flat map of registered metric keys to scalar-or-null values |

Additional rules:

* `variant_id` must be unique within the file
* `variant_id` must be a non-empty lowercase slug using letters, digits, `.`, `_`, and `-`
* `dimensions` values must be scalar-or-null
* `dimensions` keys should use `snake_case`
* `metrics` keys must be registered metric keys
* `metrics` values must be scalar-or-null

### Example (legacy flat format)

```json
{
  "f1_all": 82.3,
  "accuracy_se13": 76.2,
  "efficiency_training_time_seconds": 14400.0,
  "efficiency_inference_time_per_item_seconds": 0.42,
  "efficiency_inference_cost_per_item_usd": 0.0031
}
```

### Example (explicit variants format)

```json
{
  "variants": [
    {
      "variant_id": "model-a_prompt-short",
      "label": "Model A + short prompt",
      "dimensions": {
        "model": "model-a",
        "prompt": "short",
        "train_size": 1000
      },
      "metrics": {
        "f1_all": 82.3,
        "accuracy_all": 82.3,
        "efficiency_inference_cost_per_item_usd": 0.0031
      }
    },
    {
      "variant_id": "model-a_prompt-cot",
      "label": "Model A + chain-of-thought prompt",
      "dimensions": {
        "model": "model-a",
        "prompt": "cot",
        "train_size": 1000
      },
      "metrics": {
        "f1_all": 82.9,
        "accuracy_all": 82.9,
        "efficiency_inference_cost_per_item_usd": 0.0088
      }
    }
  ]
}
```

### Example (no registered metrics)

```json
{}
```

* * *

## costs.json

A JSON object tracking all third-party costs incurred by the task. Every task must produce this
file, even if all costs are zero.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `total_cost_usd` | float | yes | Total cost in US dollars |
| `breakdown` | object | yes | Map of cost category to either a USD amount or a rich object with `cost_usd` plus optional metadata |
| `services` | object | no | Optional map of paid service slug to total USD spend for that service |
| `budget_limit` | float | no | Optional task-specific spending cap used during execution |
| `note` | string | no | Optional explanation of unusual spend, overruns, or caveats |

### Rules

* `total_cost_usd` must be a non-negative number
* `breakdown` may be empty `{}` when `total_cost_usd` is `0`
* Cost categories in `breakdown` should be descriptive (e.g., `"claude-opus"`, `"vast-ai-gpu"`,
  `"semantic-scholar-api"`)
* Each `breakdown` value may be either:
  * a non-negative number, or
  * a JSON object containing a non-negative numeric `cost_usd` field plus optional metadata such as
    `description`, `tokens`, or `model`
* `total_cost_usd` must equal the sum of all numeric `breakdown` values and/or nested `cost_usd`
  values
* When present, `services` must be a JSON object whose values are non-negative numbers
* When present, `budget_limit` must be a non-negative number
* When present, `note` must be a string
* `note` is optional free text for human review; it must not replace structured cost data

### Example (zero cost)

```json
{
  "total_cost_usd": 0,
  "breakdown": {}
}
```

### Example (with costs)

```json
{
  "total_cost_usd": 14.25,
  "breakdown": {
    "claude-opus": 8.50,
    "claude-haiku": 3.75,
    "vast-ai-a100": 2.00
  }
}
```

### Example (with rich breakdown entries)

```json
{
  "total_cost_usd": 34.43,
  "breakdown": {
    "prompt_a_rich_zero_shot": {
      "description": "Full eval with gpt-5-mini",
      "cost_usd": 9.52
    },
    "prompt_b_cot_context": {
      "description": "Full eval with chain-of-thought context analysis",
      "cost_usd": 24.91
    }
  },
  "services": {
    "openai_api": 34.43
  },
  "budget_limit": 45.0,
  "note": "Prompt-heavy evaluation used more output tokens than the dry-run estimate."
}
```

* * *

## remote_machines_used.json

A JSON array listing all remote machines used during task execution. Every task must produce this
file, even if no remote machines were used.

### Fields (per machine object)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `provider` | string | yes | Cloud provider (e.g., `"vast.ai"`, `"lambda"`) |
| `machine_id` | string | yes | Provider-specific machine identifier |
| `gpu` | string | yes | GPU model (e.g., `"A100-80GB"`) |
| `gpu_count` | int | yes | Number of GPUs |
| `ram_gb` | int | yes | Total RAM in gigabytes |
| `duration_hours` | float | yes | Total usage duration in hours |
| `cost_usd` | float | yes | Total cost for this machine in USD |

### Rules

* The top-level value must be a JSON array
* Use an empty array `[]` when no remote machines were used
* Each element must be a JSON object with all required fields

### Example (no machines)

```json
[]
```

### Example (with machines)

```json
[
  {
    "provider": "vast.ai",
    "machine_id": "instance-12345",
    "gpu": "A100-80GB",
    "gpu_count": 1,
    "ram_gb": 64,
    "duration_hours": 2.5,
    "cost_usd": 2.00
  }
]
```

* * *

## images/ (optional)

An optional subdirectory for charts, graphs, and other visualizations.

### Rules

* All image files must be **embedded** in `results_detailed.md` using markdown image syntax:
  `![description](images/filename.png)`. Do not just list file names as text — embed them so they
  render visually on GitHub.
* Use descriptive `snake_case` file names (e.g., `f1_by_pos.png`, `cost_vs_quality.png`)
* Accepted formats: `.png`, `.svg`, `.jpg`
* Include axis labels, titles, and legends in all charts

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `TR-E001` | `results_summary.md` does not exist |
| `TR-E002` | `results_detailed.md` does not exist |
| `TR-E003` | `metrics.json` does not exist or is not valid JSON |
| `TR-E004` | `costs.json` does not exist or is not valid JSON |
| `TR-E005` | `remote_machines_used.json` does not exist or is not valid JSON |
| `TR-E006` | `results_summary.md` is missing a mandatory section |
| `TR-E007` | `results_detailed.md` is missing a mandatory section |
| `TR-E008` | `metrics.json` top-level value is not a JSON object |
| `TR-E009` | *(Removed in v2 — empty `{}` is valid for tasks with no registered metrics)* |
| `TR-E010` | `metrics.json` uses an invalid metric payload shape |
| `TR-E011` | `costs.json` is missing `total_cost_usd` or `breakdown` |
| `TR-E012` | `costs.json` `breakdown` is not a JSON object, or a breakdown entry is invalid |
| `TR-E013` | `remote_machines_used.json` top-level value is not a JSON array |
| `TR-E014` | A machine entry in `remote_machines_used.json` is missing a required field |
| `TR-E015` | `costs.json` `total_cost_usd` is not a non-negative number |
| `TR-E016` | `costs.json` `services` is not a JSON object of non-negative numbers |
| `TR-E017` | `costs.json` `budget_limit` is not a non-negative number |
| `TR-E018` | `costs.json` `note` is not a string |
| `TR-E019` | `results_detailed.md` `spec_version` is not a recognized value (`"1"` or `"2"`) |

For `TR-E007`, the mandatory section set depends on `results_detailed.md` `spec_version`: legacy `1`
files use the older section set, while `2` files must include `## Task Requirement Coverage`.

### Warnings

| Code | Description |
| --- | --- |
| `TR-W001` | `results_summary.md` total word count is under 80 |
| `TR-W002` | `results_detailed.md` total word count is under 200 |
| `TR-W003` | `## Metrics` section in `results_summary.md` has fewer than 3 bullet points |
| `TR-W004` | `results/images/` directory does not exist |
| `TR-W005` | `costs.json` `total_cost_usd` does not match sum of `breakdown` values |
| `TR-W006` | A `metrics.json` metric or dimension key is not `snake_case` |
| `TR-W007` | `## Verification` section in `results_summary.md` mentions no verificator results |
| `TR-W008` | `## Files Created` section in `results_detailed.md` lists no file paths |
| `TR-W009` | *(Promoted to error `TM-E005` in `verify_task_metrics.py` — unregistered metric keys are now errors)* |
| `TR-W010` | `## Task Requirement Coverage` does not appear to contain `REQ-*` items |
| `TR-W011` | `## Task Requirement Coverage` lacks `Done` / `Partial` / `Not done` labels |
| `TR-W012` | `## Task Requirement Coverage` is not the last `##` section |
| `TR-W013` | `## Examples` section missing in `results_detailed.md` for experiment-type task |
| `TR-W014` | `## Examples` section has fewer than 10 bullet points |
