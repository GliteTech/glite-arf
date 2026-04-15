"""Aggregate machine provisioning logs across all tasks.

Reads ``machine_log.json`` files from setup-machines step directories and
produces a project-wide summary of GPU provisioning: costs, failure rates,
GPU tier breakdown, and per-task machine info.

Aggregator version: 1
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeGuard

from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_output_format_arg,
)
from arf.scripts.verificators.common.paths import TASKS_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SETUP_MACHINES_STEP_NAME: str = "setup-machines"
_MACHINE_LOG_FILENAME: str = "machine_log.json"

_FIELD_SELECTED_OFFER: str = "selected_offer"
_FIELD_GPU: str = "gpu"
_FIELD_TOTAL_COST_USD: str = "total_cost_usd"
_FIELD_TOTAL_PROVISIONING_SECONDS: str = "total_provisioning_seconds"
_FIELD_FAILED_ATTEMPTS: str = "failed_attempts"
_FIELD_FAILURE_REASON: str = "failure_reason"
_FIELD_WASTED_COST_USD: str = "wasted_cost_usd"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MachineSummary:
    total_machines: int
    total_failed_attempts: int
    failure_rate: float
    avg_provisioning_seconds: float | None
    total_cost_usd: float
    total_wasted_cost_usd: float
    gpu_tier_costs: dict[str, float]
    failure_reasons: dict[str, int]


@dataclass(frozen=True, slots=True)
class TaskMachineInfo:
    task_id: str
    machine_count: int
    total_cost_usd: float
    total_failed: int
    gpu_models: list[str]


@dataclass(frozen=True, slots=True)
class MachineAggregation:
    summary: MachineSummary
    tasks: list[TaskMachineInfo]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _MachineAccumulator:
    total_machines: int = 0
    total_failed_attempts: int = 0
    total_cost_usd: float = 0.0
    total_wasted_cost_usd: float = 0.0
    provisioning_seconds_values: list[float] = field(default_factory=list)
    gpu_tier_costs: dict[str, float] = field(default_factory=dict)
    failure_reasons: dict[str, int] = field(default_factory=dict)


def _is_number(value: object) -> TypeGuard[int | float]:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _find_machine_logs(*, task_id: str) -> list[Path]:
    steps_dir: Path = TASKS_DIR / task_id / "logs" / "steps"
    if not steps_dir.exists():
        return []
    results: list[Path] = []
    for step_dir in sorted(steps_dir.iterdir()):
        if not step_dir.is_dir():
            continue
        if _SETUP_MACHINES_STEP_NAME not in step_dir.name:
            continue
        log_path: Path = step_dir / _MACHINE_LOG_FILENAME
        if log_path.exists():
            results.append(log_path)
    return results


def _load_machine_log(*, log_path: Path) -> list[dict[str, Any]]:
    try:
        raw: Any = json.loads(log_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(raw, list):
        return []
    entries: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _extract_gpu_model(*, entry: dict[str, Any]) -> str | None:
    offer: object = entry.get(_FIELD_SELECTED_OFFER)
    if not isinstance(offer, dict):
        return None
    gpu: object = offer.get(_FIELD_GPU)
    if isinstance(gpu, str) and len(gpu) > 0:
        return gpu
    return None


def _process_entry(
    *,
    entry: dict[str, Any],
    acc: _MachineAccumulator,
) -> tuple[float, int, str | None]:
    acc.total_machines += 1

    cost: float = 0.0
    raw_cost: object = entry.get(_FIELD_TOTAL_COST_USD)
    if _is_number(raw_cost):
        cost = float(raw_cost)
        acc.total_cost_usd += cost

    gpu_model: str | None = _extract_gpu_model(entry=entry)
    if gpu_model is not None:
        acc.gpu_tier_costs[gpu_model] = acc.gpu_tier_costs.get(gpu_model, 0.0) + cost

    raw_prov: object = entry.get(_FIELD_TOTAL_PROVISIONING_SECONDS)
    if _is_number(raw_prov):
        acc.provisioning_seconds_values.append(float(raw_prov))

    failed_count: int = 0
    raw_failed: object = entry.get(_FIELD_FAILED_ATTEMPTS)
    if isinstance(raw_failed, list):
        for attempt in raw_failed:
            if not isinstance(attempt, dict):
                continue
            failed_count += 1
            acc.total_failed_attempts += 1

            reason: object = attempt.get(_FIELD_FAILURE_REASON)
            if isinstance(reason, str) and len(reason) > 0:
                acc.failure_reasons[reason] = acc.failure_reasons.get(reason, 0) + 1

            wasted: object = attempt.get(_FIELD_WASTED_COST_USD)
            if _is_number(wasted):
                acc.total_wasted_cost_usd += float(wasted)

    return cost, failed_count, gpu_model


def _process_task(
    *,
    task_id: str,
    acc: _MachineAccumulator,
) -> TaskMachineInfo | None:
    log_paths: list[Path] = _find_machine_logs(task_id=task_id)
    if len(log_paths) == 0:
        return None

    task_cost: float = 0.0
    task_failed: int = 0
    task_gpu_models: list[str] = []
    task_machine_count: int = 0

    for log_path in log_paths:
        entries: list[dict[str, Any]] = _load_machine_log(log_path=log_path)
        for entry in entries:
            cost, failed, gpu_model = _process_entry(
                entry=entry,
                acc=acc,
            )
            task_machine_count += 1
            task_cost += cost
            task_failed += failed
            if gpu_model is not None and gpu_model not in task_gpu_models:
                task_gpu_models.append(gpu_model)

    if task_machine_count == 0:
        return None

    return TaskMachineInfo(
        task_id=task_id,
        machine_count=task_machine_count,
        total_cost_usd=task_cost,
        total_failed=task_failed,
        gpu_models=task_gpu_models,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def aggregate_machines() -> MachineAggregation:
    acc: _MachineAccumulator = _MachineAccumulator()
    task_infos: list[TaskMachineInfo] = []

    if TASKS_DIR.exists():
        task_dirs: list[Path] = sorted(
            d for d in TASKS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
        for task_dir in task_dirs:
            info: TaskMachineInfo | None = _process_task(
                task_id=task_dir.name,
                acc=acc,
            )
            if info is not None:
                task_infos.append(info)

    total_attempts: int = acc.total_machines + acc.total_failed_attempts
    failure_rate: float = acc.total_failed_attempts / total_attempts if total_attempts > 0 else 0.0

    avg_prov: float | None = None
    if len(acc.provisioning_seconds_values) > 0:
        avg_prov = sum(acc.provisioning_seconds_values) / len(acc.provisioning_seconds_values)

    summary: MachineSummary = MachineSummary(
        total_machines=acc.total_machines,
        total_failed_attempts=acc.total_failed_attempts,
        failure_rate=failure_rate,
        avg_provisioning_seconds=avg_prov,
        total_cost_usd=acc.total_cost_usd,
        total_wasted_cost_usd=acc.total_wasted_cost_usd,
        gpu_tier_costs=dict(acc.gpu_tier_costs),
        failure_reasons=dict(acc.failure_reasons),
    )

    return MachineAggregation(
        summary=summary,
        tasks=task_infos,
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_json(*, aggregation: MachineAggregation) -> str:
    return json.dumps(asdict(aggregation), indent=2, ensure_ascii=False)


def _format_markdown_short(*, aggregation: MachineAggregation) -> str:
    s: MachineSummary = aggregation.summary
    lines: list[str] = [
        "# Machine Provisioning Summary",
        "",
        f"**{s.total_machines}** machines provisioned across"
        f" **{len(aggregation.tasks)}** tasks."
        f" Total cost: **${s.total_cost_usd:.2f}**.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Total machines | {s.total_machines} |",
        f"| Total failed attempts | {s.total_failed_attempts} |",
        f"| Failure rate | {s.failure_rate:.1%} |",
    ]

    if s.avg_provisioning_seconds is not None:
        lines.append(
            f"| Avg provisioning time | {s.avg_provisioning_seconds:.0f}s |",
        )
    else:
        lines.append("| Avg provisioning time | N/A |")

    lines.extend(
        [
            f"| Total cost | ${s.total_cost_usd:.2f} |",
            f"| Total wasted cost | ${s.total_wasted_cost_usd:.2f} |",
            "",
        ]
    )

    if len(aggregation.tasks) > 0:
        lines.extend(
            [
                "## Tasks",
                "",
                "| Task ID | Machines | Cost (USD) | Failed | GPUs |",
                "|---------|----------|------------|--------|------|",
            ]
        )
        for task in aggregation.tasks:
            gpu_str: str = ", ".join(task.gpu_models)
            lines.append(
                f"| `{task.task_id}` | {task.machine_count}"
                f" | ${task.total_cost_usd:.2f}"
                f" | {task.total_failed} | {gpu_str} |",
            )
        lines.append("")

    return "\n".join(lines)


def _format_markdown_full(*, aggregation: MachineAggregation) -> str:
    s: MachineSummary = aggregation.summary
    lines: list[str] = [
        "# Machine Provisioning Summary",
        "",
        f"**{s.total_machines}** machines provisioned across"
        f" **{len(aggregation.tasks)}** tasks."
        f" Total cost: **${s.total_cost_usd:.2f}**,"
        f" wasted: **${s.total_wasted_cost_usd:.2f}**.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Total machines | {s.total_machines} |",
        f"| Total failed attempts | {s.total_failed_attempts} |",
        f"| Failure rate | {s.failure_rate:.1%} |",
    ]

    if s.avg_provisioning_seconds is not None:
        lines.append(
            f"| Avg provisioning time | {s.avg_provisioning_seconds:.0f}s |",
        )
    else:
        lines.append("| Avg provisioning time | N/A |")

    lines.extend(
        [
            f"| Total cost | ${s.total_cost_usd:.2f} |",
            f"| Total wasted cost | ${s.total_wasted_cost_usd:.2f} |",
            "",
        ]
    )

    if len(s.gpu_tier_costs) > 0:
        lines.extend(
            [
                "## GPU Tier Costs",
                "",
                "| GPU Model | Cost (USD) |",
                "|-----------|------------|",
            ]
        )
        for gpu, cost in sorted(
            s.gpu_tier_costs.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"| {gpu} | ${cost:.2f} |")
        lines.append("")

    if len(s.failure_reasons) > 0:
        lines.extend(
            [
                "## Failure Reasons",
                "",
                "| Reason | Count |",
                "|--------|-------|",
            ]
        )
        for reason, count in sorted(
            s.failure_reasons.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"| {reason} | {count} |")
        lines.append("")

    if len(aggregation.tasks) > 0:
        lines.extend(
            [
                "## Tasks",
                "",
                "| Task ID | Machines | Cost (USD) | Failed | GPUs |",
                "|---------|----------|------------|--------|------|",
            ]
        )
        for task in aggregation.tasks:
            gpu_str: str = ", ".join(task.gpu_models)
            lines.append(
                f"| `{task.task_id}` | {task.machine_count}"
                f" | ${task.total_cost_usd:.2f}"
                f" | {task.total_failed} | {gpu_str} |",
            )
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, aggregation: MachineAggregation) -> str:
    return "\n".join(task.task_id for task in aggregation.tasks)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate machine provisioning logs across all tasks",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    args: argparse.Namespace = parser.parse_args()

    aggregation: MachineAggregation = aggregate_machines()

    if args.format == OUTPUT_FORMAT_JSON:
        print(_format_json(aggregation=aggregation))
    elif args.format == OUTPUT_FORMAT_MARKDOWN:
        if args.detail == DETAIL_LEVEL_FULL:
            print(_format_markdown_full(aggregation=aggregation))
        elif args.detail == DETAIL_LEVEL_SHORT:
            print(_format_markdown_short(aggregation=aggregation))
        else:
            print(f"Unknown detail level: {args.detail}", file=sys.stderr)
            sys.exit(1)
    elif args.format == OUTPUT_FORMAT_IDS:
        print(_format_ids(aggregation=aggregation))
    else:
        print(f"Unknown format: {args.format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
