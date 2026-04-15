# Correction Instructions

## Planning Guidelines

* Many correction tasks do not need a planning step. If the correction request already names the
  target artifact, the required fix, and the verification method clearly, the execute-task
  orchestrator may skip planning entirely.
* If planning is included, keep the plan tightly focused on the exact target artifacts to correct,
  whether each fix is `update`, `delete`, `replace`, or `file_changes`, whether replacement assets
  must be created in the current task, and how aggregators and verificators will confirm the
  corrected effective state.
* When a correction affects only part of a multi-file asset, plan both sides of the change:
  * the file overlay itself
  * any structured metadata that must stay aligned with the effective file list

## Implementation Guidelines

* Do not modify the completed upstream task folder directly.
* Write correction files only in the current task's `corrections/` folder.
* Use `update` for structured metadata fixes, `delete` to remove an effective artifact, and
  `replace` when a downstream artifact should become the new effective version.
* Use `file_changes` only when a file-based asset needs a partial correction. Keep structured
  metadata aligned when the effective file inventory changes.
* If the correction needs new content, create the replacement asset in the current task first, then
  point the correction at it.

## Common Pitfalls

1. Editing the old task directly instead of creating a correction file.
2. Replacing files without updating matching metadata when the effective file inventory changes.
3. Using a correction when the real fix requires a new replacement asset that does not exist yet.

## Verification Additions

* Run `uv run python -m arf.scripts.verificators.verify_corrections $TASK_ID`.
* Re-run the relevant aggregator to confirm the corrected effective state.
* If replacement assets were created, run their asset verificators too.

## Related Skills

* `/research-code` — inspect the target artifact and prior outputs when needed
* `/planning` — define the correction strategy for complex fixes
* `/implementation` — create replacement assets and correction files
