---
name: "generate-daily-news"
description: "Generate a daily project summary with structured news files. Use when creating the
daily digest for a specific date."
---
# Generate Daily News

**Version**: 5

## Goal

Produce `news/$DATE.md` (markdown summary) and `news/$DATE.json` (structured data) for a single
day's project activity.

## Inputs

* `$DATE` — ISO date string (e.g., `2026-04-05`)

## Context

Read before starting:

* `arf/specifications/daily_news_specification.md` — authoritative format for both files
* `project/description.md` — project goals (to assess significance of findings)

## Steps

### Phase 1: Gather Data

1. Find all commits for the date:

   ```bash
   git log --all --after="$PREV_DATE 23:59:59" --before="$DATE 23:59:59" \
     --oneline --no-merges
   ```

   where `$PREV_DATE` is the day before `$DATE`.

2. Identify completed tasks. Scan `tasks/*/task.json` for tasks whose `end_time` falls on `$DATE`.
   For each completed task read:
   * `task.json` — name, status, timing
   * `results/costs.json` — cost breakdown
   * `results/metrics.json` — key metrics
   * `results/results_summary.md` — headline findings
   * `results/suggestions.json` — follow-up suggestions

3. Identify created tasks. Check git log for commits creating new `task.json` files on `$DATE`.

4. Identify cancelled tasks. Check git log for commits changing task status to `cancelled` on
   `$DATE`.

5. Count new assets. Check git log for new files under `tasks/*/assets/` on `$DATE`.

6. Identify infrastructure changes. Check git log for commits touching `arf/` on `$DATE`.

7. Gather current best results. Read the latest metrics or leaderboard data from the most recent
   completed tasks.

8. Identify papers added. Check git log for new `assets/paper/*/details.json` on `$DATE`. Read each
   `details.json` for title, authors, year, citation_key. Read `project/description.md` to assess
   which papers are most important for the project goals. Select 3-5 key papers.

9. Identify answers produced. Check git log for new `assets/answer/*/details.json` on `$DATE`. Read
   each `details.json` for the question and the short answer document.

10. Identify 2-3 key charts. Browse `results/images/` in completed tasks. Pick the charts that best
    illustrate the day's most important findings.

### Phase 2: Write the JSON File

11. Write `news/$DATE.json` following the specification. Include all structured data gathered in
    Phase 1. Round `total_cost_usd` to 2 decimal places.

### Phase 3: Write the Markdown File

12. Write `news/$DATE.md` following the specification and the writing style rules below.

#### Writing Style Rules

**Tone and structure:**

* Short sentences. Lead with the point. No filler, no hedging, no academic tone.
* **Bold** for key numbers — `**83.4 F1**`, `**$125**`, `**+0.4 F1**`.
* Short-long-short paragraph rhythm. A quick hook, then explanation, then a one-liner to land the
  point.
* Rhetorical questions where they sharpen the argument.
* Bullet lists for concrete data points. Tables for comparisons.
* No trailing summaries. The reader can read.

**Structure template:**

```text
## April 5, 2026

Opening line: N tasks completed. ~$X spent.

## N things we learned

### 1. Finding title.

Details with **bold** numbers. [Links](../overview/...) on key terms.
Follow-up: [retrain from scratch](../overview/tasks/task_pages/t0084.md) (t0084).

![Chart description](../tasks/t00XX/results/images/chart.png)

### 2. Another finding.

Details. Next: [suggestion queued](../overview/suggestions/README.md).

## N things we fixed (optional — only real bug fixes, not activity)

### 1. Bug or issue title.

What was wrong and how it was resolved.

## Where we stand (required)

| System | [F1 ALL](../overview/metrics-results/f1_all.md) |
|--------|------|
| [Best system](../overview/models/README.md) | [**XX.X**](../overview/metrics-results/f1_all.md) |

Gap to SOTA: **X F1 points**. Next bet: description of next approach.

## Costs (required)

| What | Cost |
|------|------|
| [Category](../overview/tasks/task_pages/t00XX.md) | $XX |
| **Day total** | **$XX** |
| **Project total ([full breakdown](../overview/costs/README.md))** | **$XXX** |
| **Budget remaining** | **$X,XXX** |

## Key papers added (recommended)

N papers added today. The most important:

**[Paper Title](../tasks/t00XX/assets/paper/doi_slug/summary.md)**
(Author, Year). 2-3 sentences on why it matters for the project.

[All N papers added today](../overview/papers/by-date-added/README.md)

## Key questions answered (recommended)

N questions answered. The most important:

**[Question text?](../tasks/t00XX/assets/answer/id/full_answer.md)**
2-3 sentence summary of the answer.

[All N answers](../overview/answers/README.md)
```

Each finding MUST include all three of these. No exceptions:

1. **What was learned** — the insight, not just what was done
2. **Key numbers** in `**bold**`
3. **Planned follow-up** — what happens next (task created, suggestion queued, decision made, or
   explicitly "no follow-up needed" with reason). If `results/suggestions.json` names a follow-up
   task, mention it. If a new task was created as a consequence, mention it.

After writing all findings, review each one and verify it has all three elements. If any finding is
missing the follow-up line, add it before moving on.

**"Things we fixed" must be actual fixes.** Bug diagnoses, evaluation corrections, resolved
mysteries. NOT project activity like "created 16 tasks" or "ran a brainstorm session". If there are
no real fixes, omit the section entirely.

**"Where we stand" must end with a gap-to-goal line.** After the leaderboard table, add one sentence
stating the gap to the project target and what the next bet is. Example: "Gap to SOTA: **4 F1
points**. Next bet: three retrain-with-context experiments."

#### Date Format

Use human-readable format: `## April 5, 2026` (not `## 2026-04-05`). The filename stays ISO
(`news/2026-04-05.md`).

#### Linking Rules

Link extensively. The text should read like a web page — every mention of a task, metric, dataset,
model, or paper is a clickable link with descriptive text. No task IDs in visible prose.

* **Tasks**: `[descriptive text](../overview/tasks/task_pages/<task_id>.md)`
* **F1 numbers**: `[**83.4 F1**](../overview/metrics-results/f1_all.md)`
* **Other metrics**: `[Verbs](../overview/metrics-results/f1_verb.md)`,
  `[HardEN](../overview/metrics-results/f1_hard_en.md)`
* **Datasets**: `[SemCor](../overview/datasets/README.md)`,
  `[Raganato ALL](../overview/datasets/README.md)`
* **Models**: `[SANDWiCH](../overview/models/README.md)`
* **Suggestions**: `[Suggestion queued](../overview/suggestions/README.md)`
* **Papers**: `[Paper Title](../tasks/<task_id>/assets/paper/<paper_id>/summary.md)`
* **Answers**: `[Question?](../tasks/<task_id>/assets/answer/<answer_id>/full_answer.md)`

Follow-up task references may include the task ID in parentheses after the link for easy reference:
`[retrain BEM](../overview/tasks/task_pages/t0082.md) (t0082)`.

#### Charts

Embed 2-3 key charts from the day's tasks. Use
`![description](../tasks/<task_id>/results/images/<file>.png)`.

#### Style Examples

Study these two texts carefully. Copy their rhythm, sentence length, and directness.

**Example 1: "Education as Medicine" by Vassili Philippov**

> The current state of education as a science reminds me where the medicine was slightly less than a
> hundred years ago. On a verge of converting from guesswork to a proper science. But for now many
> educational practices are still rooted in tradition and intuition rather than evidence. It's as if
> we're still relying on leeches and bloodletting to cure educational ills.
> 
> Imagine walking into a hospital in the early 1800s. Doctors rely on intuition, tradition, and
> personal experience. Treatments are based on what feels right, not what works.
> 
> A fever? Bloodletting.
> 
> A headache? Leeches.
> 
> A cough? Mercury.
> 
> There's no controlled testing, large-scale studies, or standard for proof. Medicine is built on
> anecdotes, authority, and outdated beliefs.
> 
> Now, imagine walking into a school today. Any similarities?
> 
> How do we know what works in education?
> 
> Because a famous professor says so? Because a best-selling book claims it does? Because it "feels
> right" to teachers and parents?
> 
> In many ways, education is stuck in its pre-scientific era — where intuition beats data, and
> strong beliefs outlast strong evidence.
> 
> Surely, this was the moment phonics would make a comeback, right? Nope.
> 
> Despite the growing evidence, whole language refused to die. Because it felt right. It was
> progressive. It treated children as natural learners. It made classrooms feel less rigid and more
> creative. Teachers embraced it. Textbook publishers profited from it.
> 
> In medicine, we don't accept treatments without proof. Why do we accept it in education?

**Example 2: "Faster and Safer Testing for AI Tutors" by Vassili Philippov**

> Imagine building the perfect virtual teacher — a virtual tutor that knows how to teach any
> student.
> 
> But how do you test it? How do you compare teaching strategies A vs. B? Randomized controlled
> trials (RCTs) are the gold standard, sure. But they're like waiting for a glacier to melt —
> accurate, but slow (think hundreds of students, months of data).
> 
> What if, instead of real students, we had virtual ones?
> 
> Think of it like this: How do they train self-driving cars? They don't just unleash them on the
> highway. They use incredibly detailed simulators — millions of miles driven, countless scenarios —
> before a single car hits the road.
> 
> A virtual student is the same idea. It's a model that learns like a student.
> 
> "Wait, a what?" you may say. "Are we talking about sentient AI here? Is this even possible?"
> 
> Let's break it down. Forget the sci-fi for a second.
> 
> At its core, a virtual student does one simple thing:
> 
> Predicts how a student will perform on the next learning task, based on their past learning
> history.
> 
> That's it.
> 
> We're not talking about replacing teachers. We're talking about giving them superpowers. We're
> talking about moving education from intuition to data.

### Phase 4: Commit and Push

13. Format the markdown file:

    ```bash
    uv run flowmark --inplace --nobackup news/$DATE.md
    ```

14. Commit both files:

    ```bash
    git add news/$DATE.md news/$DATE.json
    git commit -m "news: daily summary for $DATE"
    ```

15. Push to remote:

    ```bash
    git push
    ```

### Phase 5: Verify

16. Run the verificator:

    ```bash
    uv run python -m arf.scripts.verificators.verify_daily_news $DATE
    ```

17. Fix all errors and warnings. Re-run until zero errors and minimal warnings.

### Phase 6: Rebuild Overview

18. Rebuild the overview so the new daily news page appears in the dashboard:

    ```bash
    uv run python -m arf.scripts.overview.materialize
    ```

19. Commit and push the refreshed overview:

    ```bash
    git add overview/
    git commit -m "overview: refresh after $DATE daily news"
    git push
    ```

## Output Format

Two files in `news/`:

* `news/$DATE.md` — markdown summary (no `#` heading, starts with `## $DATE`)
* `news/$DATE.json` — structured JSON (see specification for schema)

Both files must be committed and pushed to the remote. The overview must be rebuilt and pushed.

## Done When

* `news/$DATE.md` exists and follows the specification
* `news/$DATE.json` exists and follows the specification
* Both files are committed to git and pushed to remote
* Verificator passes with zero errors
* Writing style matches the rules (punchy, direct, bold stats, follow-ups included)
* Overview is rebuilt via `arf.scripts.overview.materialize` and pushed to remote

## Forbidden

* NEVER use a `#` heading in the markdown file
* NEVER fabricate data — only report what actually happened on that date
* NEVER skip the verificator step
* NEVER put bare task IDs in visible text — use descriptive link text instead (task IDs may appear
  in parentheses after follow-up links only)
* NEVER write vague summaries like "several improvements were made" — use specific numbers
* NEVER write a finding without a follow-up line (what happens next, or why nothing is needed)
* NEVER put non-fix items in "things we fixed" — brainstorm sessions, task creation, and routine
  activity are not fixes
* NEVER omit the gap-to-goal line after the "Where we stand" table
