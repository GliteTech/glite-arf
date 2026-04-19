"""Tests for the LG-W007 relaxation on fresh session captures.

Spec: ``verify_logs`` currently emits LG-W007 whenever ``logs/sessions/``
contains no ``.jsonl`` transcript files. This produces false-positive
warnings for live-session brainstorm tasks, where the agent captures
sessions from inside the session still being written, so no transcripts
have been copied yet.

New behavior: LG-W007 must NOT fire when ALL of the following hold:

1. ``logs/sessions/capture_report.json`` exists and is valid JSON.
2. ``capture_report.json`` contains a ``captured_at`` ISO 8601 UTC
   timestamp within 10 minutes of the most recent completed step's
   ``completed_at`` timestamp in ``step_tracker.json``.
3. ``capture_report.json`` reports zero transcripts copied
   (``copied_sessions`` is an empty list).

If any of those conditions fail (report missing, report older than 10
minutes, or ``copied_sessions`` non-empty but no matching JSONL on disk),
LG-W007 must still fire.
"""

from pathlib import Path
from typing import Any

import pytest

from arf.scripts.verificators import verify_logs as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.log_builders import (
    build_command_log,
    build_step_log,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_step_tracker,
    build_task_folder,
)
from arf.tests.fixtures.writers import write_json

TASK_ID: str = "t0001_fresh_capture"
CAPTURE_REPORT_NAME: str = "capture_report.json"

STEP_STARTED_AT: str = "2026-04-01T00:00:00Z"
STEP_COMPLETED_AT: str = "2026-04-01T00:30:00Z"
CAPTURE_FRESH: str = "2026-04-01T00:28:00Z"
CAPTURE_STALE: str = "2026-04-01T00:00:00Z"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(*, result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _build_skeleton(*, repo_root: Path) -> Path:
    build_task_folder(repo_root=repo_root, task_id=TASK_ID)
    build_step_tracker(
        repo_root=repo_root,
        task_id=TASK_ID,
        steps=[
            {
                "step": 4,
                "step_id": "research-papers",
                "status": "completed",
                "log_file": "step_log.md",
                "started_at": STEP_STARTED_AT,
                "completed_at": STEP_COMPLETED_AT,
            },
        ],
    )
    build_command_log(repo_root=repo_root, task_id=TASK_ID, log_index=1)
    build_step_log(
        repo_root=repo_root,
        task_id=TASK_ID,
        step_order=4,
        step_id="research-papers",
    )
    task_root: Path = repo_root / "tasks" / TASK_ID
    (task_root / "logs" / "searches").mkdir(parents=True, exist_ok=True)
    (task_root / "logs" / "sessions").mkdir(parents=True, exist_ok=True)
    return task_root


def _write_capture_report(
    *,
    task_root: Path,
    captured_at: str,
    copied_sessions: list[dict[str, Any]],
) -> Path:
    report_path: Path = task_root / "logs" / "sessions" / CAPTURE_REPORT_NAME
    data: dict[str, Any] = {
        "spec_version": "1",
        "task_id": TASK_ID,
        "captured_at": captured_at,
        "checked_roots": [],
        "copied_sessions": copied_sessions,
        "errors": [],
    }
    write_json(path=report_path, data=data)
    return report_path


class TestLGW007Relaxation:
    def test_fresh_capture_empty_copied_sessions_does_not_emit_lg_w007(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        task_root: Path = _build_skeleton(repo_root=tmp_path)
        _write_capture_report(
            task_root=task_root,
            captured_at=CAPTURE_FRESH,
            copied_sessions=[],
        )

        result: VerificationResult = verify_mod.verify_logs(task_id=TASK_ID)

        assert "LG-W007" not in _codes(result=result), (
            "Fresh capture_report.json with empty copied_sessions and "
            "captured_at within 10 minutes of latest step completed_at "
            "must suppress LG-W007. "
            f"Got diagnostics: {_codes(result=result)}"
        )

    def test_stale_capture_still_emits_lg_w007(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        task_root: Path = _build_skeleton(repo_root=tmp_path)
        _write_capture_report(
            task_root=task_root,
            captured_at=CAPTURE_STALE,
            copied_sessions=[],
        )

        result: VerificationResult = verify_mod.verify_logs(task_id=TASK_ID)

        assert "LG-W007" in _codes(result=result), (
            "capture_report.json captured more than 10 minutes before "
            "the latest step completed_at must still emit LG-W007. "
            f"Got diagnostics: {_codes(result=result)}"
        )

    def test_missing_capture_report_still_emits_lg_w007(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _build_skeleton(repo_root=tmp_path)

        result: VerificationResult = verify_mod.verify_logs(task_id=TASK_ID)

        assert "LG-W007" in _codes(result=result), (
            "Missing capture_report.json with empty sessions dir must "
            "still emit LG-W007. "
            f"Got diagnostics: {_codes(result=result)}"
        )

    def test_nonempty_copied_sessions_without_jsonl_still_emits_lg_w007(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        task_root: Path = _build_skeleton(repo_root=tmp_path)
        _write_capture_report(
            task_root=task_root,
            captured_at=CAPTURE_FRESH,
            copied_sessions=[
                {
                    "source_kind": "codex",
                    "source_path": "/tmp/fake.jsonl",
                    "destination_file": "session_001.jsonl",
                    "matched_by": "pid_mapping",
                },
            ],
        )

        result: VerificationResult = verify_mod.verify_logs(task_id=TASK_ID)

        assert "LG-W007" in _codes(result=result), (
            "Non-empty copied_sessions with no matching JSONL on disk "
            "must still emit LG-W007. "
            f"Got diagnostics: {_codes(result=result)}"
        )
