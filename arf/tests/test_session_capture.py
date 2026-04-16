import json
import os
from pathlib import Path
from typing import Any

import pytest

import arf.scripts.utils.capture_task_sessions as capture_task_sessions_module
import arf.scripts.verificators.verify_logs as verify_logs_module
import arf.scripts.verificators.verify_task_complete as verify_task_complete_module
import arf.scripts.verificators.verify_task_folder as verify_task_folder_module
from arf.scripts.verificators.common import paths

type TaskID = str

TASKS_SUBDIR: str = "tasks"
TASK_JSON_FILE_NAME: str = "task.json"
STEP_TRACKER_FILE_NAME: str = "step_tracker.json"


def _write_json(*, path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj=data, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _configure_repo_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> Path:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    tasks_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=verify_task_folder_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=verify_task_complete_module, name="TASKS_DIR", value=tasks_dir)
    return tasks_dir


def _create_completed_task_skeleton(
    *,
    repo_root: Path,
    task_id: TaskID,
) -> Path:
    task_root: Path = repo_root / TASKS_SUBDIR / task_id
    _write_json(
        path=task_root / TASK_JSON_FILE_NAME,
        data={
            "task_id": task_id,
            "task_index": 1,
            "name": "Example task",
            "short_description": "Short description.",
            "status": "completed",
            "dependencies": [],
            "start_time": "2026-04-05T10:00:00Z",
            "end_time": "2026-04-05T11:00:00Z",
            "expected_assets": {},
            "task_types": [],
            "source_suggestion": None,
        },
    )
    _write_json(
        path=task_root / STEP_TRACKER_FILE_NAME,
        data={
            "task_id": task_id,
            "steps": [],
        },
    )

    for directory_name in [
        "plan",
        "research",
        "assets",
        "results",
        "corrections",
        "intervention",
        "logs/commands",
        "logs/steps",
        "logs/searches",
        "logs/sessions",
    ]:
        (task_root / directory_name).mkdir(parents=True, exist_ok=True)

    _write_text(
        path=task_root / "plan" / "plan.md",
        content="# Plan\n\nPlaceholder plan.\n",
    )
    _write_text(
        path=task_root / "research" / "research_papers.md",
        content="# Paper Research\n\nPlaceholder paper research.\n",
    )
    _write_text(
        path=task_root / "research" / "research_internet.md",
        content="# Internet Research\n\nPlaceholder internet research.\n",
    )
    _write_text(
        path=task_root / "results" / "results_summary.md",
        content="# Summary\n\nPlaceholder summary.\n",
    )
    _write_text(
        path=task_root / "results" / "results_detailed.md",
        content="# Detailed Results\n\nPlaceholder detailed results.\n",
    )
    _write_json(path=task_root / "results" / "metrics.json", data={})
    _write_json(path=task_root / "results" / "suggestions.json", data={"suggestions": []})
    _write_json(path=task_root / "results" / "costs.json", data={})
    _write_json(path=task_root / "results" / "remote_machines_used.json", data=[])
    return task_root


def _diagnostic_codes(*, diagnostics: list[Any]) -> set[str]:
    return {diagnostic.code.text for diagnostic in diagnostics}


def test_capture_task_sessions_copies_matching_transcripts_from_codex_and_claude(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0001_session_capture"
    task_root: Path = _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    codex_match: Path = codex_root / "2026" / "04" / "05" / "rollout-1.jsonl"
    codex_non_match: Path = codex_root / "2026" / "04" / "05" / "rollout-other.jsonl"
    claude_match: Path = (
        claude_root / "-Users-me-repo-worktrees-t0001_session_capture" / "session-1.jsonl"
    )

    codex_match_session_meta: dict[str, Any] = {
        "type": "session_meta",
        "payload": {
            "cwd": f"/Users/me/repo-worktrees/{task_id}",
        },
    }
    _write_text(
        path=codex_match,
        content=json.dumps(codex_match_session_meta) + "\n",
    )
    _write_text(path=codex_non_match, content='{"message":"different task"}\n')
    _write_text(path=claude_match, content=f'{{"message":"follow up for {task_id}"}}\n')
    _write_text(
        path=task_root / "logs" / "sessions" / "stale.jsonl",
        content='{"message":"stale"}\n',
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_files: set[str] = {
        path.name for path in outcome.sessions_dir.glob("*.jsonl") if path.is_file() is True
    }
    assert copied_files == {
        "codex__2026__04__05__rollout-1.jsonl",
        "claude_code__-Users-me-repo-worktrees-t0001_session_capture__session-1.jsonl",
    }
    assert (outcome.sessions_dir / "stale.jsonl").exists() is False

    report_data: dict[str, Any] = json.loads(outcome.report_path.read_text(encoding="utf-8"))
    assert report_data["task_id"] == task_id
    assert len(report_data["checked_roots"]) == 2
    assert len(report_data["copied_sessions"]) == 2


def test_verify_logs_warns_when_sessions_directory_has_report_but_no_transcripts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0002_missing_transcripts"
    task_root: Path = _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    _write_json(
        path=(
            task_root / "logs" / "sessions" / capture_task_sessions_module.CAPTURE_REPORT_FILE_NAME
        ),
        data={
            "spec_version": "1",
            "task_id": task_id,
            "captured_at": "2026-04-05T12:00:00Z",
            "checked_roots": [
                {
                    "source_kind": "codex",
                    "root_path": "/tmp/.codex/sessions",
                    "exists": True,
                    "candidate_file_count": 3,
                    "matched_file_count": 0,
                },
            ],
            "copied_sessions": [],
            "errors": [],
        },
    )

    result = verify_logs_module.verify_logs(task_id=task_id)

    codes: set[str] = _diagnostic_codes(diagnostics=result.diagnostics)
    assert "LG-W007" in codes
    assert "LG-W008" not in codes


def test_verify_task_folder_warns_when_completed_task_has_no_session_transcripts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0003_task_folder_warning"
    task_root: Path = _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    _write_json(
        path=(
            task_root / "logs" / "sessions" / capture_task_sessions_module.CAPTURE_REPORT_FILE_NAME
        ),
        data={
            "spec_version": "1",
            "task_id": task_id,
            "captured_at": "2026-04-05T12:00:00Z",
            "checked_roots": [],
            "copied_sessions": [],
            "errors": [],
        },
    )

    result = verify_task_folder_module.verify_task_folder(task_id=task_id)

    assert "FD-W006" in _diagnostic_codes(diagnostics=result.diagnostics)


def test_pid_based_matching(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0005_pid_matching"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.setattr(target=capture_task_sessions_module, name="REPO_ROOT", value=tmp_path)

    # Simulate a worktree whose parent ends with "-worktrees" and whose
    # name contains the task prefix — this is how _cwd_matches_task works.
    worktree_dir: Path = tmp_path / "repo-worktrees" / "t0005"
    worktree_dir.mkdir(parents=True, exist_ok=True)

    home_dir: Path = tmp_path / "home"

    # Create PID mapping file: ~/.claude/sessions/12345.json
    pid_sessions_dir: Path = home_dir / ".claude" / "sessions"
    pid_sessions_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        path=pid_sessions_dir / "12345.json",
        data={
            "pid": 12345,
            "sessionId": "test-session-id",
            "cwd": str(worktree_dir),
        },
    )

    # Create corresponding project JSONL file
    encoded_cwd: str = str(worktree_dir).replace("/", "-")
    projects_dir: Path = home_dir / ".claude" / "projects"
    session_jsonl: Path = projects_dir / encoded_cwd / "test-session-id.jsonl"
    _write_text(
        path=session_jsonl,
        content=f'{{"message":"working on {task_id}"}}\n',
    )

    # Set up source roots pointing at the Claude projects dir
    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=projects_dir,
            ),
        ],
        home_dir=home_dir,
    )

    # Verify the file was captured via PID mapping
    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    assert len(copied_sessions) >= 1
    pid_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "pid_mapping"
    ]
    assert len(pid_matched) >= 1, "at least one session matched by pid_mapping"


def test_codex_thread_id_matching(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0006_codex_thread"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    thread_id: str = "thread-abc-123"
    monkeypatch.setenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        value=thread_id,
    )

    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    matching_file: Path = codex_root / "2026" / "04" / "06" / f"rollout-{thread_id}.jsonl"
    _write_text(
        path=matching_file,
        content=f'{{"message":"codex session for {task_id}"}}\n',
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    thread_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "codex_thread_id"
    ]
    assert len(thread_matched) >= 1, "at least one session matched by codex_thread_id"


def test_content_fallback_when_no_pid_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0007_content_fallback"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    # No PID files, no thread ID — only content matching should work
    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    # The Codex content fallback requires a ``cwd`` field in the session JSONL
    # pointing at a worktree directory for this task. Merely mentioning the
    # task ID in a freeform message is NOT sufficient — that matches sessions
    # run from the main repo that just discussed the task.
    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    content_match: Path = codex_root / "2026" / "04" / "06" / "rollout-1.jsonl"
    session_meta: dict[str, Any] = {
        "type": "session_meta",
        "payload": {
            "id": "session-xyz",
            "cwd": f"/tmp/repo-worktrees/{task_id}",
        },
    }
    _write_text(
        path=content_match,
        content=json.dumps(session_meta) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    assert len(copied_sessions) >= 1
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) >= 1, "content fallback matched at least one session"


def test_content_fallback_skips_repo_root_codex_sessions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex sessions that run from the main repo (not a worktree) and only
    mention the task ID in freeform message content must NOT be captured by
    the content fallback. Otherwise unrelated later sessions that happen to
    discuss a task get copied into its log folder.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0014_add_anton_papers_llm_tutoring"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    repo_root_session: Path = codex_root / "2026" / "04" / "11" / "rollout-other.jsonl"
    session_meta: dict[str, Any] = {
        "type": "session_meta",
        "payload": {
            "id": "session-repo-root",
            "cwd": "/Users/me/research-ai-meetup-papers",
        },
    }
    message_event: dict[str, Any] = {
        "type": "message",
        "payload": {
            "text": f"Later session that happens to discuss {task_id} in text",
        },
    }
    _write_text(
        path=repo_root_session,
        content=json.dumps(session_meta) + "\n" + json.dumps(message_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) == 0, (
        f"repo-root codex session must not be captured by content fallback; got: {content_matched}"
    )


def test_content_fallback_captures_codex_session_with_nested_worktree_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A codex session whose worktree ``cwd`` is nested inside a tool call
    payload (not at the top-level ``session_meta``) must still be captured.
    Codex sessions include per-command tool_call events with their own ``cwd``
    — those are legitimate evidence that the session ran in the task worktree.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0014_add_anton_papers_llm_tutoring"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    worktree_session: Path = codex_root / "2026" / "04" / "11" / "rollout-worktree.jsonl"
    tool_call_event: dict[str, Any] = {
        "type": "tool_call",
        "payload": {
            "name": "shell",
            "arguments": {
                "cwd": f"/Users/me/research-ai-meetup-papers-worktrees/{task_id}",
                "command": "ls",
            },
        },
    }
    _write_text(
        path=worktree_session,
        content=json.dumps(tool_call_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) >= 1, (
        "codex session whose worktree cwd lives inside a tool_call payload "
        "must still be captured by content fallback"
    )


def test_content_fallback_skips_repo_root_claude_sessions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repo-root Claude sessions that mention the task ID in content
    should NOT be captured — only worktree sessions are precise enough."""
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0083_retrain_escher"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    # Repo-root Claude session that mentions the task ID in content
    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    repo_root_session: Path = claude_root / "-Users-me-research-wsd" / "abc123.jsonl"
    _write_text(
        path=repo_root_session,
        content=f'{{"message":"discussing {task_id} in main repo"}}\n',
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) == 0, "repo-root session should not be captured by content fallback"


def test_content_fallback_captures_worktree_claude_sessions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Worktree Claude sessions that mention the task ID should be captured."""
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0083_retrain_escher"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    # Worktree Claude session that mentions the task ID
    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    worktree_session: Path = (
        claude_root / "-Users-me-research-wsd-worktrees-t0083_retrain_escher" / "session123.jsonl"
    )
    _write_text(
        path=worktree_session,
        content=f'{{"message":"working on {task_id} in worktree"}}\n',
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) >= 1, "worktree session should be captured by content fallback"


def test_verify_task_complete_runs_verify_logs_sub_verificator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0004_verify_task_complete"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    called_labels: list[str] = []

    def _record_sub_verificator(
        *,
        module_name: str,
        args: list[str],
        label: str,
        file_path: Path,
    ) -> list[Any]:
        called_labels.append(label)
        return []

    monkeypatch.setattr(
        target=verify_task_complete_module,
        name="_run_sub_verificator",
        value=_record_sub_verificator,
    )
    monkeypatch.setattr(
        target=verify_task_complete_module,
        name="_check_git_branch_exists",
        value=lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        target=verify_task_complete_module,
        name="_check_pr_merged",
        value=lambda *, task_id, file_path: [],
    )
    monkeypatch.setattr(
        target=verify_task_complete_module,
        name="_check_no_files_outside_task",
        value=lambda *, task_id, file_path: [],
    )

    verify_task_complete_module.verify_task_complete(task_id=task_id)

    assert "verify_logs" in called_labels


# ---------------------------------------------------------------------------
# Content-CWD fallback for Claude Code orchestrator sessions
# ---------------------------------------------------------------------------


def test_content_fallback_captures_claude_orchestrator_session_by_nested_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Claude Code orchestrator sessions launched from the main repo have their
    JSONL files stored under a main-repo-encoded directory (no ``-worktrees``
    in the on-disk path), but the body records ``cwd`` values pointing into
    the worktree directory because subagents run there. Such sessions must be
    captured by the content fallback when the nested ``cwd`` matches the task
    worktree.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0018_some_task"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    orchestrator_session: Path = (
        claude_root / "-Users-me-research-ai-meetup-papers" / "orchestrator-1.jsonl"
    )
    tool_call_event: dict[str, Any] = {
        "type": "tool_call",
        "payload": {
            "name": "bash",
            "arguments": {
                "cwd": f"/Users/me/research-ai-meetup-papers-worktrees/{task_id}",
                "command": "ls",
            },
        },
    }
    _write_text(
        path=orchestrator_session,
        content=json.dumps(tool_call_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) >= 1, (
        "claude orchestrator session with nested worktree cwd must be captured by content fallback"
    )


def test_content_fallback_captures_claude_orchestrator_session_by_top_level_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same as the nested-cwd case, but the ``cwd`` lives at the top level of
    one of the JSONL lines rather than inside a tool call payload.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0018_some_task"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    orchestrator_session: Path = (
        claude_root / "-Users-me-research-ai-meetup-papers" / "orchestrator-top.jsonl"
    )
    top_level_event: dict[str, Any] = {
        "type": "user",
        "cwd": f"/Users/me/research-ai-meetup-papers-worktrees/{task_id}",
        "message": "hello",
    }
    _write_text(
        path=orchestrator_session,
        content=json.dumps(top_level_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) >= 1, (
        "claude orchestrator session with top-level worktree cwd must be "
        "captured by content fallback"
    )


def test_content_fallback_rejects_claude_orchestrator_session_referencing_other_task_worktree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A claude orchestrator session whose body ``cwd`` points at a DIFFERENT
    task's worktree must not be captured for the target task.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0018_some_task"
    other_task_id: str = "t0099_other_task"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    orchestrator_session: Path = (
        claude_root / "-Users-me-research-ai-meetup-papers" / "orchestrator-other.jsonl"
    )
    top_level_event: dict[str, Any] = {
        "type": "user",
        "cwd": f"/Users/me/research-ai-meetup-papers-worktrees/{other_task_id}",
        "message": f"loosely mentions {task_id}",
    }
    _write_text(
        path=orchestrator_session,
        content=json.dumps(top_level_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) == 0, (
        "session whose cwd points at another task's worktree must not be "
        f"captured for {task_id}; got: {content_matched}"
    )


def test_content_fallback_rejects_claude_orchestrator_session_without_worktree_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A claude orchestrator session whose body mentions the task ID in
    freeform message text but has no ``cwd`` field anywhere must not be
    captured by the content fallback.
    """
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0018_some_task"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    monkeypatch.delenv(
        name=capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    claude_root: Path = tmp_path / "home" / ".claude" / "projects"
    orchestrator_session: Path = (
        claude_root / "-Users-me-research-ai-meetup-papers" / "orchestrator-freeform.jsonl"
    )
    freeform_event: dict[str, Any] = {
        "type": "user",
        "message": f"let's discuss {task_id} in plain text without any cwd field",
    }
    _write_text(
        path=orchestrator_session,
        content=json.dumps(freeform_event) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CLAUDE_CODE_SOURCE_KIND,
                root_path=claude_root,
            ),
        ],
    )

    copied_sessions: list[dict[str, Any]] = json.loads(
        outcome.report_path.read_text(encoding="utf-8"),
    )["copied_sessions"]
    content_matched: list[dict[str, Any]] = [
        s for s in copied_sessions if s["matched_by"] == "task_id_content"
    ]
    assert len(content_matched) == 0, (
        "session without any cwd field must not be captured by content fallback"
    )


# ---------------------------------------------------------------------------
# discover_session_files — public discovery API
# ---------------------------------------------------------------------------


def _seed_claude_jsonl(
    *,
    home_dir: Path,
    repo_root: Path,
    session_id: str,
    body: str,
) -> Path:
    encoded: str = capture_task_sessions_module.cwd_to_encoded_path(
        cwd=str(repo_root),
    )
    jsonl: Path = home_dir / ".claude" / "projects" / encoded / f"{session_id}.jsonl"
    _write_text(path=jsonl, content=body)
    return jsonl


def _seed_codex_jsonl(
    *,
    home_dir: Path,
    relative_name: str,
    body: str,
) -> Path:
    jsonl: Path = home_dir / ".codex" / "sessions" / relative_name
    _write_text(path=jsonl, content=body)
    return jsonl


def test_cwd_to_encoded_path_is_public_and_matches_internal_helper() -> None:
    cwd: str = "/Users/example/glite-arf"
    public: str = capture_task_sessions_module.cwd_to_encoded_path(cwd=cwd)
    private: str = capture_task_sessions_module._cwd_to_encoded_path(cwd=cwd)
    assert public == private
    assert public == "-Users-example-glite-arf"


def test_discover_session_files_task_target_finds_content_matched_jsonl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0003_discover_task"
    _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    home_dir: Path = tmp_path / "home"
    worktree_dir: Path = home_dir / ".claude" / "projects" / f"-Users-me-repo-worktrees-{task_id}"
    jsonl: Path = worktree_dir / "session.jsonl"
    _write_text(path=jsonl, content=f'{{"message":"follow up for {task_id}"}}\n')

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.TaskTarget(task_id=task_id),
        home_dir=home_dir,
    )

    assert jsonl in result.matched_files
    assert result.target_description == f"task:{task_id}"


def test_discover_session_files_skill_target_content_match(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        target=capture_task_sessions_module,
        name="REPO_ROOT",
        value=tmp_path,
    )
    home_dir: Path = tmp_path / "home"

    hit: Path = _seed_claude_jsonl(
        home_dir=home_dir,
        repo_root=tmp_path,
        session_id="session-hit",
        body='{"tool":"Skill","input":{"skill":"human-brainstorm"}}\n',
    )
    _seed_claude_jsonl(
        home_dir=home_dir,
        repo_root=tmp_path,
        session_id="session-miss",
        body='{"tool":"Read"}\n',
    )

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.SkillSlugTarget(
            slug="human-brainstorm",
        ),
        home_dir=home_dir,
    )

    assert hit in result.matched_files
    assert result.target_description == "skill:human-brainstorm"


def test_discover_session_files_skill_target_matches_on_skill_md_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        target=capture_task_sessions_module,
        name="REPO_ROOT",
        value=tmp_path,
    )
    home_dir: Path = tmp_path / "home"

    hit: Path = _seed_claude_jsonl(
        home_dir=home_dir,
        repo_root=tmp_path,
        session_id="session-path",
        body='{"read":"arf/skills/execute-task/SKILL.md"}\n',
    )

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.SkillSlugTarget(
            slug="execute-task",
        ),
        home_dir=home_dir,
    )

    assert hit in result.matched_files


def test_discover_session_files_current_uses_codex_thread_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        target=capture_task_sessions_module,
        name="REPO_ROOT",
        value=tmp_path,
    )
    home_dir: Path = tmp_path / "home"
    thread_id: str = "abc123thread"
    monkeypatch.setenv(
        capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        thread_id,
    )

    matching: Path = _seed_codex_jsonl(
        home_dir=home_dir,
        relative_name=f"2026/04/11/rollout-{thread_id}-stuff.jsonl",
        body='{"message":"current session"}\n',
    )
    _seed_codex_jsonl(
        home_dir=home_dir,
        relative_name="2026/04/11/rollout-other.jsonl",
        body='{"message":"other session"}\n',
    )

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.CurrentSessionTarget(),
        home_dir=home_dir,
    )

    assert matching in result.matched_files
    assert result.target_description == "current"
    assert "codex" in result.resolution_note.lower()


def test_discover_session_files_current_falls_back_to_most_recent_claude_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        target=capture_task_sessions_module,
        name="REPO_ROOT",
        value=tmp_path,
    )
    home_dir: Path = tmp_path / "home"
    monkeypatch.delenv(
        capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )

    older: Path = _seed_claude_jsonl(
        home_dir=home_dir,
        repo_root=tmp_path,
        session_id="session-older",
        body='{"message":"older"}\n',
    )
    newer: Path = _seed_claude_jsonl(
        home_dir=home_dir,
        repo_root=tmp_path,
        session_id="session-newer",
        body='{"message":"newer"}\n',
    )

    os.utime(path=older, times=(1_700_000_000, 1_700_000_000))
    os.utime(path=newer, times=(1_800_000_000, 1_800_000_000))

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.CurrentSessionTarget(),
        home_dir=home_dir,
    )

    assert newer in result.matched_files
    assert older not in result.matched_files


def test_discover_session_files_current_returns_empty_when_no_sessions_exist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        target=capture_task_sessions_module,
        name="REPO_ROOT",
        value=tmp_path,
    )
    monkeypatch.delenv(
        capture_task_sessions_module.CODEX_THREAD_ID_ENV_VAR,
        raising=False,
    )
    home_dir: Path = tmp_path / "home"
    home_dir.mkdir()

    result: capture_task_sessions_module.SessionDiscoveryResult
    result = capture_task_sessions_module.discover_session_files(
        target=capture_task_sessions_module.CurrentSessionTarget(),
        home_dir=home_dir,
    )

    assert len(result.matched_files) == 0
    assert "no" in result.resolution_note.lower()


def test_capture_task_sessions_still_works_after_discovery_api_lands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: the original task-id flow must not change behavior."""
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0004_regression_check"
    task_root: Path = _create_completed_task_skeleton(repo_root=tmp_path, task_id=task_id)

    codex_root: Path = tmp_path / "home" / ".codex" / "sessions"
    codex_match: Path = codex_root / "2026" / "04" / "11" / "rollout-x.jsonl"
    session_meta: dict[str, Any] = {
        "type": "session_meta",
        "payload": {
            "cwd": f"/tmp/repo-worktrees/{task_id}",
        },
    }
    _write_text(
        path=codex_match,
        content=json.dumps(session_meta) + "\n",
    )

    outcome = capture_task_sessions_module.capture_task_sessions(
        task_id=task_id,
        source_roots=[
            capture_task_sessions_module.SessionSourceRoot(
                source_kind=capture_task_sessions_module.CODEX_SOURCE_KIND,
                root_path=codex_root,
            ),
        ],
    )

    assert len(outcome.report.copied_sessions) == 1
    assert task_root.exists()
