# How to Start a New ARF Research Project

This guide describes what to do after forking the ARF template repository. The fork already contains
the directory structure, infrastructure files, specifications, and framework scripts.

## Step 1: Fork and Clone

Fork the template repository on GitHub, rename it for your research topic, then clone locally.

```bash
git clone <your-fork-url>
cd <project-name>
```

## Step 2: Set Up the Environment

Run `/setup-project` in Claude Code (or its Codex equivalent). The skill captures the safety
acknowledgement, detects or installs `uv`, runs `uv sync`, installs pre-commit hooks, allows
`direnv`, initializes Git LFS, and runs `doctor.py`. API keys for paid services (OpenAI, vast.ai)
are provisioned later in Phase 4 of the skill, only for services your project actually declares in
`project/budget.json`.

## Step 3: Customize Project Identity

Update these files for your specific research topic:

* **`pyproject.toml`** -- Change `name`, `description`, and `version`. Add domain-specific
  dependencies as needed.
* **`CLAUDE.md`** -- Update the project description and any domain-specific context at the top. The
  structure, rules, and style sections remain unchanged.

## Step 4: Create Project Description

Create `project/description.md` to define the project's goals, scope, and research questions. This
file is read by all skills to understand project-level context.

Run the `/create-project-description` skill for an interactive guided workflow, or create the file
manually following the specification in `arf/specifications/project_description_specification.md`.

Required sections:

* **Goal** -- 2-3 sentences: the overarching research objective
* **Scope** -- In Scope / Out of Scope bulleted lists
* **Research Questions** -- 3-7 numbered, testable questions
* **Success Criteria** -- measurable completion criteria (at least 3)
* **Key References** -- anchor papers, datasets, benchmarks (at least 3)
* **Current Phase** -- 1-2 sentences on where the project is now

Validate with:

```bash
uv run python -u -m arf.scripts.verificators.verify_project_description
```

Update this file as the project evolves -- particularly Current Phase and Research Questions after
each checkpoint.

## Step 5: Define Asset Types

Review the predefined asset types in `meta/asset_types/` (paper, dataset, library, answer). Add
domain-specific asset types as needed (e.g., `model/`, `feature/`, `benchmark/`). Each asset type
subfolder must contain a `specification.md` that defines the expected format and metadata.

## Step 6: Define Categories and Metrics

In `meta/categories/`, create folders for the initial set of tags relevant to your research domain.
Categories are like tags that can be assigned to tasks and assets for filtering.

In `meta/metrics/`, define the project-wide metrics that all tasks should report against, so results
are comparable across tasks. Using consistent metrics from the start is critical -- it enables
cross-task comparison and aggregation.

## Step 7: Launch the Project Agent

Task creation is handled by the project initialization AI agent, not manually. The agent analyzes
the research topic, creates the initial set of tasks (starting with a literature survey), and sets
up the correct folder structure, branches, and task metadata automatically.

The agent follows the ARF task lifecycle: it creates tasks via the suggestions chooser, populates
`task.json` and `step_tracker.json`, creates the appropriate git branches (`new_tasks/...` for
creation, `task/...` for execution), and hands off to task subagents for execution through the stage
sequence: research, plan, execute, analyze, report.

## Checklist

Before starting research tasks, verify:

* [ ] Git LFS is installed (`git lfs install`)
* [ ] `doctor.py` passes all checks
* [ ] `pyproject.toml` name and description updated for your project
* [ ] `CLAUDE.md` project description updated
* [ ] `project/description.md` created (run `/create-project-description`)
* [ ] Asset types reviewed and domain-specific types added
* [ ] Initial categories defined in `meta/categories/`
* [ ] Project-wide metrics defined in `meta/metrics/`
* [ ] Project agent launched to create initial tasks
