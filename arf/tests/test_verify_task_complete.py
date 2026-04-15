"""Tests for the verify_task_complete verificator (TC-codes).

Tests verify that task completion checks work correctly based on the
task_folder_specification.md completeness requirements.
"""

from pathlib import Path

import pytest

import arf.scripts.verificators.verify_task_complete as verify_tc_module
import arf.scripts.verificators.verify_task_dependencies as verify_deps_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.log_builders import build_step_log
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.plan_builder import build_plan
from arf.tests.fixtures.research_builders import (
    build_research_internet,
    build_research_papers,
)
from arf.tests.fixtures.results_builders import (
    build_costs_file,
    build_metrics_file,
    build_remote_machines_file,
    build_results_detailed,
    build_results_summary,
)
from arf.tests.fixtures.suggestion_builder import build_suggestions_file
from arf.tests.fixtures.task_builder import (
    build_step_tracker,
    build_task_folder,
    build_task_json,
)

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[
            verify_tc_module,
            verify_deps_module,
        ],
    )
    # Stub out subprocess calls that reach git/gh/uv
    monkeypatch.setattr(
        verify_tc_module,
        "_check_git_branch_exists",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_tc_module,
        "_check_pr_merged",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_tc_module,
        "_check_no_files_outside_task",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_tc_module,
        "_run_sub_verificator",
        lambda *, module_name, args, label, file_path: [],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_tc_module.verify_task_complete(task_id=task_id)


COMPLETED_STEPS: list[dict[str, object]] = [
    {
        "step": 1,
        "name": "create-branch",
        "description": "Create branch.",
        "status": "completed",
        "started_at": "2026-04-01T00:00:00Z",
        "completed_at": "2026-04-01T00:00:01Z",
        "log_file": "logs/steps/001_create-branch/",
    },
    {
        "step": 2,
        "name": "implementation",
        "description": "Main work.",
        "status": "completed",
        "started_at": "2026-04-01T00:01:00Z",
        "completed_at": "2026-04-01T01:00:00Z",
        "log_file": "logs/steps/002_implementation/",
    },
    {
        "step": 3,
        "name": "reporting",
        "description": "Final report.",
        "status": "completed",
        "started_at": "2026-04-01T01:00:00Z",
        "completed_at": "2026-04-01T01:30:00Z",
        "log_file": "logs/steps/003_reporting/",
    },
]


def _build_fully_completed_task(
    *,
    repo_root: Path,
    task_id: str = TASK_ID,
) -> None:
    build_task_folder(repo_root=repo_root, task_id=task_id)
    build_task_json(
        repo_root=repo_root,
        task_id=task_id,
        task_index=TASK_INDEX,
        status="completed",
    )
    build_step_tracker(
        repo_root=repo_root,
        task_id=task_id,
        steps=COMPLETED_STEPS,
    )
    build_plan(repo_root=repo_root, task_id=task_id)
    build_research_papers(repo_root=repo_root, task_id=task_id)
    build_research_internet(repo_root=repo_root, task_id=task_id)
    build_results_summary(repo_root=repo_root, task_id=task_id)
    build_results_detailed(repo_root=repo_root, task_id=task_id)
    build_metrics_file(repo_root=repo_root, task_id=task_id)
    build_suggestions_file(repo_root=repo_root, task_id=task_id)
    build_costs_file(repo_root=repo_root, task_id=task_id)
    build_remote_machines_file(repo_root=repo_root, task_id=task_id)
    build_step_log(
        repo_root=repo_root,
        task_id=task_id,
        step_order=1,
        step_id="create-branch",
    )


# ---------------------------------------------------------------------------
# Fully completed task passes
# ---------------------------------------------------------------------------


def test_completed_task_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# TC-E001: task.json status not completed
# ---------------------------------------------------------------------------


def test_tc_e001_status_not_completed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    # Overwrite task.json with in_progress status
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
    )
    result: VerificationResult = _verify()
    assert "TC-E001" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E002: Timestamps null
# ---------------------------------------------------------------------------


def test_tc_e002_null_end_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
        end_time=None,
    )
    result: VerificationResult = _verify()
    assert "TC-E002" in _codes(result=result)


def test_tc_e002_null_start_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
        start_time=None,
    )
    result: VerificationResult = _verify()
    assert "TC-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E003: step_tracker.json missing
# ---------------------------------------------------------------------------


def test_tc_e003_step_tracker_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    tracker: Path = paths.step_tracker_path(task_id=TASK_ID)
    tracker.unlink()
    result: VerificationResult = _verify()
    assert "TC-E003" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E004: Step not finished
# ---------------------------------------------------------------------------


def test_tc_e004_step_still_in_progress(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    unfinished_steps: list[dict[str, object]] = [
        {
            "step": 1,
            "name": "create-branch",
            "description": "Create branch.",
            "status": "completed",
            "started_at": "2026-04-01T00:00:00Z",
            "completed_at": "2026-04-01T00:00:01Z",
            "log_file": "logs/steps/001_create-branch/",
        },
        {
            "step": 2,
            "name": "implementation",
            "description": "Main work.",
            "status": "in_progress",
            "started_at": "2026-04-01T00:01:00Z",
            "completed_at": None,
            "log_file": None,
        },
    ]
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=unfinished_steps,
    )
    result: VerificationResult = _verify()
    assert "TC-E004" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E005: Mandatory directory missing
# ---------------------------------------------------------------------------


def test_tc_e005_missing_mandatory_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    # Remove the plan directory
    plan_dir: Path = paths.task_dir(task_id=TASK_ID) / "plan"
    import shutil

    shutil.rmtree(plan_dir)
    result: VerificationResult = _verify()
    assert "TC-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E006: Mandatory result file missing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_file",
    [
        "results/results_summary.md",
        "results/results_detailed.md",
        "results/metrics.json",
        "results/suggestions.json",
    ],
)
def test_tc_e006_missing_result_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_file: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    target: Path = paths.task_dir(task_id=TASK_ID) / missing_file
    if target.exists():
        target.unlink()
    result: VerificationResult = _verify()
    assert "TC-E006" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E007: Expected asset directory missing
# ---------------------------------------------------------------------------


def test_tc_e007_expected_asset_dir_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
        expected_assets={"paper": 1},
    )
    # assets/paper/ dir exists (from build_task_folder) but is empty
    result: VerificationResult = _verify()
    # Should get a warning about fewer assets than expected
    assert "TC-W002" in _codes(result=result) or "TC-E007" in _codes(
        result=result,
    )


# ---------------------------------------------------------------------------
# TC-W001: Non-sequential step numbers
# ---------------------------------------------------------------------------


def test_tc_w001_non_sequential_steps(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_fully_completed_task(repo_root=tmp_path)
    bad_steps: list[dict[str, object]] = [
        {
            "step": 1,
            "name": "create-branch",
            "description": "Create branch.",
            "status": "completed",
            "started_at": "2026-04-01T00:00:00Z",
            "completed_at": "2026-04-01T00:00:01Z",
        },
        {
            "step": 3,
            "name": "implementation",
            "description": "Main work.",
            "status": "completed",
            "started_at": "2026-04-01T00:01:00Z",
            "completed_at": "2026-04-01T01:00:00Z",
        },
    ]
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=bad_steps,
    )
    result: VerificationResult = _verify()
    assert "TC-W001" in _codes(result=result)


# ---------------------------------------------------------------------------
# TC-E001: task.json missing entirely
# ---------------------------------------------------------------------------


def test_tc_e001_task_json_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    # No task.json created
    result: VerificationResult = _verify()
    assert "TC-E001" in _codes(result=result)
