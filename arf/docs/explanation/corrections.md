# Corrections and Immutability

## Why Completed Tasks Are Frozen

Once a task is completed, nothing inside its folder ever changes. No file edited. No file renamed.
No file deleted. No new file added. [Verificators](../reference/verificators.md) run on every task
branch and flag any modification to another task's folder as an error.

Why? Reproducibility. A research project's value comes from its audit trail — the ability to look at
the repository at any commit and see exactly what was known, produced, and concluded at that moment.
The moment an agent is allowed to reach back and edit an older task's results, that audit trail
becomes a lie. Experiments that "reproduce" a past result do so by accident, because the past result
is no longer what it was when the reproduction ran.

Silent retroactive rewriting destroys trust in everything the repository contains. It is exactly
what an autonomous agent will do if nothing stops it.

Immutability also makes parallelism easy. Two tasks running on different branches at the same time
cannot race each other's outputs. Neither is allowed to touch them.

## The Overlay Model

Mistakes happen. A paper gets the wrong metadata. A suggestion turns out to be a duplicate. A result
is discovered to rest on a buggy loader. ARF handles these with a
[**corrections overlay**](../../specifications/corrections_specification.md): the original data
stays exactly where it was, and a later task records — in its own folder — what should change.
[Aggregators](../reference/aggregators.md) read both the original and the corrections and combine
them at read time.

The critical detail: corrections live in the **correcting** task's folder, not the target's. A
correction written by task `t0042` goes into `tasks/t0042/corrections/`, even though it is about an
artifact produced by `t0007`. This keeps `t0007` bit-identical to what it was on the day it was
completed, while still making the corrected view discoverable.

When an aggregator walks the `tasks/` tree to collect "all suggestions," it grabs the raw
suggestions from every task and then walks every task's `corrections/` folder for corrections
targeting suggestions. It applies them on top of the raw data before returning the result. Consumers
see the effective view. The raw view is still there for anyone who needs it.

## What Can Be Corrected

The correction mechanism targets **aggregated artifacts** — the things skills and humans read
through aggregators rather than by opening individual task folders. Supported target kinds currently
include suggestions, papers, answers, datasets, libraries, models, and predictions assets. Metrics
are corrected through the same mechanism, targeted at the task's results.

Corrections do not touch raw files inside completed task folders. If an asset's underlying file is
wrong, a correction can point consumers at a replacement file in the correcting task. The original
file on disk stays untouched.

## Correction Actions

Three actions. **`update`** overrides specific fields of the target — change a paper's publication
year, change a suggestion's category. **`delete`** removes the target from the effective aggregate
view, so aggregators behave as if the artifact had never been added. **`replace`** redirects
consumers to a different artifact produced by a downstream task. Use `replace` when the original
asset is wrong enough that fixing it field by field makes no sense and a clean replacement exists.

Every correction carries a mandatory `rationale` field. Not decorative. It is what lets a future
reader (human or agent) understand why the correction exists and whether it still applies. A
correction without a rationale is a silent rewrite in disguise.

## Resolution Order

When multiple corrections target the same artifact, the aggregator applies them in order. Later
corrections win on a per-field basis. "Later" is defined by the task index of the correcting task: a
correction from `t0050` overrides a conflicting correction from `t0030` on the same field, but
fields `t0050` does not touch still reflect `t0030`'s change. A `delete`, once applied, cannot be
undone by a later `update`. To bring a deleted artifact back, a later task must explicitly restore
it through a new correction.

This per-field layering is what makes the overlay usable. Small focused corrections can accumulate
over time without each new one having to restate everything the previous ones already fixed.

## When to Use a Correction vs a New Task

Corrections are right for **metadata fixes and small data errors**: a mislabeled category, a wrong
author, a typo in a summary, a duplicate suggestion. Cheap and precisely targeted.

A new task is right for **methodological or substantive fixes**: the original result is wrong
because the methodology was wrong, and the right move is to redo the work. Trying to "correct" a bad
experimental result through a correction file would hide the fact that the original was wrong and
replace it with a value that has no experimental record. New tasks produce their own logs, plan,
results, and audit trail. A `replace` correction can then point consumers from the old artifact to
the new one.

Rule of thumb: if the correction would write a new result, it should be a new task. If the
correction would fix a mistake about an existing result, it should be a correction.

## See Also

* [Concepts](concepts.md) — the immutability principle in context
* [Task lifecycle](task_lifecycle.md) — where corrections fit into execution
* [Architecture](architecture.md) — how aggregators apply corrections at read time
* [Reference documentation](../reference/) — exact correction file format
* [How-to guides](../howto/) — writing a correction in practice
