"""Wrapper script that executes a command and logs execution metadata.

Usage:
    uv run python -m arf.scripts.utils.run_with_logs --task-id <task_id> -- <command...>

The script:
    1. Creates logs/commands/ inside the task folder if it does not exist.
    2. Runs the command via subprocess.
    3. Captures stdout and stderr to separate files.
    4. Writes a structured JSON log entry.
    5. Exits with the child process exit code.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
TASKS_DIR: Path = REPO_ROOT / "tasks"

SPEC_VERSION: str = "1"
MAX_OUTPUT_LINES: int = 10_000
TRUNCATION_NOTE: str = (
    "[TRUNCATED] Output exceeded {max_lines} lines. Only the last {max_lines} lines are shown.\n\n"
)
COMMAND_SLUG_MAX_LENGTH: int = 40
SEQUENCE_DIGITS: int = 3
TIMESTAMP_FORMAT: str = "%Y%m%dT%H%M%SZ"

REDACTED_PLACEHOLDER: str = "<REDACTED>"

# Patterns for secret redaction in captured command output.
# Each tuple: (compiled regex, replacement template).
_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # key=value patterns (api_key=..., instance_api_key=..., secret=..., etc.)
    (
        re.compile(
            r"(?i)((?:api[_-]?key|instance_api_key|secret|token|password)\s*=\s*)\S+",
        ),
        rf"\1{REDACTED_PLACEHOLDER}",
    ),
    # JSON "key": "value" patterns
    (
        re.compile(
            r'(?i)("(?:api[_-]?key|instance_api_key|secret|token|password)"\s*:\s*")[^"]*"',
        ),
        rf"\1{REDACTED_PLACEHOLDER}" + '"',
    ),
    # Bearer tokens
    (
        re.compile(r"(?i)(Bearer\s+)\S+"),
        rf"\1{REDACTED_PLACEHOLDER}",
    ),
]


# ---------------------------------------------------------------------------
# Pydantic model for command log JSON
# ---------------------------------------------------------------------------


class CommandLogEntry(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    spec_version: str
    task_id: str
    command: str
    exit_code: int
    duration_seconds: float
    started_at: str
    completed_at: str
    working_directory: str
    stdout_file: str
    stderr_file: str
    stdout_lines: int
    stderr_lines: int
    truncated: bool


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _make_command_slug(*, command_tokens: list[str]) -> str:
    """Build a filesystem-safe slug from the first 3 command tokens."""
    slug_parts: list[str] = command_tokens[:3]
    raw_slug: str = "-".join(slug_parts).lower()
    safe_slug: str = re.sub(r"[^a-z0-9\-]", "-", raw_slug)
    safe_slug = re.sub(r"-{2,}", "-", safe_slug)
    safe_slug = safe_slug.strip("-")
    return safe_slug[:COMMAND_SLUG_MAX_LENGTH]


def _next_sequence_number(*, directory: Path) -> int:
    """Find the next available sequence number in a directory."""
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


def _redact_secrets(*, text: str) -> str:
    result: str = text
    for pattern, replacement in _SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def _write_captured_output(
    *,
    file_path: Path,
    raw_output: str,
    max_lines: int,
) -> tuple[int, bool]:
    """Write captured output to file, truncating if necessary.

    Non-empty output is always terminated with a trailing newline so the
    pre-commit end-of-file-fixer does not rewrite these capture files on
    every commit. Empty output stays empty — we never emit a spurious
    newline for commands that produced no output.

    Returns (line_count, was_truncated).
    """
    raw_output = _redact_secrets(text=raw_output)
    lines: list[str] = raw_output.splitlines(keepends=True)
    total_lines: int = len(lines)
    truncated: bool = total_lines > max_lines

    with open(file=file_path, mode="w", encoding="utf-8") as f:
        if truncated:
            f.write(
                TRUNCATION_NOTE.format(max_lines=max_lines),
            )
            tail: list[str] = lines[-max_lines:]
            for line in tail:
                f.write(line)
            if len(tail) > 0 and not tail[-1].endswith("\n"):
                f.write("\n")
        else:
            f.write(raw_output)
            if len(raw_output) > 0 and not raw_output.endswith("\n"):
                f.write("\n")

    return total_lines, truncated


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def run_command_with_logging(
    *,
    task_id: str,
    command_tokens: list[str],
) -> int:
    """Execute a command and write structured logs. Returns the exit code."""
    task_dir: Path = TASKS_DIR / task_id
    commands_dir: Path = task_dir / "logs" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    seq: int = _next_sequence_number(directory=commands_dir)
    started_at: datetime = datetime.now(tz=UTC)
    timestamp_str: str = started_at.strftime(TIMESTAMP_FORMAT)
    slug: str = _make_command_slug(command_tokens=command_tokens)
    base_name: str = f"{seq:0{SEQUENCE_DIGITS}d}_{timestamp_str}_{slug}"

    full_command: str = " ".join(command_tokens)
    cwd: str = str(Path.cwd())

    # Scrub VIRTUAL_ENV from the child process environment. Wrapped commands
    # are usually ``uv run ...`` executed inside a sibling git worktree whose
    # own ``.venv`` does not match the outer shell's ``VIRTUAL_ENV``. Leaving
    # that variable set makes ``uv`` print a noisy ignore-warning on every
    # invocation. Only ``VIRTUAL_ENV`` is removed; ``PATH``, ``PYTHONPATH``,
    # and every other variable propagate unchanged.
    child_env: dict[str, str] = os.environ.copy()
    child_env.pop("VIRTUAL_ENV", None)

    start_time: float = time.monotonic()
    result: subprocess.CompletedProcess[str] = subprocess.run(
        command_tokens,
        capture_output=True,
        text=True,
        env=child_env,
    )
    end_time: float = time.monotonic()

    completed_at: datetime = datetime.now(tz=UTC)
    duration: float = round(end_time - start_time, 3)

    stdout_filename: str = f"{base_name}.stdout.txt"
    stderr_filename: str = f"{base_name}.stderr.txt"

    stdout_lines, stdout_truncated = _write_captured_output(
        file_path=commands_dir / stdout_filename,
        raw_output=result.stdout,
        max_lines=MAX_OUTPUT_LINES,
    )
    stderr_lines, stderr_truncated = _write_captured_output(
        file_path=commands_dir / stderr_filename,
        raw_output=result.stderr,
        max_lines=MAX_OUTPUT_LINES,
    )

    log_entry: CommandLogEntry = CommandLogEntry(
        spec_version=SPEC_VERSION,
        task_id=task_id,
        command=full_command,
        exit_code=result.returncode,
        duration_seconds=duration,
        started_at=started_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        completed_at=completed_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        working_directory=cwd,
        stdout_file=stdout_filename,
        stderr_file=stderr_filename,
        stdout_lines=stdout_lines,
        stderr_lines=stderr_lines,
        truncated=stdout_truncated or stderr_truncated,
    )

    json_path: Path = commands_dir / f"{base_name}.json"
    json_path.write_text(
        log_entry.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )

    # Print stdout/stderr to the terminal so the caller still sees output
    if len(result.stdout) > 0:
        sys.stdout.write(result.stdout)
        sys.stdout.flush()
    if len(result.stderr) > 0:
        sys.stderr.write(result.stderr)
        sys.stderr.flush()

    return result.returncode


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Execute a command and log execution metadata",
        usage=(
            "uv run python -m arf.scripts.utils.run_with_logs --task-id <task_id> -- <command...>"
        ),
    )
    parser.add_argument(
        "--task-id",
        required=True,
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute (after --)",
    )
    args: argparse.Namespace = parser.parse_args()

    command_tokens: list[str] = args.command
    # Strip leading "--" if present (argparse REMAINDER quirk)
    if len(command_tokens) > 0 and command_tokens[0] == "--":
        command_tokens = command_tokens[1:]

    if len(command_tokens) == 0:
        parser.error("No command specified. Use: -- <command...>")

    task_dir: Path = TASKS_DIR / args.task_id
    if not task_dir.is_dir():
        print(
            f"Error: task directory does not exist: {task_dir}",
            file=sys.stderr,
        )
        sys.exit(2)

    exit_code: int = run_command_with_logging(
        task_id=args.task_id,
        command_tokens=command_tokens,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
