"""Tests for the public worktree path helper and raw-path CLI."""

import subprocess
import sys
from pathlib import Path

import arf.scripts.utils.worktree as worktree_module

# ---------------------------------------------------------------------------
# worktree_path_for — pure path computation, no validation
# ---------------------------------------------------------------------------


def test_worktree_path_for_returns_sibling_worktrees_path() -> None:
    slug: str = "infra_bootstrap"
    result: Path = worktree_module.worktree_path_for(slug=slug)
    assert result == worktree_module.WORKTREES_BASE / slug


def test_worktree_path_for_accepts_task_slug() -> None:
    slug: str = "t0001_example"
    result: Path = worktree_module.worktree_path_for(slug=slug)
    assert result == worktree_module.WORKTREES_BASE / slug


def test_worktree_path_for_accepts_arbitrary_slug_without_validation() -> None:
    slug: str = "not-a-task-id"
    result: Path = worktree_module.worktree_path_for(slug=slug)
    assert result == worktree_module.WORKTREES_BASE / slug


def test_worktree_path_for_derives_from_repo_name_not_hardcoded() -> None:
    base: Path = worktree_module.WORKTREES_BASE
    assert base.name == f"{worktree_module.REPO_ROOT.name}-worktrees"
    assert base.parent == worktree_module.REPO_ROOT.parent


# ---------------------------------------------------------------------------
# raw-path CLI subcommand
# ---------------------------------------------------------------------------


def _run_cli(*, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "arf.scripts.utils.worktree", *args],
        capture_output=True,
        text=True,
        cwd=worktree_module.REPO_ROOT,
        check=False,
    )


def test_raw_path_cli_prints_worktree_path_for_infra_slug() -> None:
    result: subprocess.CompletedProcess[str] = _run_cli(
        args=["raw-path", "infra_bootstrap"],
    )
    assert result.returncode == 0, result.stderr
    expected: Path = worktree_module.WORKTREES_BASE / "infra_bootstrap"
    assert result.stdout.strip() == str(expected)


def test_raw_path_cli_accepts_non_task_slug() -> None:
    result: subprocess.CompletedProcess[str] = _run_cli(
        args=["raw-path", "not-a-task-id"],
    )
    assert result.returncode == 0, result.stderr
    expected: Path = worktree_module.WORKTREES_BASE / "not-a-task-id"
    assert result.stdout.strip() == str(expected)


def test_path_cli_still_rejects_non_task_slug() -> None:
    """Regression: the existing `path` subcommand must still validate."""
    result: subprocess.CompletedProcess[str] = _run_cli(
        args=["path", "not-a-task-id"],
    )
    assert result.returncode != 0
    assert "invalid task_id format" in result.stderr


def test_path_cli_accepts_task_id_format(tmp_path: Path) -> None:
    result: subprocess.CompletedProcess[str] = _run_cli(
        args=["path", "t0001_example"],
    )
    assert result.returncode == 0, result.stderr
    expected: Path = worktree_module.WORKTREES_BASE / "t0001_example"
    assert result.stdout.strip() == str(expected)


# ---------------------------------------------------------------------------
# Backward compatibility: _worktree_path still exists and matches the public helper
# ---------------------------------------------------------------------------


def test_private_helper_still_works_for_internal_callers() -> None:
    task_id: str = "t0042_backward_compat"
    assert worktree_module._worktree_path(task_id=task_id) == (
        worktree_module.worktree_path_for(slug=task_id)
    )
