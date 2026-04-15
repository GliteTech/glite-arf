"""Tests for the verify_pr_premerge verificator (PM-codes).

The PR premerge verificator relies heavily on git, gh CLI, and subprocess
calls. Tests stub all external calls to isolate verification logic.
"""

from pathlib import Path

import pytest

import arf.scripts.verificators.verify_pr_premerge as verify_pm_module
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
PR_NUMBER: int = 42

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
]


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_pm_module],
    )
    # Stub all git/gh/subprocess-dependent functions
    monkeypatch.setattr(
        verify_pm_module,
        "_check_branch_name",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_pr_target",
        lambda *, pr_number, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_file_isolation",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_has_commits",
        lambda *, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_sensitive_files",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_large_files",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_run_sub_verificator",
        lambda *, module_name, args, label, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_pr_body_sections",
        lambda *, pr_number, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_merge_conflicts",
        lambda *, pr_number, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_commit_messages",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_pr_title",
        lambda *, task_id, pr_number, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_step_commit_mapping",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_ruff",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_mypy",
        lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        verify_pm_module,
        "_check_expected_assets",
        lambda *, task_data, task_id, file_path: [],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _build_complete_task(*, repo_root: Path) -> None:
    build_task_folder(repo_root=repo_root, task_id=TASK_ID)
    build_task_json(
        repo_root=repo_root,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
    )
    build_step_tracker(
        repo_root=repo_root,
        task_id=TASK_ID,
        steps=COMPLETED_STEPS,
    )
    build_plan(repo_root=repo_root, task_id=TASK_ID)
    build_research_papers(repo_root=repo_root, task_id=TASK_ID)
    build_research_internet(repo_root=repo_root, task_id=TASK_ID)
    build_results_summary(repo_root=repo_root, task_id=TASK_ID)
    build_results_detailed(repo_root=repo_root, task_id=TASK_ID)
    build_metrics_file(repo_root=repo_root, task_id=TASK_ID)
    build_suggestions_file(repo_root=repo_root, task_id=TASK_ID)
    build_costs_file(repo_root=repo_root, task_id=TASK_ID)
    build_remote_machines_file(repo_root=repo_root, task_id=TASK_ID)
    build_step_log(
        repo_root=repo_root,
        task_id=TASK_ID,
        step_order=1,
        step_id="create-branch",
    )


# ---------------------------------------------------------------------------
# Completed task with explicit PR number passes
# ---------------------------------------------------------------------------


def test_completed_task_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# PM-E005: task.json status not completed
# ---------------------------------------------------------------------------


def test_pm_e005_status_not_completed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
    )
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E006: Timestamps null
# ---------------------------------------------------------------------------


def test_pm_e006_null_timestamps(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
        start_time=None,
        end_time=None,
    )
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E006" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E007: step_tracker.json missing
# ---------------------------------------------------------------------------


def test_pm_e007_step_tracker_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    tracker: Path = paths.step_tracker_path(task_id=TASK_ID)
    tracker.unlink()
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E007" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E007: Step not finished
# ---------------------------------------------------------------------------


def test_pm_e007_step_not_finished(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    unfinished: list[dict[str, object]] = [
        {
            "step": 1,
            "name": "create-branch",
            "description": "Create branch.",
            "status": "completed",
            "started_at": "2026-04-01T00:00:00Z",
            "completed_at": "2026-04-01T00:00:01Z",
        },
        {
            "step": 2,
            "name": "implementation",
            "description": "Main work.",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
        },
    ]
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=unfinished,
    )
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E007" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E008: Mandatory directory missing
# ---------------------------------------------------------------------------


def test_pm_e008_missing_mandatory_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    import shutil

    plan_dir: Path = paths.task_dir(task_id=TASK_ID) / "plan"
    shutil.rmtree(plan_dir)
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E008" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E009: Mandatory result file missing
# ---------------------------------------------------------------------------


def test_pm_e009_missing_result_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_complete_task(repo_root=tmp_path)
    summary: Path = paths.results_summary_path(task_id=TASK_ID)
    summary.unlink()
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E009" in _codes(result=result)


# ---------------------------------------------------------------------------
# PM-E005: task.json missing entirely
# ---------------------------------------------------------------------------


def test_pm_e005_task_json_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=COMPLETED_STEPS,
    )
    # No task.json
    result: VerificationResult = verify_pm_module.verify_pr_premerge(
        task_id=TASK_ID,
        pr_number=PR_NUMBER,
    )
    assert "PM-E005" in _codes(result=result)
