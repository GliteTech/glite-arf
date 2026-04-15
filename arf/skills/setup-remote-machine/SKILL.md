---
name: "setup-remote-machine"
description: >-
  Provision, validate, monitor, and tear down remote GPU machines for task
  execution. Use when a task needs remote machine setup, monitoring, or
  teardown.
---
# Setup Remote Machine

**Version**: 3

## Goal

Provision a Vast.ai GPU instance, verify SSH connectivity and GPU availability, prepare the
execution environment, and make the machine ready for task execution. Also defines the teardown
protocol and execution monitoring procedures.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `0011-train-baseline-bert`)

## Context

Read before starting:

* `tasks/$TASK_ID/plan/plan.md` — Section 5 (Remote Machines) defines GPU requirements, estimated
  runtime, and budget
* `arf/specifications/remote_machines_specification.md` — machine_log.json schema, lifecycle states,
  price/performance protocol
* `arf/specifications/task_results_specification.md` — schemas for `remote_machines_used.json` and
  `costs.json`
* `project/budget.json` — per-task budget limit
* `arf/specifications/project_budget_specification.md` — `project/budget.json` schema and threshold
  rules
* `arf/scripts/utils/vast_machines.py` — Python library for programmatic provisioning (optional but
  recommended for automated retry and pre-validated filters)
* Current project spend and budget left — run:
  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_costs --format json --detail full
  ```

* * *

## Critical Rule

Wrap ALL CLI commands (`vastai`, `scp`, `ssh`) with `run_with_logs.py`:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  vastai search offers '...' --raw
```

The examples below show raw commands for clarity; always add the `run_with_logs.py` wrapper when
executing them.

* * *

## Steps

### Phase 1: Search for Optimal Machine

1. Read `tasks/$TASK_ID/plan/plan.md` Section 5 (Remote Machines). Extract:
   * Minimum GPU VRAM required
   * Minimum system RAM and disk space
   * Preferred GPU model (if any)
   * Estimated runtime on a reference GPU
   * Budget limit for this task

2. Build the search query. Determine the reliability threshold from the table in
   `arf/specifications/remote_machines_specification.md` based on estimated task duration:
   * Under 1h: `reliability>0.95`
   * 1-5h: `reliability>0.98`
   * 5-24h: `reliability>0.995`
   * Over 24h: `reliability>0.999`

   ```bash
   vastai search offers \
     'num_gpus=1 gpu_ram>=<MIN_VRAM> cpu_ram>=<MIN_RAM> \
     disk_space>=<MIN_DISK> reliability><THRESHOLD> \
     compute_cap<1200 cuda_max_good>=12.6 \
     rentable=true verified=true' \
     --order 'dph' --limit 20 --raw
   ```

   The `compute_cap<1200` filter blocks Blackwell-architecture GPUs (RTX 5090, RTX PRO 6000) whose
   sm_120 compute capability is incompatible with PyTorch 2.6.0. The `cuda_max_good>=12.6` filter
   blocks machines with CUDA drivers too old to run the container image. See
   `arf/specifications/remote_machines_specification.md` "Default Search Filters" for details.

   Add `gpu_name=<MODEL>` if the plan specifies a required model. For tasks over 5 hours, also add
   `duration>=<2x_estimated_hours/24>` to filter out machines that would evict before completion.

   For programmatic provisioning, use `arf.scripts.utils.vast_machines.build_query_string()` which
   encodes these filters automatically.

3. Record `search_started_at` as an ISO 8601 timestamp when the search begins. This will be used to
   calculate `total_provisioning_seconds` later.

4. Parse the JSON output. For all qualifying offers, calculate both `estimated_total_cost` and
   `estimated_hours` using the relative speed table from
   `arf/specifications/remote_machines_specification.md`:

   ```text
   estimated_hours = reference_hours / relative_speed
   estimated_total_cost = dph_total * estimated_hours
   ```

5. Find the cost-efficiency sweet spot per the specification Decision Steps: sort by
   `estimated_hours` (fastest first), then select the fastest GPU where stepping down to the next
   cheaper tier would add substantial wait time (>30 min) for modest savings (<$2-3). Do NOT simply
   pick the lowest `estimated_total_cost` — the user's waiting time has real cost. If two offers
   have similar `estimated_hours` (within 20%), prefer the cheaper one.

6. Check budget before provisioning:
   * Read the current project spend using:
     ```bash
     uv run python -u -m arf.scripts.aggregators.aggregate_costs --format json --detail full
     ```
   * If `estimated_total_cost > per_task_default_limit` from `project/budget.json`, create
     `tasks/$TASK_ID/intervention/budget_exceeded.md` and STOP.
   * If `stop_threshold_reached` is true or `estimated_total_cost > budget_left_before_stop_usd`,
     create `tasks/$TASK_ID/intervention/budget_exceeded.md` and STOP.
   * The intervention file must state which limit was exceeded and include the current remaining
     budget from the cost aggregator.

7. Log the search results and selection rationale. Initialize `machine_log.json` in the step log
   directory with `search_criteria`, `selected_offer`, `selection_rationale`, and
   `search_started_at` fields. Set `failed_attempts` to `[]`.

### Phase 1.5: Track Failed Attempts

If any offer fails during Phase 2-4 (creation timeout, SSH failure, GPU verification mismatch),
record a `failed_attempts` entry in `machine_log.json` before trying the next offer:

```json
{
  "offer_id": 12345,
  "instance_id": "34408778",
  "gpu": "RTX 5090",
  "failure_reason": "sm_120 compute capability not supported by PyTorch 2.6.0",
  "failure_phase": "gpu_verification",
  "duration_seconds": 180.0,
  "wasted_cost_usd": 0.12,
  "timestamp": "2026-04-05T10:30:00Z"
}
```

Destroy the failed instance before trying the next offer. After 3 consecutive failures, create an
intervention file and STOP.

### Phase 2: Create Instance

1. Create the instance:

   ```bash
   vastai create instance <OFFER_ID> \
     --image pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel \
     --ssh --disk <DISK_GB> --raw
   ```

   Use the latest stable PyTorch image that matches the required CUDA version. Prefer `devel` images
   (include CUDA compiler) over `runtime` images.

2. Extract `instance_id` from the response (`new_contract` field).

3. Update `machine_log.json` with `instance_id`, `offer_id`, `image`, `disk_gb`, and `created_at`
   timestamp.

4. Label the instance in the Vast.ai dashboard:

   ```bash
   vastai label instance <INSTANCE_ID> "$PROJECT/$TASK_ID"
   ```

   Record the label in `machine_log.json` as the `label` field. This makes instances identifiable in
   the provider dashboard.

5. Record the `instance_id` prominently in the step log so it can be found during teardown even if
   context is lost.

### Phase 3: Wait for Readiness

1. Poll instance status every 30 seconds:

   ```bash
   vastai show instance <INSTANCE_ID> --raw
   ```

2. Wait until `actual_status` is `"running"` (not just `cur_state == "running"` — the
   `actual_status` field reflects the real container state).

3. Extract `ssh_host` and `ssh_port` from the response.

4. Timeout: If the instance does not reach `"running"` within 10 minutes:
   * Destroy it: `vastai destroy instance <INSTANCE_ID>`
   * Log the failure
   * Try the next-best offer from Phase 1
   * If 3 consecutive offers fail, create an intervention file and STOP

5. Update `machine_log.json` with `ssh_host`, `ssh_port`, and `ready_at` timestamp. Calculate
   `total_provisioning_seconds` as the difference between `search_started_at` and `ready_at`.

### Phase 4: Verify SSH and GPU

1. Connect via SSH with retries (up to 5 attempts, 30 seconds apart):

   ```bash
   ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 \
     -i ~/.ssh/id_ed25519 -p <SSH_PORT> root@<SSH_HOST> \
     "echo connected"
   ```

   SSH key gotcha: keys must be registered on Vast.ai (`vastai show ssh-keys`). If authentication
   fails after the instance is running, the key may not be attached. Use
   `vastai attach ssh <INSTANCE_ID> "$(cat ~/.ssh/id_ed25519.pub)"` to attach it.

2. Verify GPU availability:

   ```bash
   ssh ... "nvidia-smi --query-gpu=name,memory.total,driver_version \
     --format=csv,noheader"
   ```

3. Verify CUDA:

   ```bash
   ssh ... "nvcc --version"
   ```

4. Check available disk space:

   ```bash
   ssh ... "df -h / | tail -1"
   ```

5. Update `machine_log.json` with `gpu_verified` and `cuda_version`.

6. If GPU verification fails (wrong GPU model, insufficient VRAM):
   * Destroy the instance
   * Log the discrepancy
   * Try another offer

### Phase 5: Prepare Environment

1. Copy data to the remote machine. Use `scp` for files under 100 MB, `vastai copy` for larger
   transfers:

   ```bash
   # Small files
   scp -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 \
     -P <SSH_PORT> <LOCAL_PATH> root@<SSH_HOST>:<REMOTE_PATH>

   # Large files/directories
   vastai copy <LOCAL_PATH> <INSTANCE_ID>:<REMOTE_PATH>
   ```

2. Install additional dependencies if needed:

   ```bash
   ssh ... "pip install <packages>"
   ```

3. Verify the environment by running a smoke test:

   ```bash
   ssh ... "python -c 'import torch; print(torch.cuda.is_available())'"
   ```

4. Log the list of files copied and packages installed.

5. If the plan estimates >2 hours of runtime, configure checkpointing:
   * Set up the training script to save checkpoints every 30 minutes
   * Record the checkpoint save path in `machine_log.json` as `checkpoint_path`
   * Configure the training script to write a heartbeat file every 5 minutes with current epoch,
     step, loss, and timestamp. Record the path as `heartbeat_path`
   * Training scripts should handle `SIGTERM` gracefully: save a final checkpoint before exiting
   * See `arf/specifications/remote_machines_specification.md` "Mandatory Checkpointing" for details

* * *

## Execution on Remote Machines

This section is referenced by the `implementation` step in execute-task, not by `setup-machines`.

### Running Long Jobs

ALWAYS use `tmux` for long-running jobs so they survive SSH disconnection:

```bash
# Start a detached tmux session
ssh ... "tmux new-session -d -s work \
  'python train.py > /root/output.log 2>&1; echo DONE >> /root/output.log'"
```

### Monitoring

* Check if the job is running:
  ```bash
  ssh ... "tmux has-session -t work 2>/dev/null && echo running || echo finished"
  ```

* Tail logs:
  ```bash
  ssh ... "tail -50 /root/output.log"
  ```

* Reconnect to tmux (interactive, for debugging):
  ```bash
  ssh -p <SSH_PORT> root@<SSH_HOST> -t "tmux attach -t work"
  ```

* Check instance cost accumulation:
  ```bash
  vastai show instance <INSTANCE_ID> --raw | \
    python3 -c "import sys,json; d=json.load(sys.stdin); \
    cost=d['dph_total']*d['client_run_time']/3600; \
    print(f'Running {d[\"client_run_time\"]:.0f}s, cost ~${cost:.4f}')"
  ```

* Check whether the instance is still alive:
  ```bash
  vastai show instance <INSTANCE_ID> --raw | \
    python3 -c "import sys,json; d=json.load(sys.stdin); \
    print(f'Status: {d[\"actual_status\"]}')"
  ```

### Handling Disconnection

If the SSH connection drops during a long job:

1. Verify instance is still running via `vastai show instance`
2. Reconnect and check tmux: `ssh ... "tmux ls"`
3. Tail the output log to check progress
4. The job continues inside tmux regardless of SSH disconnection

* * *

## Teardown Protocol

This section is executed during the `teardown` step of execute-task.

### Steps

1. Verify job completion on the remote machine:

   ```bash
   ssh ... "tmux has-session -t work 2>/dev/null && echo STILL_RUNNING || echo DONE"
   ```

   If still running, wait or investigate. NEVER destroy a machine with an active job unless
   explicitly instructed.

2. Download results from the remote machine:

   ```bash
   scp -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 \
     -P <SSH_PORT> -r root@<SSH_HOST>:<REMOTE_RESULTS_DIR> \
     tasks/$TASK_ID/<LOCAL_DEST>
   ```

3. Verify all expected output files are present locally. List expected files from `plan/plan.md`
   Section 7 (Expected Assets) and confirm each was downloaded.

4. Destroy the instance:

   ```bash
   vastai destroy instance <INSTANCE_ID>
   ```

5. Confirm destruction by polling:

   ```bash
   vastai show instance <INSTANCE_ID> --raw
   ```

   The instance should return an error or show a terminated state. Poll up to 3 times with 10-second
   intervals.

6. Update `machine_log.json`:
   * Set `destroyed_at` to the current ISO 8601 timestamp
   * Calculate `total_duration_hours` from `created_at` to `destroyed_at`
   * Set `total_cost_usd` — calculate from `dph_total` (from the last `vastai show instance` output
     before destruction) multiplied by `total_duration_hours`

7. Update results files. Use exactly the field names shown below — do not use aliases from
   `machine_log.json` (e.g., use `ram_gb` not `gpu_ram_gb`, `duration_hours` not
   `total_duration_hours`, `machine_id` not `instance_id`).

   `results/remote_machines_used.json` — add a machine entry with all required fields:

   ```json
   [
     {
       "provider": "vast.ai",
       "machine_id": "<INSTANCE_ID>",
       "gpu": "RTX-4090",
       "gpu_count": 1,
       "ram_gb": 64,
       "duration_hours": 2.5,
       "cost_usd": 2.00
     }
   ]
   ```

   `results/costs.json` — add the machine cost to `breakdown` using key format
   `"vast-ai-<gpu-model-lowercase>"`:

   ```json
   {
     "total_cost_usd": 2.00,
     "breakdown": {
       "vast-ai-rtx4090": 2.00
     }
   }
   ```

   See `arf/specifications/task_results_specification.md` for the full schema.

8. Run the machine destruction verificator:

   ```bash
   uv run python -m arf.scripts.verificators.verify_machines_destroyed \
     --task-id $TASK_ID
   ```

   Fix any errors before proceeding.

* * *

## Done When

* `machine_log.json` exists with all required fields populated including v2 fields:
  `search_started_at`, `total_provisioning_seconds`, `failed_attempts`, `label`
* Instance labeled in Vast.ai dashboard with `"$PROJECT/$TASK_ID"`
* SSH connection verified and `nvidia-smi` output logged
* All data and scripts copied to the remote machine
* Smoke test (`torch.cuda.is_available()`) passes
* For jobs >2h: `checkpoint_path` and `heartbeat_path` set in `machine_log.json`
* Step log written with machine specs, search rationale, and SSH details

For teardown:

* All results downloaded and verified locally
* Instance destroyed and confirmed
* `machine_log.json` has `destroyed_at` and `total_cost_usd`
* `remote_machines_used.json` and `costs.json` updated
* `verify_machines_destroyed.py` passes with no errors

* * *

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER leave an instance running without a corresponding `teardown` step in `step_tracker.json`

* NEVER skip the budget check in Phase 1

* NEVER destroy a machine while a job is still running (unless the user explicitly instructs it)

* NEVER commit or hardcode SSH private keys, API keys, or instance credentials — use
  `~/.ssh/id_ed25519` or read paths from environment

* NEVER use `vastai copy` to copy to `/root` or `/` as destination (breaks SSH permissions)
