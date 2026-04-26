---
name: "setup-project"
description: >-
  One-shot interactive onboarding for a newly forked Glite ARF template. Shows
  the safety acknowledgement, installs dependencies, runs doctor.py, chains
  into create-project-description, provisions the paid services the project
  declared, then invokes the four meta/ sub-skills. Use once per fork, right
  after cloning.
---
# Setup Project

**Version**: 7

## Goal

Take a freshly forked Glite ARF repository from clone to ready-to-run-first-task through a single
interactive dialogue: capture the safety acknowledgement, install dependencies, validate the
environment, guide project description and budget creation, and populate `meta/` with the project's
categories, metrics, task types, and any extra asset types.

## Inputs

* `$ARGUMENTS` — ignored. The skill always runs the same workflow.

## Context

Read before starting:

* `arf/docs/explanation/safety.md` — autonomy and safety document quoted verbatim in Phase 1.
* `README.md` "Bootstrap a new project" section — the canonical onboarding flow this skill
  implements.
* `arf/specifications/project_description_specification.md` — required for Phase 3 verification.
* `arf/specifications/project_budget_specification.md` — required for Phase 3 verification.
* `arf/skills/create-project-description/SKILL.md` — the skill chained in Phase 3.
* `arf/skills/add-category/SKILL.md`, `arf/skills/add-metric/SKILL.md`,
  `arf/skills/add-task-type/SKILL.md`, `arf/skills/add-asset-type/SKILL.md` — chained in Phase 5.
* `arf/styleguide/agent_instructions_styleguide.md` — governs how this skill is written.
* `doctor.py` — the environment validator run in Phase 2.

## Steps

### Phase 1: Safety acknowledgement

1. Read `arf/docs/explanation/safety.md` and print a **summary** to the user with exactly these five
   bullet points, each in one sentence:
   * Shell and filesystem access in task worktrees
   * Git commits and pushes on the user's behalf
   * Paid LLM API usage that can cost tens to hundreds of dollars
   * Remote GPU provisioning on vast.ai that costs real money per minute
   * Prompt injection from downloaded papers and web content
2. Immediately after the summary, print the full text of `arf/docs/explanation/safety.md` inline so
   the user can read the complete document without leaving the session.
3. Ask exactly: "Type `I understand and accept these risks` to proceed, or anything else to cancel."
   Wait for the user's input.
4. If the user's reply is not the exact string `I understand and accept these risks` (case and
   punctuation included), print `Setup cancelled. Re-run /setup-project when ready.` and exit
   without touching any files.

### Phase 2: Environment preparation

5. Confirm the repository looks like a fresh fork: `project/` does not exist or is empty,
   `meta/categories/` has no subdirectories, `meta/metrics/` has no subdirectories. If any of those
   checks fail, print what was found and ask: "This repo has existing project configuration. Type
   `continue anyway` to overwrite it or anything else to cancel." Only proceed on the exact string
   `continue anyway`.

6. Ensure `uv` is installed:
   * Run `uv --version`. If it exits `0`, move on.
   * If `uv` is missing, propose the official Astral installer:
     * macOS or Linux → `curl -LsSf https://astral.sh/uv/install.sh | sh`
     * Windows (PowerShell) →
       `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   * Show the exact command and ask: "Install uv with `<command>`? Type `yes` to run it or anything
     else to cancel." Run the command only on the exact string `yes`. On anything else, print the
     manual install instructions from <https://docs.astral.sh/uv/> and exit so the user can install
     it themselves, then re-run `/setup-project`.
   * After install, confirm `uv --version` now exits `0`. If not, exit with
     `uv install did not register on PATH. Open a new shell and re-run /setup-project.`

7. Install Python dependencies:

   ```bash
   uv sync
   ```

8. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

9. Ensure git LFS is installed and configured:
   * Run `git lfs version`. If it exits `0`, run `git lfs install` and move on.
   * If `git lfs` is missing, detect the platform with `uname -s`:
     * `Darwin` → propose `brew install git-lfs`
     * `Linux` (check `/etc/os-release` for `ID=ubuntu` or `ID=debian`) → propose
       `sudo apt-get install -y git-lfs`
    * Any other platform → print <https://git-lfs.com/> instructions and exit with
      `Install git-lfs manually, then re-run /setup-project.`
   * Show the user the exact command and ask: "Install git-lfs with `<command>`? Type `yes` to run
     it or anything else to cancel." Run the command only on the exact string `yes`.
   * After install, run `git lfs install` to register hooks.

10. Ensure `direnv` trusts the repo's `.envrc`:
    * If `.envrc` does not exist in the repo root, skip this step.
    * Run `direnv status 2>&1`. If the output contains `Found RC allowed 1`, the file is already
      trusted — move on.
    * If `direnv` is not installed (`command -v direnv` fails), tell the user that `doctor.py` will
      block on this, point them at `brew install direnv` on macOS or
      `sudo apt-get install -y direnv` on Debian/Ubuntu, remind them to add the shell hook per
      <https://direnv.net/docs/hook.html>, and exit so they can install it themselves.
    * If the `.envrc` is not allowed, ask: "Allow direnv to load this repo's `.envrc`? This lets
      direnv activate the project's virtualenv automatically. Type `yes` to run `direnv allow` or
      anything else to cancel." Run `direnv allow` only on the exact string `yes`. On cancel, print
      `doctor.py will block until you run direnv allow manually.` and exit.

11. Run `python3 doctor.py` and surface its output verbatim to the user. If `doctor.py` reports any
    blocker (non-zero exit), print `Fix the blockers above and re-run /setup-project.` and exit. Do
    not proceed to Phase 3.

### Phase 3: Project description and budget

12. Print one line — `Running /create-project-description now.` — then immediately read
    `arf/skills/create-project-description/SKILL.md` and follow every step of that skill's dialogue
    inline in this conversation until its own `Done When` is satisfied. Do not pause for user
    confirmation to kick it off; the user already accepted setup in Phase 1. Do not ask the skill's
    questions here — ask them the way that skill specifies them.

13. After `create-project-description` returns, confirm both files exist:

    ```bash
    uv run python -u -m arf.scripts.verificators.verify_project_description
    uv run python -u -m arf.scripts.verificators.verify_project_budget
    ```

    If either verificator reports errors, stop and tell the user to re-run
    `/create-project-description` to fix them before continuing.

### Phase 4: Paid service provisioning

Paid services are declared by `create-project-description` in `project/budget.json` under
`available_services`. Canonical slugs are `openai_api`, `anthropic_api`, `vast_ai` (see
`arf/scripts/verificators/common/project_budget.py` for the alias map). This phase verifies
credentials only for services that are actually declared, and lets the user drop a service from the
project when they do not want to provide credentials.

14. Load `project/budget.json`, read `available_services`. If the list is empty, print
    `No paid services declared; skipping provisioning.` and advance to Phase 5.

15. For each slug in `available_services`, dispatch to the matching block below. After any block
    that edits `project/budget.json`, re-run
    `uv run python -u -m arf.scripts.verificators.verify_project_budget` and fix any errors before
    continuing.

    **`openai_api`**:
    * Read `.env`. If it contains a non-empty `OPENAI_API_KEY=` line, print
      `OPENAI_API_KEY present in .env — ok.` and move on.
    * Otherwise ask: "This project declares `openai_api` but no OPENAI_API_KEY is set. Paste the key
      now, type `skip` to remove `openai_api` from `project/budget.json` (you will use a different
      LLM provider or local models), or type `cancel` to stop setup."
    * On a pasted key: sanity-check it is non-empty and at least 20 characters long. Append
      `OPENAI_API_KEY=<pasted>` to `.env`; create `.env` with that single line if the file does not
      exist. Confirm with `grep -c "^OPENAI_API_KEY=" .env`. Never echo the pasted key.
    * On `skip`: edit `project/budget.json` to drop `"openai_api"` from `available_services`. Re-run
      `verify_project_budget`.
    * On `cancel`: print `Setup paused. Re-run /setup-project when ready.` and exit.

    **`vast_ai`**:
    * Run `uv run vastai show user 2>&1`. If it exits `0` and prints a username, print
      `vastai authenticated — ok.` and move on.
    * Otherwise ask: "This project declares `vast_ai` but vastai is not authenticated. Paste your
      vast.ai API key now, type `create` for account signup instructions, type `skip` to remove
      `vast_ai` from `project/budget.json` (all training will run locally; `/setup-remote-machine`
      will refuse to run until `vast_ai` is re-added), or type `cancel` to stop setup."
    * On a pasted key: run `uv run vastai set api-key <pasted>`, then re-check with
      `vastai show user`. Never echo the pasted key.
    * On `create`: print the signup URL <https://cloud.vast.ai/create_account> and the key page
      <https://cloud.vast.ai/account/>, then re-ask the question. Loop until the user pastes a key,
      types `skip`, or types `cancel`.
    * On `skip`: edit `project/budget.json` to drop `"vast_ai"` from `available_services`. Re-run
      `verify_project_budget`. Tell the user that `/setup-remote-machine` will now refuse to run.
    * On `cancel`: as above.

    **`anthropic_api`**: tell the user Anthropic credentials are managed by the Claude Code or Codex
    CLI they are running, no key file is needed, and move on. Nothing else to do.

    **Any other slug**: tell the user the service is declared but `/setup-project` has no
    provisioning block for it, so credentials for it must be handled manually. Do not exit; move on
    to the next slug.

### Phase 5: Customize meta/

16. Read `project/description.md` into context so subsequent sub-skills inherit it.

17. For each of the four sub-skills below, in the order listed, do the following without asking the
    user for confirmation between them:
    * Print one line — `Running /<skill-name> to populate meta/<area>/.`
    * Read `arf/skills/<skill-name>/SKILL.md` and follow every step of that skill's dialogue inline
      in this conversation, passing `project/description.md` as the `$ARGUMENTS` path.
    * When the skill's `Done When` is satisfied, print the count of entries that were added, then
      move to the next skill.

    Skills to run, in order:
    * `add-category`
    * `add-metric`
    * `add-task-type`
    * `add-asset-type`

### Phase 6: Generate project README

18. Replace the template `README.md` at the repo root with a project-specific version. Read
    `project/description.md`, `project/budget.json`, and list the entries in `meta/categories/`,
    `meta/metrics/`, `meta/task_types/`. Write `README.md` with the following sections in order:

    * `# <Project Title>` — from the `#` heading in `project/description.md`.
    * `## Goal` — the 2-5 sentence goal from `project/description.md`.
    * `## Research Questions` — the numbered list from `project/description.md`.
    * `## Success Criteria` — the bulleted list from `project/description.md`.
    * `## Current Phase` — from `project/description.md`.
    * `## Results Dashboard` — one line linking to `overview/README.md` for aggregated results,
      metrics, and task status.
    * `## Getting Started` — for new contributors to the configured project: clone the repo, run
      `uv sync`, install hooks if needed, and run `python3 doctor.py`. Tell them not to run
      `/setup-project` again unless they intentionally want to re-initialize a fresh fork. 3-6
      lines.
    * `## Daily Workflow` — quick links to `/create-task`, `/execute-task`, brainstorming, and
      regenerating `overview/README.md`. Keep under 10 lines.
    * `## Key Rules` — the verificator-enforced rules for anyone working in the repo: CLI
      wrapping with `run_with_logs`, task isolation, commit per step, immutability + corrections,
      read through aggregators, register metrics before reporting. Copy these from the template
      README's "Key rules" section.
    * `## Project Structure` — the top-level directory layout tree from the template README.
    * `## Categories` — bulleted list of category slugs with display names.
    * `## Metrics` — bulleted list of every key under `meta/metrics/` with its display name and
      unit.
    * `## Task Types` — bulleted list of every slug under `meta/task_types/` with its display name
      (mark the generic template types separately from project-specific ones if any were added).
    * `## Budget and Services` — one line with total budget, currency, and the final
      `available_services` list.
    * `## Documentation` — links to `arf/docs/explanation/safety.md`, `arf/docs/tutorial/`,
      `arf/docs/reference/`, and the style guides.
    * `## License` — keep the same license as the template (Apache 2.0) unless the user says
      otherwise.

    Do **not** include: the template's "Who made this" section, "Is Glite ARF right for me?", "What
    Glite ARF gives you", "Source of truth", "Contributing", "Citing Glite ARF", or badge URLs.
    Those are template-level content that does not belong in a project fork.

19. Run `uv run flowmark --inplace --nobackup README.md` to normalize formatting.

20. Show the user the generated README and ask: "Review the project README. Should I change
    anything?" Apply any requested edits and re-run flowmark after each round. After user
    confirmation, commit with message `Replace template README with project-specific version`.

### Phase 7: Wrap-up and first tasks

21. Print a summary to the user with:
    * The final `available_services` list from `project/budget.json` after Phase 4 edits.
    * The number of entries added in each of `meta/categories/`, `meta/metrics/`,
      `meta/task_types/`, `meta/asset_types/`.
    * The list of files now present under `project/`.

22. Print one line — `Running /human-brainstorm to plan first tasks.` — then immediately read
    `arf/skills/human-brainstorm/SKILL.md` and follow every step of that skill's dialogue inline in
    this conversation until its own `Done When` is satisfied. The project is brand-new so
    aggregators will return empty results for tasks, suggestions, and metrics — that is expected.
    The brainstorm session should focus on translating the project description and research
    questions into concrete first tasks (typically a literature survey, dataset download, or
    baseline experiment). See `arf/docs/tutorial/` for the recommended first-task patterns.

## Done When

* The user typed the exact acknowledgement phrase in Phase 1.
* `uv sync`, `uv run pre-commit install`, and `python3 doctor.py` all completed successfully, or the
  skill exited cleanly after telling the user which blocker to fix.
* Either `git lfs install` ran successfully, or the user declined the install prompt and the skill
  exited with manual install instructions.
* `project/description.md` exists and passes `verify_project_description`.
* `project/budget.json` exists and passes `verify_project_budget` both before and after Phase 4.
* Phase 4 either verified credentials for every slug in `available_services`, or the user explicitly
  dropped the slug and `verify_project_budget` still passes.
* Each of `/add-category`, `/add-metric`, `/add-task-type`, `/add-asset-type` was invoked and the
  user saw its result.
* `README.md` was replaced with the project-specific version, flowmark-normalized, user-confirmed,
  and committed.
* The `/human-brainstorm` dialogue completed and the user has at least one task planned or
  explicitly deferred task creation.

## Forbidden

* NEVER proceed past Phase 1 without the exact acknowledgement string. Any other reply ends the
  skill.
* NEVER skip `python3 doctor.py`. Blockers must be surfaced to the user.
* NEVER echo a pasted API key back to the chat or to any log.
* NEVER write anything to `meta/` directly from this skill. Delegate to the sub-skills.
* NEVER edit `project/budget.json` `available_services` without re-running `verify_project_budget`
  afterwards.

(Framework-wide rule: no `tasks/tXXXX_*` folders for any setup or infrastructure work — see
`CLAUDE.md` rule 0.)
