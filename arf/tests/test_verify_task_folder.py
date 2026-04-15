from pathlib import Path

import pytest

import arf.scripts.common.task_description as task_description_module
import arf.scripts.verificators.verify_task_folder as verify_task_folder_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
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
from arf.tests.fixtures.writers import write_text

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[
            verify_task_folder_module,
            task_description_module,
        ],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_task_folder_module.verify_task_folder(task_id=task_id)


def _build_completed_task_with_all_files(
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
    build_step_tracker(repo_root=repo_root, task_id=task_id)
    build_results_summary(repo_root=repo_root, task_id=task_id)
    build_results_detailed(repo_root=repo_root, task_id=task_id)
    build_metrics_file(repo_root=repo_root, task_id=task_id)
    build_suggestions_file(repo_root=repo_root, task_id=task_id)
    build_costs_file(repo_root=repo_root, task_id=task_id)
    build_remote_machines_file(repo_root=repo_root, task_id=task_id)
    write_text(
        path=paths.plan_path(task_id=task_id),
        content="# Plan\n\n## Objective\n\nTest plan.\n",
    )
    write_text(
        path=paths.research_papers_path(task_id=task_id),
        content="# Research Papers\n\nSummary.\n",
    )
    write_text(
        path=paths.research_internet_path(task_id=task_id),
        content="# Research Internet\n\nSummary.\n",
    )
    step_dir: Path = paths.step_logs_dir(task_id=task_id) / "001_init"
    step_dir.mkdir(parents=True, exist_ok=True)
    write_text(
        path=step_dir / "step_log.md",
        content="# Step Log\n\nCompleted.\n",
    )


# ---------------------------------------------------------------------------
# Valid folder passes
# ---------------------------------------------------------------------------


def test_valid_folder_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_fd_e001_folder_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert "FD-E001" in _codes(result=result)


def test_fd_e002_task_json_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-E002" in _codes(result=result)


def test_fd_e003_step_tracker_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID, task_index=TASK_INDEX)
    result: VerificationResult = _verify()
    assert "FD-E003" in _codes(result=result)


@pytest.mark.parametrize(
    "missing_dir",
    [
        "plan",
        "research",
        "assets",
        "results",
        "corrections",
        "intervention",
        "logs",
    ],
)
def test_fd_e004_required_dir_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_dir: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    all_dirs: list[str] = [
        "plan",
        "research",
        "assets",
        "results",
        "corrections",
        "intervention",
        "logs",
    ]
    dirs_to_create: list[str] = [d for d in all_dirs if d != missing_dir]
    build_task_folder(
        repo_root=tmp_path,
        task_id=TASK_ID,
        subdirs=dirs_to_create,
        include_log_subdirs=missing_dir != "logs",
    )
    build_task_json(repo_root=tmp_path, task_id=TASK_ID, task_index=TASK_INDEX)
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-E004" in _codes(result=result)


@pytest.mark.parametrize(
    "missing_log_subdir",
    ["commands", "steps", "searches", "sessions"],
)
def test_fd_e005_log_subdir_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_log_subdir: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(
        repo_root=tmp_path,
        task_id=TASK_ID,
        include_log_subdirs=False,
    )
    all_log_subdirs: list[str] = ["commands", "steps", "searches", "sessions"]
    for sub in all_log_subdirs:
        if sub != missing_log_subdir:
            log_sub_path: Path = paths.task_dir(task_id=TASK_ID) / "logs" / sub
            log_sub_path.mkdir(parents=True, exist_ok=True)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID, task_index=TASK_INDEX)
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-E005" in _codes(result=result)


@pytest.mark.parametrize(
    ("builder_to_skip", "expected_code"),
    [
        ("results_summary", "FD-E006"),
        ("results_detailed", "FD-E007"),
        ("metrics", "FD-E008"),
        ("suggestions", "FD-E009"),
        ("costs", "FD-E010"),
        ("remote_machines", "FD-E011"),
    ],
)
def test_fd_e006_to_e011_completed_missing_results(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    builder_to_skip: str,
    expected_code: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    file_map: dict[str, Path] = {
        "results_summary": paths.results_summary_path(task_id=TASK_ID),
        "results_detailed": paths.results_detailed_path(task_id=TASK_ID),
        "metrics": paths.metrics_path(task_id=TASK_ID),
        "suggestions": paths.suggestions_path(task_id=TASK_ID),
        "costs": paths.costs_path(task_id=TASK_ID),
        "remote_machines": paths.remote_machines_path(task_id=TASK_ID),
    }
    file_map[builder_to_skip].unlink()
    result: VerificationResult = _verify()
    assert expected_code in _codes(result=result)


def test_fd_e012_completed_missing_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.plan_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "FD-E012" in _codes(result=result)


def test_fd_e012_skipped_when_planning_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.plan_path(task_id=TASK_ID).unlink()
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=[{"name": "planning", "status": "skipped"}],
    )
    result: VerificationResult = _verify()
    assert "FD-E012" not in _codes(result=result)


def test_completed_task_with_all_optional_steps_skipped_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A task type that skips planning, research-papers and research-internet
    must pass verification when their producer files are absent and the steps
    are marked skipped in step_tracker.json.

    This closes the structural gap between meta/task_types/*/description.json
    ``optional_steps`` lists and the required-file checks in
    ``_check_completed_files``: every optional step whose absence produces a
    missing-file diagnostic must have a matching ``skip_if_step`` entry.
    """
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.plan_path(task_id=TASK_ID).unlink()
    paths.research_papers_path(task_id=TASK_ID).unlink()
    paths.research_internet_path(task_id=TASK_ID).unlink()
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=[
            {"name": "planning", "status": "skipped"},
            {"name": "research-papers", "status": "skipped"},
            {"name": "research-internet", "status": "skipped"},
        ],
    )
    result: VerificationResult = _verify()
    codes: list[str] = _codes(result=result)
    assert "FD-E012" not in codes, f"FD-E012 must not fire when planning is skipped. Codes: {codes}"
    assert "FD-E013" not in codes, (
        f"FD-E013 must not fire when research-papers is skipped. Codes: {codes}"
    )
    assert "FD-E014" not in codes, (
        f"FD-E014 must not fire when research-internet is skipped. Codes: {codes}"
    )


def test_fd_e013_completed_missing_research_papers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.research_papers_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "FD-E013" in _codes(result=result)


def test_fd_e013_skipped_when_step_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.research_papers_path(task_id=TASK_ID).unlink()
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=[{"name": "research-papers", "status": "skipped"}],
    )
    result: VerificationResult = _verify()
    assert "FD-E013" not in _codes(result=result)


def test_fd_e014_completed_missing_research_internet(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    paths.research_internet_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "FD-E014" in _codes(result=result)


def test_fd_e015_completed_no_step_folders(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    # Remove the step folder we created
    import shutil

    step_dir: Path = paths.step_logs_dir(task_id=TASK_ID) / "001_init"
    shutil.rmtree(step_dir)
    result: VerificationResult = _verify()
    assert "FD-E015" in _codes(result=result)


def test_fd_e016_unexpected_file_in_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    unexpected_file: Path = paths.task_dir(task_id=TASK_ID) / "random.txt"
    write_text(path=unexpected_file, content="unexpected")
    result: VerificationResult = _verify()
    assert "FD-E016" in _codes(result=result)


def test_fd_e016_unexpected_dir_in_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    unexpected_dir: Path = paths.task_dir(task_id=TASK_ID) / "unexpected_dir"
    unexpected_dir.mkdir()
    result: VerificationResult = _verify()
    assert "FD-E016" in _codes(result=result)


def test_fd_e016_pycache_ignored(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    pycache_dir: Path = paths.task_dir(task_id=TASK_ID) / "__pycache__"
    pycache_dir.mkdir()
    result: VerificationResult = _verify()
    assert "FD-E016" not in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_fd_w001_empty_commands_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-W001" in _codes(result=result)


def test_fd_w002_empty_searches_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-W002" in _codes(result=result)


def test_fd_w003_no_images_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-W003" in _codes(result=result)


def test_fd_w004_no_asset_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="not_started",
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "FD-W004" in _codes(result=result)


def test_fd_w005_corrections_in_non_completed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
        start_time="2026-04-01T00:00:00Z",
        end_time=None,
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    corrections_file: Path = paths.corrections_dir(task_id=TASK_ID) / "correction.json"
    write_text(path=corrections_file, content="{}")
    result: VerificationResult = _verify()
    assert "FD-W005" in _codes(result=result)


def test_fd_w006_no_session_transcripts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_completed_task_with_all_files(repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert "FD-W006" in _codes(result=result)
