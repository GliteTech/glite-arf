---
name: "add-category"
description: >-
  Interactively add one or more entries to meta/categories/, grounded in
  project/description.md. Use during project setup or any time a new
  cross-cutting tag is needed.
---
# Add Category

**Version**: 1

## Goal

Add one or more category entries to `meta/categories/` through an interactive dialogue that proposes
candidates derived from the project description, confirms each with the user, writes the required
files, and passes the category verificator.

## Inputs

* `$ARGUMENTS` — optional path to `project/description.md`. If absent, the skill uses
  `project/description.md` by convention; if that file does not exist, the skill asks the user for
  categories without the grounding proposal step.

## Context

Read before starting:

* `arf/specifications/category_specification.md` — folder layout, `description.json` schema,
  verification rules.
* `arf/styleguide/markdown_styleguide.md`, `arf/styleguide/agent_instructions_styleguide.md`.
* `project/description.md` if present.
* Existing entries under `meta/categories/` so proposals do not duplicate them.

## Steps

1. Read `arf/specifications/category_specification.md` to load the contract.

2. Print a 2-4 sentence explanation of what a category is in Glite ARF (a project-wide tag that
   papers, tasks, and other assets reference to enable filtering and grouping). Point the user to
   `arf/specifications/category_specification.md` for full details.

3. Read the project description (from `$ARGUMENTS` or `project/description.md`). If neither is
   available, skip step 4 and instead ask the user to list categories themselves.

4. Propose 3-8 candidate categories based on the project description. For each candidate, list:
   * Suggested slug (lowercase, hyphen-separated, starts with a letter).
   * Suggested display name.
   * One-sentence rationale grounded in the project description.

5. Ask the user which candidates to accept, which to edit, which to drop, and whether to add any not
   listed. Accept a "none for now" response — categories can be added later by running this skill
   again.

6. For each accepted category, ask for:
   * A one-sentence `short_description` (≤ 200 characters).
   * A 2-5 sentence `detailed_description` (50-1000 characters).

   Use the candidate rationale as a starting draft the user can edit.

7. For each accepted category, write `meta/categories/<slug>/description.json` with:

   ```json
   {
     "spec_version": 1,
     "name": "<Display Name>",
     "short_description": "<sentence>",
     "detailed_description": "<paragraph>"
   }
   ```

8. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_categories
   ```

   Fix every error reported. Warnings may be shown to the user and left as-is if the user prefers.

9. Show the user the list of new category folders and ask for confirmation.

10. On confirmation, commit with message `Add <N> project categories` listing the slugs in the body.

## Output Format

One folder per accepted category under `meta/categories/<slug>/`, each containing a
`description.json` that conforms to `category_specification.md` v1.

## Done When

* For each accepted category, `meta/categories/<slug>/description.json` exists and passes
  `verify_categories` with no errors.
* The user explicitly confirmed the list before commit, or explicitly chose to add no categories.
* The commit landed, or the user was told "no changes made" when they chose to add none.

## Forbidden

* NEVER invent a category without user confirmation.
* NEVER write placeholder text like `[TBD]` into `description.json`.
* NEVER commit without showing the user the final list first.
* NEVER silence a `verify_categories` error — fix the content.
