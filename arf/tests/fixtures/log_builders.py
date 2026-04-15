from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import (
    write_frontmatter_md,
    write_json,
    write_text,
)

SPEC_VERSION_COMMAND_LOG: str = "1"
SPEC_VERSION_STEP_LOG: str = "3"
DEFAULT_TIMESTAMP: str = "20260401T000000Z"
DEFAULT_STARTED_AT: str = "2026-04-01T00:00:00Z"
DEFAULT_COMPLETED_AT: str = "2026-04-01T00:01:00Z"
DEFAULT_DURATION_SECONDS: float = 60.0
DEFAULT_WORKING_DIR: str = "/tmp/test-workdir"
STATUS_COMPLETED: str = "completed"
DEFAULT_STDOUT: str = "test output\n"
DEFAULT_STDERR: str = ""


def _command_slug(*, command: str) -> str:
    slug: str = command.replace(" ", "-").replace("/", "-")[:40]
    safe_chars: list[str] = []
    for ch in slug:
        if ch.isalnum() or ch == "-":
            safe_chars.append(ch)
    return "".join(safe_chars) if len(safe_chars) > 0 else "command"


def build_command_log(
    *,
    repo_root: Path,
    task_id: str,
    log_index: int = 1,
    command: str = "echo test",
    exit_code: int = 0,
) -> Path:
    cmd_dir: Path = paths.command_logs_dir(task_id=task_id)
    slug: str = _command_slug(command=command)
    prefix: str = f"{log_index:03d}_{DEFAULT_TIMESTAMP}_{slug}"

    json_path: Path = cmd_dir / f"{prefix}.json"
    stdout_path: Path = cmd_dir / f"{prefix}.stdout.txt"
    stderr_path: Path = cmd_dir / f"{prefix}.stderr.txt"

    stdout_rel: str = f"{prefix}.stdout.txt"
    stderr_rel: str = f"{prefix}.stderr.txt"

    data: dict[str, object] = {
        "spec_version": SPEC_VERSION_COMMAND_LOG,
        "task_id": task_id,
        "command": command,
        "exit_code": exit_code,
        "duration_seconds": DEFAULT_DURATION_SECONDS,
        "started_at": DEFAULT_STARTED_AT,
        "completed_at": DEFAULT_COMPLETED_AT,
        "working_directory": DEFAULT_WORKING_DIR,
        "stdout_file": stdout_rel,
        "stderr_file": stderr_rel,
        "stdout_lines": 1,
        "stderr_lines": 0,
        "truncated": False,
    }
    write_json(path=json_path, data=data)
    write_text(path=stdout_path, content=DEFAULT_STDOUT)
    write_text(path=stderr_path, content=DEFAULT_STDERR)
    return json_path


def build_step_log(
    *,
    repo_root: Path,
    task_id: str,
    step_order: int,
    step_id: str,
    status: str = STATUS_COMPLETED,
) -> Path:
    step_dir: Path = paths.step_folder_path(
        task_id=task_id,
        step_order=step_order,
        step_id=step_id,
    )
    step_dir.mkdir(parents=True, exist_ok=True)

    frontmatter: dict[str, str | int] = {
        "spec_version": SPEC_VERSION_STEP_LOG,
        "task_id": task_id,
        "step_number": step_order,
        "step_name": step_id.replace("-", " ").title(),
        "status": status,
        "started_at": DEFAULT_STARTED_AT,
        "completed_at": DEFAULT_COMPLETED_AT,
    }

    body: str = (
        "# Step Log\n"
        "\n"
        "## Summary\n"
        "\n"
        "This step completed successfully and produced all expected"
        " outputs as specified in the plan.\n"
        "\n"
        "## Actions Taken\n"
        "\n"
        "* Executed the primary operation defined for this step\n"
        "* Validated outputs against expected format and content\n"
        "\n"
        "## Outputs\n"
        "\n"
        "All expected files were created in the appropriate locations.\n"
        "\n"
        "## Issues\n"
        "\n"
        "No issues encountered during execution.\n"
    )

    log_path: Path = step_dir / "step_log.md"
    write_frontmatter_md(
        path=log_path,
        frontmatter=frontmatter,
        body=body,
    )
    return log_path
