# Deduplication Instructions

## Planning Guidelines

* Use the `/create-dedup-task` skill if available to bootstrap the task structure.
* Run the appropriate aggregator script (e.g., `aggregate_papers.py`,
  `aggregate_suggestions.py`) to collect all assets across tasks before starting.
* Identify the duplicate detection strategy: exact match on DOI/paper ID, fuzzy title
  matching, or semantic similarity for suggestions.
* Plan which asset types to scan: papers, suggestions, datasets, answers, or all of them.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute
  imports, keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`,
  centralized paths in `code/paths.py`, named constants, explicit type annotations,
  100-char line limit.
* **NEVER** modify files in completed task folders. All deduplication is done via the
  corrections mechanism: create correction files in the current task's `corrections/`
  folder that mark duplicates for removal or replacement.
* Run aggregators first to get a full inventory of assets. Parse the aggregated output
  to find duplicates programmatically.
* For each duplicate group, keep the earliest (lowest task ID) instance as the canonical
  version. Create a correction file that removes the later duplicates.
* Correction files must reference the exact task ID, asset type, and asset ID being
  corrected. Follow the correction format in `arf/specifications/`.
* Log every duplicate found with both the kept and removed asset identifiers.

## Common Pitfalls

* Modifying completed task folders instead of using corrections. This violates the
  immutability principle and will be caught by verificators.
* Missing near-duplicates that differ only in metadata (same paper, different DOI format
  or slightly different title).
* Not running aggregators before scanning, leading to an incomplete inventory.
* Creating correction files with incorrect task ID references.

## Verification Additions

* Confirm no files outside the current task folder were modified.
* Verify each correction file references a valid task ID and asset ID.
* Run the aggregator again after corrections to confirm duplicates are filtered.
* Check that the canonical (kept) asset is complete and well-formed.

## Related Skills

* `/create-dedup-task` -- bootstraps the deduplication task structure.
* `/implementation` -- general implementation workflow for the coding steps.
