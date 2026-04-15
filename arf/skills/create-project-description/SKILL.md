---
name: "create-project-description"
description: >-
  Guide creation of `project/description.md` and `project/budget.json` for a
  new or revised ARF project. Use when project goals, scope, or budget need to
  be defined.
---
# Create Project Description

**Version**: 2

## Goal

Guide the user through creating `project/description.md` and `project/budget.json` via an
interactive dialog, ensuring all required content is filled.

## Inputs

* `$ARGUMENTS` — optional path to an existing description document or notes file to use as starting
  material.

## Context

Read before starting:

* `arf/specifications/project_description_specification.md` — mandatory sections, minimum content
  requirements, and verification rules
* `arf/specifications/project_budget_specification.md` — `project/budget.json` schema and threshold
  rules
* `arf/styleguide/markdown_styleguide.md` — formatting rules (100-char lines, `*` bullets, heading
  hierarchy)

## Steps

### Phase 1: Gather Raw Input

1. Read `arf/specifications/project_description_specification.md` to load section requirements.
2. If `$ARGUMENTS` contains a file path, read that file as starting material.
3. Ask the user to paste or describe everything they have about the project: goals, research
   questions, existing papers, datasets, code, scope constraints, or any other context. Accept any
   format — the user does not need to match the final structure.
4. Read any additional files the user points to.

### Phase 2: Identify Gaps and Ask Questions

5. Map the gathered input to the specification's required sections: Goal, Scope (In Scope / Out of
   Scope), Research Questions, Success Criteria, Key References, Current Phase. Also check for
   budget and pre-existing data/code.

6. List all sections that have insufficient content and show the user the full list of questions
   that will be asked. Example output:

   "I need to ask you about the following:
   1. Goal — What is the main research question or objective?
   2. Scope — What is explicitly out of scope?
   3. Success Criteria — How will you know the project succeeded?
   4. Budget — What is the total budget?
   5. Pre-existing data — Do you have existing data or code? Let me ask them one at a time."

7. Ask the questions one by one. Wait for the user's answer to each question before asking the next.
   The questions by section:
   * Goal: "What is the main research question or objective?"
   * Scope: "What is explicitly out of scope for this project?"
   * Research Questions: "What specific questions do you want to answer?"
   * Success Criteria: "How will you know the project has succeeded? What measurable outcomes
     matter?"
   * Key References: "What are the 3-5 most important papers, datasets, or benchmarks for this
     project?"
   * Current Phase: "Where is the project right now, and what comes next?"
   * Budget: "What is the total budget for this project? What currency? What is the maximum you want
     to spend on a single task? Which paid services are available (e.g., OpenAI API, Anthropic API,
     Vast.ai, AWS)?"
   * Pre-existing data/code: "Does this project work with any pre-existing user data or code (e.g.,
     datasets you already have, scripts, applications, previous analysis results)? If so, where are
     they located?"

8. After all questions are answered, if any answer is still insufficient for the section's minimum
   requirements, ask a follow-up for that specific section.

### Phase 3: Collect Pre-Existing Data

Skip this phase if the user has no pre-existing data or code.

9. For each data/code source the user identified, ask what it is and why it matters for the project.
10. Copy or symlink the files into `project/data/` (for datasets and data files) or `project/code/`
    (for scripts and applications). Ask the user whether to copy or symlink — copying is safer but
    uses more space; symlinking keeps one source of truth but breaks if the original moves.
11. For each copied/symlinked item, ask the user to briefly describe it: what it contains, what
    format it is in, and how the project will use it.

### Phase 4: Generate

12. Create `project/` directory (and `project/data/`, `project/code/` if needed).
13. Write `project/description.md` following the specification. If pre-existing data or code was
    collected, add a `## Pre-Existing Data and Code` section after Current Phase with:
    * A bulleted list of each item with its path relative to `project/`, format, and description
    * How each item connects to the project's research questions
14. Write `project/budget.json` following `arf/specifications/project_budget_specification.md` with
    the following structure:
    ```json
    {
      "total_budget": 500.00,
      "currency": "USD",
      "per_task_default_limit": 50.00,
      "available_services": ["openai_api", "anthropic_api"],
      "alerts": {
        "warn_at_percent": 80,
        "stop_at_percent": 100
      }
    }
    ```
    * `total_budget` — maximum spend for the entire project (float)
    * `currency` — ISO 4217 currency code (e.g., `"USD"`, `"EUR"`)
    * `per_task_default_limit` — default max spend per task (float); individual tasks can override
      this in their `plan/plan.md` Cost Estimation section
    * `available_services` — list of paid services the project may use
    * `alerts.warn_at_percent` — percentage of total budget that triggers a warning (int)
    * `alerts.stop_at_percent` — percentage that blocks new task creation (int)
15. Run the verificators:
    ```
    uv run python -u -m arf.scripts.verificators.verify_project_description
    uv run python -u -m arf.scripts.verificators.verify_project_budget
    ```
16. Fix any errors or warnings reported by the verificators.

### Phase 5: Review and Commit

17. Present all generated files to the user for review. Ask: "Please review the project description
    and budget. Should I change anything?"
18. Apply any requested changes and re-run the verificator.
19. After user confirmation, commit all files.

## Done When

* `project/description.md` exists and passes the verificator with no errors
* `project/budget.json` exists and passes `verify_project_budget.py`
* Pre-existing data/code is copied or symlinked into `project/` (if applicable)
* User has explicitly confirmed the content of all files
* All files are committed to the repository

## Forbidden

* NEVER fabricate project goals, research questions, or success criteria — always ask the user
* NEVER skip the review step — the user must confirm before committing
* Do not commit without explicit user confirmation
* NEVER write placeholder text like "[TBD]" or "[fill in later]" in the final file
* NEVER skip running the verificators after writing the files
* NEVER copy user data without asking whether to copy or symlink first
