# Corrections Specification

**Version**: 3

* * *

## Purpose

This specification defines the format for correction files that let downstream tasks change the
**aggregated effective view** of completed-task outputs without modifying completed task folders.

Completed task folders are immutable. When a later task discovers an error in a suggestion, paper,
answer, dataset, library, model, or predictions asset, it creates a correction file in its own
`corrections/` folder. Aggregators and other framework consumers then read the correction files and
expose the corrected effective state.

This mechanism is framework-generic. It is not tied to any project-specific domain.

**Producer**: Any downstream task that needs to correct an aggregated artifact from an earlier
completed task.

**Consumers**:

* **Aggregator scripts** — compute the effective corrected state
* **Verificator scripts** — validate correction structure and references
* **Research, planning, and implementation skills** — discover the current effective assets instead
  of stale upstream versions
* **Human reviewers** — audit why an earlier output was corrected

* * *

## Scope

This version covers these aggregated artifact kinds:

* `suggestion`
* `paper`
* `answer`
* `dataset`
* `library`
* `model`
* `predictions`

Correction files do **not** modify raw files in completed task folders. They only change what
downstream consumers treat as the effective state.

* * *

## File Location

````text
tasks/<correcting_task>/corrections/<target_kind>_<target_id>.json
````

Each correction is a separate JSON file in the correcting task's `corrections/` folder.

Examples:

```text
tasks/t0016_brainstorm_results_4/corrections/suggestion_S-0010-05.json
tasks/t0014_dedup_checkpoint_1/corrections/paper_10.18653_v1_2020.acl-main.95.json
tasks/t0042_fix_answer_sources/corrections/answer_when-to-use-remote-machines.json
```

* * *

## Correction Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Correction spec version; new files use `"3"`. |
| `correction_id` | string | yes | Unique ID in format `C-XXXX-NN`. |
| `correcting_task` | string | yes | Task ID that contains this correction file. |
| `target_task` | string | yes | Completed task that owns the target artifact. |
| `target_kind` | string | yes | One of the supported target kinds. |
| `target_id` | string | yes | ID of the target artifact. |
| `action` | string | yes | One of `update`, `delete`, `replace`. |
| `changes` | object or null | yes | Metadata changes or replacement pointer. |
| `file_changes` | object or null | no | Partial file overlay for supported asset kinds. |
| `rationale` | string | yes | Why the correction exists. |

* * *

## Field Details

### `correction_id`

Format: `C-XXXX-NN`

* `C` is a literal prefix
* `XXXX` is the zero-padded task index from the correcting task
* `NN` is a zero-padded sequential number within the correcting task

Regex: `^C-\d{4}-\d{2}$`

### `target_task`

Must reference an existing task. Corrections primarily target completed tasks because those folders
are immutable.

### `target_kind`

| Value | Target |
| --- | --- |
| `suggestion` | A suggestion object in `results/suggestions.json` |
| `paper` | A paper asset in `assets/paper/<paper_id>/` |
| `answer` | An answer asset in `assets/answer/<answer_id>/` |
| `dataset` | A dataset asset in `assets/dataset/<dataset_id>/` |
| `library` | A library asset in `assets/library/<library_id>/` |
| `model` | A model asset in `assets/model/<model_id>/` |
| `predictions` | A predictions asset in `assets/predictions/<predictions_id>/` |

### `action`

| Value | Meaning |
| --- | --- |
| `update` | Override structured metadata and, optionally, selected files |
| `delete` | Remove the target from the effective aggregate output |
| `replace` | Redirect consumers to a replacement artifact from a downstream task |

### `changes`

The meaning depends on `action`:

* `update`
  * Structured metadata overrides
  * May be `null` if `file_changes` is present and the correction only changes files
* `delete`
  * Must be `null`
* `replace`
  * Must include `replacement_task` and `replacement_id`

For `update`, `changes` may override any structured field exposed by the aggregator for that
artifact kind, except the immutable primary ID:

* `suggestion`: any suggestion field except `id`
* `paper`: any `details.json` field except `paper_id`
* `answer`: any `details.json` field except `answer_id`
* `dataset`: any `details.json` field except `dataset_id`
* `library`: any `details.json` field except `library_id`
* `model`: any `details.json` field except `model_id`
* `predictions`: any `details.json` field except `predictions_id`

For `replace`, `changes` must identify the replacement artifact:

````json
{
  "replacement_task": "t0042_fix_loader",
  "replacement_id": "wsd_data_loader"
}
````

The replacement must be the **same target kind** as the original target.

### `file_changes`

`file_changes` is optional and is only allowed with `action: "update"` for asset kinds that expose
files through aggregators:

* `paper`
* `answer`
* `dataset`
* `library`
* `model`
* `predictions`

It is not allowed for `suggestion`.

`file_changes` is a JSON object keyed by the logical file path being corrected:

```json
{
  "full_answer.md": {
    "action": "replace",
    "replacement_task": "t0042_fix_answer_sources",
    "replacement_id": "when-to-use-remote-machines",
    "replacement_path": "full_answer.md"
  }
}
```

Allowed file actions:

| Action | Meaning |
| --- | --- |
| `add` | Add a new effective file from another artifact |
| `delete` | Remove a file from the effective artifact |
| `replace` | Replace one file with a file from another artifact |

Rules:

* `delete` must not set replacement fields
* `add` and `replace` must set:
  * `replacement_task`
  * `replacement_id`
  * `replacement_path`
* `replacement_task` and `replacement_id` must identify an artifact of the same `target_kind`
* `replacement_path` must exist in the replacement artifact's effective file set

Important: `file_changes` rewires the **effective file sources**. If the file inventory itself
changes, update the corresponding structured metadata in `changes` too:

* `paper`: update `summary_path` and `files` if needed
* `answer`: update `short_answer_path` and/or `full_answer_path` if the canonical document paths
  change
* `dataset`: update `description_path` and `files` if needed
* `library`: update `description_path`, `module_paths`, and/or `test_paths`
* `model`: update `description_path` and `files`
* `predictions`: update `description_path` and `files`

* * *

## Effective-State Resolution

Consumers apply corrections in this order:

1. Load the raw target artifact.
2. Discover all correction files across tasks.
3. Sort corrections by correcting task index, then `correction_id`.
4. Apply whole-artifact actions:
   * `delete` removes the target
   * `replace` changes the effective target to a downstream artifact
   * later corrections win
5. Apply `update` metadata overrides to the effective artifact.
6. Apply `file_changes` to the effective artifact's file set.
7. Resolve file replacements transitively. File overlays may themselves point at artifacts that
   already have correction overlays.

Cycle rules:

* Whole-artifact replacement cycles are invalid.
* File-level replacement cycles are invalid.

Later corrections win per field and per file path.

* * *

## Supported Logical File Paths

The logical file paths used in `file_changes` must match the target kind.

Canonical document paths are metadata-driven for current asset versions:

* `paper`: `details.json` `summary_path` in v3; legacy v2 falls back to `summary.md`
* `answer`: `details.json` `short_answer_path` and `full_answer_path` in v2; legacy v1 falls back to
  `short_answer.md` and `full_answer.md`
* `dataset`: `details.json` `description_path` in v2; legacy v1 falls back to `description.md`
* `library`: `details.json` `description_path` in v2; legacy v1 falls back to `description.md`
* `model`: `details.json` `description_path` in v2; legacy v1 falls back to `description.md`
* `predictions`: `details.json` `description_path` in v2; legacy v1 falls back to `description.md`

With those rules applied, the effective supported logical file paths are:

* `paper`
  * the canonical summary document path
  * any path listed in `details.json` `files`
* `answer`
  * the canonical short answer document path
  * the canonical full answer document path
* `dataset`
  * the canonical description document path
  * any path listed in `details.json` `files`
* `library`
  * the canonical description document path
  * any path listed in `module_paths`
  * any path listed in `test_paths`
* `model`
  * the canonical description document path
  * any path listed in `details.json` `files`
* `predictions`
  * the canonical description document path
  * any path listed in `details.json` `files`

For `add`, the target path becomes a new logical file path in the effective artifact.

* * *

## Examples

### Update a Suggestion

````json
{
  "spec_version": "3",
  "correction_id": "C-0042-01",
  "correcting_task": "t0042_prioritize_followups",
  "target_task": "t0036_answer_wsd_architecture_and_training_questions",
  "target_kind": "suggestion",
  "target_id": "S-0036-04",
  "action": "update",
  "changes": {
    "priority": "high",
    "status": "active"
  },
  "rationale": "New evidence makes this follow-up actionable and higher priority."
}
````

### Delete a Duplicate Paper

```json
{
  "spec_version": "3",
  "correction_id": "C-0042-02",
  "correcting_task": "t0042_dedup_checkpoint_2",
  "target_task": "t0014_dedup_checkpoint_1",
  "target_kind": "paper",
  "target_id": "10.18653_v1_2020.acl-main.95",
  "action": "delete",
  "changes": null,
  "rationale": "This paper duplicates an earlier canonical copy that is already kept."
}
```

### Replace One File in an Answer Asset

````json
{
  "spec_version": "3",
  "correction_id": "C-0042-03",
  "correcting_task": "t0042_fix_answer_sources",
  "target_task": "t0033_answer_wsd_resource_context_and_annotation_questions",
  "target_kind": "answer",
  "target_id": "when-to-use-remote-machines",
  "action": "update",
  "changes": {
    "confidence": "high"
  },
  "file_changes": {
    "full_answer.md": {
      "action": "replace",
      "replacement_task": "t0042_fix_answer_sources",
      "replacement_id": "when-to-use-remote-machines",
      "replacement_path": "full_answer.md"
    }
  },
  "rationale": "The long-form answer had a sourcing mistake; only the full answer file changed."
}
````

### Replace a Library with a Downstream Version

```json
{
  "spec_version": "3",
  "correction_id": "C-0042-04",
  "correcting_task": "t0042_refactor_loader_api",
  "target_task": "t0012_build_wsd_data_loader_and_scorer",
  "target_kind": "library",
  "target_id": "wsd_data_loader",
  "action": "replace",
  "changes": {
    "replacement_task": "t0042_refactor_loader_api",
    "replacement_id": "wsd_data_loader"
  },
  "rationale": "Downstream tasks should use the refactored loader library instead of the old API."
}
```

* * *

## Backward Compatibility

Existing correction files with `spec_version` `"1"` or `"2"` remain valid.

Older files use only the subset that existed at the time:

* suggestion metadata updates
* paper deletion
* library replacement

The verifier accepts legacy versions so completed historical tasks do not need to be modified.

* * *

## Verification Rules

Verificators must check at least:

* required fields are present
* `correction_id` format and task-index match
* `correcting_task` matches the containing task folder
* `target_task` exists
* `target_kind` and `action` are valid
* the target artifact exists
* `changes` matches the action semantics
* `file_changes` is only used where supported
* referenced replacement artifacts and replacement files exist
* self-references and cycles are rejected
* filename matches `<target_kind>_<target_id>.json`
