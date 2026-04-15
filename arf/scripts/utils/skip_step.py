"""Utility to mark a step as skipped and create its step log.

Creates the step log directory, writes a minimal step_log.md with the
required frontmatter and sections, and updates step_tracker.json.

Usage:
    uv run python -m arf.scripts.utils.skip_step <task_id> <step_id> "<reason>"

Multiple steps can be skipped in one invocation:
    uv run python -m arf.scripts.utils.skip_step <task_id> \
        <step_id_1> "<reason_1>" <step_id_2> "<reason_2>"

Exit codes:
    0 — all steps skipped successfully
    1 — error (step not found, task missing, etc.)
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    step_tracker_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIELD_STEPS: str = "steps"
FIELD_STEP: str = "step"
FIELD_NAME: str = "name"
FIELD_STATUS: str = "status"
FIELD_LOG_FILE: str = "log_file"
FIELD_STARTED_AT: str = "started_at"
FIELD_COMPLETED_AT: str = "completed_at"

STATUS_NOT_STARTED: str = "not_started"
STATUS_SKIPPED: str = "skipped"

# Statuses this utility will accept as input. `not_started` is the normal
# first-time skip path; `skipped` makes re-invocation idempotent so the
# orchestrator can safely replay batch skips without losing tracker state.
ALLOWED_INPUT_STATUSES: frozenset[str] = frozenset(
    {STATUS_NOT_STARTED, STATUS_SKIPPED},
)

STEP_LOG_SPEC_VERSION: str = "3"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SkipRequest:
    step_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class SkipResult:
    step_id: str
    step_number: int
    log_dir: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_step(
    *,
    steps: list[dict[str, object]],
    step_id: str,
) -> dict[str, object] | None:
    for step in steps:
        if step.get(FIELD_NAME) == step_id:
            return step
    return None


def _build_step_log(
    *,
    task_id: str,
    step_number: int,
    step_id: str,
    reason: str,
    timestamp: str,
) -> str:
    summary: str = (
        f"Step {step_number} ({step_id}) was skipped during execution of task"
        f" {task_id} by the execute-task orchestrator, which elected not to run"
        f" this optional step. Reason recorded by the orchestrator at skip"
        f" time: {reason}"
    )
    return (
        f"---\n"
        f'spec_version: "{STEP_LOG_SPEC_VERSION}"\n'
        f'task_id: "{task_id}"\n'
        f"step_number: {step_number}\n"
        f'step_name: "{step_id}"\n'
        f'status: "skipped"\n'
        f'started_at: "{timestamp}"\n'
        f'completed_at: "{timestamp}"\n'
        f"---\n"
        f"\n"
        f"# {step_id} (skipped)\n"
        f"\n"
        f"## Summary\n"
        f"\n"
        f"{summary}\n"
        f"\n"
        f"## Actions Taken\n"
        f"\n"
        f"1. Step skipped: {reason}\n"
        f"2. Created minimal step log for audit trail.\n"
        f"\n"
        f"## Outputs\n"
        f"\n"
        f"No outputs — step skipped.\n"
        f"\n"
        f"## Issues\n"
        f"\n"
        f"No issues encountered.\n"
    )


def skip_steps(
    *,
    task_id: str,
    requests: list[SkipRequest],
) -> list[SkipResult]:
    """Mark steps as skipped and create their step logs.

    Returns a list of SkipResult for each successfully skipped step.
    Exits with code 1 on any error.
    """
    tracker_file: Path = step_tracker_path(task_id=task_id)
    if not tracker_file.exists():
        print(
            f"Error: step_tracker.json not found for task {task_id}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        tracker: dict[str, object] = json.loads(
            tracker_file.read_text(encoding="utf-8"),
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"Error: cannot read step_tracker.json: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    raw_steps: object = tracker.get(FIELD_STEPS)
    if not isinstance(raw_steps, list):
        print(
            "Error: step_tracker.json has no 'steps' list",
            file=sys.stderr,
        )
        sys.exit(1)

    steps: list[dict[str, object]] = [s for s in raw_steps if isinstance(s, dict)]

    task_dir: Path = TASKS_DIR / task_id
    timestamp: str = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: list[SkipResult] = []

    for req in requests:
        step: dict[str, object] | None = _find_step(
            steps=steps,
            step_id=req.step_id,
        )
        if step is None:
            print(
                f"Error: step '{req.step_id}' not found in step_tracker.json",
                file=sys.stderr,
            )
            sys.exit(1)

        current_status: object = step.get(FIELD_STATUS)
        if current_status not in ALLOWED_INPUT_STATUSES:
            allowed: str = ", ".join(sorted(ALLOWED_INPUT_STATUSES))
            print(
                f"Error: step '{req.step_id}' has status"
                f" '{current_status}', expected one of: {allowed}",
                file=sys.stderr,
            )
            sys.exit(1)

        already_skipped: bool = current_status == STATUS_SKIPPED

        step_number: object = step.get(FIELD_STEP)
        assert isinstance(step_number, int), f"step number is int for {req.step_id}"

        log_dir_name: str = f"{step_number:03d}_{req.step_id}"
        log_dir: Path = task_dir / "logs" / "steps" / log_dir_name
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file: Path = log_dir / "step_log.md"

        # On first skip, always write the step log. On re-skip of an
        # already-skipped step, only write the log if it is missing —
        # this keeps a healthy re-invocation byte-for-byte idempotent
        # and preserves the original skip timestamp in the frontmatter.
        if not already_skipped or not log_file.exists():
            step_log_content: str = _build_step_log(
                task_id=task_id,
                step_number=step_number,
                step_id=req.step_id,
                reason=req.reason,
                timestamp=timestamp,
            )
            log_file.write_text(step_log_content, encoding="utf-8")

        step[FIELD_STATUS] = STATUS_SKIPPED

        log_rel: str = f"logs/steps/{log_dir_name}/"
        step[FIELD_LOG_FILE] = log_rel

        results.append(
            SkipResult(
                step_id=req.step_id,
                step_number=step_number,
                log_dir=log_rel,
            ),
        )

    tracker_file.write_text(
        json.dumps(tracker, indent=2) + "\n",
        encoding="utf-8",
    )

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=("Mark steps as skipped and create their step logs."),
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g., t0061_ablation_study)",
    )
    parser.add_argument(
        "pairs",
        nargs="+",
        help=('Pairs of step_id and reason: <step_id> "<reason>" [<step_id> "<reason>" ...]'),
    )
    args: argparse.Namespace = parser.parse_args()

    pairs: list[str] = args.pairs
    if len(pairs) % 2 != 0:
        print(
            "Error: arguments must be pairs of <step_id> <reason>",
            file=sys.stderr,
        )
        sys.exit(1)

    requests: list[SkipRequest] = []
    for i in range(0, len(pairs), 2):
        requests.append(
            SkipRequest(step_id=pairs[i], reason=pairs[i + 1]),
        )

    results: list[SkipResult] = skip_steps(
        task_id=args.task_id,
        requests=requests,
    )

    for r in results:
        print(
            f"Skipped step {r.step_number:03d}_{r.step_id} -> {r.log_dir}",
        )

    print(f"\n{len(results)} step(s) skipped.")


if __name__ == "__main__":
    main()
