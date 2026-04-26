# Skills Reference

Skills are reusable agent workflows. Each one lives at `arf/skills/<slug>/SKILL.md`. Claude Code
discovers them via `.claude/skills/<slug>` symlinks; Codex via `.codex/skills/<slug>`.

Format: `arf/specifications/agent_skills_specification.md`.

## All Skills

| Slug | Description | Primary Output |
| --- | --- | --- |
| [add-paper](../../skills/add-paper/SKILL.md) | Download a paper, create metadata assets, and register it in the current task. | `assets/paper/<paper_id>/` |
| [check-markdown-style](../../skills/check-markdown-style/SKILL.md) | Check a Markdown file against the project markdown style guide and report violations. | Style violation report |
| [check-python-style](../../skills/check-python-style/SKILL.md) | Check a Python file against the project Python style guide and report violations. | Style violation report |
| [check-skill](../../skills/check-skill/SKILL.md) | Verify an ARF skill's structure, shared metadata, symlinks, and markdown quality. | Skill verification report |
| [compare-literature](../../skills/compare-literature/SKILL.md) | Compare task results against published literature and write the comparison output. | `results/compare_literature.md` |
| [create-dedup-task](../../skills/create-dedup-task/SKILL.md) | Create a deduplication checkpoint task that scans for duplicate papers and overlapping work. | `tasks/<task_id>/` (dedup) |
| [create-project-description](../../skills/create-project-description/SKILL.md) | Guide creation of `project/description.md` and `project/budget.json` for a new or revised ARF project. | `project/description.md`, `project/budget.json` |
| [create-task](../../skills/create-task/SKILL.md) | Create a new not-started task folder with task.json and task_description.md. | `tasks/<task_id>/task.json`, `task_description.md` |
| [download_paper](../../skills/download_paper/SKILL.md) | Resolve paper identifiers, fetch the PDF and metadata, and prepare inputs for paper asset creation. | Downloaded PDF and metadata |
| [execute-task](../../skills/execute-task/SKILL.md) | Run an ARF task through all required stages and merge the final PR. | Merged PR, completed task |
| [generate-daily-news](../../skills/generate-daily-news/SKILL.md) | Generate a daily project summary with structured news files. | `news/<date>.md`, `news/<date>.json` |
| [generate-suggestions](../../skills/generate-suggestions/SKILL.md) | Generate follow-up task suggestions from completed task outputs and project context. | `results/suggestions.json` |
| [human-brainstorm](../../skills/human-brainstorm/SKILL.md) | Run an interactive brainstorming session to review state and choose next actions. | Brainstorm log, updated suggestions/tasks |
| [implementation](../../skills/implementation/SKILL.md) | Execute `plan/plan.md`, produce assets, and verify results. | Task assets, `results/` |
| [planning](../../skills/planning/SKILL.md) | Synthesize research outputs into a task plan with steps, costs, risks, and checks. | `plan/plan.md` |
| [research-code](../../skills/research-code/SKILL.md) | Review libraries and prior tasks to write implementation-oriented code research. | `research/research_code.md` |
| [research-internet](../../skills/research-internet/SKILL.md) | Conduct structured internet research and write `research/research_internet.md`. | `research/research_internet.md` |
| [research-papers](../../skills/research-papers/SKILL.md) | Review downloaded papers and write `research/research_papers.md`. | `research/research_papers.md` |
| [setup-project](../../skills/setup-project/SKILL.md) | One-shot interactive onboarding for a newly forked Glite ARF template. | `project/`, `meta/`, project README, initial task plan |
| [setup-remote-machine](../../skills/setup-remote-machine/SKILL.md) | Provision, validate, monitor, and tear down remote GPU machines for task execution. | Provisioned remote machine |

## Skill File Layout

A skill directory contains:

* `SKILL.md` — required. YAML frontmatter (`name`, `description`) plus body sections (Goal, Inputs,
  Context, Steps, Done When, Forbidden)
* Supporting files as needed

Expose the skill via symlinks:

* `.claude/skills/<slug>` → `arf/skills/<slug>`
* `.codex/skills/<slug>` → `arf/skills/<slug>`
