# 1. Set Up a Project

First of five tutorials. By the end of the series you will have an ARF project with one completed
task, a refreshed dashboard, and a results page on GitHub.

## What You'll Build

A tiny project called **MyResearch** that studies image augmentation. This part lays the skeleton:
GitHub repo, environment, description, budget, project-specific metadata, and the first task plan.

## Step 1: Fork the ARF Repository

ARF lives in a single GitHub repository. Fork it on github.com — click **Fork**, name the new repo
`myproject`, then clone your fork locally:

```bash
git clone git@github.com:<you>/myproject.git ~/myproject
cd ~/myproject
```

The fork already contains everything you need: the `arf/` directory (skills, verificators,
aggregators, specifications), `doctor.py` (the environment validator), [`meta/`](../../../meta/)
with default asset types, categories, metrics, and task types, and the top-level tooling files
(`pyproject.toml`, `uv.lock`, `ruff.toml`, etc.). No template, no copy-paste — just fork and go.

## Step 2: Run setup-project

The [`setup-project`](../../skills/setup-project/SKILL.md) skill is the canonical onboarding path
for a fresh fork. It shows the safety acknowledgement, prepares the environment, runs `doctor.py`,
creates `project/description.md` and `project/budget.json`, provisions declared paid services,
populates `meta/`, replaces the template README, and starts a first `/human-brainstorm` session.

Invoke it from the repo root:

```text
/setup-project   # Claude Code
$setup-project   # Codex
```

The skill asks about the project goal, scope, research questions, success criteria, key references,
budget, services, categories, metrics, task types, and first tasks. Answer in your own words. It
maps your answers to the required specs and runs the relevant verificators.

For this tutorial, tell the skill: a small project that studies image augmentation on CIFAR-10 with
ResNet-18, $100 budget, OpenAI and Anthropic APIs available.

When the skill finishes, `project/description.md` and `project/budget.json` exist and pass
verification, `meta/` has been populated for the project, the root README is project-specific, and
the first task has been planned or explicitly deferred.

## Next

Skeleton ready. Continue to [2. Review meta/](02_customize_meta.md) to inspect what setup created
and make any final adjustments before running real tasks.
