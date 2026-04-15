# Suggestions Specification

**Version**: 2

* * *

## Purpose

This specification defines the JSON format for `results/suggestions.json`, which contains follow-up
task proposals generated at the end of each task.

**Producer**: Task agents during the `suggestions` step.

**Consumers**:

* **Task planners** — select which suggestions become new tasks
* **Aggregator scripts** — combine suggestions across tasks for prioritization
* **Human reviewers** — evaluate suggestion quality at checkpoints
* **Verificator scripts** — validate structure and completeness

* * *

## File Location

```text
tasks/<task_id>/results/suggestions.json
```

Every completed task must produce this file. If the task generates no follow-up suggestions, the
file must contain an empty suggestions array.

* * *

## Top-Level Structure

The file is a JSON object with two required fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `suggestions` | list[Suggestion] | yes | Array of suggestion objects (may be empty `[]`) |

* * *

## Suggestion Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Unique ID in format `S-XXXX-NN` (see below) |
| `title` | string | yes | Short human-readable title, max 120 characters |
| `description` | string | yes | Detailed description, 20-1000 characters |
| `kind` | string | yes | Suggestion type (see allowed values below) |
| `priority` | string | yes | Priority level (see allowed values below) |
| `source_task` | string | yes | Task ID that generated this suggestion |
| `source_paper` | string or null | yes | Paper ID that motivated this suggestion, or `null` |
| `categories` | list[string] | yes | Category slugs from `meta/categories/`, may be `[]` |
| `status` | string | no | Lifecycle status (see below); defaults to `"active"` |

* * *

## Field Details

### `id`

Format: `S-XXXX-NN` where:

* `S` is a literal prefix
* `XXXX` is the zero-padded `task_index` from `task.json`
* `NN` is a zero-padded 2-digit sequential number within the task (starting at `01`)

The regex pattern is `^S-\d{4}-\d{2}$`.

Examples: `S-0002-01`, `S-0002-02`, `S-0003-05`

### `kind`

One of:

| Value | When to use |
| --- | --- |
| `experiment` | A research experiment to run or replicate |
| `technique` | A method or approach to implement and test |
| `evaluation` | An evaluation methodology or metric to adopt |
| `dataset` | A dataset to download, create, or augment |
| `library` | A software library or tool to build |

### `priority`

One of: `high`, `medium`, `low`.

### `source_task`

Must exactly match the containing task folder name (e.g., `t0002_recent_papers_survey`).

### `source_paper`

The paper ID (DOI slug or `no-doi_*` format) that motivated this suggestion. Set to `null` if the
suggestion is not derived from a specific paper.

### `categories`

List of category slugs from `meta/categories/`. Each slug must correspond to an existing category
directory. An empty list `[]` is valid when no categories apply.

### `status`

Lifecycle status of the suggestion. Optional; defaults to `"active"` when omitted.

| Value | Description |
| --- | --- |
| `active` | Suggestion is a candidate for future work (default) |
| `rejected` | Suggestion was reviewed and deemed not worth pursuing |

Existing suggestion files without a `status` field are treated as `"active"`.

The `status` field can be set directly in `suggestions.json` when the suggestion is first created,
or it can be overridden via the correction mechanism (see `corrections_specification.md`) for
suggestions in completed task folders.

More generally, downstream correction files may override any structured suggestion field except the
immutable `id`. This keeps completed task folders immutable while still allowing the aggregated
suggestion view to be corrected later.

* * *

## Suggestion Lifecycle

A suggestion has two independent dimensions:

**Status** (`status` field or correction overlay):

* `active` — the suggestion is a candidate for future work
* `rejected` — the suggestion was reviewed and deemed not worth pursuing

**Coverage** (tracked via `source_suggestion` in `task.json`):

* **Open** — no task references this suggestion via `source_suggestion`
* **Closed** — at least one task has `"source_suggestion": "S-XXXX-NN"`

An **actionable** suggestion is one that is both `active` and open. The aggregator's `--uncovered`
flag returns only actionable suggestions, excluding both covered and rejected ones.

Coverage is tracked in `task.json` (see `task_file_specification.md`), not in `suggestions.json`
itself. This is a one-directional link: task points to suggestion. The `suggestions.json` file is
never modified after the task that produced it is completed. Status overrides for completed task
suggestions use the correction mechanism (see `corrections_specification.md`).

Aggregators and overview pages may expose an additional derived field, `date_added`, for
project-level browsing. This value is not stored in `suggestions.json`; it is derived from the
source task timing, using the source task `end_time` when present and falling back to `start_time`
otherwise.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `SG-E001` | File is missing or not valid JSON |
| `SG-E002` | Top-level value is not a JSON object |
| `SG-E003` | Missing `spec_version` field |
| `SG-E004` | Missing or non-array `suggestions` field |
| `SG-E005` | Array element is not a JSON object |
| `SG-E006` | Required field missing in suggestion object |
| `SG-E007` | `id` does not match format `S-XXXX-NN` |
| `SG-E008` | `kind` is not one of the allowed values |
| `SG-E009` | `priority` is not one of the allowed values |
| `SG-E010` | `source_task` does not match the containing task folder name |
| `SG-E011` | Duplicate suggestion `id` within the file |
| `SG-E012` | `categories` is not a list |
| `SG-E013` | `status` is not one of the allowed values |

### Warnings

| Code | Description |
| --- | --- |
| `SG-W001` | `title` exceeds 120 characters |
| `SG-W002` | `description` is under 20 characters |
| `SG-W003` | `description` exceeds 1000 characters |
| `SG-W004` | `title` is empty or whitespace-only |
| `SG-W005` | `description` is empty or whitespace-only |
| `SG-W006` | A category slug does not exist in `meta/categories/` |

* * *

## Complete Example

```json
{
  "spec_version": "2",
  "suggestions": [
    {
      "id": "S-0002-01",
      "title": "Replicate SOTA results on standard evaluation benchmarks",
      "description": "Replicate Chen2025's 94.2% benchmark with a 44M-parameter model.",
      "kind": "experiment",
      "priority": "high",
      "source_task": "t0002_recent_papers_survey",
      "source_paper": "10.18653_v1_2025.naacl-long.358",
      "categories": ["evaluation", "transformer-models"]
    },
    {
      "id": "S-0002-02",
      "title": "Download SemCor sense-annotated training corpus",
      "description": "Download SemCor 3.0 for supervised WSD training.",
      "kind": "dataset",
      "priority": "medium",
      "source_task": "t0002_recent_papers_survey",
      "source_paper": null,
      "categories": ["dataset", "supervised-wsd"]
    }
  ]
}
```

The `status` field is optional. When omitted, it defaults to `"active"`. Files with `spec_version`
`"1"` remain valid; all their suggestions are treated as `"active"`.

### Empty Suggestions File

```json
{
  "spec_version": "2",
  "suggestions": []
}
```
