# Daily News Specification

**Version**: 2

* * *

## Purpose

This specification defines the format for daily project news files: a markdown summary and a
structured JSON companion. Each day's activity is captured in a pair of files under the top-level
`news/` directory.

**Producer**: The `generate-daily-news` skill.

**Consumers**:

* **Project maintainers** — daily review of progress and costs
* **Verificator scripts** — validate structure and completeness

* * *

## File Location

```text
news/<date>.md
news/<date>.json
```

`<date>` is an ISO 8601 date string in `YYYY-MM-DD` format (e.g., `2026-04-05`). Both files must
exist for a given date.

* * *

## Markdown File Format

### Structure

The file must NOT begin with a `#` heading. It starts with a `##` heading containing the date in
human-readable format:

```markdown
## April 5, 2026
```

The date in the heading must correspond to the filename date. Accepted formats: `Month D, YYYY` or
`Month DD, YYYY` (e.g., `April 5, 2026` or `April 05, 2026`).

The file body uses `##` section headings and `###` subsections for individual findings.

**Required `##` sections:**

* A numbered findings heading (e.g., `## Eight things we learned`, `## Two things we fixed`)
* `## Where we stand` — a table of current best results, ending with a gap-to-goal line
* `## Costs` — a spending breakdown table with day total, project total, and budget remaining

**Recommended `##` sections** (warn if missing):

* `## Key papers added` — summaries of the most important papers added on this date, with links to
  their full summaries
* `## Key questions answered` — summaries of the most important research questions answered, with
  links to full answer documents

**Individual findings** use `###` headings (e.g., `### 1. Prompt design doesn't matter.`). Each
finding must include: what was learned, key numbers with `**bold**` formatting, and planned
follow-up with task ID in parentheses.

### Links

The markdown file should link extensively to overview pages:

* **Tasks** link to `overview/tasks/task_pages/<task_id>.md`
* **Metrics and numbers** link to `overview/metrics-results/<metric_key>.md`
* **Datasets** link to `overview/datasets/README.md`
* **Models** link to `overview/models/README.md`
* **Suggestions** link to `overview/suggestions/README.md`
* **Papers** link to their summary documents
* **Answers** link to their full answer documents

Link text should be descriptive prose, not task IDs. Task IDs may appear in parentheses after
descriptive link text for follow-up references (e.g., "(t0082)").

### Charts

The file should embed 2-3 key charts from the day's completed tasks using standard markdown image
syntax: `![description](../tasks/<task_id>/results/images/<filename>.png)`.

### Writing Style

The daily news uses a direct, punchy writing style:

* **Short sentences.** Lead with the point. No filler, no hedging, no academic tone.
* **Bold for key numbers** — `**83.4 F1**`, `**$125**`, `**+0.4 F1**`.
* **Short-long-short paragraph rhythm.** A quick hook, then explanation, then a one-liner to land
  the point.
* **Rhetorical questions** where they sharpen the argument.
* **Bullet lists** for concrete data points. **Tables** for comparisons.
* **No trailing summaries.** The reader can read.

* * *

## JSON File Format

### Top-Level Structure

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (`"2"`) |
| `date` | string | yes | ISO date (`YYYY-MM-DD`), must match filename |
| `tasks_completed` | list[TaskCompleted] | yes | Tasks completed on this date (may be `[]`) |
| `tasks_created` | list[TaskCreated] | yes | Tasks created on this date (may be `[]`) |
| `tasks_cancelled` | list[TaskCancelled] | yes | Tasks cancelled on this date (may be `[]`) |
| `total_cost_usd` | float | yes | Total spend for the day |
| `assets_added` | integer | yes | Count of new assets added |
| `papers_added` | integer | yes | Count of new paper assets added |
| `infrastructure_changes` | list[string] | yes | Brief descriptions (may be `[]`) |
| `current_best_results` | list[BestResult] | yes | Leaderboard snapshot (may be `[]`) |
| `key_findings` | list[string] | yes | One-sentence summaries (may be `[]`) |

### TaskCompleted Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | string | yes | Task folder name (e.g., `t0065_multi_sentence_context_bem`) |
| `name` | string | yes | Human-readable task name |
| `cost_usd` | float | yes | Total cost of this task |
| `key_finding` | string | yes | One-sentence summary of the main result |

### TaskCreated Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | string | yes | Task folder name |
| `name` | string | yes | Human-readable task name |
| `reason` | string | yes | Why this task was created |

### TaskCancelled Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | string | yes | Task folder name |
| `reason` | string | yes | Why this task was cancelled |

### BestResult Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `system` | string | yes | System or model name |
| `f1` | float | yes | F1 score |
| `type` | string | yes | System type (e.g., `"fine-tuned"`, `"LLM zero-shot"`) |

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `DN-E001` | `.json` file is missing or not valid JSON |
| `DN-E002` | `.json` top-level value is not a JSON object |
| `DN-E003` | Missing `spec_version` field in JSON |
| `DN-E004` | Missing `date` field in JSON |
| `DN-E005` | `date` does not match ISO format or does not match filename date |
| `DN-E006` | Missing required JSON field |
| `DN-E007` | A required JSON field has wrong type |
| `DN-E008` | `tasks_completed` element missing required sub-field |
| `DN-E009` | `tasks_created` element missing required sub-field |
| `DN-E010` | `tasks_cancelled` element missing required sub-field |
| `DN-E011` | `.md` file is missing or not readable |
| `DN-E012` | `.md` file starts with `# ` heading (must start with `## <date>`) |
| `DN-E013` | `.md` file first `## ` heading does not contain a date matching the filename |
| `DN-E014` | `.md` file missing `## Where we stand` section |
| `DN-E015` | `.md` file missing `## Costs` section |
| `DN-E016` | `total_cost_usd` is not a number |
| `DN-E017` | `current_best_results` element missing required sub-field |
| `DN-E018` | News file is not committed to git |
| `DN-E019` | News file is not pushed to remote |

### Warnings

| Code | Description |
| --- | --- |
| `DN-W001` | `.md` file has no numbered findings heading |
| `DN-W002` | `key_findings` list is empty |
| `DN-W003` | `total_cost_usd` is zero |
| `DN-W004` | `.md` file is under 200 characters |
| `DN-W005` | `.md` file exceeds 10000 characters |
| `DN-W006` | `.md` file has no embedded images |
| `DN-W007` | `.md` file has fewer than 5 markdown links |
| `DN-W008` | `.md` file missing `## Key papers added` section |
| `DN-W009` | `.md` file missing `## Key questions answered` section |

* * *

## Complete Example

### JSON File (`news/2026-04-05.json`)

```json
{
  "spec_version": "2",
  "date": "2026-04-05",
  "tasks_completed": [
    {
      "task_id": "t0065_multi_sentence_context_bem",
      "name": "Multi-sentence context for BEM",
      "cost_usd": 0.22,
      "key_finding": "Adding one surrounding sentence gives +0.4 F1; more context causes truncation collapse"
    }
  ],
  "tasks_created": [
    {
      "task_id": "t0082_retrain_bem_preceding_context",
      "name": "Retrain BEM with preceding-sentence context",
      "reason": "Inference-only context injection limited by train-test mismatch"
    }
  ],
  "tasks_cancelled": [
    {
      "task_id": "t0067_multi_sentence_context_consec",
      "reason": "Superseded by retrain-from-scratch task t0084"
    }
  ],
  "total_cost_usd": 153.66,
  "assets_added": 9,
  "papers_added": 7,
  "infrastructure_changes": [
    "Added verificator and aggregator test coverage"
  ],
  "current_best_results": [
    {
      "system": "SANDWiCH",
      "f1": 87.4,
      "type": "fine-tuned"
    }
  ],
  "key_findings": [
    "Prompt design doesn't matter for WSD; reasoning effort level drives the gap"
  ]
}
```

### Markdown File (`news/2026-04-05.md`)

```markdown
## April 5, 2026

**7 tasks completed. ~$154 spent.**

## Three things we learned

### 1. Prompt design doesn't matter. Reasoning effort does.

Under [controlled conditions](../overview/tasks/task_pages/t0061.md):

* Prompt C: [**82.8 F1**](../overview/metrics-results/f1_all.md)
* Best variant: [**83.4 F1**](../overview/metrics-results/f1_all.md)

Next: [diagnosing the interaction](../overview/tasks/task_pages/t0081.md) (t0081).

![Cost vs Quality](../tasks/t0061/results/images/cost_vs_f1.png)

## Where we stand

| System | [F1 ALL](../overview/metrics-results/f1_all.md) |
|--------|------|
| [SANDWiCH](../overview/models/README.md) | [**87.4**](../overview/metrics-results/f1_all.md) |

Gap to SOTA: **4 F1 points**. Next bet: retrain-with-context.

## Costs

| What | Cost |
|------|------|
| [Prompt ablation](../overview/tasks/task_pages/t0061.md) (OpenAI) | $125 |
| **Day total** | **~$154** |
| **Project total** | **~$500** |
| **Budget remaining** | **~$1,500** |

## Key papers added

**[Paper Title](../tasks/t0061/assets/paper/doi_slug/summary.md)**
(Author, Year). Why this paper matters for the project.

## Key questions answered

**[What is the F1 ceiling?](../tasks/t0063/assets/answer/id/full_answer.md)**
Summary of the answer in 2-3 sentences.
```
