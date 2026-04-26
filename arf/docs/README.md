# Glite ARF Documentation

The Glite Autonomous Research Framework (Glite ARF, or just "ARF" in the internal docs) is a
file-based system for running AI-driven research projects without chaos. Every task runs in
isolation. Every artifact has a specification. Every step is logged. Every output is checked by a
verificator before it can be committed, catching mistakes AI agents reliably make. Completed work is
frozen so later runs can build on it without breaking it.

## Read This First

* [**Autonomy and Safety**](explanation/safety.md) — ARF runs AI agents with high permissions on
  your machine and GitHub account. Read what that means and what you must do on your side before
  forking.

## Why ARF?

* [Two Hundred Hypotheses, One Framework](blog/two-hundred-hypotheses.md) — the story behind the
  framework: what went wrong running 200 AI agents on a real research project, and how rigid rules
  fixed it

## How It Works

* [Core Concepts](explanation/concepts.md) — the six fundamental principles and the problem ARF
  solves
* [Architecture](explanation/architecture.md) — how skills, specifications, verificators,
  aggregators, utilities, and meta fit together
* [Task Lifecycle](explanation/task_lifecycle.md) — the seven phases from creation to merge
* [Corrections and Immutability](explanation/corrections.md) — why completed tasks are frozen and
  how downstream tasks correct prior work
* [Remote Machines](explanation/remote_machines.md) — how tasks spin up GPU instances, track costs,
  and tear them down
* [Autonomy and Safety](explanation/safety.md) — risks of running autonomous agents and how ARF
  contains them

## Walkthrough

Five pages. One small project. Read in order.

1. [Set Up a Project](tutorial/01_set_up_a_project.md)
2. [Review meta/](tutorial/02_customize_meta.md)
3. [Run Your First Task](tutorial/03_run_your_first_task.md)
4. [Brainstorm Next Tasks](tutorial/04_brainstorm_next_tasks.md)
5. [Inspect Results](tutorial/05_inspect_results.md)

## How-To Guides

Daily operations:

* [Use the overview dashboard](howto/use_the_overview_dashboard.md)
* [Run a task from the pool](howto/run_a_task.md)
* [Brainstorm next tasks](howto/brainstorm_next_tasks.md)
* [Create a task manually](howto/create_a_task_manually.md)
* [Run tasks in parallel](howto/run_tasks_in_parallel.md)

Occasional:

* [Apply a correction](howto/apply_a_correction.md) — fix something in completed work
* [Use aggregators](howto/use_aggregators.md) — one-off queries the dashboard does not cover
* [Debug a failed verificator](howto/debug_a_failed_verificator.md) — when a step fails verification

Extending the project (most common first):

* [Add a category](howto/add_a_category.md)
* [Add a metric](howto/add_a_metric.md)
* [Add a task type](howto/add_a_task_type.md)
* [Add an asset type](howto/add_an_asset_type.md)

Extending the framework (rarely needed):

* [Add a skill](howto/add_a_skill.md)
* [Add a verificator](howto/add_a_verificator.md)
* [Add an aggregator](howto/add_an_aggregator.md)

## Reference

* [Glossary](reference/glossary.md) — every framework term, alphabetical
* [Skills](reference/skills.md) — every skill with version and primary output
* [Task Folder Structure](reference/task_folder_structure.md) — annotated directory tree
* [Asset Types](reference/asset_types.md) — default asset types and their folder layouts
* [Specifications](reference/specifications.md) — every spec, grouped by category
* [Verificators](reference/verificators.md) — every verificator with diagnostic codes
* [Aggregators](reference/aggregators.md) — every aggregator with CLI flags
* [Utilities](reference/utilities.md) — helper scripts (prestep, poststep, run_with_logs, etc.)

## Source of Truth

The specs in [`arf/specifications/`](../specifications/) and
[`meta/asset_types/`](../../meta/asset_types/) are authoritative. These docs synthesize and link to
them — they never replace them. Specs and skills carry plain-integer version numbers
(`**Version**: N`); files produced under a spec carry a matching `spec_version` field.

Everything under `arf/` and most of `meta/` is framework-generic. Project-specific content lives in
`project/` and `tasks/`.
