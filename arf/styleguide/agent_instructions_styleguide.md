# Agent Instructions Style Guide

This document defines how to write instruction files for AI coding agents (Claude Code, OpenAI Codex
CLI, and similar tools). It covers all file types: `CLAUDE.md`, `AGENTS.md`, rules, and skills.

Target audience: developers writing or maintaining agent instructions in ARF projects.

* * *

## Quick Reference

### Frequently Ignored Rules

1. Use imperative mood — "Run the tests" not "You should run the tests"
2. Specify verification criteria — every workflow needs a "Done when" section with concrete checks
3. Never describe code abstractly — point to file paths, not prose descriptions of what code does
4. List forbidden actions explicitly — "NEVER modify files outside the task folder" is clearer than
   hoping the agent infers boundaries
5. Include concrete examples — at least one Do/Don't pair per non-trivial rule

* * *

## Instruction File Types

### Overview

| File | Purpose | Loaded |
| --- | --- | --- |
| `CLAUDE.md` | Project-wide context, rules | Auto |
| `AGENTS.md` | Cross-tool equivalent | Auto (Codex) |
| `.claude/rules/*.md` | Path-scoped rules | Auto on match |
| `.claude/skills/*/SKILL.md` | Reusable workflow definitions | On demand |

### CLAUDE.md

The primary instruction file. Claude Code loads it automatically by walking up the directory tree
from the current working directory. Place one at the repository root; add directory-level files
(e.g., `paper/CLAUDE.md`) when a subdirectory needs context-specific guidance.

#### What belongs here:

* Build, test, lint commands the agent cannot guess
* Project structure (abbreviated tree, not exhaustive)
* Architectural decisions specific to the project
* Critical rules (5-10, numbered)
* Developer environment quirks (required env vars, gotchas)

#### What does not belong here:

* Full API documentation (link to docs instead)
* File-by-file descriptions of the codebase (the agent can read files)
* Standard language conventions the agent already knows
* Detailed specifications (put in `arf/specifications/` and reference)

### .claude/rules/

Modular rule files that auto-load when the agent works on files matching a glob pattern. Use YAML
frontmatter to scope:

```markdown
---
paths:
  - "tasks/*/results/**"
---

# Results Format Rules

* Every results file must contain a Methodology section.
* Include machine specs, runtime, and timestamps.
```

Use rules when guidance applies only to specific file paths. If a rule applies everywhere, put it in
`CLAUDE.md` instead.

### .claude/skills/

Reusable workflow definitions invoked explicitly (via slash commands or agent discovery). Each skill
lives in its own subdirectory with a `SKILL.md` file. Use skills for multi-step workflows that would
bloat `CLAUDE.md` or rules. In ARF repositories, author skills in `arf/skills/` and expose them
through discovery symlinks in `.claude/skills/` and `.codex/skills/`.

### Cross-Tool Compatibility (Claude Code + Codex)

Claude Code reads `CLAUDE.md`. Codex CLI reads `AGENTS.md`. To avoid duplication, symlink one to the
other:

```bash
# In the repository root
ln -s CLAUDE.md AGENTS.md
git add AGENTS.md
```

Git stores symlinks natively. On macOS and Linux, cloning recreates the symlink automatically. On
Windows, symlinks require Developer Mode or special permissions — document this in the project
README if Windows contributors are expected.

Skills must also be symlinked so both tools discover them. In ARF, the canonical location is
`arf/skills/`. Symlink each skill directory into both discovery directories using relative paths:

```bash
# For each skill directory
mkdir -p .claude/skills
mkdir -p .codex/skills
ln -s ../../arf/skills/my_skill .claude/skills/my_skill
ln -s ../../arf/skills/my_skill .codex/skills/my_skill
git add .claude/skills/my_skill
git add .codex/skills/my_skill
```

What is shared vs tool-specific:

| Feature | Claude Code | Codex CLI |
| --- | --- | --- |
| Main instruction file | `CLAUDE.md` | `AGENTS.md` |
| Directory walk direction | Upward from CWD | Downward from root |
| Path-scoped rules | `.claude/rules/` | No equivalent |
| Skills | `.claude/skills/` | `.codex/skills/` |
| Hooks / automation | `.claude/settings.json` | No equivalent |
| Override file | N/A | `AGENTS.override.md` |

Write shared instructions in standard markdown that both tools process identically. When using
Claude-specific features (path frontmatter in rules, skills, hooks), add a comment at the top of
`CLAUDE.md` noting that Codex users may need to read these files manually.

* * *

## Structuring Instructions

### The Goal-Context-Constraints-Done Pattern

Every instruction file or skill should contain four elements:

1. Goal — one sentence stating what the agent must accomplish
2. Context — what to read first, what inputs exist, where outputs go
3. Constraints — numbered rules, forbidden patterns, format specs
4. Done when — explicit completion criteria with verification steps

#### Why:

Without a clear goal, the agent invents one. Without constraints, it takes shortcuts. Without
done-when criteria, it cannot verify its own work — and neither can you.

### Front-Load Critical Information

The context window is finite. Models degrade as context grows. Place the most important rules in the
first 20 lines.

#### Do:

```markdown
# Research Agent

## Goal

Produce `research/research_papers.md` summarizing findings from existing
papers relevant to this task.

## Critical Rules

1. NEVER fabricate citations. Every claim needs a source.
2. Read the paper before summarizing it.
3. Follow the format in `arf/specifications/research_papers_specification.md`.
```

#### Don't:

```markdown
# Research Agent

## Background

In this project we use a structured approach to research. The AI Research
Framework was designed to help manage complex research workflows. It uses
a task-based architecture where each task goes through several stages
including research, planning, execution, and analysis...

(40 lines of background before the agent learns what to do)
```

### Numbered Steps for Sequential Workflows

Use numbered steps when order matters. Use bullets for unordered constraints. Never use bullets for
a sequence of actions.

#### Do:

```markdown
## Steps

1. Read `task.json` to understand the task objective.
2. Search existing papers in `assets/` for relevant work.
3. Conduct internet research for recent publications.
4. Write findings to `research/research_papers.md`.
5. Run the verificator:
   `uv run python -m arf.scripts.verificators.verify_research_papers <task_id>`.
```

#### Don't:

```markdown
## Steps

* Read the task description
* Look at papers
* Do internet research
* Write the research file
* Verify
```

### Progressive Disclosure for Complex Workflows

Break multi-stage workflows into phases. Each phase has its own goal and done-when criteria. This
prevents the agent from losing track in long instruction files.

#### Do:

```markdown
## Phase 1: Research

### Goal
Understand the state of the art for this task.

### Steps
1. ...
2. ...

### Done when
* `research/research_papers.md` exists with at least 5 sources.
* Verificator passes with no errors.

---

## Phase 2: Planning

### Goal
Design the implementation approach.

### Steps
1. ...
```

* * *

## Writing Style

### Use Imperative Mood

Write commands, not suggestions. The agent is executing instructions, not reading a discussion.

#### Do:

```markdown
Run the verificator after completing each phase.
Read `plan/plan.md` before starting implementation.
Create a log entry in `logs/` for every completed step.
```

#### Don't:

```markdown
You should consider running the verificator after each phase.
It would be good to read the plan before starting.
A log entry could be created for completed steps.
```

### Be Concrete, Not Abstract

Reference specific file paths, command names, and section titles. Abstract descriptions rot faster
than file paths (and the agent can verify paths exist).

#### Do:

```markdown
Follow the format defined in `arf/specifications/logs_specification.md`.
Read `tasks/0001-baseline/results/results_summary.md` as an example.
```

#### Don't:

```markdown
Follow the standard log format used across the project.
Look at a previous task's results for an example of the expected format.
```

### Use Emphasis Sparingly

Reserve `CRITICAL`, `NEVER`, and `MUST` for rules where violation causes real damage. Use at most
3-5 emphasized rules per file. When everything is critical, nothing is.

#### Do:

```markdown
## Rules

1. Log every step in `logs/`.
2. Use `uv run` for all Python commands.
3. NEVER modify files outside the current task folder.
4. MUST run the verificator before marking a phase complete.
5. Commit after each completed phase.
```

#### Don't:

```markdown
## Rules

1. CRITICAL: Log every step.
2. IMPORTANT: Use uv run.
3. MUST: Never modify other folders.
4. CRITICAL: Run verificator.
5. IMPORTANT: Commit often.
```

### Quantify Instead of Qualifying

Numbers are unambiguous. Adjectives are not.

#### Do:

```markdown
Keep CLAUDE.md under 150 lines.
Include at least 3 sources in the research summary.
The results file must contain a metrics table with per-category breakdown.
```

#### Don't:

```markdown
Keep CLAUDE.md short.
Include several sources in the research summary.
The results file should have comprehensive metrics.
```

* * *

## Handling Complexity

### Split Strategies

* Path-scoped rules: Extract guidance that applies to specific files into `.claude/rules/` with
  frontmatter globs.
* Skills: Extract reusable multi-step workflows into `arf/skills/*/SKILL.md`, then expose them
  through `.claude/skills/` and `.codex/skills/`.
* Referenced specifications: Move format definitions to `arf/specifications/` and reference them:
  "Follow the format in `arf/specifications/logs_specification.md`."
* Directory-level `CLAUDE.md`: Add a `CLAUDE.md` in a subdirectory for context that only applies
  there (e.g., `paper/CLAUDE.md` for paper writing rules).

### Reference, Don't Repeat

Point to existing files rather than copying content into instructions. Duplicated instructions drift
apart and create contradictions.

#### Do:

```markdown
Follow the Python style guide in `arf/styleguide/python_styleguide.md`.
```

#### Don't:

```markdown
## Python Style Rules

Use dataclasses instead of tuples. Use keyword arguments for 2+
heterogeneous parameters. Never return tuples. Centralize paths...
(copying 50 lines from the styleguide)
```

### Version Numbers

Every specification and skill must include a version number. This allows verificators and agents to
detect format changes and ensures files produced under an older spec can be identified and migrated.

Versions are plain integers (1, 2, 3), not semantic version strings. Increment by 1 for every change
— there is no minor/major distinction.

* Specifications: Include `\*\*Version\*\*: N` near the top of the document (after the title).
* Data files produced by specs (JSON, YAML frontmatter): Include a `spec_version` field as a string
  matching the specification version (e.g., `"2"`).
* Skills: Include `\*\*Version\*\*: N` in the skill body even when the file also has YAML
  frontmatter.

#### Do:

```markdown
# Paper Asset Specification

\*\*Version\*\*: 2
```

```json
{
  "spec_version": "2",
  "paper_id": "10.18653_v1_E17-1010"
}
```

#### Don't:

```markdown
# Paper Asset Specification

\*\*Version\*\*: 1.1
```

```markdown
# Paper Asset Specification

(no version — impossible to tell which format a file follows)
```

* * *

### Sub-Agents for Multi-Stage Workflows

Run each stage of a complex workflow in a separate sub-agent. This prevents context pollution — a
research sub-agent's 50 paper summaries do not need to occupy the planning sub-agent's context
window.

Each sub-agent should receive:

* Its own focused goal and instructions
* Only the outputs from previous stages it actually needs
* Its own done-when criteria

* * *

## Verification and Anti-Hallucination

### Require Reading Before Acting

Never let the agent act on assumptions about file contents. Require explicit reading.

#### Do:

```markdown
Read `task.json` and confirm the status is `in_progress` before
proceeding.
```

#### Don't:

```markdown
The task should be in progress at this point.
```

### Exact-Quote Grounding

For citation-heavy tasks (research summaries, literature reviews), require the agent to provide
exact quotes with source references.

```markdown
For every claim about a paper's findings, provide:
* The exact quote from the paper
* The filename and page number
* Your interpretation of the quote

If no supporting quote exists, mark the claim as "Unverifiable."
```

### Forbid Shortcuts Explicitly

Agents abbreviate when context is long. List specific forbidden shortcuts — vague instructions like
"be thorough" are ignored.

#### Do:

```markdown
## Forbidden

* NEVER summarize log output as "[... N files processed ...]".
  Write every file path.
* NEVER skip per-category metric breakdowns. Report ES, DE, CN
  separately even when results are similar.
* NEVER use placeholder text like "[same as above]" or "[see
  previous section]". Write the full content each time.
```

### Allow Uncertainty

Give the agent an explicit escape hatch for situations it cannot resolve. This prevents fabrication.

```markdown
If you cannot determine the correct value from available files, write
"Unknown — requires human review" and create an intervention file in
`intervention/`.
```

### File-Existence Checks

After the agent creates output files, require verification.

```markdown
## Verification

1. Confirm `research/research_papers.md` exists and has at least 20 lines.
2. Confirm `logs/001_research_complete.md` exists.
3. Run: `uv run python -m arf.scripts.verificators.verify_research_papers <task_id>`
4. Fix any errors before proceeding. Warnings may be noted but do not
   block progress.
```

* * *

## Templates

### Root CLAUDE.md

```markdown
# <project-name>

<One-sentence project description.>

## Commands

| Command                     | Purpose              |
|-----------------------------|----------------------|
| `uv sync`                   | Install dependencies |
| `uv run python -u <script>` | Run a script        |
| `uv run ruff check --fix .` | Lint and fix         |
| `uv run mypy .`             | Type check           |

## Project Structure

<abbreviated directory tree — 10-15 lines max>

## Key Rules

1. All task-branch CLI calls must be wrapped in
   `uv run python -m arf.scripts.utils.run_with_logs`.
2. One task = one folder = one branch = one PR.
3. No files outside the current task folder may be modified.
4. ...
```

### Rule File (.claude/rules/)

```markdown
---
paths:
  - "tasks/*/results/**"
---

# Results Format Rules

* Include a Methodology section with machine specs and timestamps.
* Include a Metrics Table with per-category breakdown.
* Include a Verification section with concrete checks.
* Reference all charts as `![description](images/filename.png)`.
```

### Skill File (`arf/skills/*/SKILL.md`)

```markdown
---
name: "skill-slug"
description: "State what the skill does and when it should be used."
---

# <Skill Name>

\*\*Version\*\*: 1

## Goal

<One sentence: what this skill accomplishes.>

## Inputs

* `{{ argument_name }}` — <description>

## Context

Read before starting:
* `arf/specifications/<relevant_spec>.md`
* `tasks/{{ task_id }}/task.json`

## Steps

1. <First action.>
2. <Second action.>
3. ...

## Output Format

<Exact format specification for what the skill produces.>

## Done When

* <File X exists with at least N lines.>
* <Verificator passes with no errors.>
* <Specific content check.>

## Forbidden

* NEVER <specific bad action>.
* NEVER <another specific bad action>.
```

ARF repositories should expose the same skill directory through:

```text
.claude/skills/<skill-slug> -> ../../arf/skills/<skill-slug>
.codex/skills/<skill-slug>  -> ../../arf/skills/<skill-slug>
```

Required frontmatter keys:

* `name` — must match the skill directory slug
* `description` — must state both capability and trigger context

Optional tool-specific metadata is allowed only when there is a clear need and it does not break the
shared baseline format. See `arf/specifications/agent_skills_specification.md`.

* * *

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
| --- | --- | --- |
| Kitchen-sink CLAUDE.md (500+ lines) | Important rules lost in noise | Split into rules + skills |
| Vague goals ("improve the code") | Agent cannot verify completion | Add measurable checks |
| Describing code in prose | Descriptions go stale | Point to file paths |
| Style rules in instructions | Redundant with linters | Use ruff/mypy; reference config files |
| No forbidden-actions list | Agent guesses boundaries | Add explicit NEVER list |
| Hedged language ("you might want to") | Wastes tokens, weakens rules | Imperative mood: "Do X" |
| Duplicated instructions across files | Drift and contradictions | Single source; reference it |
| Every rule marked CRITICAL | Emphasis loses meaning | Reserve emphasis for 3-5 rules max |
| Abstract examples ("like the widget") | Agent cannot locate the referent | Name `src/x.py` |
| No verification step | Silent failures go undetected | Add done-when with concrete checks |
| No version number | Cannot track format changes | Add `\*\*Version\*\*: N` to specs and skills |
| Missing skill frontmatter | Tool discovery lacks metadata | Add YAML `name` + `description` |

* * *

## Checklist

When writing or reviewing an instruction file:

1. Goal stated in the first 3 lines
2. Imperative mood throughout
3. Concrete file paths, not abstract descriptions
4. Numbered steps for sequential workflows
5. Done-when / verification criteria present
6. Forbidden actions listed explicitly
7. At least one Do/Don't example per non-trivial rule
8. Emphasis used on at most 3-5 rules
9. Follows the markdown style guide (Flowmark-normalized, 100-char target, `*` bullets)
10. Skills have required YAML frontmatter (`name`, `description`)
11. Cross-tool compatible (or tool-specific features documented)
12. Version number present (specifications and skills)
