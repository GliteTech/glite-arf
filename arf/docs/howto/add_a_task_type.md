# How to Add a Task Type

## Goal

Register a new task type in [`meta/task_types/`](../../../meta/task_types/) so future tasks can be
created against it.

## Prerequisites

* A kebab-case slug (e.g. `baseline-evaluation`, `download-dataset`)
* Read
  [`arf/specifications/task_type_specification.md`](../../specifications/task_type_specification.md)

## Steps

1. Create the folder: `meta/task_types/<slug>/`. Slug rules: lowercase letters, digits, and hyphens
   only, starting with a letter.
2. Create `meta/task_types/<slug>/description.json` with these fields:
   * `spec_version` — integer, currently `1`
   * `name` — human-friendly display name (title case, max 50 chars)
   * `short_description` — one-sentence summary (max 200 chars)
   * `detailed_description` — 2-5 sentence paragraph (50-1000 chars)
   * `optional_steps` — array of optional step slugs from: `research-papers`, `research-internet`,
     `research-code`, `planning`, `setup-machines`, `teardown`, `creative-thinking`,
     `compare-literature`. Use `[]` when only the seven always-required steps apply.
3. Create `meta/task_types/<slug>/instruction.md` with at least these two mandatory `##` sections:
   `## Planning Guidelines` and `## Implementation Guidelines`. Recommended optional sections:
   `## Common Pitfalls`, `## Verification Additions`, `## Related Skills`. The file has no YAML
   frontmatter.
4. Use
   [`meta/task_types/baseline-evaluation/description.json`](../../../meta/task_types/baseline-evaluation/description.json)
   and
   [`meta/task_types/baseline-evaluation/instruction.md`](../../../meta/task_types/baseline-evaluation/instruction.md)
   as templates.
5. Run
   [`uv run python -m arf.scripts.verificators.verify_task_types`](../../scripts/verificators/verify_task_types.py).

## Verification

```bash
uv run python -m arf.scripts.verificators.verify_task_types
```

Expected: no errors, new slug listed among validated task types.

## Pitfalls

* A value in `optional_steps` is not one of the eight allowed optional step slugs
* Missing `## Planning Guidelines` or `## Implementation Guidelines` in `instruction.md`
* `spec_version` written as a string instead of an integer
* `instruction.md` written in descriptive rather than imperative mood
* `instruction.md` under 200 characters (too brief)
* Overlapping scope with an existing task type

## See Also

* `../reference/task_types.md`
* `../../specifications/task_type_specification.md`
