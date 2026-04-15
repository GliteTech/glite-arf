"""Stop hook: verify logs before agent finishes.

Called by Claude Code when the agent attempts to stop. Checks if:
1. We are on a task branch (task/<task_id>).
2. The task has a logs/ directory.

If both conditions are met, runs verify_logs.py and prints the result.
Always exits 0 so it never blocks the agent from stopping — it only
provides advisory feedback.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
VERIFY_LOGS_SCRIPT: Path = REPO_ROOT / "arf" / "scripts" / "verificators" / "verify_logs.py"
TASK_BRANCH_PREFIX: str = "task/"


def _get_current_branch() -> str | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except OSError:
        return None


def main() -> None:
    branch: str | None = _get_current_branch()
    if branch is None or not branch.startswith(TASK_BRANCH_PREFIX):
        sys.exit(0)

    task_id: str = branch[len(TASK_BRANCH_PREFIX) :]
    logs_path: Path = REPO_ROOT / "tasks" / task_id / "logs"
    if not logs_path.is_dir():
        sys.exit(0)

    result: subprocess.CompletedProcess[str] = subprocess.run(
        [
            "uv",
            "run",
            "python",
            str(VERIFY_LOGS_SCRIPT),
            task_id,
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if len(result.stdout) > 0:
        print(result.stdout)
    if len(result.stderr) > 0:
        print(result.stderr, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
