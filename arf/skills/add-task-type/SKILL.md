---
name: "add-task-type"
description: >-
  Interactively add one or more task types to meta/task_types/, grounded in
  project/description.md. Use during project setup or any time a recurring kind
  of task needs standardized planning and implementation guidance.
---
# Add Task Type

**Version**: 1

## Goal

Add one or more task types to `meta/task_types/` through an interactive dialogue that proposes
candidates derived from the project description, confirms each with the user, writes both
`description.json` and `instruction.md` per spec, and passes the task types verificator.

## Inputs

* `$ARGUMENTS` — optional path to `project/description.md`. If absent, the skill uses
  `project/description.md` by convention; if that file does not exist, the skill asks the user to
  list task types directly.

## Context

Read before starting:

* `arf/specifications/task_type_specification.md` — folder layout, `description.json` schema,
  `optional_steps` allowed values, `instruction.md` mandatory sections, verification rules.
* `arf/styleguide/markdown_styleguide.md`, `arf/styleguide/agent_instructions_styleguide.md`.
* `project/description.md` if present.
* Existing entries under `meta/task_types/` so proposals do not duplicate them. The template ships
  with 19 generic task types (such as `build-model`, `literature-survey`, `experiment-run`) — read
  one like `meta/task_types/literature-survey/instruction.md` as a structural example.

## Steps

1. Read `arf/specifications/task_type_specification.md` to load the contract.

2. Print a 2-4 sentence explanation: task types classify tasks by their nature and give the planning
   and implementation skills type-specific guidance. They also drive the Phase 1 budget gate through
   `has_external_costs`. Point the user to `arf/specifications/task_type_specification.md` for full
   details.

3. List the 19 generic task types already present under `meta/task_types/` so the user knows what is
   reusable out of the box.

4. Read the project description. If not available, skip step 5 and ask the user to list task types
   directly.

5. Propose 3-8 project-specific task types based on the project description — focus on recurring
   workflows that the generic task types do not already cover. For each candidate, list:
   * Suggested slug (lowercase, hyphen-separated, starts with a letter).
   * Suggested display name.
   * A one-sentence rationale.
   * Suggested `optional_steps` from the allowed set: `research-papers`, `research-internet`,
     `research-code`, `planning`, `setup-machines`, `teardown`, `creative-thinking`,
     `compare-literature`.
   * Suggested `has_external_costs` (`true` when the task can incur paid GPU or API spend; set
     `true` when in doubt).

6. Ask the user which candidates to accept, edit, drop, or add. Accept "none for now" — the 19
   built-in types may be sufficient for the first tasks.

7. For each accepted task type, confirm with the user:
   * `name` (≤ 50 characters).
   * `short_description` (≤ 200 characters).
   * `detailed_description` (50-1000 characters).
   * Final `optional_steps` list.
   * Final `has_external_costs` boolean.

8. For each accepted task type, write two files:

   * `meta/task_types/<slug>/description.json`:

     ```json
     {
       "spec_version": 2,
       "name": "<Display Name>",
       "short_description": "<sentence>",
       "detailed_description": "<paragraph>",
       "optional_steps": ["<step>", "..."],
       "has_external_costs": false
     }
     ```

   * `meta/task_types/<slug>/instruction.md`, containing at minimum the two mandatory sections
     `## Planning Guidelines` and `## Implementation Guidelines`. Draft each with 3-6 bullets
     tailored to the task type. Recommended additions: `## Common Pitfalls`, `## Related Skills`.

   Ask the user to confirm each drafted `instruction.md` before writing it.

9. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_task_types
   ```

   Fix every error reported.

10. Show the user the final list of new task type folders and ask for confirmation.

11. On confirmation, commit with message `Add <N> project task types` listing the slugs in the body.

## Output Format

One folder per accepted task type under `meta/task_types/<slug>/`, each containing
`description.json` and `instruction.md` that conform to `task_type_specification.md` v2.

## Done When

* For each accepted task type, `description.json` and `instruction.md` exist and pass
  `verify_task_types` with no errors.
* The user explicitly confirmed each drafted `instruction.md` before it was written.
* The user explicitly confirmed the final list before commit, or chose to add none.
* The commit landed, or the user was told "no changes made" when they chose to add none.

## Forbidden

* NEVER invent a task type without user confirmation.
* NEVER include an `optional_steps` value outside the allowed set in `task_type_specification.md`.
* NEVER write an `instruction.md` missing `## Planning Guidelines` or
  `## Implementation Guidelines`.
* NEVER commit without showing the user the final list first.
* NEVER silence a `verify_task_types` error — fix the content.
