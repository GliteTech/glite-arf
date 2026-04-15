# Glite ARF Overview

This document describes the Glite Autonomous Research Framework (Glite ARF). "ARF" is used as the
short form throughout the framework's internal docs, skills, and specifications.

## Problems

* AI working autonomously creates a mess
* AI tends to write long texts that people don't read or understand
* If something didn't work in subagents it is difficult to understand what went wrong

## Fundamental Principles

* Task Isolation: Full isolation of tasks, one task = one folder, the ONLY exception is adding
  dependencies to `pyproject.toml` and other global Python-related files like `uv.lock`,
  `ruff.toml`, `.gitignore`, `mypy.ini`
* Immutability of Completed Tasks + Corrections Overlay: After the task is completed nothing in the
  task folder can be changed. A verification script is launched after each step to ensure that
  nothing in other task folders was changed in the task branch
* Structure Enforced by Scripts (Verificators): Very rigid structure enforced by scripts
  (verificators). Without verification all other principles won't work as AI agents are not 100%
  reliable and in a large project the errors accumulate
* No Duplication
* Comprehensive Logging: Mandatory logging with structure verification makes AI work debuggable
* Subagent Isolation: Each task is done in an independent subagent working in its own branch, in its
  own Git worktree folder

## Secondary Principles

* Everything are files in the repo; the framework does not use databases, third-party task trackers,
  etc.
* The whole project is done in a separate repository
* Visualize all results as charts and graphs; humans will read them
* Virtual documents: scripts that collect assets from task folders into virtual asset files
* Materialized asset collections and LLM context archives only for human review via GitHub
* Task ids combine number ids for easy sorting with a slug for human understanding, but must start
  with a letter (`t`) for Python to work with task folders
* Checkpoints for human evaluation
* Every single step should be logged; presence and structure of all logs is enforced by scripts
* Each task is done in an individual branch and results in a PR
* Each task stage and each action in each stage is a separate well-described commit
* No data duplication, full normalization of data. Each data lives in the corresponding JSON/MD file
  in the corresponding folder and when we need collective data they are collected by scripts
* New tasks can only be created by one single-thread system/skill called suggestions chooser; there
  are manual and autonomous modes or research
* Later downstream tasks can correct all results (results, metrics, assets, etc.) of previously done
  tasks, not by changing anything in previous task folders but by creating special files that record
  what is corrected by what. This is needed in case we find later mistakes in already completed
  tasks
* Some tasks may require human interventions (capture, accepting agreement to download a dataset,
  costs over budget, etc.); they generate special intervention files
* All task-branch command line tool calls after worktree creation are wrapped in
  `uv run python -m arf.scripts.utils.run_with_logs`
* No human interventions for everything that can be resolved automatically, such as merging
  conflicts
* If tasks are executed in parallel in separate branches, duplication of assets like
  papers/suggestions is possible. It is solved by special deduplication tasks that find duplicates
  and use the correction mechanism to remove them

## Solutions

* Recommended first steps for internet/papers review
* Each task and each asset can be assigned to any category; categories act like tags
* Each task also produces predefined things suggestions (hypothesis) and metrics; metrics can be a
  single flat set or multiple named variants within one task

## Glossary

* task - an atomic operation in this project (aka step or subproject), each located in its own
  folder
* category - a tag that can be assigned to papers and other types of assets that allow filtering;
  each category should be a folder in `meta/categories/`
* agent (aka skill)
* verificator - a Python script that checks certain rules to help LLM-based agents not deviate from
  specified rules
* aggregator - a Python script that combines one type of data from different tasks into one output;
  it supports filtering by categories and/or task ids
* suggestion - a task candidate, either a hypothesis or downloading of a new dataset, or developing
  a new library, etc.
* metrics - registered quantitative measurements that can be reported either once per task or once
  per task variant
* plan - task execution plan that includes which remote machines to use, budget estimation, etc.
* step - one step in task execution, usually run by an independent subagent of the task agent
* dependency
* cost - includes all third-party costs of this task, including paid API costs like OpenAI and paid
  third-party compute like Vast.ai
* checkpoints
* corrections - a mechanism for later downstream tasks to correct anything (metrics, assets, etc.)
  of previously done tasks in aggregators
* materialized aggregators
* LLM context archives under `overview/llm-context/`
* asset type - a type of possible task output such as paper, dataset, library, answer, etc. All
  asset types are defined in `meta/asset_types` and there is a subfolder with the asset type name in
  `assets`
* logs - detailed logs describing all process of researching, planning, executing and analysing each
  step of each task. Log format is specified in `arf/specifications/logs_specification.md`

## Aggregators

Each aggregator is a Python script that can return all data and filtered data by category and/or
task ids:

* Tasks
* Completed tasks
* Suggestions
* All answers
* All papers
* All assets such as features, datasets, etc.
* All results
* All result summaries (2 levels of shortness)

## Assets

* Everything tasks produce are assets
* Assets could be of different types
* Predefined asset types: papers, datasets, libraries, answers, suggestions, models, predictions

## Task Properties

* Name
* short description
* status (`no_started`, `cancelled`, `in_process`, `completed`, `permanently_failed`,
  `intervention_blocked`)
* dependency
* start time
* end time
* expected_assets: how many and which assets are expected to be produced by this task: datasets,
  libraries, papers, answers, models, predictions

## Task Subagents

Most task steps are executed by subagents. The task agents keep track of execution in
`step_tracker.json` in the task folder.

* Each task is done in an independent subagent that goes through mandatory stages using subagents
* Task stage subagent: research in the existing papers. First read short summaries to decide which
  categories are needed, then get more detail and if needed full papers. This skill should produce a
  summary of all knowledge from downloaded papers about how to perform the task in the best way
* Task stage subagent: research on the internet and papers not yet found, downloading and
  summarizing all relevant papers using a separate skill. This skill should produce a summary of all
  human knowledge related to how to perform this task in the best way
* Task stage subagent: research in previous tasks and summarizing all relevant findings. This skill
  should produce a summary of all relevant previously written code, libraries, datasets, and other
  assets from previously completed tasks, etc.
* Task stage subagent: answering one or more explicit questions into answer assets, using papers,
  internet sources, and/or code experiments as evidence
* Task stage subagent: planning
* Task stage subagent: creating remote machine(s) if needed
* Task stage subagent: implementation with usage of remote machines if needed
* Task stage subagent: destroying remote machine(s) if needed
* Task stage subagent: creative out-of-the-box thinking
* Task stage subagent: comparison to literature
* Task stage subagent: results summarization
* Task stage subagent: formulating new suggestions
* Task stage subagent: post-task reporting (W&B, etc.)
* Paper downloading and summarizing: creates a new agent; correctness of format is verified by a
  verificator script

## Checkpoint

* Rematerialization of all aggregators and LLM context archives
* Reviewing all done tasks with recommendations on what to change in the process/agents
* Reports

## Other Skills

* Suggestions chooser
* Creating a new task based on suggestion; it should define dependency, etc.
* Adding new category
* Adding new metrics

## Verificators

Verification scripts can produce errors and warnings. Both are optional for the agents but there
should be VERY serious reasons to continue if there are errors.

* logs are created
* dependency validation before starting a task: all dependency task IDs exist, all dependencies have
  status completed, and if a dependency's assets were corrected by a downstream task a warning is
  flagged
* assets are created and in needed format; this folder should contain only subfolders, one for each
  asset type, which themselves contain subfolders for each asset
* task results are created and in needed format
* no other tasks are affected and no files outside this task folder are created
* git repo rules are followed: a new branch is created with the right name, commits for each step,
  PR, merge, etc.
* research files are in the correct place, long enough, and have needed sections
* suggestion validation: suggestion files have needed format and warnings if no suggestion files
* result files are in the correct place and contain needed sections
* task completed correctly
* paper duplication finder
* correction format verification
* step starting prerequisites: for each type of step check that all required prerequisites are ready
* intervention

## Mandatory Task Folder Structure

* assets folder with subfolders for each asset type
* corrections folder with specially formatted files that can either delete or replace any
  asset/metric/result/suggestion/etc. of previous tasks
* intervention folder with list of all human interventions needed to start or continue this task
* logs folder with subfolders for subagents
* plan folder with `plan.md` that should have at least the following mandatory sections: Objective,
  Approach, Cost Estimation, Step by Step, Remote Machines, Assets Needed, Expected Assets, Time
  Estimation, Risks & Fallbacks, Verification Criteria
* research folder with all research results: `research_papers.md`, `research_internet.md`,
  `research_code.md`
* results folder with at least the following files: `results_summary.md`, `results_detailed.md`,
  `metrics.json`, `suggestions.json`, `costs.json`, `remove_machines_used.json`. It should also
  contain an `images` subfolder with all charts/graphs/etc. `metrics.json` may use either the legacy
  flat format or the explicit multi-variant format
* `step_tracker.json` - task plan and tracker; it should initially be populated with all the steps
  and stages and tracked
* `task.json` - includes name, one-sentence description, one-paragraph description, long
  description, dependency, status, costs

## Misc

* all paper assets are named by DOI
* plan must contain list of all needed assets, types of machines needed, estimation of costs, time
  estimation, new libraries to install
* script for creating a log for starting a task, script for creating a log for completing a task
* task folders are named `tXXXX_slug` (`t` prefix + 4-digit number + underscore slug, e.g.,
  `t0002_recent_papers`), valid Python identifiers for absolute imports (max 9999 tasks)

## Naming Convensions

* branch naming convention: task branch `task/<task_id>`, creating new tasks:
  `new_tasks/<first_task_index>-<last_task_index>`

## Known Issues

* Even the simplest tasks, such as downloading one paper, that usually take about 1 minute in this
  framework take much longer
