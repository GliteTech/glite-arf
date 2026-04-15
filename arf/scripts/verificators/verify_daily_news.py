"""Verificator for daily news files.

Validates ``news/<date>.md`` and ``news/<date>.json`` against the daily news
specification (``arf/specifications/daily_news_specification.md``).

Usage::

    uv run python -m arf.scripts.verificators.verify_daily_news 2026-04-05
    uv run python -m arf.scripts.verificators.verify_daily_news --all

Exit codes:
    0 -- no errors
    1 -- one or more errors found
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date as date_type
from datetime import datetime
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.paths import (
    NEWS_DIR,
    REPO_ROOT,
    news_json_path,
    news_md_path,
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

FIELD_SPEC_VERSION: str = "spec_version"
FIELD_DATE: str = "date"
FIELD_TASKS_COMPLETED: str = "tasks_completed"
FIELD_TASKS_CREATED: str = "tasks_created"
FIELD_TASKS_CANCELLED: str = "tasks_cancelled"
FIELD_TOTAL_COST_USD: str = "total_cost_usd"
FIELD_ASSETS_ADDED: str = "assets_added"
FIELD_PAPERS_ADDED: str = "papers_added"
FIELD_INFRASTRUCTURE_CHANGES: str = "infrastructure_changes"
FIELD_CURRENT_BEST_RESULTS: str = "current_best_results"
FIELD_KEY_FINDINGS: str = "key_findings"

DATE_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FINDINGS_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+thing",
    re.IGNORECASE,
)

IMAGE_PATTERN: re.Pattern[str] = re.compile(r"!\[.*?\]\(.*?\)")
LINK_PATTERN: re.Pattern[str] = re.compile(r"(?<!!)\[.*?\]\(.*?\)")

HUMAN_DATE_FORMATS: list[str] = [
    "%B %d, %Y",
    "%B %-d, %Y",
]

REQUIRED_TOP_LEVEL_FIELDS: list[str] = [
    FIELD_TASKS_COMPLETED,
    FIELD_TASKS_CREATED,
    FIELD_TASKS_CANCELLED,
    FIELD_TOTAL_COST_USD,
    FIELD_ASSETS_ADDED,
    FIELD_PAPERS_ADDED,
    FIELD_INFRASTRUCTURE_CHANGES,
    FIELD_CURRENT_BEST_RESULTS,
    FIELD_KEY_FINDINGS,
]

LIST_FIELDS: list[str] = [
    FIELD_TASKS_COMPLETED,
    FIELD_TASKS_CREATED,
    FIELD_TASKS_CANCELLED,
    FIELD_INFRASTRUCTURE_CHANGES,
    FIELD_CURRENT_BEST_RESULTS,
    FIELD_KEY_FINDINGS,
]

INT_FIELDS: list[str] = [FIELD_ASSETS_ADDED, FIELD_PAPERS_ADDED]

TASK_COMPLETED_REQUIRED: list[str] = ["task_id", "name", "cost_usd", "key_finding"]
TASK_CREATED_REQUIRED: list[str] = ["task_id", "name", "reason"]
TASK_CANCELLED_REQUIRED: list[str] = ["task_id", "reason"]
BEST_RESULT_REQUIRED: list[str] = ["system", "f1", "type"]

MD_SECTION_WHERE_WE_STAND: str = "where we stand"
MD_SECTION_COSTS: str = "costs"
MD_SECTION_KEY_PAPERS: str = "key papers added"
MD_SECTION_KEY_ANSWERS: str = "key questions answered"

MD_MAX_LENGTH: int = 15000
MD_MIN_LENGTH: int = 200
MD_MIN_LINKS: int = 5

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "DN"

DN_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
DN_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
DN_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
DN_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
DN_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
DN_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
DN_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
DN_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
DN_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
DN_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
DN_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
DN_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
DN_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
DN_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)
DN_E015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=15,
)
DN_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
DN_E017: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=17,
)
DN_E018: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=18,
)
DN_E019: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=19,
)

DN_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
DN_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
DN_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
DN_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
DN_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
DN_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
DN_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
DN_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
DN_W009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=9,
)

# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _JsonLoadResult:
    data: dict[str, Any] | None
    diagnostics: list[Diagnostic]


@dataclass(frozen=True, slots=True)
class _MdLoadResult:
    content: str | None
    diagnostics: list[Diagnostic]


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------


def _parse_human_date(*, heading_text: str) -> date_type | None:
    cleaned: str = heading_text.strip()
    for fmt in HUMAN_DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    # Try with zero-padded day as fallback
    try:
        return datetime.strptime(cleaned, "%B %d, %Y").date()
    except ValueError:
        return None


def _iso_to_date(*, iso_str: str) -> date_type | None:
    try:
        return datetime.strptime(iso_str, "%Y-%m-%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# JSON checks
# ---------------------------------------------------------------------------


def _check_json_load(
    *,
    file_path: Path,
) -> _JsonLoadResult:
    if not file_path.exists():
        return _JsonLoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E001,
                    message="JSON file is missing",
                    file_path=file_path,
                ),
            ],
        )
    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return _JsonLoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E001,
                    message="JSON file is not readable",
                    file_path=file_path,
                ),
            ],
        )
    try:
        data: object = json.loads(raw)
    except json.JSONDecodeError:
        return _JsonLoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E001,
                    message="JSON file is not valid JSON",
                    file_path=file_path,
                ),
            ],
        )
    if not isinstance(data, dict):
        return _JsonLoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E002,
                    message="Top-level value is not a JSON object",
                    file_path=file_path,
                ),
            ],
        )
    return _JsonLoadResult(data=data, diagnostics=[])


def _check_json_top_level(
    *,
    data: dict[str, Any],
    date: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if FIELD_SPEC_VERSION not in data:
        diagnostics.append(
            Diagnostic(
                code=DN_E003,
                message="Missing 'spec_version' field",
                file_path=file_path,
            ),
        )
    if FIELD_DATE not in data:
        diagnostics.append(
            Diagnostic(
                code=DN_E004,
                message="Missing 'date' field",
                file_path=file_path,
            ),
        )
    else:
        date_value: object = data[FIELD_DATE]
        if not isinstance(date_value, str) or DATE_PATTERN.match(date_value) is None:
            diagnostics.append(
                Diagnostic(
                    code=DN_E005,
                    message=f"'date' value '{date_value}' is not a valid ISO date",
                    file_path=file_path,
                ),
            )
        elif date_value != date:
            diagnostics.append(
                Diagnostic(
                    code=DN_E005,
                    message=(f"'date' value '{date_value}' does not match filename date '{date}'"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_json_required_fields(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data:
            diagnostics.append(
                Diagnostic(
                    code=DN_E006,
                    message=f"Missing required field '{field}'",
                    file_path=file_path,
                ),
            )
            continue
        value: object = data[field]
        if field in LIST_FIELDS and not isinstance(value, list):
            diagnostics.append(
                Diagnostic(
                    code=DN_E007,
                    message=f"Field '{field}' must be a list, got {type(value).__name__}",
                    file_path=file_path,
                ),
            )
        if field in INT_FIELDS and not isinstance(value, int | float):
            diagnostics.append(
                Diagnostic(
                    code=DN_E007,
                    message=(f"Field '{field}' must be a number, got {type(value).__name__}"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_json_nested_objects(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    tasks_completed: object = data.get(FIELD_TASKS_COMPLETED)
    if isinstance(tasks_completed, list):
        for i, item in enumerate(tasks_completed):
            if not isinstance(item, dict):
                continue
            for field in TASK_COMPLETED_REQUIRED:
                if field not in item:
                    diagnostics.append(
                        Diagnostic(
                            code=DN_E008,
                            message=(f"tasks_completed[{i}] missing required field '{field}'"),
                            file_path=file_path,
                        ),
                    )

    tasks_created: object = data.get(FIELD_TASKS_CREATED)
    if isinstance(tasks_created, list):
        for i, item in enumerate(tasks_created):
            if not isinstance(item, dict):
                continue
            for field in TASK_CREATED_REQUIRED:
                if field not in item:
                    diagnostics.append(
                        Diagnostic(
                            code=DN_E009,
                            message=(f"tasks_created[{i}] missing required field '{field}'"),
                            file_path=file_path,
                        ),
                    )

    tasks_cancelled: object = data.get(FIELD_TASKS_CANCELLED)
    if isinstance(tasks_cancelled, list):
        for i, item in enumerate(tasks_cancelled):
            if not isinstance(item, dict):
                continue
            for field in TASK_CANCELLED_REQUIRED:
                if field not in item:
                    diagnostics.append(
                        Diagnostic(
                            code=DN_E010,
                            message=(f"tasks_cancelled[{i}] missing required field '{field}'"),
                            file_path=file_path,
                        ),
                    )

    best_results: object = data.get(FIELD_CURRENT_BEST_RESULTS)
    if isinstance(best_results, list):
        for i, item in enumerate(best_results):
            if not isinstance(item, dict):
                continue
            for field in BEST_RESULT_REQUIRED:
                if field not in item:
                    diagnostics.append(
                        Diagnostic(
                            code=DN_E017,
                            message=(f"current_best_results[{i}] missing required field '{field}'"),
                            file_path=file_path,
                        ),
                    )

    return diagnostics


def _check_json_cost(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    cost: object = data.get(FIELD_TOTAL_COST_USD)
    if cost is not None and not isinstance(cost, int | float):
        return [
            Diagnostic(
                code=DN_E016,
                message=(f"'total_cost_usd' must be a number, got {type(cost).__name__}"),
                file_path=file_path,
            ),
        ]
    return []


def _check_json_warnings(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    key_findings: object = data.get(FIELD_KEY_FINDINGS)
    if isinstance(key_findings, list) and len(key_findings) == 0:
        diagnostics.append(
            Diagnostic(
                code=DN_W002,
                message="'key_findings' list is empty",
                file_path=file_path,
            ),
        )
    cost: object = data.get(FIELD_TOTAL_COST_USD)
    if isinstance(cost, int | float) and cost == 0:
        diagnostics.append(
            Diagnostic(
                code=DN_W003,
                message="'total_cost_usd' is zero",
                file_path=file_path,
            ),
        )
    return diagnostics


# ---------------------------------------------------------------------------
# Markdown checks
# ---------------------------------------------------------------------------


def _check_md_load(
    *,
    file_path: Path,
) -> _MdLoadResult:
    if not file_path.exists():
        return _MdLoadResult(
            content=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E011,
                    message="Markdown file is missing",
                    file_path=file_path,
                ),
            ],
        )
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return _MdLoadResult(
            content=None,
            diagnostics=[
                Diagnostic(
                    code=DN_E011,
                    message="Markdown file is not readable",
                    file_path=file_path,
                ),
            ],
        )
    return _MdLoadResult(content=content, diagnostics=[])


def _extract_headings(
    *,
    lines: list[str],
    level: int,
) -> list[str]:
    prefix: str = "#" * level + " "
    headings: list[str] = []
    for line in lines:
        stripped: str = line.strip()
        if stripped.startswith(prefix):
            headings.append(stripped[len(prefix) :].strip())
    return headings


def _check_md_structure(
    *,
    content: str,
    date: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    lines: list[str] = content.splitlines()

    first_nonblank: str | None = None
    for line in lines:
        stripped: str = line.strip()
        if len(stripped) > 0:
            first_nonblank = stripped
            break

    if first_nonblank is None:
        diagnostics.append(
            Diagnostic(
                code=DN_E013,
                message="Markdown file is empty",
                file_path=file_path,
            ),
        )
        return diagnostics

    if first_nonblank.startswith("# ") and not first_nonblank.startswith("## "):
        diagnostics.append(
            Diagnostic(
                code=DN_E012,
                message="Markdown file starts with '# ' heading (must use '## ')",
                file_path=file_path,
            ),
        )

    if first_nonblank.startswith("## "):
        heading_text: str = first_nonblank[3:].strip()
        expected_date: date_type | None = _iso_to_date(iso_str=date)
        parsed_heading: date_type | None = _parse_human_date(
            heading_text=heading_text,
        )
        if parsed_heading is None or expected_date is None:
            diagnostics.append(
                Diagnostic(
                    code=DN_E013,
                    message=(
                        f"First '## ' heading '{heading_text}' is not a recognized date format"
                    ),
                    file_path=file_path,
                ),
            )
        elif parsed_heading != expected_date:
            diagnostics.append(
                Diagnostic(
                    code=DN_E013,
                    message=(
                        f"First '## ' heading date "
                        f"({parsed_heading.isoformat()}) does not match "
                        f"filename date '{date}'"
                    ),
                    file_path=file_path,
                ),
            )

    h2_headings_lower: list[str] = [h.lower() for h in _extract_headings(lines=lines, level=2)]

    if MD_SECTION_WHERE_WE_STAND not in h2_headings_lower:
        diagnostics.append(
            Diagnostic(
                code=DN_E014,
                message="Missing '## Where we stand' section",
                file_path=file_path,
            ),
        )

    if MD_SECTION_COSTS not in h2_headings_lower:
        diagnostics.append(
            Diagnostic(
                code=DN_E015,
                message="Missing '## Costs' section",
                file_path=file_path,
            ),
        )

    return diagnostics


def _check_md_warnings(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    lines: list[str] = content.splitlines()

    h2_headings: list[str] = _extract_headings(lines=lines, level=2)
    h2_headings_lower: list[str] = [h.lower() for h in h2_headings]

    has_findings: bool = any(FINDINGS_HEADING_PATTERN.search(h) is not None for h in h2_headings)
    if not has_findings:
        diagnostics.append(
            Diagnostic(
                code=DN_W001,
                message="No numbered findings heading found",
                file_path=file_path,
            ),
        )

    content_length: int = len(content)
    if content_length < MD_MIN_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=DN_W004,
                message=f"Markdown file is under {MD_MIN_LENGTH} characters ({content_length})",
                file_path=file_path,
            ),
        )
    if content_length > MD_MAX_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=DN_W005,
                message=(f"Markdown file exceeds {MD_MAX_LENGTH} characters ({content_length})"),
                file_path=file_path,
            ),
        )

    image_count: int = len(IMAGE_PATTERN.findall(content))
    if image_count == 0:
        diagnostics.append(
            Diagnostic(
                code=DN_W006,
                message="No embedded images found",
                file_path=file_path,
            ),
        )

    link_count: int = len(LINK_PATTERN.findall(content))
    if link_count < MD_MIN_LINKS:
        diagnostics.append(
            Diagnostic(
                code=DN_W007,
                message=(
                    f"Only {link_count} markdown links found (expected at least {MD_MIN_LINKS})"
                ),
                file_path=file_path,
            ),
        )

    if MD_SECTION_KEY_PAPERS not in h2_headings_lower:
        diagnostics.append(
            Diagnostic(
                code=DN_W008,
                message="Missing '## Key papers added' section",
                file_path=file_path,
            ),
        )

    if MD_SECTION_KEY_ANSWERS not in h2_headings_lower:
        diagnostics.append(
            Diagnostic(
                code=DN_W009,
                message="Missing '## Key questions answered' section",
                file_path=file_path,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Git checks
# ---------------------------------------------------------------------------

GIT_CMD: str = "git"


def _run_git(*, args: list[str]) -> str | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GIT_CMD, *args],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10.0,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None


def _check_git_committed(
    *,
    date: str,
    json_path: Path,
    md_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for file_path in [json_path, md_path]:
        if not file_path.exists():
            continue
        try:
            relative: str = str(file_path.relative_to(REPO_ROOT))
        except ValueError:
            continue
        status_output: str | None = _run_git(
            args=["status", "--porcelain", "--", relative],
        )
        if status_output is None:
            continue
        if len(status_output) > 0:
            diagnostics.append(
                Diagnostic(
                    code=DN_E018,
                    message=f"File is not committed: {relative}",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_git_pushed(
    *,
    date: str,
    json_path: Path,
    md_path: Path,
) -> list[Diagnostic]:
    branch: str | None = _run_git(args=["rev-parse", "--abbrev-ref", "HEAD"])
    if branch is None:
        return []
    tracking: str | None = _run_git(
        args=["rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"],
    )
    if tracking is None:
        return []
    local_ref: str | None = _run_git(args=["rev-parse", "HEAD"])
    remote_ref: str | None = _run_git(args=["rev-parse", tracking])
    if local_ref is None or remote_ref is None:
        return []
    if local_ref == remote_ref:
        return []
    diagnostics: list[Diagnostic] = []
    for file_path in [json_path, md_path]:
        if not file_path.exists():
            continue
        try:
            relative: str = str(file_path.relative_to(REPO_ROOT))
        except ValueError:
            continue
        remote_has: str | None = _run_git(
            args=["cat-file", "-t", f"{remote_ref}:{relative}"],
        )
        if remote_has is None:
            diagnostics.append(
                Diagnostic(
                    code=DN_E019,
                    message=f"File is not pushed to remote: {relative}",
                    file_path=file_path,
                ),
            )
    return diagnostics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_daily_news(*, date: str) -> VerificationResult:
    json_path: Path = news_json_path(date=date)
    md_path: Path = news_md_path(date=date)
    diagnostics: list[Diagnostic] = []

    # JSON checks
    json_result: _JsonLoadResult = _check_json_load(file_path=json_path)
    diagnostics.extend(json_result.diagnostics)
    if json_result.data is not None:
        data: dict[str, Any] = json_result.data
        diagnostics.extend(
            _check_json_top_level(data=data, date=date, file_path=json_path),
        )
        diagnostics.extend(
            _check_json_required_fields(data=data, file_path=json_path),
        )
        diagnostics.extend(
            _check_json_nested_objects(data=data, file_path=json_path),
        )
        diagnostics.extend(
            _check_json_cost(data=data, file_path=json_path),
        )
        diagnostics.extend(
            _check_json_warnings(data=data, file_path=json_path),
        )

    # Markdown checks
    md_result: _MdLoadResult = _check_md_load(file_path=md_path)
    diagnostics.extend(md_result.diagnostics)
    if md_result.content is not None:
        content: str = md_result.content
        diagnostics.extend(
            _check_md_structure(content=content, date=date, file_path=md_path),
        )
        diagnostics.extend(
            _check_md_warnings(content=content, file_path=md_path),
        )

    # Git checks
    diagnostics.extend(
        _check_git_committed(date=date, json_path=json_path, md_path=md_path),
    )
    diagnostics.extend(
        _check_git_pushed(date=date, json_path=json_path, md_path=md_path),
    )

    return VerificationResult(
        file_path=json_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_dates() -> list[str]:
    if not NEWS_DIR.exists():
        return []
    dates: list[str] = []
    for json_file in sorted(NEWS_DIR.glob("*.json")):
        stem: str = json_file.stem
        if DATE_PATTERN.match(stem) is not None:
            dates.append(stem)
    return dates


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify daily news files against specification.",
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="ISO date (YYYY-MM-DD) to verify",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all news files in news/",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.all:
        dates: list[str] = _discover_dates()
        if len(dates) == 0:
            print("No news files found in news/")
            sys.exit(0)
        exit_code: int = 0
        for date in dates:
            result: VerificationResult = verify_daily_news(date=date)
            print_verification_result(result=result)
            if exit_code_for_result(result=result) != 0:
                exit_code = 1
        sys.exit(exit_code)
    elif args.date is not None:
        result = verify_daily_news(date=args.date)
        print_verification_result(result=result)
        sys.exit(exit_code_for_result(result=result))
    else:
        parser.error("Provide a date or use --all")


if __name__ == "__main__":
    main()
