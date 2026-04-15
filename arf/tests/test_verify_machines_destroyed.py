"""Tests for the verify_machines_destroyed verificator (RM-codes).

Tests verify remote machine destruction checks based on
remote_machines_specification.md. All Vast.ai API calls are stubbed.
"""

from pathlib import Path

import pytest

import arf.scripts.verificators.verify_machines_destroyed as verify_rm_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.results_builders import build_remote_machines_file
from arf.tests.fixtures.task_builder import (
    build_task_folder,
    build_task_json,
)
from arf.tests.fixtures.writers import write_json

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1
INSTANCE_ID: str = "12345678"


def _full_machine_log_entry(
    **overrides: object,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "provider": "vast.ai",
        "instance_id": INSTANCE_ID,
        "offer_id": "offer_001",
        "search_criteria": {"gpu_name": "RTX 2080 Ti"},
        "selected_offer": {"offer_id": "offer_001", "gpu": "RTX 2080 Ti"},
        "selection_rationale": "Selected for cost efficiency and reliability.",
        "image": "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
        "disk_gb": 50,
        "ssh_host": "192.168.1.1",
        "ssh_port": 22,
        "gpu_verified": True,
        "cuda_version": "12.1",
        "created_at": "2026-04-01T00:00:00Z",
        "ready_at": "2026-04-01T00:05:00Z",
        "destroyed_at": "2026-04-01T02:00:00Z",
        "total_duration_hours": 2.0,
        "total_cost_usd": 0.08,
        "label": "my-project/t0001_test",
        "search_started_at": "2026-04-01T00:00:00Z",
        "total_provisioning_seconds": 300.0,
        "failed_attempts": [],
        "checkpoint_path": None,
        "heartbeat_path": None,
    }
    entry.update(overrides)
    return entry


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_rm_module],
    )
    # Stub out Vast.ai API calls
    monkeypatch.setattr(
        verify_rm_module,
        "_check_instance_via_api",
        lambda *, instance_id: None,
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_rm_module.verify_machines_destroyed(task_id=task_id)


def _build_machine_log(
    *,
    repo_root: Path,
    task_id: str,
    entries: list[dict[str, object]],
) -> Path:
    step_dir: Path = paths.step_logs_dir(task_id=task_id) / "008_setup-machines"
    step_dir.mkdir(parents=True, exist_ok=True)
    log_path: Path = step_dir / "machine_log.json"
    payload: list[object] = list(entries)
    write_json(path=log_path, data=payload)
    return log_path


# ---------------------------------------------------------------------------
# No machines used passes
# ---------------------------------------------------------------------------


def test_no_machines_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[],
    )
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# Machine properly destroyed passes
# ---------------------------------------------------------------------------


def test_machine_destroyed_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[_full_machine_log_entry()],
    )
    result: VerificationResult = _verify()
    assert len(result.errors) == 0


# ---------------------------------------------------------------------------
# RM-E001: Machine has no destroyed_at timestamp
# ---------------------------------------------------------------------------


def test_rm_e001_no_destroyed_at(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                "destroyed_at": None,
                "total_cost_usd": None,
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E001" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-E002: Vast.ai confirms instance still active
# ---------------------------------------------------------------------------


def test_rm_e002_instance_still_active(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    # Override the API stub to return "running"
    monkeypatch.setattr(
        verify_rm_module,
        "_check_instance_via_api",
        lambda *, instance_id: "running",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                "destroyed_at": None,
                "total_cost_usd": None,
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-E002: destroyed_at set but API says still running
# ---------------------------------------------------------------------------


def test_rm_e002_destroyed_at_but_still_running(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    monkeypatch.setattr(
        verify_rm_module,
        "_check_instance_via_api",
        lambda *, instance_id: "running",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                "destroyed_at": "2026-04-01T02:00:00Z",
                "total_cost_usd": 0.08,
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-E003: machine_log.json is invalid JSON
# ---------------------------------------------------------------------------


def test_rm_e003_invalid_machine_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    step_dir: Path = paths.step_logs_dir(task_id=TASK_ID) / "008_setup-machines"
    step_dir.mkdir(parents=True, exist_ok=True)
    bad_log: Path = step_dir / "machine_log.json"
    bad_log.write_text("NOT JSON {{{", encoding="utf-8")
    result: VerificationResult = _verify()
    assert "RM-E003" in _codes(result=result)


# ---------------------------------------------------------------------------
# No machine_log.json, non-empty remote_machines_used, API check
# ---------------------------------------------------------------------------


def test_no_machine_log_but_rm_file_api_running(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    monkeypatch.setattr(
        verify_rm_module,
        "_check_instance_via_api",
        lambda *, instance_id: "running",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    # No machine_log.json exists
    result: VerificationResult = _verify()
    assert "RM-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# remote_machines_used.json missing: no errors
# ---------------------------------------------------------------------------


def test_rm_file_missing_no_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    # No remote_machines_used.json at all
    result: VerificationResult = _verify()
    assert result.passed is True


# ---------------------------------------------------------------------------
# RM-E004: Machine entry missing required field
# ---------------------------------------------------------------------------


def test_rm_e004_missing_required_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                # Missing many required fields like ssh_host, cuda_version, etc.
                "destroyed_at": "2026-04-01T02:00:00Z",
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E004" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-E005: instance_id mismatch with remote_machines_used.json
# ---------------------------------------------------------------------------


def test_rm_e005_instance_id_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": "99999999",
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                "destroyed_at": "2026-04-01T02:00:00Z",
                "total_cost_usd": 0.08,
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-E006: total_cost_usd mismatch
# ---------------------------------------------------------------------------


def test_rm_e006_cost_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.33,
                "cost_usd": 5.00,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            {
                "instance_id": INSTANCE_ID,
                "destroyed_at": "2026-04-01T02:00:00Z",
                "total_cost_usd": 0.08,
            },
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-E006" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W001: Vast.ai API unreachable
# ---------------------------------------------------------------------------


def test_rm_w001_api_unreachable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    # API returns None = unreachable (default stub)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[_full_machine_log_entry()],
    )
    result: VerificationResult = _verify()
    assert "RM-W001" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W002: Cost exceeds plan estimate by >50%
# ---------------------------------------------------------------------------


def test_rm_w002_cost_over_estimate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    # Create plan with $5 estimate
    plan_dir: Path = paths.task_dir(task_id=TASK_ID) / "plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "plan.md").write_text(
        "## Cost Estimation\n\nGPU compute: $5\n",
        encoding="utf-8",
    )
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 5.0,
                "cost_usd": 15.0,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(total_cost_usd=15.0),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W002" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W003: Machine running more than 12 hours
# ---------------------------------------------------------------------------


def test_rm_w003_long_running(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 15.0,
                "cost_usd": 5.0,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                total_duration_hours=15.0,
                total_cost_usd=5.0,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W003" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W004: selection_rationale empty or under 20 characters
# ---------------------------------------------------------------------------


def test_rm_w004_short_rationale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(selection_rationale="cheap"),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W004" in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W005: Incomplete failed_attempt entry
# ---------------------------------------------------------------------------


def test_rm_w005_incomplete_failed_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                failed_attempts=[
                    {
                        "offer_id": "offer_bad",
                        # Missing failure_reason, failure_phase, timestamp
                    },
                ],
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W005" in _codes(result=result)


def test_rm_w005_not_emitted_for_valid_failed_attempts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                failed_attempts=[
                    {
                        "offer_id": "offer_bad",
                        "failure_reason": "SSH timeout after 120s",
                        "failure_phase": "ssh_connect",
                        "timestamp": "2026-04-01T00:01:00Z",
                    },
                ],
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W005" not in _codes(result=result)


def test_rm_w005_not_emitted_when_no_failed_attempts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    # Build entry without the failed_attempts key (v1 compat)
    entry: dict[str, object] = _full_machine_log_entry()
    del entry["failed_attempts"]
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[entry],
    )
    result: VerificationResult = _verify()
    assert "RM-W005" not in _codes(result=result)


# ---------------------------------------------------------------------------
# RM-W006: No checkpoint for long job
# ---------------------------------------------------------------------------


def test_rm_w006_no_checkpoint_for_long_job(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 5.0,
                "cost_usd": 1.50,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                total_duration_hours=5.0,
                total_cost_usd=1.50,
                checkpoint_path=None,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W006" in _codes(result=result)


def test_rm_w006_not_emitted_for_short_job(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 1.0,
                "cost_usd": 0.04,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                total_duration_hours=1.0,
                total_cost_usd=0.04,
                checkpoint_path=None,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W006" not in _codes(result=result)


def test_rm_w006_not_emitted_when_checkpoint_set(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 5.0,
                "cost_usd": 1.50,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                total_duration_hours=5.0,
                total_cost_usd=1.50,
                checkpoint_path="/root/checkpoints",
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "RM-W006" not in _codes(result=result)


# ---------------------------------------------------------------------------
# v2 fields accepted without errors
# ---------------------------------------------------------------------------


def test_v2_fields_accepted_without_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        payload=[
            {
                "provider": "vast.ai",
                "machine_id": INSTANCE_ID,
                "gpu": "RTX 2080 Ti",
                "gpu_count": 1,
                "ram_gb": 21,
                "duration_hours": 2.0,
                "cost_usd": 0.08,
            },
        ],
    )
    _build_machine_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        entries=[
            _full_machine_log_entry(
                label="my-project/t0001_test",
                search_started_at="2026-04-01T00:00:00Z",
                total_provisioning_seconds=300.0,
                failed_attempts=[
                    {
                        "offer_id": "offer_bad",
                        "failure_reason": "SSH timeout",
                        "failure_phase": "ssh_connect",
                        "timestamp": "2026-04-01T00:01:00Z",
                    },
                ],
                checkpoint_path="/root/checkpoints",
                heartbeat_path="/root/heartbeat.json",
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert len(result.errors) == 0, f"Unexpected errors: {_codes(result=result)}"
