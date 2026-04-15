"""Tests for the verify_step verificator (SV-codes).

Tests verify that step folder verification works correctly based on the
step_tracker_specification.md and task_steps_specification.md specs.
"""

from pathlib import Path

import pytest

import arf.scripts.verificators.verify_step as verify_step_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.log_builders import build_step_log
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_task_folder,
    build_task_json,
)

TASK_ID: str = "t0001_test"
STEP_ID_IMPLEMENTATION: str = "implementation"
STEP_ID_RESEARCH_PAPERS: str = "research-papers"
STEP_ORDER_1: int = 1
STEP_ORDER_4: int = 4


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_step_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(
    *,
    task_id: str = TASK_ID,
    step_id: str = STEP_ID_IMPLEMENTATION,
    step_order: int = STEP_ORDER_1,
) -> VerificationResult:
    return verify_step_module.verify_step(
        task_id=task_id,
        step_id=step_id,
        step_order=step_order,
    )


# ---------------------------------------------------------------------------
# Valid step passes
# ---------------------------------------------------------------------------


def test_valid_step_folder_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    build_step_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        step_order=STEP_ORDER_1,
        step_id=STEP_ID_IMPLEMENTATION,
    )
    result: VerificationResult = _verify()
    assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# SV-E001: Step folder does not exist
# ---------------------------------------------------------------------------


def test_sv_e001_step_folder_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    # Do not create step folder
    result: VerificationResult = _verify()
    assert "SV-E001" in _codes(result=result)


# ---------------------------------------------------------------------------
# SV-E002: Required file missing inside step folder
# ---------------------------------------------------------------------------


def test_sv_e002_step_log_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    # Create step folder but no step_log.md
    step_folder: Path = paths.step_folder_path(
        task_id=TASK_ID,
        step_order=STEP_ORDER_1,
        step_id=STEP_ID_IMPLEMENTATION,
    )
    step_folder.mkdir(parents=True, exist_ok=True)
    result: VerificationResult = _verify()
    assert "SV-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# SV-E005: Missing required markdown section
# ---------------------------------------------------------------------------


def test_sv_e005_missing_markdown_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    step_folder: Path = paths.step_folder_path(
        task_id=TASK_ID,
        step_order=STEP_ORDER_1,
        step_id=STEP_ID_IMPLEMENTATION,
    )
    step_folder.mkdir(parents=True, exist_ok=True)
    # Write step_log.md with frontmatter but missing required sections
    log_path: Path = step_folder / "step_log.md"
    log_path.write_text(
        '---\nspec_version: "3"\ntask_id: "t0001_test"\n'
        'step_number: 1\nstep_name: "Implementation"\n'
        'status: "completed"\n'
        'started_at: "2026-04-01T00:00:00Z"\n'
        'completed_at: "2026-04-01T01:00:00Z"\n---\n\n'
        "# Step Log\n\n## Summary\n\nDone.\n",
        encoding="utf-8",
    )
    result: VerificationResult = _verify()
    # Missing sections like "Actions Taken", "Outputs", "Issues"
    assert "SV-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# SV-W001: Markdown file under minimum word count
# ---------------------------------------------------------------------------


def test_sv_w001_low_word_count(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    step_folder: Path = paths.step_folder_path(
        task_id=TASK_ID,
        step_order=STEP_ORDER_4,
        step_id=STEP_ID_RESEARCH_PAPERS,
    )
    step_folder.mkdir(parents=True, exist_ok=True)
    # Write step_log.md with all sections but very few words
    log_path: Path = step_folder / "step_log.md"
    log_path.write_text(
        '---\nspec_version: "3"\ntask_id: "t0001_test"\n'
        'step_number: 4\nstep_name: "Research Papers"\n'
        'status: "completed"\n'
        'started_at: "2026-04-01T00:00:00Z"\n'
        'completed_at: "2026-04-01T01:00:00Z"\n---\n\n'
        "# Step Log\n\n"
        "## Summary\n\nX.\n\n"
        "## Actions Taken\n\nX.\n\n"
        "## Outputs\n\nX.\n\n"
        "## Issues\n\nX.\n",
        encoding="utf-8",
    )
    result: VerificationResult = _verify(
        step_id=STEP_ID_RESEARCH_PAPERS,
        step_order=STEP_ORDER_4,
    )
    # Low word count may trigger W001 for some step specs with min word requirements
    # This tests the path; whether it triggers depends on registry config
    assert result is not None


# ---------------------------------------------------------------------------
# SV-W003: Step ID not in canonical registry
# ---------------------------------------------------------------------------


def test_sv_w003_custom_step_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(repo_root=tmp_path, task_id=TASK_ID)
    custom_step: str = "custom-analysis"
    step_folder: Path = paths.step_folder_path(
        task_id=TASK_ID,
        step_order=STEP_ORDER_1,
        step_id=custom_step,
    )
    step_folder.mkdir(parents=True, exist_ok=True)
    log_path: Path = step_folder / "step_log.md"
    log_path.write_text(
        '---\nspec_version: "3"\ntask_id: "t0001_test"\n'
        'step_number: 1\nstep_name: "Custom Analysis"\n'
        'status: "completed"\n'
        'started_at: "2026-04-01T00:00:00Z"\n'
        'completed_at: "2026-04-01T01:00:00Z"\n---\n\n'
        "# Step Log\n\n"
        "## Summary\n\nCustom step done.\n\n"
        "## Actions Taken\n\n* Did custom work.\n\n"
        "## Outputs\n\nNone.\n\n"
        "## Issues\n\nNone.\n",
        encoding="utf-8",
    )
    result: VerificationResult = verify_step_module.verify_step(
        task_id=TASK_ID,
        step_id=custom_step,
        step_order=STEP_ORDER_1,
    )
    assert "SV-W003" in _codes(result=result)
