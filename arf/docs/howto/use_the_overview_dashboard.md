# How to Use the Overview Dashboard

## Goal

Read project state through the [`overview/`](../../../overview/) dashboard instead of `cat`-ing
files in `tasks/`. The dashboard is the day-to-day surface for tasks, metrics, papers, suggestions,
costs, and daily news.

## Prerequisites

* You are on `main` (or any branch) with merged tasks
* `uv sync` has been run

## Steps

### 1. Regenerate the dashboard

```bash
uv run python -m arf.scripts.overview.materialize
```

The [materializer](../../scripts/overview/materialize.py) runs every aggregator, applies
corrections, and writes markdown into `overview/`. It is idempotent — re-run it any time the source
data changes.

### 2. Commit and push

The dashboard is committed. After regenerating:

```bash
git add overview/
git commit -m "overview: refresh dashboard"
git push
```

GitHub renders the result. Anyone with repo access can browse the project state without cloning.

### 3. Open overview/README.md

Start at [`overview/README.md`](../../../overview/README.md). The badge row shows live counts for
every entity type and links to its section. Below the badges: recently completed tasks, latest
papers, current best metric values, and budget burn.

### 4. Find what you need

| Question | Where to look |
| --- | --- |
| What did I finish recently? | `overview/tasks/by-date-added/` or the README's "recently completed" list |
| What is my current best on metric X? | `overview/metrics-results/<metric>.md` |
| What papers do I have on topic Y? | `overview/papers/by-category/<category>.md` |
| What should I work on next? | `overview/suggestions/` (grouped by priority and kind) |
| How much have I spent? | `overview/costs/README.md` |
| What happened this week? | `overview/news/<date>.md` for each day |
| Which tasks are blocked? | `overview/tasks/by-status/intervention_blocked.md` |
| What does task t0042 contain? | `overview/tasks/task_pages/t0042_*.md` |

Every page links to every related entity. A task page links to its papers, its metrics, its
suggestions. A metric page links to every task that reported it. Click through.

## Verification

The dashboard regenerated successfully if `overview/README.md` modification time is recent and the
badge counts match the latest aggregator output:

```bash
ls -la overview/README.md
uv run python -m arf.scripts.aggregators.aggregate_tasks --format ids | wc -l
```

The task count should match the badge.

## Pitfalls

* **Stale dashboard after manual merges.** The `execute-task` skill regenerates the dashboard
  automatically after merging. But if you merge a PR by hand outside the skill, run the materializer
  yourself or the badges and pages drift from reality.
* **Editing dashboard files by hand.** Every file under `overview/` is generated. Hand edits are
  overwritten on the next materializer run. Fix the source: edit the task, the spec, or the
  aggregator.
* **Reading raw `tasks/<id>/results/` files** for day-to-day work. Those files are the source of
  truth and useful for debugging one task, but the dashboard is the human-facing view. Open it
  first.
* **Skipping the commit.** The dashboard lives in git so collaborators can browse it on GitHub
  without cloning. Regenerating without committing helps no one but you.

## See Also

* [Tutorial part 5: Inspect Results](../tutorial/05_inspect_results.md)
* [Use aggregators](use_aggregators.md) — when you need a one-off query the dashboard does not cover
* [Generate daily news](../../skills/generate-daily-news/SKILL.md)
* [Materializer source](../../scripts/overview/materialize.py)
