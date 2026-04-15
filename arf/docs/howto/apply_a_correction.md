# How to Apply a Correction

## Goal

Correct an aggregated artifact from a completed task (suggestion, paper, answer, dataset, library,
model, or predictions asset) without modifying the target task folder.

## Prerequisites

* An active task to own the correction — corrections live in the *correcting* task's folder
* The target task ID and the target artifact ID
* Read
  [`arf/specifications/corrections_specification.md`](../../specifications/corrections_specification.md)

## Steps

1. Identify the target: completed task ID plus `target_kind` and `target_id` (e.g. `paper` +
   `10.18653_v1_E17-1010`). `target_kind` must be one of `suggestion`, `paper`, `answer`, `dataset`,
   `library`, `model`, `predictions`.
2. Create `tasks/<your_task_id>/corrections/` if it does not exist.
3. Create one JSON file per correction:
   `tasks/<your_task_id>/corrections/<target_kind>_<target_id>.json`.
4. Populate these fields:
   * `spec_version` — string, currently `"3"`
   * `correction_id` — matches regex `^C-\d{4}-\d{2}$`, where `XXXX` is the zero-padded task index
     of the correcting task and `NN` is a sequential number within that task
   * `correcting_task` — your task ID (must match the containing folder)
   * `target_task` — the completed task ID
   * `target_kind` — one of the seven supported kinds above
   * `target_id` — the artifact identifier
   * `action` — `update`, `delete`, or `replace`
   * `changes` — metadata overrides for `update`; `null` for `delete`;
     `{"replacement_task", "replacement_id"}` for `replace`
   * `file_changes` (optional, `update` only) — file-level overlay for asset kinds that expose
     files. Not allowed for `suggestion`
   * `rationale` — one paragraph explaining why the correction exists
5. Run
   [`uv run python -m arf.scripts.verificators.verify_corrections`](../../scripts/verificators/verify_corrections.py)
   `<your_task_id>`.
6. Re-run the relevant aggregator to confirm the overlay applied:
   `uv run python -m arf.scripts.aggregators.aggregate_papers --ids <target_id>`.
7. Commit the correction file as its own step.

## Example

An `update` correction fixing a paper's publication year:

```json
{
  "spec_version": "3",
  "correction_id": "C-0034-01",
  "correcting_task": "t0034_paper_audit",
  "target_task": "t0001_initial_survey",
  "target_kind": "paper",
  "target_id": "10.18653_v1_E17-1010",
  "action": "update",
  "changes": {
    "year": 2017,
    "date_published": "2017-04-03"
  },
  "rationale": "Original entry listed year as 2016; EACL proceedings confirm April 2017."
}
```

## Note on Metrics and Results

There is no `metric` or `result` `target_kind`. To correct a value that lives inside an asset (e.g.
a number in a `predictions` asset's description), use `target_kind: "predictions"` (or the
appropriate asset kind) and put the change in `changes` or `file_changes`. Raw files in completed
task folders are never modified — only the effective aggregated view changes.

## Verification

* `verify_corrections` exits with no errors
* The aggregator output reflects the corrected values
* `git status` shows no changes inside the target task folder

## Pitfalls

* Placing the correction file inside the *target* task folder — completed tasks are immutable
* Self-referencing corrections (`correcting_task == target_task`)
* Replacement cycles: A replaces B while B replaces A
* Using a `target_kind` that is not one of the seven supported kinds
* `correction_id` does not match the `C-XXXX-NN` format or the `XXXX` does not match the correcting
  task's index
* Filename does not match `<target_kind>_<target_id>.json`
* Using `file_changes` with `target_kind: "suggestion"` (not supported)
* Missing `rationale` — verificator rejects it
* `spec_version` written as an integer instead of the string `"3"`

## See Also

* `../../specifications/corrections_specification.md`
* `../corrections.md`
* [Use aggregators](use_aggregators.md)
