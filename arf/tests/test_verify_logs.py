from pathlib import Path

import pytest

from arf.scripts.verificators import verify_logs as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.log_builders import build_command_log, build_step_log
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_step_tracker,
    build_task_folder,
)
from arf.tests.fixtures.writers import write_json, write_text

TASK_ID: str = "t0001_test"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_mod.verify_logs(task_id=task_id)


def _build_valid_log_structure(
    *,
    repo_root: Path,
    task_id: str = TASK_ID,
) -> None:
    build_task_folder(repo_root=repo_root, task_id=task_id)
    build_step_tracker(
        repo_root=repo_root,
        task_id=task_id,
        steps=[
            {"step": 4, "status": "completed", "log_file": "step_log.md"},
        ],
    )
    build_command_log(repo_root=repo_root, task_id=task_id, log_index=1)
    build_step_log(
        repo_root=repo_root,
        task_id=task_id,
        step_order=4,
        step_id="research-papers",
    )
    searches_dir: Path = repo_root / "tasks" / task_id / "logs" / "searches"
    searches_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir: Path = repo_root / "tasks" / task_id / "logs" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)


class TestValidPasses:
    def test_valid_logs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _build_valid_log_structure(repo_root=tmp_path)
        result: VerificationResult = _run()
        assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
        assert result.passed is True


class TestE001MissingLogsDir:
    def test_missing_logs_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        task_dir: Path = tmp_path / "tasks" / TASK_ID
        task_dir.mkdir(parents=True, exist_ok=True)
        result: VerificationResult = _run()
        assert "LG-E001" in _codes(result=result)


class TestE002MissingCommandsDir:
    def test_missing_commands_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(
            repo_root=tmp_path,
            task_id=TASK_ID,
            include_log_subdirs=False,
        )
        logs_path: Path = tmp_path / "tasks" / TASK_ID / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        (logs_path / "steps").mkdir(exist_ok=True)
        result: VerificationResult = _run()
        assert "LG-E002" in _codes(result=result)


class TestE003MissingStepsDir:
    def test_missing_steps_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(
            repo_root=tmp_path,
            task_id=TASK_ID,
            include_log_subdirs=False,
        )
        logs_path: Path = tmp_path / "tasks" / TASK_ID / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        (logs_path / "commands").mkdir(exist_ok=True)
        result: VerificationResult = _run()
        assert "LG-E003" in _codes(result=result)


class TestE004InvalidCommandLog:
    def test_invalid_json_command_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        cmd_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "commands"
        write_text(
            path=cmd_dir / "001_20260401T000000Z_bad.json",
            content="not valid json",
        )
        result: VerificationResult = _run()
        assert "LG-E004" in _codes(result=result)

    def test_missing_required_fields(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        cmd_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "commands"
        write_json(
            path=cmd_dir / "001_20260401T000000Z_partial.json",
            data={"spec_version": "1", "task_id": TASK_ID},
        )
        result: VerificationResult = _run()
        assert "LG-E004" in _codes(result=result)


class TestE005StepLogMissingSections:
    def test_step_log_no_frontmatter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(
            repo_root=tmp_path,
            task_id=TASK_ID,
            steps=[
                {
                    "step": 4,
                    "status": "completed",
                    "log_file": "step_log.md",
                },
            ],
        )
        step_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "steps" / "004_research-papers"
        step_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=step_dir / "step_log.md",
            content="No frontmatter, just text.",
        )
        result: VerificationResult = _run()
        assert "LG-E005" in _codes(result=result)


class TestE006TaskIdMismatch:
    def test_command_log_wrong_task_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        build_command_log(
            repo_root=tmp_path,
            task_id=TASK_ID,
            log_index=1,
        )
        cmd_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "commands"
        json_files: list[Path] = sorted(cmd_dir.glob("*.json"))
        assert len(json_files) > 0
        import json

        data: dict[str, object] = json.loads(json_files[0].read_text(encoding="utf-8"))
        data["task_id"] = "t9999_wrong"
        json_files[0].write_text(json.dumps(data, indent=2), encoding="utf-8")
        result: VerificationResult = _run()
        assert "LG-E006" in _codes(result=result)


class TestE007StepNumberNotInTracker:
    def test_step_number_mismatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(
            repo_root=tmp_path,
            task_id=TASK_ID,
            steps=[
                {"step": 4, "status": "completed", "log_file": "x"},
            ],
        )
        build_step_log(
            repo_root=tmp_path,
            task_id=TASK_ID,
            step_order=99,
            step_id="nonexistent",
        )
        build_step_log(
            repo_root=tmp_path,
            task_id=TASK_ID,
            step_order=4,
            step_id="research-papers",
        )
        result: VerificationResult = _run()
        assert "LG-E007" in _codes(result=result)


class TestE008CompletedStepNoLog:
    def test_completed_step_missing_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(
            repo_root=tmp_path,
            task_id=TASK_ID,
            steps=[
                {
                    "step": 7,
                    "status": "completed",
                    "log_file": "step_log.md",
                },
            ],
        )
        result: VerificationResult = _run()
        assert "LG-E008" in _codes(result=result)


class TestW001MissingSearchesDir:
    def test_missing_searches_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(
            repo_root=tmp_path,
            task_id=TASK_ID,
            include_log_subdirs=False,
        )
        logs_path: Path = tmp_path / "tasks" / TASK_ID / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        (logs_path / "commands").mkdir(exist_ok=True)
        (logs_path / "steps").mkdir(exist_ok=True)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "LG-W001" in _codes(result=result)


class TestW004NonZeroExitCode:
    def test_nonzero_exit(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        build_command_log(
            repo_root=tmp_path,
            task_id=TASK_ID,
            log_index=1,
            exit_code=1,
        )
        result: VerificationResult = _run()
        assert "LG-W004" in _codes(result=result)


class TestW005NoCommandLogs:
    def test_empty_commands_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "LG-W005" in _codes(result=result)


class TestW002SearchLogMissingFields:
    def test_search_log_missing_optional_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _build_valid_log_structure(repo_root=tmp_path)
        searches_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "searches"
        write_json(
            path=searches_dir / "search_001.json",
            data={"spec_version": "1", "task_id": TASK_ID},
        )
        result: VerificationResult = _run()
        assert "LG-W002" in _codes(result=result)


class TestW003StepLogSectionBelowMinWords:
    def test_summary_too_short(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from arf.scripts.verificators.common import paths as p

        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(
            repo_root=tmp_path,
            task_id=TASK_ID,
            steps=[
                {
                    "step": 4,
                    "status": "completed",
                    "log_file": "step_log.md",
                },
            ],
        )
        build_command_log(repo_root=tmp_path, task_id=TASK_ID, log_index=1)
        step_dir: Path = p.step_folder_path(
            task_id=TASK_ID,
            step_order=4,
            step_id="research-papers",
        )
        step_dir.mkdir(parents=True, exist_ok=True)
        log_path: Path = step_dir / "step_log.md"
        log_path.write_text(
            '---\nspec_version: "3"\ntask_id: "t0001_test"\n'
            'step_number: 4\nstep_name: "Research Papers"\n'
            'status: "completed"\n'
            'started_at: "2026-04-01T00:00:00Z"\n'
            'completed_at: "2026-04-01T01:00:00Z"\n---\n\n'
            "# Step Log\n\n"
            "## Summary\n\nDone.\n\n"
            "## Actions Taken\n\n* Stuff.\n\n"
            "## Outputs\n\nFiles.\n\n"
            "## Issues\n\nNone.\n",
            encoding="utf-8",
        )
        searches_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "searches"
        searches_dir.mkdir(parents=True, exist_ok=True)
        sessions_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        result: VerificationResult = _run()
        assert "LG-W003" in _codes(result=result)


class TestW006StepMissingLogFileField:
    def test_completed_step_no_log_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_step_tracker(
            repo_root=tmp_path,
            task_id=TASK_ID,
            steps=[
                {
                    "step": 4,
                    "status": "completed",
                },
            ],
        )
        build_command_log(repo_root=tmp_path, task_id=TASK_ID, log_index=1)
        build_step_log(
            repo_root=tmp_path,
            task_id=TASK_ID,
            step_order=4,
            step_id="research-papers",
        )
        searches_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "searches"
        searches_dir.mkdir(parents=True, exist_ok=True)
        sessions_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        result: VerificationResult = _run()
        assert "LG-W006" in _codes(result=result)


class TestW007MissingSessionsDir:
    def test_no_sessions_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(
            repo_root=tmp_path,
            task_id=TASK_ID,
            include_log_subdirs=False,
        )
        logs_path: Path = tmp_path / "tasks" / TASK_ID / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        (logs_path / "commands").mkdir(exist_ok=True)
        (logs_path / "steps").mkdir(exist_ok=True)
        (logs_path / "searches").mkdir(exist_ok=True)
        build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "LG-W007" in _codes(result=result)


class TestW008CaptureReportMissing:
    def test_sessions_dir_no_capture_report(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _build_valid_log_structure(repo_root=tmp_path)
        sessions_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "sessions"
        write_text(
            path=sessions_dir / "session_001.jsonl",
            content='{"role":"user","content":"hi"}\n',
        )
        result: VerificationResult = _run()
        assert "LG-W008" in _codes(result=result)


class TestGzippedSessionTranscripts:
    def test_jsonl_gz_recognized_as_session_transcript(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _build_valid_log_structure(repo_root=tmp_path)
        sessions_dir: Path = tmp_path / "tasks" / TASK_ID / "logs" / "sessions"
        write_text(
            path=sessions_dir / "session_001.jsonl.gz",
            content="compressed-placeholder",
        )
        result: VerificationResult = _run()
        # Should warn about missing capture report (W008), NOT about
        # missing sessions dir (W007) — the .jsonl.gz file counts as a
        # session transcript.
        assert "LG-W007" not in _codes(result=result)
        assert "LG-W008" in _codes(result=result)
