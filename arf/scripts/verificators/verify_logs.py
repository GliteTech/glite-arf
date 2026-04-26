"""Verificator for task log files.

Checks the logs/ directory structure, command logs, step logs, and search
logs against the logs specification (arf/specifications/logs_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_logs <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.constants import FRONTMATTER_FIELD_TASK_ID
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
    parse_frontmatter,
)
from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    command_logs_dir,
    logs_dir,
    search_logs_dir,
    session_capture_report_path,
    session_logs_dir,
    step_logs_dir,
    step_tracker_path,
)
from arf.scripts.verificators.common.reporting import (
    exit_code_for_result,
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
    VerificationResult,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "LG"

FRONTMATTER_FIELD_STEP_NUMBER: str = "step_number"
FRONTMATTER_FIELD_STEP_NAME: str = "step_name"
FRONTMATTER_FIELD_STATUS: str = "status"
FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
FRONTMATTER_FIELD_STARTED_AT: str = "started_at"
FRONTMATTER_FIELD_COMPLETED_AT: str = "completed_at"

FIELD_COMMAND: str = "command"
FIELD_EXIT_CODE: str = "exit_code"
FIELD_DURATION_SECONDS: str = "duration_seconds"
FIELD_WORKING_DIRECTORY: str = "working_directory"
FIELD_STDOUT_FILE: str = "stdout_file"
FIELD_STDERR_FILE: str = "stderr_file"
FIELD_STDOUT_LINES: str = "stdout_lines"
FIELD_STDERR_LINES: str = "stderr_lines"
FIELD_TRUNCATED: str = "truncated"

FIELD_TIMESTAMP: str = "timestamp"
FIELD_SOURCE: str = "source"
FIELD_QUERY: str = "query"
FIELD_RESULTS_COUNT: str = "results_count"
FIELD_RESULTS: str = "results"
FIELD_ERROR: str = "error"

FIELD_CAPTURED_AT: str = "captured_at"
FIELD_CHECKED_ROOTS: str = "checked_roots"
FIELD_COPIED_SESSIONS: str = "copied_sessions"
FIELD_ERRORS: str = "errors"

FIELD_SOURCE_KIND: str = "source_kind"
FIELD_ROOT_PATH: str = "root_path"
FIELD_EXISTS: str = "exists"
FIELD_CANDIDATE_FILE_COUNT: str = "candidate_file_count"
FIELD_MATCHED_FILE_COUNT: str = "matched_file_count"

FIELD_SOURCE_PATH: str = "source_path"
FIELD_COPIED_PATH: str = "copied_path"
FIELD_MATCHED_BY: str = "matched_by"

STEP_LOG_REQUIRED_FRONTMATTER: list[str] = [
    FRONTMATTER_FIELD_SPEC_VERSION,
    FRONTMATTER_FIELD_TASK_ID,
    FRONTMATTER_FIELD_STEP_NUMBER,
    FRONTMATTER_FIELD_STEP_NAME,
    FRONTMATTER_FIELD_STATUS,
    FRONTMATTER_FIELD_STARTED_AT,
    FRONTMATTER_FIELD_COMPLETED_AT,
]

COMMAND_LOG_REQUIRED_FIELDS: list[str] = [
    FRONTMATTER_FIELD_SPEC_VERSION,
    FRONTMATTER_FIELD_TASK_ID,
    FIELD_COMMAND,
    FIELD_EXIT_CODE,
    FIELD_DURATION_SECONDS,
    FRONTMATTER_FIELD_STARTED_AT,
    FRONTMATTER_FIELD_COMPLETED_AT,
    FIELD_WORKING_DIRECTORY,
    FIELD_STDOUT_FILE,
    FIELD_STDERR_FILE,
    FIELD_STDOUT_LINES,
    FIELD_STDERR_LINES,
    FIELD_TRUNCATED,
]

SEARCH_LOG_REQUIRED_FIELDS: list[str] = [
    FRONTMATTER_FIELD_SPEC_VERSION,
    FRONTMATTER_FIELD_TASK_ID,
    FRONTMATTER_FIELD_STEP_NUMBER,
    FIELD_TIMESTAMP,
    FIELD_SOURCE,
    FIELD_QUERY,
    FIELD_RESULTS_COUNT,
    FIELD_RESULTS,
    FIELD_ERROR,
]
SESSION_CAPTURE_REPORT_REQUIRED_FIELDS: list[str] = [
    FRONTMATTER_FIELD_SPEC_VERSION,
    FRONTMATTER_FIELD_TASK_ID,
    FIELD_CAPTURED_AT,
    FIELD_CHECKED_ROOTS,
    FIELD_COPIED_SESSIONS,
    FIELD_ERRORS,
]
SESSION_ROOT_SCAN_REQUIRED_FIELDS: list[str] = [
    FIELD_SOURCE_KIND,
    FIELD_ROOT_PATH,
    FIELD_EXISTS,
    FIELD_CANDIDATE_FILE_COUNT,
    FIELD_MATCHED_FILE_COUNT,
]
CAPTURED_SESSION_REQUIRED_FIELDS: list[str] = [
    FIELD_SOURCE_KIND,
    FIELD_SOURCE_PATH,
    FIELD_COPIED_PATH,
    FIELD_MATCHED_BY,
]

SECTION_SUMMARY: str = "Summary"
SECTION_ACTIONS_TAKEN: str = "Actions Taken"
SECTION_OUTPUTS: str = "Outputs"
SECTION_ISSUES: str = "Issues"

MANDATORY_STEP_SECTIONS: list[str] = [
    SECTION_SUMMARY,
    SECTION_ACTIONS_TAKEN,
    SECTION_OUTPUTS,
    SECTION_ISSUES,
]

MIN_SUMMARY_WORDS: int = 20

STEP_TRACKER_FIELD_STEPS: str = "steps"
STEP_TRACKER_FIELD_STEP: str = "step"
STEP_TRACKER_FIELD_STATUS: str = "status"
STEP_TRACKER_FIELD_LOG_FILE: str = "log_file"

COMPLETED_STATUSES: set[str] = {"completed", "failed", "skipped"}
SESSION_LOGS_RELATIVE_PREFIX: str = "logs/sessions"

# A brainstorm task that captures its own live session may finish
# `capture_task_sessions.py` before the in-flight JSONL transcript has
# been flushed to disk, so the report legitimately records zero copies.
# Within this window we trust the capture report and do not emit
# LG-W007. Older tasks (capture far in the past) still warn: the
# transcript should have appeared long ago.
LIVE_SESSION_CAPTURE_WINDOW_SECONDS: float = 600.0
STEP_TRACKER_FIELD_COMPLETED_AT: str = "completed_at"

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

LG_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
LG_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
LG_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
LG_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
LG_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
LG_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
LG_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
LG_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)

LG_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
LG_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
LG_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
LG_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
LG_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
LG_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
LG_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
LG_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_logs_dir(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if not logs_dir(task_id=task_id).is_dir():
        return [
            Diagnostic(
                code=LG_E001,
                message="logs/ directory does not exist",
                file_path=file_path,
            ),
        ]
    return []


def _check_commands_dir(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if not command_logs_dir(task_id=task_id).is_dir():
        return [
            Diagnostic(
                code=LG_E002,
                message="logs/commands/ directory does not exist",
                file_path=file_path,
            ),
        ]
    return []


def _check_steps_dir(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if not step_logs_dir(task_id=task_id).is_dir():
        return [
            Diagnostic(
                code=LG_E003,
                message="logs/steps/ directory does not exist",
                file_path=file_path,
            ),
        ]
    return []


def _check_command_logs(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Validate all command log JSON files in commands/."""
    cmds_dir: Path = command_logs_dir(task_id=task_id)
    if not cmds_dir.is_dir():
        return []

    diagnostics: list[Diagnostic] = []
    json_files: list[Path] = sorted(cmds_dir.glob("*.json"))

    if len(json_files) == 0:
        diagnostics.append(
            Diagnostic(
                code=LG_W005,
                message="No command logs found in logs/commands/",
                file_path=file_path,
            ),
        )
        return diagnostics

    for json_file in json_files:
        data: dict[str, Any] | None = load_json_file(file_path=json_file)
        if data is None:
            diagnostics.append(
                Diagnostic(
                    code=LG_E004,
                    message=f"Invalid JSON in command log: {json_file.name}",
                    file_path=json_file,
                ),
            )
            continue

        missing: list[str] = check_required_fields(
            data=data,
            required_fields=COMMAND_LOG_REQUIRED_FIELDS,
        )
        if len(missing) > 0:
            diagnostics.append(
                Diagnostic(
                    code=LG_E004,
                    message=(f"Command log {json_file.name} missing fields: {', '.join(missing)}"),
                    file_path=json_file,
                ),
            )
            continue

        # E006: task_id match
        log_task_id: object = data.get(FRONTMATTER_FIELD_TASK_ID)
        if str(log_task_id) != task_id:
            diagnostics.append(
                Diagnostic(
                    code=LG_E006,
                    message=(
                        f"Command log {json_file.name} has task_id "
                        f"'{log_task_id}', expected '{task_id}'"
                    ),
                    file_path=json_file,
                ),
            )

        # W004: non-zero exit code
        exit_code: object = data.get(FIELD_EXIT_CODE)
        if isinstance(exit_code, int) and exit_code != 0:
            diagnostics.append(
                Diagnostic(
                    code=LG_W004,
                    message=(f"Command log {json_file.name} has non-zero exit code: {exit_code}"),
                    file_path=json_file,
                ),
            )

    return diagnostics


def _check_step_log_file(
    *,
    step_file: Path,
    task_id: str,
    tracker_steps: dict[int, dict[str, Any]],
) -> list[Diagnostic]:
    """Validate a single step log markdown file."""
    diagnostics: list[Diagnostic] = []

    try:
        content: str = step_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        diagnostics.append(
            Diagnostic(
                code=LG_E005,
                message=f"Cannot read step log: {step_file.name}",
                file_path=step_file,
            ),
        )
        return diagnostics

    # Frontmatter
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        diagnostics.append(
            Diagnostic(
                code=LG_E005,
                message=f"Step log {step_file.name} missing YAML frontmatter",
                file_path=step_file,
            ),
        )
        return diagnostics

    frontmatter: dict[str, Any] | None = parse_frontmatter(
        raw_yaml=split_result.raw_yaml,
    )
    if frontmatter is None:
        diagnostics.append(
            Diagnostic(
                code=LG_E005,
                message=f"Step log {step_file.name} has unparseable frontmatter",
                file_path=step_file,
            ),
        )
        return diagnostics

    # Check required frontmatter fields
    for field_name in STEP_LOG_REQUIRED_FRONTMATTER:
        if field_name not in frontmatter:
            diagnostics.append(
                Diagnostic(
                    code=LG_E005,
                    message=(
                        f"Step log {step_file.name} missing frontmatter field: '{field_name}'"
                    ),
                    file_path=step_file,
                ),
            )

    # E006: task_id match
    fm_task_id: object = frontmatter.get(FRONTMATTER_FIELD_TASK_ID)
    if fm_task_id is not None and str(fm_task_id) != task_id:
        diagnostics.append(
            Diagnostic(
                code=LG_E006,
                message=(
                    f"Step log {step_file.name} has task_id '{fm_task_id}', expected '{task_id}'"
                ),
                file_path=step_file,
            ),
        )

    # E007: step_number matches tracker
    step_num: object = frontmatter.get(FRONTMATTER_FIELD_STEP_NUMBER)
    if isinstance(step_num, int) and step_num not in tracker_steps:
        diagnostics.append(
            Diagnostic(
                code=LG_E007,
                message=(
                    f"Step log {step_file.name} has step_number={step_num} "
                    f"which does not exist in step_tracker.json"
                ),
                file_path=step_file,
            ),
        )

    # Mandatory sections
    body: str = split_result.body
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )
    found_headings: set[str] = {s.heading for s in sections}
    for required in MANDATORY_STEP_SECTIONS:
        if required not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=LG_E005,
                    message=(
                        f"Step log {step_file.name} missing mandatory section: '## {required}'"
                    ),
                    file_path=step_file,
                ),
            )

    # W003: Summary word count
    for section in sections:
        if section.heading == SECTION_SUMMARY:
            word_count: int = count_words(text=section.content)
            if word_count < MIN_SUMMARY_WORDS:
                diagnostics.append(
                    Diagnostic(
                        code=LG_W003,
                        message=(
                            f"Step log {step_file.name} Summary has "
                            f"{word_count} words (minimum: {MIN_SUMMARY_WORDS})"
                        ),
                        file_path=step_file,
                    ),
                )
            break

    return diagnostics


def _extract_step_number_from_name(*, name: str) -> int | None:
    """Extract the 3-digit step number from a folder or file name like '004_research-papers'."""
    match: re.Match[str] | None = re.match(r"^(\d{3})_", name)
    if match is not None:
        return int(match.group(1))
    return None


def _check_step_logs(
    *,
    task_id: str,
    file_path: Path,
    tracker_steps: dict[int, dict[str, Any]],
) -> list[Diagnostic]:
    """Validate step log folders and cross-reference with step_tracker."""
    steps_dir: Path = step_logs_dir(task_id=task_id)
    if not steps_dir.is_dir():
        return []

    diagnostics: list[Diagnostic] = []
    step_numbers_with_logs: set[int] = set()

    # Support both folder-based (new) and flat file (legacy) step logs
    for entry in sorted(steps_dir.iterdir()):
        step_num: int | None = _extract_step_number_from_name(name=entry.name)
        if step_num is None:
            continue

        if entry.is_dir():
            # New folder-based step log — the folder itself is the log
            step_numbers_with_logs.add(step_num)
            # Validate step_log.md if present
            step_log_file: Path = entry / "step_log.md"
            if step_log_file.exists():
                diagnostics.extend(
                    _check_step_log_file(
                        step_file=step_log_file,
                        task_id=task_id,
                        tracker_steps=tracker_steps,
                    ),
                )
        elif entry.is_file() and entry.suffix == ".md":
            # Legacy flat file step log
            diagnostics.extend(
                _check_step_log_file(
                    step_file=entry,
                    task_id=task_id,
                    tracker_steps=tracker_steps,
                ),
            )
            # Extract step number from frontmatter
            try:
                content: str = entry.read_text(encoding="utf-8")
                fm_result: FrontmatterResult | None = extract_frontmatter_and_body(
                    content=content,
                )
                if fm_result is not None:
                    fm: dict[str, Any] | None = parse_frontmatter(
                        raw_yaml=fm_result.raw_yaml,
                    )
                    if fm is not None:
                        fm_step: object = fm.get(FRONTMATTER_FIELD_STEP_NUMBER)
                        if isinstance(fm_step, int):
                            step_numbers_with_logs.add(fm_step)
            except (OSError, UnicodeDecodeError):
                pass

    # E008: Completed steps without logs
    for step_num_key, step_data in tracker_steps.items():
        step_status: str = str(step_data.get(STEP_TRACKER_FIELD_STATUS, ""))
        if step_status in COMPLETED_STATUSES and step_num_key not in step_numbers_with_logs:
            diagnostics.append(
                Diagnostic(
                    code=LG_E008,
                    message=(
                        f"Step {step_num_key} has status '{step_status}' but no step log was found"
                    ),
                    file_path=file_path,
                ),
            )

    # W006: log_file field missing
    for step_num_key, step_data in tracker_steps.items():
        step_status = str(step_data.get(STEP_TRACKER_FIELD_STATUS, ""))
        if step_status in COMPLETED_STATUSES:
            log_file_val: object = step_data.get(STEP_TRACKER_FIELD_LOG_FILE)
            if log_file_val is None:
                diagnostics.append(
                    Diagnostic(
                        code=LG_W006,
                        message=(
                            f"Step {step_num_key} is '{step_status}' but "
                            f"log_file is null in step_tracker.json"
                        ),
                        file_path=file_path,
                    ),
                )

    return diagnostics


def _check_search_logs(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Validate search log files if the searches/ directory exists."""
    searches_dir: Path = search_logs_dir(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    if not searches_dir.is_dir():
        diagnostics.append(
            Diagnostic(
                code=LG_W001,
                message="logs/searches/ directory does not exist",
                file_path=file_path,
            ),
        )
        return diagnostics

    json_files: list[Path] = sorted(searches_dir.glob("*.json"))
    for json_file in json_files:
        data: dict[str, Any] | None = load_json_file(file_path=json_file)
        if data is None:
            diagnostics.append(
                Diagnostic(
                    code=LG_W002,
                    message=f"Invalid JSON in search log: {json_file.name}",
                    file_path=json_file,
                ),
            )
            continue

        missing: list[str] = check_required_fields(
            data=data,
            required_fields=SEARCH_LOG_REQUIRED_FIELDS,
        )
        if len(missing) > 0:
            diagnostics.append(
                Diagnostic(
                    code=LG_W002,
                    message=(f"Search log {json_file.name} missing fields: {', '.join(missing)}"),
                    file_path=json_file,
                ),
            )

        # E006: task_id match (error, not warning)
        log_task_id: object = data.get(FRONTMATTER_FIELD_TASK_ID)
        if log_task_id is not None and str(log_task_id) != task_id:
            diagnostics.append(
                Diagnostic(
                    code=LG_E006,
                    message=(
                        f"Search log {json_file.name} has task_id "
                        f"'{log_task_id}', expected '{task_id}'"
                    ),
                    file_path=json_file,
                ),
            )

    return diagnostics


SESSION_TRANSCRIPT_SUFFIXES: tuple[str, ...] = (".jsonl", ".jsonl.gz")


def _session_transcript_files(*, task_id: str) -> list[Path]:
    sessions_dir: Path = session_logs_dir(task_id=task_id)
    if sessions_dir.is_dir() is False:
        return []
    return sorted(
        path
        for path in sessions_dir.iterdir()
        if path.is_file() is True
        and any(path.name.endswith(suffix) for suffix in SESSION_TRANSCRIPT_SUFFIXES)
    )


def _session_log_relative_path(*, transcript_path: Path) -> str:
    return f"{SESSION_LOGS_RELATIVE_PREFIX}/{transcript_path.name}"


def _check_session_capture_report(
    *,
    task_id: str,
    file_path: Path,
    transcript_files: list[Path],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    report_path: Path = session_capture_report_path(task_id=task_id)

    if report_path.exists() is False:
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message="logs/sessions/capture_report.json does not exist",
                file_path=file_path,
            ),
        )
        return diagnostics

    report_data: dict[str, Any] | None = load_json_file(file_path=report_path)
    if report_data is None:
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message="logs/sessions/capture_report.json is not valid JSON",
                file_path=report_path,
            ),
        )
        return diagnostics

    missing_report_fields: list[str] = check_required_fields(
        data=report_data,
        required_fields=SESSION_CAPTURE_REPORT_REQUIRED_FIELDS,
    )
    if len(missing_report_fields) > 0:
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message=(
                    "logs/sessions/capture_report.json missing fields: "
                    f"{', '.join(missing_report_fields)}"
                ),
                file_path=report_path,
            ),
        )
        return diagnostics

    report_task_id: object = report_data.get(FRONTMATTER_FIELD_TASK_ID)
    if str(report_task_id) != task_id:
        diagnostics.append(
            Diagnostic(
                code=LG_E006,
                message=(
                    "logs/sessions/capture_report.json has task_id "
                    f"'{report_task_id}', expected '{task_id}'"
                ),
                file_path=report_path,
            ),
        )

    checked_roots: object = report_data.get(FIELD_CHECKED_ROOTS)
    if not isinstance(checked_roots, list):
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message="logs/sessions/capture_report.json field 'checked_roots' is not a list",
                file_path=report_path,
            ),
        )
    else:
        for index, root_entry in enumerate(checked_roots):
            if not isinstance(root_entry, dict):
                diagnostics.append(
                    Diagnostic(
                        code=LG_W008,
                        message=(
                            "logs/sessions/capture_report.json checked_roots["
                            f"{index}] is not an object"
                        ),
                        file_path=report_path,
                    ),
                )
                continue
            missing_root_fields: list[str] = check_required_fields(
                data=root_entry,
                required_fields=SESSION_ROOT_SCAN_REQUIRED_FIELDS,
            )
            if len(missing_root_fields) > 0:
                diagnostics.append(
                    Diagnostic(
                        code=LG_W008,
                        message=(
                            "logs/sessions/capture_report.json checked_roots["
                            f"{index}] missing fields: {', '.join(missing_root_fields)}"
                        ),
                        file_path=report_path,
                    ),
                )

    copied_sessions: object = report_data.get(FIELD_COPIED_SESSIONS)
    if not isinstance(copied_sessions, list):
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message="logs/sessions/capture_report.json field 'copied_sessions' is not a list",
                file_path=report_path,
            ),
        )
        return diagnostics

    reported_paths: set[str] = set()
    for index, copied_entry in enumerate(copied_sessions):
        if not isinstance(copied_entry, dict):
            diagnostics.append(
                Diagnostic(
                    code=LG_W008,
                    message=(
                        "logs/sessions/capture_report.json copied_sessions["
                        f"{index}] is not an object"
                    ),
                    file_path=report_path,
                ),
            )
            continue

        missing_copied_fields: list[str] = check_required_fields(
            data=copied_entry,
            required_fields=CAPTURED_SESSION_REQUIRED_FIELDS,
        )
        if len(missing_copied_fields) > 0:
            diagnostics.append(
                Diagnostic(
                    code=LG_W008,
                    message=(
                        "logs/sessions/capture_report.json copied_sessions["
                        f"{index}] missing fields: {', '.join(missing_copied_fields)}"
                    ),
                    file_path=report_path,
                ),
            )
            continue

        copied_path: object = copied_entry.get(FIELD_COPIED_PATH)
        if isinstance(copied_path, str):
            reported_paths.add(copied_path)

    actual_paths: set[str] = {
        _session_log_relative_path(transcript_path=transcript_file)
        for transcript_file in transcript_files
    }
    if reported_paths != actual_paths:
        diagnostics.append(
            Diagnostic(
                code=LG_W008,
                message=(
                    "logs/sessions/capture_report.json copied_sessions does not match the "
                    "transcript files present in logs/sessions/"
                ),
                file_path=report_path,
            ),
        )

    return diagnostics


def _parse_iso_timestamp(*, value: object) -> datetime | None:
    if not isinstance(value, str) or len(value) == 0:
        return None
    text: str = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed: datetime = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _latest_step_completed_at(*, task_id: str) -> datetime | None:
    steps: dict[int, dict[str, Any]] = _load_tracker_steps(task_id=task_id)
    latest: datetime | None = None
    for step_data in steps.values():
        timestamp: datetime | None = _parse_iso_timestamp(
            value=step_data.get(STEP_TRACKER_FIELD_COMPLETED_AT),
        )
        if timestamp is None:
            continue
        if latest is None or timestamp > latest:
            latest = timestamp
    return latest


def _is_fresh_empty_capture(*, task_id: str) -> bool:
    report_path: Path = session_capture_report_path(task_id=task_id)
    if not report_path.exists():
        return False
    report_data: dict[str, Any] | None = load_json_file(file_path=report_path)
    if report_data is None:
        return False

    copied_sessions: object = report_data.get(FIELD_COPIED_SESSIONS)
    if not isinstance(copied_sessions, list) or len(copied_sessions) != 0:
        return False

    captured_at: datetime | None = _parse_iso_timestamp(
        value=report_data.get(FIELD_CAPTURED_AT),
    )
    if captured_at is None:
        return False

    latest_completed: datetime | None = _latest_step_completed_at(task_id=task_id)
    if latest_completed is None:
        return False

    delta_seconds: float = abs((latest_completed - captured_at).total_seconds())
    return delta_seconds <= LIVE_SESSION_CAPTURE_WINDOW_SECONDS


def _check_session_logs(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    sessions_dir: Path = session_logs_dir(task_id=task_id)
    fresh_empty_capture: bool = _is_fresh_empty_capture(task_id=task_id)

    if sessions_dir.is_dir() is False:
        if fresh_empty_capture is False:
            diagnostics.append(
                Diagnostic(
                    code=LG_W007,
                    message="logs/sessions/ directory does not exist",
                    file_path=file_path,
                ),
            )
        diagnostics.extend(
            _check_session_capture_report(
                task_id=task_id,
                file_path=file_path,
                transcript_files=[],
            ),
        )
        return diagnostics

    transcript_files: list[Path] = _session_transcript_files(task_id=task_id)
    if len(transcript_files) == 0 and fresh_empty_capture is False:
        diagnostics.append(
            Diagnostic(
                code=LG_W007,
                message="logs/sessions/ contains no captured session transcript JSONL files",
                file_path=file_path,
            ),
        )

    diagnostics.extend(
        _check_session_capture_report(
            task_id=task_id,
            file_path=file_path,
            transcript_files=transcript_files,
        ),
    )
    return diagnostics


def _load_tracker_steps(
    *,
    task_id: str,
) -> dict[int, dict[str, Any]]:
    """Load step_tracker.json and return a dict of step_number -> step data."""
    tracker_path: Path = step_tracker_path(task_id=task_id)
    if not tracker_path.exists():
        return {}

    try:
        raw: str = tracker_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict):
        return {}

    steps: object = data.get(STEP_TRACKER_FIELD_STEPS)
    if not isinstance(steps, list):
        return {}

    result: dict[int, dict[str, Any]] = {}
    for step in steps:
        if isinstance(step, dict):
            step_num: object = step.get(STEP_TRACKER_FIELD_STEP)
            if isinstance(step_num, int):
                result[step_num] = step

    return result


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_logs(*, task_id: str) -> VerificationResult:
    file_path: Path = logs_dir(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: logs/ directory
    dir_check: list[Diagnostic] = _check_logs_dir(
        task_id=task_id,
        file_path=file_path,
    )
    diagnostics.extend(dir_check)
    if len(dir_check) > 0:
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # E002: commands/ directory
    diagnostics.extend(
        _check_commands_dir(
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E003: steps/ directory
    diagnostics.extend(
        _check_steps_dir(
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # Load step tracker for cross-referencing
    tracker_steps: dict[int, dict[str, Any]] = _load_tracker_steps(
        task_id=task_id,
    )

    # E004, E006, W004, W005: command log validation
    diagnostics.extend(
        _check_command_logs(
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E005, E006, E007, E008, W003, W006: step log validation
    diagnostics.extend(
        _check_step_logs(
            task_id=task_id,
            file_path=file_path,
            tracker_steps=tracker_steps,
        ),
    )

    # W001, W002: search log validation
    diagnostics.extend(
        _check_search_logs(
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # W007, W008: session transcript capture validation
    diagnostics.extend(
        _check_session_logs(
            task_id=task_id,
            file_path=file_path,
        ),
    )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify log files for a given task",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_logs(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
