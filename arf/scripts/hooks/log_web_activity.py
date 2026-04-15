"""PostToolUse hook: log WebSearch and WebFetch calls to logs/searches/.

Called by Claude Code after every WebSearch or WebFetch tool use. Detects
the task context from the hook input's ``cwd`` field (works in both the
main repo and worktrees) and falls back to git branch detection.

Hook input is received via stdin as JSON with fields: tool_name,
tool_input, tool_response, session_id, cwd.

Exit code is always 0 (logging only, never blocks).
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
TASK_BRANCH_PREFIX: str = "task/"
SEQUENCE_DIGITS: int = 3
TIMESTAMP_FORMAT: str = "%Y%m%dT%H%M%SZ"
MAX_OUTPUT_LENGTH: int = 50_000
WORKTREES_SUFFIX: str = "-worktrees"

TASK_ID_PATTERN: re.Pattern[str] = re.compile(r"t\d{4}_.+")


@dataclass(frozen=True, slots=True)
class TaskContext:
    task_id: str
    repo_root: Path


def _detect_task_from_cwd(*, cwd: str) -> TaskContext | None:
    """Detect task context from the working directory path.

    Checks if cwd is inside a worktree (../<repo>-worktrees/<task_id>/)
    or inside the main repo. Returns TaskContext or None.
    """
    cwd_path: Path = Path(cwd).resolve()

    # Check worktree path: ../<repo-name>-worktrees/<task_id>/
    worktrees_base: Path = REPO_ROOT.parent / f"{REPO_ROOT.name}{WORKTREES_SUFFIX}"
    if str(cwd_path).startswith(str(worktrees_base)):
        relative: Path = cwd_path.relative_to(worktrees_base)
        task_id: str = relative.parts[0] if len(relative.parts) > 0 else ""
        if TASK_ID_PATTERN.match(task_id) is not None:
            wt_root: Path = worktrees_base / task_id
            tasks_dir: Path = wt_root / "tasks"
            if tasks_dir.is_dir():
                return TaskContext(task_id=task_id, repo_root=wt_root)

    # Check if cwd is inside the main repo
    if str(cwd_path).startswith(str(REPO_ROOT)):
        # Try to detect task from git branch in the main repo
        return None

    return None


def _detect_task_from_branch(*, repo_root: Path) -> TaskContext | None:
    """Fall back to git branch detection."""
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        branch: str = result.stdout.strip()
        if not branch.startswith(TASK_BRANCH_PREFIX):
            return None
        task_id: str = branch[len(TASK_BRANCH_PREFIX) :]
        return TaskContext(task_id=task_id, repo_root=repo_root)
    except OSError:
        return None


def _next_sequence_number(*, directory: Path) -> int:
    if not directory.exists():
        return 1
    max_seq: int = 0
    for entry in directory.iterdir():
        match: re.Match[str] | None = re.match(r"^(\d{3})_", entry.name)
        if match is not None:
            seq: int = int(match.group(1))
            if seq > max_seq:
                max_seq = seq
    return max_seq + 1


def _read_hook_input() -> dict[str, Any] | None:
    try:
        raw: str = sys.stdin.read()
        if len(raw) == 0:
            return None
        data: object = json.loads(raw)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def main() -> None:
    hook_data: dict[str, Any] | None = _read_hook_input()
    if hook_data is None:
        sys.exit(0)

    tool_name: str = str(hook_data.get("tool_name", ""))
    if tool_name not in {"WebSearch", "WebFetch"}:
        sys.exit(0)

    # Detect task context: try cwd first, fall back to git branch
    cwd: str = str(hook_data.get("cwd", ""))
    ctx: TaskContext | None = None
    if len(cwd) > 0:
        ctx = _detect_task_from_cwd(cwd=cwd)
    if ctx is None:
        ctx = _detect_task_from_branch(repo_root=REPO_ROOT)
    if ctx is None:
        sys.exit(0)

    searches_dir: Path = ctx.repo_root / "tasks" / ctx.task_id / "logs" / "searches"
    if not searches_dir.parent.exists():
        sys.exit(0)

    tool_input: object = hook_data.get("tool_input", {})
    tool_response: object = hook_data.get("tool_response", {})

    searches_dir.mkdir(parents=True, exist_ok=True)

    now: datetime = datetime.now(tz=UTC)
    timestamp_str: str = now.strftime(TIMESTAMP_FORMAT)
    source: str = "web-search" if tool_name == "WebSearch" else "web-fetch"

    seq: int = _next_sequence_number(directory=searches_dir)
    base_name: str = f"{seq:0{SEQUENCE_DIGITS}d}_{timestamp_str}_{source}"

    log_entry: dict[str, object] = {
        "spec_version": "1",
        "task_id": ctx.task_id,
        "tool": tool_name,
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "input": tool_input,
    }

    if isinstance(tool_input, dict):
        if tool_name == "WebSearch":
            log_entry["query"] = tool_input.get("query", "")
        if tool_name == "WebFetch":
            log_entry["url"] = tool_input.get("url", "")
            log_entry["prompt"] = tool_input.get("prompt", "")

    json_path: Path = searches_dir / f"{base_name}.json"
    json_path.write_text(
        json.dumps(log_entry, indent=2) + "\n",
        encoding="utf-8",
    )

    # Save response to a separate file
    response_str: str = ""
    if isinstance(tool_response, dict):
        response_str = json.dumps(tool_response, indent=2)
    elif isinstance(tool_response, str):
        response_str = tool_response

    if len(response_str) > 0:
        output_path: Path = searches_dir / f"{base_name}.output.txt"
        output_path.write_text(
            response_str[:MAX_OUTPUT_LENGTH],
            encoding="utf-8",
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
