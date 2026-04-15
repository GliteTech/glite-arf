# Remote Machines

## Why Remote Machines

Research workloads are bursty. Most tasks need nothing beyond a laptop: a literature survey, a plan,
a brainstorm. A few tasks need a GPU for hours at a time: training a model, running a sweep,
benchmarking inference. Buying a GPU for the bursty ones wastes money. Running everything on a
laptop wastes time.

ARF solves this by treating remote compute as a rentable resource that tasks can spin up on demand,
use, and destroy. The task that needs the GPU pays for exactly the minutes it runs. The next task
starts from nothing.

## Automatic Lifecycle

When a task's plan declares that it needs remote compute, the
[`execute-task`](../../skills/execute-task/SKILL.md) orchestrator runs two optional steps around the
main work:

1. **`setup-machines`** — invoke
   [`setup-remote-machine`](../../skills/setup-remote-machine/SKILL.md). The skill searches a
   provider (currently Vast.ai) for offers matching the plan's GPU requirements, selects one by
   minimizing estimated total cost, creates the instance, waits for it to reach `ready`, verifies
   SSH and GPU via `nvidia-smi`, and writes a `machine_log.json` into the step log folder.
2. **`implementation`** — runs the task's work on the provisioned machine, streaming output through
   [`run_with_logs.py`](../../scripts/utils/run_with_logs.py) into the task's `logs/`.
3. **`teardown`** — destroy every machine the task created. This step is not optional in spirit: a
   verificator (`verify_machines_destroyed`) runs at task completion and blocks the PR if any
   instance is still alive. Leaving machines running is the single fastest way to burn a budget.

Every machine passes through a fixed state sequence:

```text
searching -> creating -> waiting -> ready -> in-use -> destroying -> destroyed
```

## Selection: Price vs Performance

Plans declare GPU requirements as minimum specifications (e.g., "at least one A100 40GB, CUDA 12+,
at least 200 GB disk"). The setup skill queries the provider, filters to matching offers, and picks
the one that minimizes **estimated total cost** = hourly rate × estimated runtime. A cheaper hourly
rate on a slower GPU sometimes wins; a faster GPU sometimes wins on total cost. The selection and
its rationale are recorded in `machine_log.json` as `selected_offer` and `selection_rationale`, so
reviewers can audit the decision later.

### Pre-validated Filters

Every search query includes `compute_cap<1200 cuda_max_good>=12.6` by default. These block
Blackwell-architecture GPUs (RTX 5090, RTX PRO 6000) whose sm_120 compute capability is incompatible
with PyTorch 2.6.0, and machines with CUDA drivers too old to run the container image.

### Instance Labeling

After creation, each instance is labeled with `"<project>/<task_id>"` in the provider dashboard.
This makes running machines identifiable without cross-referencing logs.

### Provisioning Library

The `arf.scripts.utils.vast_machines` module provides a Python API wrapping the official Vast.ai
SDK. It encodes default filters, the GPU speed tier table, reliability thresholds, and the
cost-efficiency ranking algorithm.

## Failed Attempt Tracking

When provisioning fails (GPU incompatibility, SSH failure, creation timeout), each attempt is
recorded in `machine_log.json` as a `failed_attempts` entry with the offer ID, GPU model, failure
reason, failure phase, duration, and wasted cost. This data feeds
[`aggregate_machines`](../../scripts/aggregators/aggregate_machines.py) for cross-task visibility
into provisioning reliability and waste.

## Checkpointing

Jobs estimated at more than 2 hours must configure checkpoint saving every 30 minutes. Training
scripts should write a heartbeat file every 5 minutes. Both paths are recorded in
`machine_log.json`. The verificator warns (`RM-W006`) when a long job has no `checkpoint_path` set.

## Cost Tracking

Machine costs flow into two places:

* **`tasks/<task_id>/results/costs.json`** — the task's own cost file, with `vast_ai` or similar as
  a service entry and the hours × rate total.
* **`tasks/<task_id>/results/remote_machines_used.json`** — one record per machine with its
  provider, instance ID, GPU model, duration, and exact cost.

Both files feed [`aggregate_costs`](../../scripts/aggregators/aggregate_costs.py) and the
[`overview/costs/`](../../../overview/costs/) dashboard page. Budget enforcement lives in
`project/budget.json`: the setup-machines step reads the current spend via `aggregate_costs`, adds
its own estimate, and refuses to provision if the total would exceed the stop threshold. The plan
must either shrink or the budget must be raised explicitly.

## Verification

Three verificators enforce the rules:

* `verify_machines_destroyed` — every machine in `machine_log.json` reached state `destroyed`.
* `verify_task_results` — `remote_machines_used.json` is present and well-formed whenever the task
  used remote compute.
* `verify_pr_premerge` — the task's total cost plus the project's running total stays within budget.

A task cannot merge unless all three pass. This is the guardrail that catches the most expensive
kind of agent mistake: forgetting to tear down an instance.

## When a Task Needs Remote Compute

The decision belongs to the [`planning`](../../skills/planning/SKILL.md) skill. During planning, the
agent estimates whether the work fits on the local machine. If not, it writes a "Remote Machines"
section in `plan/plan.md` specifying the minimum GPU, the estimated runtime, and the cost estimate.
The orchestrator reads this and decides whether to run `setup-machines`.

Tasks that do not need GPUs skip the whole remote-machines path. No cost, no machine log, no
teardown step.

## Prerequisites

Remote machine support currently uses **Vast.ai** as the compute provider. Install the Vast.ai CLI
before running any task that needs remote compute:

```bash
pip install vastai
vastai set api-key YOUR_API_KEY
```

The API key is available from your [Vast.ai account page](https://cloud.vast.ai/account/). The
`setup-remote-machine` skill calls `vastai` commands directly, so the CLI must be on `$PATH` and
authenticated before task execution begins.

## See Also

* [Setup-remote-machine skill](../../skills/setup-remote-machine/SKILL.md)
* [Remote machines specification](../../specifications/remote_machines_specification.md)
* [Provisioning library](../../scripts/utils/vast_machines.py) — Python API for Vast.ai
* [Machine usage aggregator](../../scripts/aggregators/aggregate_machines.py) — cross-task stats
* [Task lifecycle](task_lifecycle.md) — where setup-machines and teardown fit into task phases
