# Autonomy and Safety

Glite ARF runs AI agents (Claude Code and OpenAI Codex CLI) **autonomously** with high permissions.
This page documents what that means, what risks you accept by using the framework, what ARF does to
contain mistakes, and what you must do on your side to keep those mistakes bounded.

If you are evaluating whether to fork ARF for your own research, read this page before you do.

## What the agents can do

When a task is running, the agent in that task's worktree can:

* Create, modify, and delete any file inside the task's worktree
* Execute arbitrary shell commands through `uv run`, `git`, `gh`, and any installed tool
* Read any file under the repository root — including `.env`, `uv.lock`, and other secrets if
  present
* Create branches, commit, and `git push` to your GitHub repository
* Open, comment on, and merge pull requests via the `gh` CLI
* Make paid API calls to LLM providers (Anthropic, OpenAI, OpenRouter, etc.)
* Fetch arbitrary web pages and download arbitrary files from the internet
* Provision remote GPU instances on vast.ai and run arbitrary code on them

Completed task folders are immutable under the framework's own rules, but those rules are enforced
by verificators that run *after* a step. They do not prevent an agent from writing to a completed
folder mid-step; they detect that it happened and fail the step.

## Risks you are accepting

### Shell and filesystem access

Every task runs commands in a worktree on your machine. A buggy skill, a poisoned input, or an agent
that misreads its instructions can delete or overwrite files anywhere inside that worktree — and,
with shell access, anywhere the user running the agent can reach. Running ARF inside a container or
VM limits blast radius to the container.

### Git and GitHub operations

Agents commit and push branches on your behalf using your git credentials. Without branch protection
on `main`, an agent that misroutes a push can overwrite history on your default branch. With branch
protection in place — which the framework recommends — the worst case becomes a junk branch and a
bad PR, which you reject.

### Paid LLM API usage

A single task typically costs between a few cents and a few dollars in LLM tokens. A project with
dozens or hundreds of tasks, retries, and long-context agents can cost tens to hundreds of dollars.
Set hard spend caps with your LLM provider. Do not use a personal API key with your credit card
attached to an uncapped account.

### Remote machine provisioning

The `setup-remote-machine` skill rents real GPU instances on vast.ai using your API key. These cost
real money by the minute. The framework enforces a `project/budget.json` check before provisioning
and a teardown verificator at the end — but a bug, a misconfigured key, or a failed teardown can
leave an instance running. Use a vast.ai API key scoped to a dedicated account or subaccount with an
enforced spend cap.

### Data sent to LLM providers

Every task sends your code, task descriptions, paper summaries, intermediate results, and in many
cases your raw data to the configured LLM provider. Check the provider's terms for training opt-out,
retention, and geographic restrictions before pointing ARF at confidential inputs. For
security-sensitive work, use a provider and plan that contractually excludes your prompts from
training.

### Prompt injection

ARF downloads papers, scrapes web pages, and reads arbitrary internet content during research
stages. Any of that content can carry instructions aimed at hijacking the agent ("ignore your prior
instructions and…"). Skill and verificator design try to isolate untrusted content, but prompt
injection is an unsolved problem. Treat anything the agent fetches from the open internet as
potentially adversarial.

## What ARF does to contain mistakes

* **Task isolation.** Each task runs in its own worktree on its own branch. One task cannot touch
  another task's folder at the filesystem level without tripping the folder-boundary verificator.
* **Specifications + verificators.** Every artifact has a shape it must satisfy. A verificator runs
  after each step and blocks progress if the shape is wrong, catching the most common agent mistakes
  (truncated outputs, fabricated fields, misplaced files) before they reach `main`.
* **PR-gated workflow.** Every task ends in a pull request. Nothing lands on `main` without passing
  CI and, ideally, human review.
* **Immutability + corrections.** Completed task folders are frozen. If later work finds a mistake
  in an earlier task, the fix is a correction overlay in a new task folder — not an edit of the old
  one. Your history stays auditable.
* **Budget gating.** Expensive steps (remote machines, large batch LLM calls) check
  `project/budget.json` before starting and write an intervention file instead of spending when the
  cap would be exceeded.
* **Intervention files.** When an agent hits something it cannot resolve automatically (missing
  credential, human approval, cost overrun), it creates an intervention file and stops rather than
  guessing.

These contain mistakes. They do not eliminate them. An agent can still waste money, leak data to the
LLM provider, or push a bad PR before a verificator catches it.

## What you must do

Before you run ARF on anything that matters:

* **Run in a container or VM if you need OS-level isolation.** The easiest path is a devcontainer or
  a disposable cloud VM with a fresh GitHub account scoped to the ARF project.
* **Use dedicated API keys, per provider, with hard spend caps.** Never reuse a personal uncapped
  key. LLM providers typically let you set monthly spend limits; use them.
* **Enable branch protection on `main`.** Require PRs and passing CI. ARF's workflow assumes this;
  without it, an agent push can overwrite history.
* **Review every PR before merging.** Do not auto-merge ARF PRs. The verificator layer catches shape
  mistakes; only a human catches "the model fabricated these results".
* **Keep `project/budget.json` tight.** The budget gate only works if the number in the file
  reflects what you are actually willing to spend.
* **Treat external content as untrusted.** Papers, web pages, datasets pulled from the open internet
  can carry prompt injection. When reviewing a PR that consumed external content, look for outputs
  that do not match the task instructions — that is the tell.
* **Rotate keys if a task logs them.** ARF's logging tries to scrub secrets from captured stdout,
  but capture-and-scrub is best-effort. Treat any key that appears in a worktree as compromised.

## Not a substitute for judgment

ARF's guardrails are designed to catch mistakes agents reliably make. They are not designed to catch
a user pointing an autonomous agent at production data with an uncapped API key and no branch
protection. You are responsible for what the agents do under your account, with your credentials, on
your infrastructure.

If in doubt: start small. Run the tutorial project. Watch what the agent does. Tighten the budget
and the sandbox before you scale up.
