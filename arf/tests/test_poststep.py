"""Tests for poststep skipped-step log warnings."""

from pathlib import Path

import pytest

import arf.scripts.utils.poststep as poststep_module
from arf.tests.fixtures.log_builders import build_step_log
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_task_folder

TASK_ID: str = "t0001_test"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[poststep_module],
    )


def _build_tracker(
    *,
    steps: list[dict[str, object]],
) -> dict[str, object]:
    return {"steps": steps}


def _make_step(
    *,
    step: int,
    name: str,
    status: str,
) -> dict[str, object]:
    return {"step": step, "name": name, "status": status}


# ---------------------------------------------------------------------------
# Skipped-step log warnings
# ---------------------------------------------------------------------------


def test_no_warning_when_skipped_step_has_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_step_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        step_order=3,
        step_id="research-papers",
        status="skipped",
    )
    tracker: dict[str, object] = _build_tracker(
        steps=[
            _make_step(step=3, name="research-papers", status="skipped"),
            _make_step(step=5, name="implementation", status="in_progress"),
        ],
    )
    poststep_module._warn_missing_skipped_step_logs(
        task_id=TASK_ID,
        tracker=tracker,
        current_step_order=5,
    )
    captured: str = capsys.readouterr().out
    assert "WARNING" not in captured


def test_warning_when_skipped_step_missing_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    tracker: dict[str, object] = _build_tracker(
        steps=[
            _make_step(step=3, name="research-papers", status="skipped"),
            _make_step(step=5, name="implementation", status="in_progress"),
        ],
    )
    poststep_module._warn_missing_skipped_step_logs(
        task_id=TASK_ID,
        tracker=tracker,
        current_step_order=5,
    )
    captured: str = capsys.readouterr().out
    assert "WARNING" in captured
    assert "research-papers" in captured


def test_no_warning_for_skipped_step_after_current(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    tracker: dict[str, object] = _build_tracker(
        steps=[
            _make_step(step=3, name="implementation", status="in_progress"),
            _make_step(step=8, name="suggestions", status="skipped"),
        ],
    )
    poststep_module._warn_missing_skipped_step_logs(
        task_id=TASK_ID,
        tracker=tracker,
        current_step_order=3,
    )
    captured: str = capsys.readouterr().out
    assert "WARNING" not in captured


def test_no_warning_for_completed_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    tracker: dict[str, object] = _build_tracker(
        steps=[
            _make_step(step=3, name="research-papers", status="completed"),
            _make_step(step=5, name="implementation", status="in_progress"),
        ],
    )
    poststep_module._warn_missing_skipped_step_logs(
        task_id=TASK_ID,
        tracker=tracker,
        current_step_order=5,
    )
    captured: str = capsys.readouterr().out
    assert "WARNING" not in captured
