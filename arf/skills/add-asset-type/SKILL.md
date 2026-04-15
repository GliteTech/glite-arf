---
name: "add-asset-type"
description: >-
  Interactively scaffold a new asset type under meta/asset_types/, grounded in
  project/description.md. Creates a specification.md stub patterned on the
  built-in asset types. Use during project setup when a custom asset kind is
  needed; accept "none for now" to skip.
---
# Add Asset Type

**Version**: 1

## Goal

Scaffold one or more new asset types under `meta/asset_types/<slug>/` by creating a
`specification.md` stub that matches the structure of the built-in asset types (answer, dataset,
library, model, paper, predictions). The full asset-type surface — producer skills, verificators,
aggregator formatters — is out of scope for this skill; it seeds the specification so later work can
flesh those out.

## Inputs

* `$ARGUMENTS` — optional path to `project/description.md`. If absent, the skill uses
  `project/description.md` by convention; if that file does not exist, the skill asks the user which
  asset types to scaffold without the grounding proposal step.

## Context

Read before starting:

* `meta/asset_types/` — list of existing built-in types. Read one complete example such as
  `meta/asset_types/paper/specification.md` before drafting a new stub.
* `arf/styleguide/markdown_styleguide.md`, `arf/styleguide/agent_instructions_styleguide.md`.
* `arf/specifications/agent_skills_specification.md` — only indirectly relevant, but useful
  background on how the spec-producer pattern works across the framework.
* `project/description.md` if present.

## Steps

1. List the six built-in asset types currently under `meta/asset_types/`: `answer`, `dataset`,
   `library`, `model`, `paper`, `predictions`.
2. Print a 2-4 sentence explanation: asset types classify the concrete artifacts tasks produce
   (papers, datasets, models, …). Adding a new asset type is a multi-step effort — this skill only
   scaffolds the `specification.md` so the user can describe the asset's folder structure, metadata
   fields, and verification rules. Building the matching producer skill, verificator, aggregator
   formatter, and test coverage is framework work that should be done through `/self-improvement`
   afterwards.
3. Read the project description. If not available, skip step 4 and ask the user directly whether
   they want to scaffold any new asset types.
4. Propose 0-3 candidate asset types based on what the project description says will be produced
   that is not already covered by the six built-in types. For each candidate, list:
   * Suggested slug (lowercase, hyphen-separated, starts with a letter).
   * Suggested display name.
   * One-sentence rationale citing the project description.
5. Ask the user which candidates to accept, edit, drop, or add. Accept "none for now" as the
   expected default — most projects never need custom asset types.
6. For each accepted asset type, ask the user for:
   * A 1-3 sentence purpose statement.
   * The list of **Producer** subagents or skills expected to create the asset.
   * The list of **Consumer** subagents or scripts expected to read the asset.
   * A first pass at the folder structure: what files will live inside each
     `tasks/<task_id>/assets/<slug>/<asset_id>/` directory.
7. For each accepted asset type, write `meta/asset_types/<slug>/specification.md` with:
   * Title `# <Display Name> Asset Specification`
   * `**Version**: 1`
   * `## Purpose` — the user's purpose statement.
   * `## Producer` — user's producer list.
   * `## Consumers` — user's consumer list.
   * `## Asset Folder Structure` — the folder-and-files sketch from step 6.
   * `## Asset ID` — placeholder note saying the project must define this before tasks start
     producing the asset.
   * `## Fields` — empty table with `Field | Type | Required | Description` header so the user can
     fill it in.
   * `## Verification Rules` — placeholder note saying a verificator must be added through
     `/self-improvement` before tasks can produce this asset type.
   * Do **not** create `verificator.py`, `aggregator.py`, `format_overview.py`, or any Python code.
     The scaffold is markdown-only.
8. Show the user the list of new asset-type folders and print the next-step hint: "Run
   `/self-improvement` to add the matching verificator, aggregator, and tests before any task starts
   producing this asset type."
9. Ask the user for confirmation and commit with message `Scaffold <N> project asset types` listing
   the slugs in the body.

## Output Format

One folder per accepted asset type under `meta/asset_types/<slug>/` containing a single
`specification.md` stub. No Python code. No sibling directories.

## Done When

* For each accepted asset type, `meta/asset_types/<slug>/specification.md` exists with the required
  sections from step 7.
* The user saw the next-step hint pointing at `/self-improvement`.
* The commit landed, or the user was told "no changes made" when they chose to add none.

## Forbidden

* NEVER write Python code (`verificator.py`, `aggregator.py`, `format_overview.py`, or tests) in
  this skill — that belongs in `/self-improvement`.
* NEVER invent an asset type without user confirmation.
* NEVER skip the next-step hint — users must know the scaffold is incomplete.
* NEVER claim the new asset type is usable before `/self-improvement` has added the verificator.
