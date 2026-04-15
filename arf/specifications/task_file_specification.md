# Task File Specification

**Version**: 4

---

## Purpose

This specification defines the format and requirements for the `task.json` file that describes a
task's identity, scope, status, and dependencies, plus the optional sibling markdown file that
stores the long task description for spec version `4`.

**Producer**: Task creation skill or human operator.

**Consumers**:

* **Task subagents** — read to understand the task objective and constraints
* **Verificator scripts** — validate task metadata and dependency chains
* **Aggregator scripts** — collect task listings and status across the project
* **Human reviewers** — monitor project progress at checkpoints

---

## File Location

```text
tasks/<task_id>/task.json
tasks/<task_id>/<long_description_file>  # Optional in spec_version 4, recommended: task_description.md
```

One file per task. Created when the task folder is initialized. Updated as the task progresses
through its lifecycle.

---

## Task ID

The task ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

* Format: `t<NNNN>_<slug>` where `t` is a literal prefix, `NNNN` is a zero-padded 4-digit integer,
  and `<slug>` is a lowercase underscore-separated description.
* The `t` prefix makes task folder names valid Python identifiers, enabling absolute imports from
  the repo root.
* Only underscores are allowed as separators (no hyphens).
* Task IDs are globally unique and monotonically increasing.
* The `task_id` field in `task.json` must exactly match the folder name.
* Maximum 9999 tasks per project.

### Do:

```text
t0011_build_semcor_loader
t0012_bert_baseline_wsd
t0042_llm_zero_shot_wsd
```

### Don't:

```text
0011_build_semcor_loader  # Missing t prefix
t1-papers                 # Not zero-padded
t0011 build semcor loader # Spaces not allowed
t0003-download-corpus     # Hyphens not allowed
```

---

## Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | int | no | Current version is `4` for new files. Omit only for legacy spec version `3` files. |
| `task_id` | string | yes | Must match the folder name |
| `task_index` | int | yes | Numeric task index (1-9999), must match digits in task_id |
| `name` | string | yes | Human-readable task name (under 80 characters) |
| `short_description` | string | yes | One-sentence summary of the task objective |
| `long_description` | string | conditional | Inline detailed description. Required for legacy spec version `3`. In spec version `4`, use exactly one of this field or `long_description_file`. |
| `long_description_file` | string | conditional | Markdown file name in the task root containing the detailed description. Allowed only in spec version `4`. |
| `status` | string | yes | Current task status (see Status Values below) |
| `dependencies` | list[string] | yes | Task IDs that must complete before this task starts |
| `start_time` | string / null | yes | ISO 8601 UTC timestamp, `null` when not started |
| `end_time` | string / null | yes | ISO 8601 UTC timestamp, `null` when not finished |
| `expected_assets` | object | yes | Map of asset type to expected count |
| `task_types` | list[string] | yes | Task type slugs from `meta/task_types/`, `[]` if unclassified |
| `source_suggestion` | string / null | yes | Suggestion ID this task implements, or `null` |

---

## Status Values

| Status | Description |
| --- | --- |
| `"not_started"` | Task created but work has not begun |
| `"in_progress"` | Task is actively being worked on |
| `"completed"` | Task finished successfully, all assets produced |
| `"cancelled"` | Task was abandoned before completion |
| `"permanently_failed"` | Task failed and will not be retried |
| `"intervention_blocked"` | Task is paused waiting for human intervention |

### Status Transitions

```text
not_started --> in_progress --> completed
                           \-> cancelled
                           \-> permanently_failed
                           \-> intervention_blocked --> in_progress
```

A task may move from `intervention_blocked` back to `in_progress` after the human intervention is
resolved.

---

## Field Details

### `spec_version`

Current task file version is `4`.

Compatibility rules:

* New task files **must** set `"spec_version": 4`.
* Legacy task files may omit `spec_version`; omitted means legacy spec version `3`.
* Supported versions are `3` and `4`.

### `task_index`

An integer from 1 to 9999 representing the task's sequential number. Must match the 4-digit portion
of `task_id` — for `t0003_download_training_corpus`, `task_index` must be `3`. Used for generating
suggestion IDs (`S-XXXX-NN`) and correction IDs (`C-XXXX-NN`), and for display in the overview.

### `short_description`

A single sentence (no more than 200 characters) that captures the task's primary objective. Should
be understandable without reading the long description.

### `long_description`

The resolved long description provides full context: what the task does, why it matters, what it
produces, and any important constraints or scope boundaries.

Storage rules:

* Legacy spec version `3`: `long_description` is required and must be inline text in `task.json`.
* Spec version `4`: set exactly one of `long_description` or `long_description_file`.
* If `long_description_file` is used, aggregators and skills treat the referenced markdown file as
  the task's long description.

### `long_description_file`

Name of a markdown file stored directly in the task root next to `task.json`.

Rules:

* Allowed only in spec version `4`
* Must be a single file name in the task root, not an absolute path or nested path
* Recommended file name: `task_description.md`
* The file content may be any markdown; there is no required internal section structure

### `task_types`

A list of task type slugs from `meta/task_types/`. Each slug must match an existing folder under
`meta/task_types/`. Tasks may have multiple types (e.g., a task that trains a model and evaluates it
could have `["build-model", "baseline-evaluation"]`).

Use an empty list `[]` when the task does not fit any predefined type. Skills treat `task_types` as
a minimum — they may also infer additional types from the task description.

```json
"task_types": ["download-dataset"]
```

### `dependencies`

An array of task IDs (strings) that must have status `"completed"` before this task can start. Empty
array `[]` if no dependencies. All referenced task IDs must exist as task folders.

### `expected_assets`

A JSON object mapping asset type names to expected counts. Asset type names must match subdirectory
names under `assets/` (e.g., `"paper"`, `"dataset"`, `"library"`, `"answer"`). Counts are integers
representing how many assets of that type the task is expected to produce.

```json
"expected_assets": {
  "paper": 10,
  "dataset": 1
}
```

Use an empty object `{}` if the task produces no assets (e.g., a pure research task).

### `source_suggestion`

The suggestion ID (format `S-XXXX-NN`) that this task was created from. Set to `null` when the task
was created manually or is not based on a specific suggestion. When non-null, the referenced
suggestion must exist in some task's `results/suggestions.json`.

```json
"source_suggestion": "S-0002-01"
```

---

## Examples

### Legacy spec version 3 (inline `long_description`)

```json
{
  "task_id": "t0003_download_training_corpus",
  "task_index": 3,
  "name": "Download training corpus",
  "short_description": "Download the annotated training corpus and prepare it as a dataset asset.",
  "long_description": "The annotated training corpus is the primary labeled dataset for supervised experiments in this project. It contains 226,000 labeled instances across 352 documents. This task downloads the corpus, verifies its integrity via SHA-256 checksums, documents its structure and statistics, and registers it as a dataset asset.",
  "task_types": ["download-dataset"],
  "status": "not_started",
  "dependencies": [
    "t0001_initial_literature_survey"
  ],
  "start_time": null,
  "end_time": null,
  "expected_assets": {
    "dataset": 1
  },
  "source_suggestion": "S-0001-03"
}
```

### Spec version 4 (`long_description_file`)

`task.json`:

```json
{
  "spec_version": 4,
  "task_id": "t0004_download_training_corpus",
  "task_index": 4,
  "name": "Download training corpus",
  "short_description": "Download the annotated training corpus and prepare it as a dataset asset.",
  "long_description_file": "task_description.md",
  "task_types": ["download-dataset"],
  "status": "not_started",
  "dependencies": [
    "t0001_initial_literature_survey"
  ],
  "start_time": null,
  "end_time": null,
  "expected_assets": {
    "dataset": 1
  },
  "source_suggestion": "S-0001-03"
}
```

`task_description.md`:

```markdown
# Training Corpus Task

The annotated training corpus is the primary labeled dataset for supervised experiments in this
project. This task downloads the corpus, verifies its integrity via SHA-256 checksums, documents
its structure and statistics, and registers it as a dataset asset.
```

---

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `TF-E001` | `task.json` does not exist or is not valid JSON |
| `TF-E002` | `task_id` does not match the task folder name |
| `TF-E003` | A required field is missing |
| `TF-E004` | `status` is not one of the allowed values |
| `TF-E005` | `task_id` format is invalid (not `tNNNN_slug`) |
| `TF-E006` | A dependency references a task ID that does not exist |
| `TF-E007` | `start_time` or `end_time` is not valid ISO 8601 or `null` |
| `TF-E008` | `source_suggestion` is not a string, `null`, or does not match `S-XXXX-NN` format |
| `TF-E009` | `source_suggestion` references a suggestion ID that does not exist |
| `TF-E010` | `task_index` is not an integer or does not match the numeric part of `task_id` |
| `TF-E011` | `task_types` is not a list |
| `TF-E012` | A task type slug in `task_types` does not exist in `meta/task_types/` |
| `TF-E013` | `spec_version` is not an integer or is not one of the supported versions |
| `TF-E014` | The long-description fields are invalid for the selected spec version |
| `TF-E015` | `long_description_file` is not a valid markdown file name in the task root |
| `TF-E016` | The referenced `long_description_file` is missing or unreadable |

### Warnings

| Code | Description |
| --- | --- |
| `TF-W001` | `short_description` exceeds 200 characters |
| `TF-W002` | `name` exceeds 80 characters |
| `TF-W003` | Status is `"in_progress"` but `start_time` is `null` |
| `TF-W004` | Status is `"completed"` but `end_time` is `null` |
| `TF-W005` | `expected_assets` is empty (task produces no assets) |
| `TF-W006` | A dependency task does not have status `"completed"` |
