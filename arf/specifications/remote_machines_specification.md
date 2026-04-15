# Remote Machines Specification

**Version**: 2

* * *

## Purpose

This specification defines the protocol, data formats, and verification rules for provisioning and
managing remote GPU machines during task execution. It covers the full machine lifecycle from search
through destruction, the price/performance decision protocol, and how machine data integrates with
the existing cost and results tracking.

**Producer**: The `setup-machines` and `teardown` steps of the task execution skill, implemented by
the `/setup-remote-machine` skill. The `arf.scripts.utils.vast_machines` library provides
programmatic access to the provisioning protocol.

**Consumers**:

* **Task execution agents** — follow this protocol during GPU tasks
* **Verificator scripts** — confirm machines are destroyed and costs logged
* **Aggregator scripts** — collect machine usage data across tasks (`aggregate_machines`,
  `aggregate_costs`)
* **Human reviewers** — audit GPU spend at checkpoints

* * *

## Machine Lifecycle

Every remote machine goes through these states in order:

```text
searching -> creating -> waiting -> ready -> in-use -> destroying -> destroyed
```

| State | Description |
| --- | --- |
| `searching` | Querying provider for available offers |
| `creating` | Instance creation request sent, awaiting confirmation |
| `waiting` | Instance created, waiting for `actual_status == "running"` |
| `ready` | SSH verified, GPU confirmed, environment prepared |
| `in-use` | Task execution running on the machine |
| `destroying` | Destruction request sent |
| `destroyed` | Instance confirmed destroyed by provider |

A machine must reach `destroyed` before the task can be marked complete. Any machine that does not
reach `destroyed` is a verification error.

* * *

## machine_log.json

The primary tracking file for remote machine usage. Created during the `setup-machines` step and
updated during `teardown`. Located in the setup-machines step log directory:

```text
tasks/<task_id>/logs/steps/NNN_setup-machines/machine_log.json
```

### Schema

A JSON array of machine objects. Most tasks use a single machine, but multi-GPU distributed tasks
may use several.

### Fields (per machine object)

| Field | Type | Required | Set during | Description |
| --- | --- | --- | --- | --- |
| `provider` | string | yes | creating | Cloud provider (e.g., `"vast.ai"`) |
| `instance_id` | string | yes | creating | Provider-specific instance ID |
| `offer_id` | int | yes | creating | Offer ID used to create the instance |
| `search_criteria` | object | yes | searching | Filters used (see below) |
| `selected_offer` | object | yes | searching | Details of the chosen offer (see below) |
| `selection_rationale` | string | yes | searching | Why this offer minimizes estimated total cost |
| `image` | string | yes | creating | Docker image used |
| `disk_gb` | int | yes | creating | Disk space allocated in GB |
| `label` | string\|null | no | creating | Instance label in provider dashboard (e.g., `"my-project/t0042_train"`) |
| `ssh_host` | string | yes | ready | SSH hostname |
| `ssh_port` | int | yes | ready | SSH port |
| `gpu_verified` | string | yes | ready | GPU model confirmed by `nvidia-smi` |
| `cuda_version` | string | yes | ready | CUDA version from `nvidia-smi` |
| `created_at` | string | yes | creating | ISO 8601 timestamp |
| `ready_at` | string | yes | ready | ISO 8601 timestamp |
| `destroyed_at` | string\|null | yes | destroyed | ISO 8601 timestamp, `null` until destroyed |
| `total_duration_hours` | float\|null | yes | destroyed | Hours from `created_at` to `destroyed_at` |
| `total_cost_usd` | float\|null | yes | destroyed | Final cost from provider, `null` until known |
| `search_started_at` | string | v2 | searching | ISO 8601 timestamp when offer search began |
| `total_provisioning_seconds` | float | v2 | ready | Wall-clock seconds from `search_started_at` to `ready_at` |
| `failed_attempts` | array | v2 | searching–ready | Failed provisioning attempts before success (see below) |
| `checkpoint_path` | string\|null | no | ready | Remote path where training checkpoints are saved |
| `heartbeat_path` | string\|null | no | ready | Remote path to heartbeat file updated by training script |

Fields marked "v2" are required for new machine_log.json files. Existing v1 files without these
fields remain valid — verificators and aggregators handle their absence gracefully.

### search_criteria Object

| Field | Type | Description |
| --- | --- | --- |
| `gpu_name` | string\|null | Required GPU model (e.g., `"RTX_4090"`) |
| `num_gpus` | int | Number of GPUs needed |
| `min_gpu_ram` | float\|null | Minimum per-GPU VRAM in GB |
| `min_cpu_ram` | float\|null | Minimum system RAM in GB |
| `min_disk` | float\|null | Minimum disk space in GB |
| `min_reliability` | float | Minimum reliability score (see thresholds below) |
| `extra_filters` | string\|null | Any additional vastai query filters |

### selected_offer Object

| Field | Type | Description |
| --- | --- | --- |
| `offer_id` | int | Vast.ai offer ID |
| `gpu` | string | GPU model name |
| `gpu_count` | int | Number of GPUs |
| `gpu_ram_gb` | float | Per-GPU VRAM in GB |
| `cpu_ram_gb` | float | Total system RAM in GB |
| `disk_gb` | float | Available disk space in GB |
| `price_per_hour` | float | Total $/hour (GPU + storage) |
| `reliability` | float | Machine reliability score |
| `location` | string | Geographic location |

### failed_attempts Array

Each element records one provisioning attempt that failed before the successful machine was created.
The array is empty (`[]`) when the first attempt succeeds.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `offer_id` | int | yes | Vast.ai offer ID that was attempted |
| `instance_id` | string\|null | yes | Instance ID if creation succeeded before failure; `null` if creation itself failed |
| `gpu` | string | yes | GPU model of the attempted offer |
| `failure_reason` | string | yes | Human-readable description of what went wrong |
| `failure_phase` | string | yes | One of: `"search"`, `"creation"`, `"waiting"`, `"gpu_verification"`, `"ssh"` |
| `duration_seconds` | float | yes | Seconds spent on this attempt before abandoning |
| `wasted_cost_usd` | float | yes | Cost incurred by this failed attempt (`0.0` if instance never reached billing) |
| `timestamp` | string | yes | ISO 8601 timestamp when the attempt started |

### Example

```json
[
  {
    "provider": "vast.ai",
    "instance_id": "33920288",
    "offer_id": 33661505,
    "search_criteria": {
      "gpu_name": null,
      "num_gpus": 1,
      "min_gpu_ram": 10.0,
      "min_cpu_ram": 16.0,
      "min_disk": 100.0,
      "min_reliability": 0.95,
      "extra_filters": null
    },
    "selected_offer": {
      "offer_id": 33661505,
      "gpu": "RTX 2080 Ti",
      "gpu_count": 1,
      "gpu_ram_gb": 11.0,
      "cpu_ram_gb": 21.4,
      "disk_gb": 158.0,
      "price_per_hour": 0.0614,
      "reliability": 0.995,
      "location": "Ohio, US"
    },
    "selection_rationale": "Estimated 4h job. RTX 2080 Ti at $0.061/h = $0.25 total. Next option (RTX 4070 at $0.069/h) is 1.5x faster but only saves ~1.3h, netting $0.05 more total.",
    "image": "pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel",
    "disk_gb": 100,
    "label": "my-project/t0042_train_model",
    "ssh_host": "ssh6.vast.ai",
    "ssh_port": 10288,
    "gpu_verified": "NVIDIA GeForce RTX 2080 Ti",
    "cuda_version": "12.8",
    "created_at": "2026-03-31T22:25:00Z",
    "ready_at": "2026-03-31T22:28:30Z",
    "destroyed_at": "2026-03-31T23:45:00Z",
    "total_duration_hours": 1.33,
    "total_cost_usd": 0.08,
    "search_started_at": "2026-03-31T22:20:00Z",
    "total_provisioning_seconds": 510.0,
    "failed_attempts": [
      {
        "offer_id": 33661400,
        "instance_id": "33920200",
        "gpu": "RTX 5090",
        "failure_reason": "sm_120 compute capability not supported by PyTorch 2.6.0",
        "failure_phase": "gpu_verification",
        "duration_seconds": 180.0,
        "wasted_cost_usd": 0.12,
        "timestamp": "2026-03-31T22:20:00Z"
      }
    ],
    "checkpoint_path": null,
    "heartbeat_path": null
  }
]
```

* * *

## Instance Labeling

After creating an instance, label it in the provider dashboard so humans can identify which project
and task each machine belongs to. Use the format `"<project-name>/<task_id>"`:

```bash
vastai label instance <INSTANCE_ID> "my-project/$TASK_ID"
```

Record the label in `machine_log.json` as the `label` field. This has no effect on billing or
lifecycle — it is purely for dashboard readability.

* * *

## Default Search Filters

Every search query MUST include these filters to prevent known-incompatible hardware:

```text
compute_cap<1200 cuda_max_good>=12.6
```

* `compute_cap<1200` — blocks Blackwell-architecture GPUs (RTX 5090, RTX PRO 6000 S/WS) whose sm_120
  compute capability is not supported by PyTorch 2.6.0 or earlier. Remove this filter only after
  verifying that the task's PyTorch version supports sm_120.
* `cuda_max_good>=12.6` — blocks machines with CUDA drivers too old (e.g., driver 535.x only
  supports CUDA 12.2) to run the container image. Adjust the version to match the image's CUDA
  requirement.

These filters are encoded as `DEFAULT_FILTERS` in `arf.scripts.utils.vast_machines` and are applied
automatically when using the library.

* * *

## Price/Performance Decision Protocol

The goal is to find the **best price/performance balance** within budget. The user's waiting time
has real cost — spending $3 extra to save 5 hours is almost always worth it. But spending $50 extra
for a 10% speedup is not. Never optimize purely for minimum cost at the expense of the user's time.

### Formula

```text
estimated_total_cost = price_per_hour * estimated_hours(gpu_tier)
```

### GPU Relative Speed Tiers

Use these approximate relative speeds for common training/inference workloads (normalized to RTX
3090 = 1.0x):

| GPU | VRAM | Relative Speed | Typical $/hr Range |
| --- | --- | --- | --- |
| GTX 1080 Ti | 11 GB | 0.35x | $0.04-0.08 |
| RTX 2080 Ti | 11 GB | 0.55x | $0.05-0.10 |
| RTX 3060 | 12 GB | 0.40x | $0.03-0.07 |
| RTX 3070 | 8 GB | 0.60x | $0.06-0.10 |
| RTX 3080 | 10 GB | 0.80x | $0.08-0.15 |
| RTX 3090 | 24 GB | 1.0x | $0.10-0.20 |
| RTX 4070 | 12 GB | 0.90x | $0.06-0.12 |
| RTX 4070 Ti | 12 GB | 1.05x | $0.07-0.15 |
| RTX 4080 | 16 GB | 1.30x | $0.15-0.25 |
| RTX 4090 | 24 GB | 1.60x | $0.20-0.40 |
| RTX 5060 Ti | 16 GB | 1.00x | $0.07-0.20 |
| RTX 5070 Ti | 16 GB | 1.50x | $0.09-0.12 |
| RTX 5090 | 32 GB | 2.50x | $0.30-0.65 |
| A100 40GB | 40 GB | 1.80x | $0.50-1.00 |
| A100 80GB | 80 GB | 2.00x | $0.80-1.50 |
| H100 | 80 GB | 3.00x | $1.50-3.00 |
| H200 | 141GB | 3.50x | $2.30-2.60 |
| RTX PRO 6000 S | 96 GB | 2.80x | $0.73-1.12 |
| RTX PRO 6000 WS | 96 GB | 2.80x | $0.90-1.33 |

These are rough estimates. Actual performance depends on model size, batch size, and memory
requirements. When VRAM is the bottleneck (model does not fit), only GPUs with sufficient VRAM
should be considered.

### Reliability Thresholds

Machine reliability is critical, especially for long-running tasks where a crash means restarting
hours of work. Use these minimum thresholds based on estimated task duration:

| Estimated Duration | Min Reliability | Rationale |
| --- | --- | --- |
| Under 1 hour | 0.95 | Short jobs, easy to retry |
| 1-5 hours | 0.98 | Moderate risk from restarts |
| 5-24 hours | 0.995 | High cost of restart |
| Over 24 hours | 0.999 | Only very stable machines |

When filtering offers, always apply the reliability threshold from the table above. A machine with
99.5% reliability has a ~12% chance of failing during a 24-hour job. At 99.9%, the risk drops to
~2.4%.

For tasks over 5 hours, also prefer machines with `max_days` (maximum rental duration) greater than
2x the estimated duration to avoid forced eviction.

### Decision Steps

1. Determine minimum VRAM required for the task
2. Filter offers to those meeting VRAM, RAM, disk, and reliability requirements. Always include the
   default search filters (`compute_cap<1200 cuda_max_good>=12.6`) to block incompatible hardware
3. For all qualifying offers, calculate both `estimated_total_cost` and `estimated_hours` using the
   relative speed table
4. Eliminate offers where `estimated_total_cost` exceeds the task budget
5. Sort remaining offers by `estimated_hours` (fastest first)
6. Find the cost-efficiency sweet spot: starting from the fastest offer, check whether stepping down
   to a slower GPU tier saves significant money relative to the time it adds. Select the fastest GPU
   where stepping down to the next cheaper tier would add substantial wait time (>30 min) for modest
   savings (<$2-3). In other words: pay 3x more for 2x speedup (good trade), but don't pay 20x more
   for 10% speedup (bad trade)
7. Document the rationale in `selection_rationale` including estimated time, estimated cost, and why
   this GPU was chosen over faster and cheaper alternatives

* * *

## Mandatory Checkpointing

Jobs estimated at more than 2 hours MUST configure checkpoint saving to protect against instance
eviction, crashes, or SSH disconnection. A full restart of a multi-hour training run wastes both
time and money.

### Requirements

* Save a checkpoint every 30 minutes (at minimum) to a known path on the remote machine
* Record the checkpoint path in `machine_log.json` as `checkpoint_path`
* Training scripts should handle `SIGTERM` gracefully: save a final checkpoint before exiting
* On re-provisioning after a failure, the implementation step must check for existing checkpoints
  and resume from the latest one

### Heartbeat

Training scripts should write a heartbeat file every 5 minutes containing the current epoch, step,
loss, and timestamp. Record the path in `machine_log.json` as `heartbeat_path`. The monitoring agent
can poll this file via SSH to detect silent crashes (heartbeat age > 2× the expected interval).

Example heartbeat content:

```json
{"epoch": 3, "step": 1200, "loss": 0.42, "timestamp": "2026-04-05T14:30:00Z"}
```

### Jobs under 2 hours

Checkpointing is optional but recommended. The `checkpoint_path` and `heartbeat_path` fields may be
`null`.

* * *

## Cost Integration

Machine costs must be recorded in two places:

### 1. costs.json

Add a line item to `breakdown` using the format `"vast-ai-<gpu_model_lowercase>"`:

```json
{
  "total_cost_usd": 2.50,
  "breakdown": {
    "claude-opus": 2.00,
    "vast-ai-rtx-2080-ti": 0.50
  }
}
```

### 2. remote_machines_used.json

Follow the schema in `arf/specifications/task_results_specification.md`:

```json
[
  {
    "provider": "vast.ai",
    "machine_id": "33920288",
    "gpu": "RTX 2080 Ti",
    "gpu_count": 1,
    "ram_gb": 21,
    "duration_hours": 1.33,
    "cost_usd": 0.08
  }
]
```

The `machine_id` must match `instance_id` from `machine_log.json`. The `cost_usd` must match
`total_cost_usd` from `machine_log.json`.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `RM-E001` | `machine_log.json` lists a machine without `destroyed_at` |
| `RM-E002` | Vast.ai API confirms instance is still running/active |
| `RM-E003` | `machine_log.json` is missing or not valid JSON |
| `RM-E004` | A required field is missing from a machine entry |
| `RM-E005` | `instance_id` in `machine_log.json` does not match `machine_id` in `remote_machines_used.json` |
| `RM-E006` | `total_cost_usd` in `machine_log.json` does not match `cost_usd` in `remote_machines_used.json` |

### Warnings

| Code | Description |
| --- | --- |
| `RM-W001` | Vast.ai API unreachable (cannot confirm destruction, but `destroyed_at` is present) |
| `RM-W002` | Actual cost exceeds plan estimate by more than 50% |
| `RM-W003` | Machine was running for more than 12 hours |
| `RM-W004` | `selection_rationale` is empty or under 20 characters |
| `RM-W005` | A `failed_attempts` entry is missing required sub-fields |
| `RM-W006` | Job ran more than 2 hours but no `checkpoint_path` is set |
