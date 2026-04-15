"""Tests for the verify_task_dependencies verificator (TD-codes).

Tests verify that dependency checking works correctly: tasks with no
dependencies pass, dependency tasks must exist and be completed.
"""

from pathlib import Path

import pytest

import arf.scripts.verificators.verify_task_dependencies as verify_deps_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_task_folder,
    build_task_json,
)

TASK_ID: str = "t0002_dependent"
DEP_TASK_ID: str = "t0001_dep"
TASK_INDEX: int = 2
DEP_TASK_INDEX: int = 1


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_deps_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_deps_module.verify_task_dependencies(task_id=task_id)


# ---------------------------------------------------------------------------
# No dependencies passes
# ---------------------------------------------------------------------------


def test_no_dependencies_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=[],
    )
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# Completed dependency passes
# ---------------------------------------------------------------------------


def test_completed_dependency_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    # Create dependency task with completed status
    build_task_folder(repo_root=tmp_path, task_id=DEP_TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=DEP_TASK_ID,
        task_index=DEP_TASK_INDEX,
        status="completed",
    )
    # Create task under test
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=[DEP_TASK_ID],
    )
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# TD-E001: Dependency task folder does not exist
# ---------------------------------------------------------------------------


def test_td_e001_dependency_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=["t9999_nonexistent"],
    )
    result: VerificationResult = _verify()
    assert "TD-E001" in _codes(result=result)


# ---------------------------------------------------------------------------
# TD-E002: Dependency task.json unreadable
# ---------------------------------------------------------------------------


def test_td_e002_dependency_bad_task_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    # Create dep folder but no task.json
    build_task_folder(repo_root=tmp_path, task_id=DEP_TASK_ID)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=[DEP_TASK_ID],
    )
    result: VerificationResult = _verify()
    assert "TD-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# TD-E003: Dependency not completed
# ---------------------------------------------------------------------------


def test_td_e003_dependency_not_completed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=DEP_TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=DEP_TASK_ID,
        task_index=DEP_TASK_INDEX,
        status="in_progress",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=[DEP_TASK_ID],
    )
    result: VerificationResult = _verify()
    assert "TD-E003" in _codes(result=result)


# ---------------------------------------------------------------------------
# TD-E004: Own task.json missing
# ---------------------------------------------------------------------------


def test_td_e004_own_task_json_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    # No task.json
    result: VerificationResult = _verify()
    assert "TD-E004" in _codes(result=result)


# ---------------------------------------------------------------------------
# Multiple dependencies: one missing, one not completed
# ---------------------------------------------------------------------------


def test_multiple_dependency_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    dep2_id: str = "t0003_incomplete"
    # dep1 does not exist at all
    # dep2 exists but not completed
    build_task_folder(repo_root=tmp_path, task_id=dep2_id)
    build_task_json(
        repo_root=tmp_path,
        task_id=dep2_id,
        task_index=3,
        status="in_progress",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        dependencies=["t9999_nonexistent", dep2_id],
    )
    result: VerificationResult = _verify()
    codes: list[str] = _codes(result=result)
    assert "TD-E001" in codes
    assert "TD-E003" in codes
