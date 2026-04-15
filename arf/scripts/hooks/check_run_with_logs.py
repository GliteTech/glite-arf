"""PostToolUse hook: remind agent to use run_with_logs.py for all commands.

Called by Claude Code after every Bash tool use. Checks if:
1. We are on a task branch (task/<task_id>) — detected via cwd or git branch.
2. The command is NOT already wrapped in run_with_logs.py.
3. The command is not a git or prestep/poststep command (exempt).

Hook input is received via stdin as JSON with fields: tool_name,
tool_input, tool_response, session_id, cwd.

If conditions are met, prints a reminder to stdout so it appears as
additionalContext in the agent's next turn.

Exit code is always 0 (advisory only, never blocks).
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
TASK_BRANCH_PREFIX: str = "task/"
WORKTREES_SUFFIX: str = "-worktrees"
TASK_ID_PATTERN: re.Pattern[str] = re.compile(r"t\d{4}_.+")
EXEMPT_COMMAND_MARKERS: list[str] = [
    "git ",
    "prestep.py",
    "poststep.py",
    "run_with_logs.py",
]


@dataclass(frozen=True, slots=True)
class TaskContext:
    task_id: str
    repo_root: Path


def _detect_task_from_cwd(*, cwd: str) -> TaskContext | None:
    """Detect task context from the working directory path."""
    cwd_path: Path = Path(cwd).resolve()

    worktrees_base: Path = REPO_ROOT.parent / f"{REPO_ROOT.name}{WORKTREES_SUFFIX}"
    if str(cwd_path).startswith(str(worktrees_base)):
        relative: Path = cwd_path.relative_to(worktrees_base)
        task_id: str = relative.parts[0] if len(relative.parts) > 0 else ""
        if TASK_ID_PATTERN.match(task_id) is not None:
            wt_root: Path = worktrees_base / task_id
            return TaskContext(task_id=task_id, repo_root=wt_root)

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

    # Detect task context: try cwd first, fall back to git branch
    cwd: str = str(hook_data.get("cwd", ""))
    ctx: TaskContext | None = None
    if len(cwd) > 0:
        ctx = _detect_task_from_cwd(cwd=cwd)
    if ctx is None:
        ctx = _detect_task_from_branch(repo_root=REPO_ROOT)
    if ctx is None:
        sys.exit(0)

    task_dir: Path = ctx.repo_root / "tasks" / ctx.task_id
    if not task_dir.is_dir():
        sys.exit(0)

    tool_input: object = hook_data.get("tool_input", {})
    command_str: str = ""
    if isinstance(tool_input, dict):
        command_str = str(tool_input.get("command", ""))
    elif isinstance(tool_input, str):
        command_str = tool_input

    if len(command_str) == 0:
        sys.exit(0)

    is_exempt: bool = any(marker in command_str for marker in EXEMPT_COMMAND_MARKERS)
    if is_exempt:
        sys.exit(0)

    print(
        "REMINDER: CLI commands in task branches should be wrapped "
        "with run_with_logs.py:\n"
        f"  uv run python -m arf.scripts.utils.run_with_logs "
        f"--task-id {ctx.task_id} -- <command>",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
