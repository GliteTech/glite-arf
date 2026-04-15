# Core Concepts

## The Problem ARF Solves

AI agents are messy. They rewrite files they shouldn't touch. They invent results that sound
plausible. They forget what they did two steps ago. They write long prose nobody reads.

For a one-off script, that's annoying. For a research project spanning hundreds of experiments and
months of compute, it's fatal. Results stop being reproducible. Provenance disappears. The project
rots from the inside until further progress is impossible.

ARF makes autonomous AI research **auditable** and **incrementally correct**. Not by making the
agents smarter. By putting hard structure around them. Every piece of work goes into a known shape.
Every step is recorded. No task is allowed to contaminate the rest of the project.

The framework is opinionated on purpose. The opinions are cheap when things go right and expensive
to violate when things go wrong. That is the trade you want when an LLM is writing your code at two
in the morning.

## Six Fundamental Principles

Six principles. They reinforce each other. Remove one and the rest weaken.

1. [Task Isolation](#1-task-isolation)
2. [Immutability and Corrections Overlay](#2-immutability-and-corrections-overlay)
3. [Structure Enforced by Verificators](#3-structure-enforced-by-verificators)
4. [No Duplication](#4-no-duplication)
5. [Comprehensive Logging](#5-comprehensive-logging)
6. [Subagent Isolation](#6-subagent-isolation)

### 1. Task Isolation

Every unit of work lives in its own folder under `tasks/tXXXX_slug/` and runs on its own git branch.
Inside that folder, the task has full freedom. Outside it, the task changes nothing. The only
exceptions are a small set of global tooling files like `pyproject.toml`, `uv.lock`, and `ruff.toml`
— these control the shared build environment, and a task that adds a dependency or changes a lint
rule has to update them.

What does this prevent? Cross-task contamination. Without isolation, a task that "quickly fixes a
bug in the shared loader" silently changes the meaning of every previous experiment that used that
loader. With isolation, the agent cannot edit those files at all. Any fix must be a new task or a
[correction](corrections.md). A task that trains a new model writes its code, model weights, and
results under its own folder. Earlier tasks stay bit-identical.

### 2. Immutability and Corrections Overlay

Once a task is completed, nothing inside its folder ever changes. Did a later task discover an
earlier result was wrong? A paper was misclassified? A suggestion is now obsolete? The later task
does not reach back. It writes a small correction file in its own `corrections/` directory.
Aggregators combine the original data and the corrections at read time.

This preserves a critical property: the repository at any commit tells you exactly what was known,
when, and how that knowledge changed. You can replay history. The failure mode prevented is silent
retroactive rewriting, which destroys reproducibility.

One rule falls out of this and it is easy to get wrong: **skills must read through
[aggregators](../reference/aggregators.md), not by enumerating files in task folders.** Aggregators
apply the corrections overlay at read time; a raw directory walk does not. A skill that lists papers
by globbing `tasks/*/assets/paper/*` will see the stale originals and miss every fix a later task
made. The same goes for suggestions, metrics, and every other aggregated artifact.

Full mechanism: see [corrections](corrections.md).

### 3. Structure Enforced by Verificators

AI agents are not 100% reliable. They forget rules. They skip sections. They confidently produce
broken outputs. ARF does not try to fix this by trusting the agent's common sense. It fixes it by
removing common sense from the loop entirely.

**Every artifact has a [specification](../reference/specifications.md).** The format of `task.json`,
the mandatory sections in a results file, the fields of a paper asset's `details.json`, the
lifecycle of a remote machine — all written down as formal specs under
[`arf/specifications/`](../../specifications/) and
[`meta/asset_types/`](../../../meta/asset_types/). Nothing is left to interpretation. If a skill
produces a file, the spec for that file already exists and the skill must conform.

**Every specification is enforced by a [verificator](../reference/verificators.md)**: a small Python
script that reads the artifact and checks it rule by rule. Does the log file exist? Does the results
file have the required sections? Were any files outside the current task folder modified? Does this
JSON match its spec? Verificators run after each step, produce errors (which block) and warnings
(which don't), and emit diagnostic codes so failures can be looked up.

The two halves have to ship together. A spec without a verificator is a suggestion, and suggestions
get dropped when context gets long. A verificator without a spec has no ground truth to check
against. **Structure is only real if something checks it.**

### 4. No Duplication

Every piece of data lives in exactly one place. A paper is stored once, in the task that first added
it. A metric is reported once, in the task that produced it. When the framework needs a combined
view — every paper across every task, every suggestion in a category — an
**[aggregator](../reference/aggregators.md)** walks the task folders and computes it on demand.

This prevents drift: the same paper summarized three different ways with no way to know which is
current. Normalization makes corrections possible (only one thing to correct) and keeps the
repository conceptually small.

### 5. Comprehensive Logging

Every step of every task writes a log to `logs/`. Every command-line invocation goes through
[`run_with_logs.py`](../../scripts/utils/run_with_logs.py), which records the command, its
arguments, its output, and its exit code. Verificators check that the logs are there.

Why bother? Because something always eventually goes wrong. When it does, you need to reconstruct
what the agent actually did, not what it claimed in its final summary. Without logs, subagent
failure is opaque. With logs, it's debuggable. See [architecture](architecture.md) for how logging
fits into the execution pipeline.

### 6. Subagent Isolation

Complex tasks run as a chain of [subagents](../reference/skills.md): research, then planning, then
implementation. Each one gets its own context window and sees only the inputs it needs. A research
subagent that read fifty paper summaries does not pollute the planning subagent that comes after.

This addresses a hard limit of current LLMs: they degrade as context fills up. Splitting a task into
isolated stages keeps each stage focused and gives the framework a natural place to insert
verification between stages.

## Tasks, Assets, and Suggestions

Three vocabulary items recur everywhere.

A **task** is one atomic unit of work: download this dataset, train this model, answer this
question. A task has a folder, a branch, a status, a plan, results, and mandatory stages. One task
becomes one pull request.

An **asset** is a typed output produced by a task. [Asset types](../reference/asset_types.md) are
defined per project under [`meta/asset_types/`](../../../meta/asset_types/), each with its own
specification. Most projects start with the standard set — paper, dataset, library, model,
predictions, answer — and add or modify types as needed. Assets are the currency of the project —
what one task hands to the next.

A **suggestion** is a proposal for a future task. Every completed task writes a
`results/suggestions.json` listing follow-up ideas the research or analysis stage came up with.
Suggestions are not tasks yet — they sit in a pool until a
[brainstorming session](../howto/brainstorm_next_tasks.md) reviews them and promotes the chosen ones
into real task folders. This is the pipeline: **tasks generate suggestions, suggestions become new
tasks**. It is the loop that keeps the project moving without anyone hand-picking what to do next.

(Categories are a minor supporting concept: free-form tags on tasks, assets, and suggestions under
[`meta/categories/`](../../../meta/categories/) that enable filtering without imposing a hierarchy.)

## Generic vs Project-Specific

ARF has a hard boundary between framework-generic code and project-specific content. Everything
under `arf/` is generic and stays reusable across any research project. So do the generic pieces of
`meta/` — asset type specs, generic boilerplate. None of it references the specific domain a project
is researching.

Project-specific content belongs in `project/` (description, budget, goals) and in `tasks/`
(everything the project actually does). ARF is meant to be lifted into new projects. Domain
contamination makes that lift harder. When editing a file under `arf/`, ask: would this make sense
in a completely different research project? If no, it belongs somewhere else.

## See Also

* [Architecture](architecture.md) — how the framework's components fit together
* [Task lifecycle](task_lifecycle.md) — the stages every task moves through
* [Corrections](corrections.md) — how immutability and change coexist
* [Reference documentation](../reference/) — exact file formats and field definitions
* [Tutorial](../tutorial/) — a guided first task
