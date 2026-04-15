"""Tests for the aggregate_machines aggregator.

Tests are written before the implementation exists. They define the
expected contract for MachineAggregation, MachineSummary, and
TaskMachineInfo dataclasses and the aggregate_machines() function.
"""

from pathlib import Path
from typing import Any

import pytest

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_task_folder,
    build_task_json,
)
from arf.tests.fixtures.writers import write_json

TASK_ID_1: str = "t0001_test"
TASK_ID_2: str = "t0002_test"


def _full_machine_log_entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "provider": "vast.ai",
        "instance_id": "12345678",
        "offer_id": 33661505,
        "search_criteria": {
            "gpu_name": None,
            "num_gpus": 1,
            "min_gpu_ram": 10.0,
        },
        "selected_offer": {
            "offer_id": 33661505,
            "gpu": "RTX 3090",
            "gpu_count": 1,
            "gpu_ram_gb": 24.0,
            "cpu_ram_gb": 32.0,
            "disk_gb": 200.0,
            "price_per_hour": 0.15,
            "reliability": 0.99,
            "location": "US",
        },
        "selection_rationale": "Cost efficient option for estimated 2h job.",
        "image": "pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel",
        "disk_gb": 100,
        "label": "my-project/t0001_test",
        "ssh_host": "ssh6.vast.ai",
        "ssh_port": 10288,
        "gpu_verified": "NVIDIA GeForce RTX 3090",
        "cuda_version": "12.6",
        "created_at": "2026-04-01T00:00:00Z",
        "ready_at": "2026-04-01T00:05:00Z",
        "destroyed_at": "2026-04-01T02:00:00Z",
        "total_duration_hours": 2.0,
        "total_cost_usd": 0.30,
        "search_started_at": "2026-04-01T00:00:00Z",
        "total_provisioning_seconds": 300.0,
        "failed_attempts": [],
        "checkpoint_path": None,
        "heartbeat_path": None,
    }
    entry.update(overrides)
    return entry


def _setup(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
) -> None:
    import arf.scripts.aggregators.aggregate_machines as agg_module

    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        aggregator_modules=[agg_module],
    )


def _build_machine_log(
    *,
    task_id: str,
    entries: list[dict[str, object]],
    step_name: str = "001_setup-machines",
) -> Path:
    step_dir: Path = paths.step_logs_dir(task_id=task_id) / step_name
    step_dir.mkdir(parents=True, exist_ok=True)
    log_path: Path = step_dir / "machine_log.json"
    payload: list[object] = list(entries)
    write_json(path=log_path, data=payload)
    return log_path


def _aggregate() -> Any:
    from arf.scripts.aggregators.aggregate_machines import aggregate_machines

    return aggregate_machines()


# ---------------------------------------------------------------------------
# test_no_tasks_returns_empty
# ---------------------------------------------------------------------------


def test_no_tasks_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No task folders at all. Summary should have all zeros."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)

    result = _aggregate()

    assert result.summary.total_machines == 0
    assert result.summary.total_failed_attempts == 0
    assert result.summary.failure_rate == 0.0
    assert result.summary.avg_provisioning_seconds is None
    assert result.summary.total_cost_usd == 0.0
    assert result.summary.total_wasted_cost_usd == 0.0
    assert len(result.summary.gpu_tier_costs) == 0
    assert len(result.summary.failure_reasons) == 0
    assert len(result.tasks) == 0


# ---------------------------------------------------------------------------
# test_task_without_machines_skipped
# ---------------------------------------------------------------------------


def test_task_without_machines_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Task exists but has no setup-machines step directory."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    result = _aggregate()

    assert len(result.tasks) == 0
    assert result.summary.total_machines == 0


# ---------------------------------------------------------------------------
# test_single_task_single_machine
# ---------------------------------------------------------------------------


def test_single_task_single_machine(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """One task with one machine. Verify all summary fields match."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[_full_machine_log_entry()],
    )

    result = _aggregate()

    assert result.summary.total_machines == 1
    assert result.summary.total_cost_usd == pytest.approx(0.30)
    assert result.summary.total_failed_attempts == 0
    assert result.summary.failure_rate == 0.0
    assert result.summary.avg_provisioning_seconds == pytest.approx(300.0)
    assert result.summary.total_wasted_cost_usd == 0.0
    assert result.summary.gpu_tier_costs == {"RTX 3090": pytest.approx(0.30)}

    assert len(result.tasks) == 1
    task_info = result.tasks[0]
    assert task_info.task_id == TASK_ID_1
    assert task_info.machine_count == 1
    assert task_info.total_cost_usd == pytest.approx(0.30)
    assert task_info.total_failed == 0
    assert task_info.gpu_models == ["RTX 3090"]


# ---------------------------------------------------------------------------
# test_multiple_tasks_sums_costs
# ---------------------------------------------------------------------------


def test_multiple_tasks_sums_costs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Two tasks with machines. Verify total_cost_usd is the sum."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)

    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[_full_machine_log_entry(total_cost_usd=0.30)],
    )

    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_2)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID_2,
        task_index=2,
    )
    _build_machine_log(
        task_id=TASK_ID_2,
        entries=[
            _full_machine_log_entry(
                instance_id="99999999",
                total_cost_usd=1.50,
            ),
        ],
    )

    result = _aggregate()

    assert result.summary.total_cost_usd == pytest.approx(1.80)
    assert result.summary.total_machines == 2
    assert len(result.tasks) == 2


# ---------------------------------------------------------------------------
# test_failed_attempts_counted
# ---------------------------------------------------------------------------


def test_failed_attempts_counted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Machine log with 2 failed_attempts entries. Verify count."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    failed_attempts: list[dict[str, object]] = [
        {
            "offer_id": 11111111,
            "gpu": "RTX 3090",
            "failure_reason": "SSH connection timeout",
            "wasted_cost_usd": 0.02,
        },
        {
            "offer_id": 22222222,
            "gpu": "RTX 3090",
            "failure_reason": "GPU verification failed",
            "wasted_cost_usd": 0.01,
        },
    ]
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[
            _full_machine_log_entry(failed_attempts=failed_attempts),
        ],
    )

    result = _aggregate()

    assert result.summary.total_failed_attempts == 2
    assert result.tasks[0].total_failed == 2


# ---------------------------------------------------------------------------
# test_failure_rate_calculation
# ---------------------------------------------------------------------------


def test_failure_rate_calculation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """1 success + 2 failures -> failure_rate = 2/3."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    failed_attempts: list[dict[str, object]] = [
        {
            "offer_id": 11111111,
            "gpu": "RTX 3090",
            "failure_reason": "SSH timeout",
            "wasted_cost_usd": 0.02,
        },
        {
            "offer_id": 22222222,
            "gpu": "RTX 3090",
            "failure_reason": "GPU verification failed",
            "wasted_cost_usd": 0.01,
        },
    ]
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[
            _full_machine_log_entry(failed_attempts=failed_attempts),
        ],
    )

    result = _aggregate()

    # 1 succeeded machine + 2 failed attempts = 2/3 failure rate
    assert result.summary.failure_rate == pytest.approx(2.0 / 3.0)


# ---------------------------------------------------------------------------
# test_gpu_tier_costs_grouped
# ---------------------------------------------------------------------------


def test_gpu_tier_costs_grouped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Two machines with different GPUs. Verify gpu_tier_costs dict."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    rtx_entry: dict[str, object] = _full_machine_log_entry(
        instance_id="11111111",
        total_cost_usd=0.30,
    )
    a100_offer: dict[str, object] = {
        "offer_id": 44444444,
        "gpu": "A100",
        "gpu_count": 1,
        "gpu_ram_gb": 80.0,
        "cpu_ram_gb": 64.0,
        "disk_gb": 500.0,
        "price_per_hour": 0.75,
        "reliability": 0.98,
        "location": "EU",
    }
    a100_entry: dict[str, object] = _full_machine_log_entry(
        instance_id="22222222",
        selected_offer=a100_offer,
        total_cost_usd=1.50,
        gpu_verified="NVIDIA A100-SXM4-80GB",
    )

    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[rtx_entry, a100_entry],
    )

    result = _aggregate()

    assert result.summary.gpu_tier_costs["RTX 3090"] == pytest.approx(0.30)
    assert result.summary.gpu_tier_costs["A100"] == pytest.approx(1.50)
    assert len(result.summary.gpu_tier_costs) == 2


# ---------------------------------------------------------------------------
# test_failure_reasons_grouped
# ---------------------------------------------------------------------------


def test_failure_reasons_grouped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Failed attempts with different reasons. Verify counts."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    failed_attempts: list[dict[str, object]] = [
        {
            "offer_id": 11111111,
            "gpu": "RTX 3090",
            "failure_reason": "SSH connection timeout",
            "wasted_cost_usd": 0.02,
        },
        {
            "offer_id": 22222222,
            "gpu": "RTX 3090",
            "failure_reason": "GPU verification failed",
            "wasted_cost_usd": 0.01,
        },
        {
            "offer_id": 33333333,
            "gpu": "RTX 3090",
            "failure_reason": "SSH connection timeout",
            "wasted_cost_usd": 0.02,
        },
    ]
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[
            _full_machine_log_entry(failed_attempts=failed_attempts),
        ],
    )

    result = _aggregate()

    assert result.summary.failure_reasons["SSH connection timeout"] == 2
    assert result.summary.failure_reasons["GPU verification failed"] == 1
    assert len(result.summary.failure_reasons) == 2


# ---------------------------------------------------------------------------
# test_v1_machine_log_without_timing
# ---------------------------------------------------------------------------


def test_v1_machine_log_without_timing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Machine log missing v2 fields. Aggregator handles gracefully."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    v1_entry: dict[str, object] = {
        "provider": "vast.ai",
        "instance_id": "12345678",
        "offer_id": 33661505,
        "search_criteria": {"gpu_name": "RTX 3090"},
        "selected_offer": {
            "offer_id": 33661505,
            "gpu": "RTX 3090",
            "gpu_count": 1,
        },
        "selection_rationale": "Cost efficient.",
        "image": "pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel",
        "disk_gb": 100,
        "ssh_host": "ssh6.vast.ai",
        "ssh_port": 10288,
        "gpu_verified": True,
        "cuda_version": "12.6",
        "created_at": "2026-04-01T00:00:00Z",
        "ready_at": "2026-04-01T00:05:00Z",
        "destroyed_at": "2026-04-01T02:00:00Z",
        "total_duration_hours": 2.0,
        "total_cost_usd": 0.30,
        # No search_started_at, total_provisioning_seconds, failed_attempts
    }
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[v1_entry],
    )

    result = _aggregate()

    assert result.summary.total_machines == 1
    assert result.summary.total_cost_usd == pytest.approx(0.30)
    # No v2 timing data available, so avg should be None
    assert result.summary.avg_provisioning_seconds is None
    assert result.summary.total_failed_attempts == 0


# ---------------------------------------------------------------------------
# test_wasted_cost_summed
# ---------------------------------------------------------------------------


def test_wasted_cost_summed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Failed attempts with wasted_cost_usd. Verify total."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID_1)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID_1)

    failed_attempts: list[dict[str, object]] = [
        {
            "offer_id": 11111111,
            "gpu": "RTX 3090",
            "failure_reason": "SSH timeout",
            "wasted_cost_usd": 0.05,
        },
        {
            "offer_id": 22222222,
            "gpu": "RTX 3090",
            "failure_reason": "GPU verification failed",
            "wasted_cost_usd": 0.12,
        },
    ]
    _build_machine_log(
        task_id=TASK_ID_1,
        entries=[
            _full_machine_log_entry(failed_attempts=failed_attempts),
        ],
    )

    result = _aggregate()

    assert result.summary.total_wasted_cost_usd == pytest.approx(0.17)
