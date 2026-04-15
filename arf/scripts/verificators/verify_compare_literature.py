"""Verificator for compare_literature.md.

Checks that the optional compare_literature.md file (produced by the
compare-literature step) has correct structure and content, as defined
in arf/specifications/compare_literature_specification.md.

This file is optional. When it does not exist the verificator exits 0.

Usage:
    uv run python -m arf.scripts.verificators.verify_compare_literature <task_id>
    uv run python -m arf.scripts.verificators.verify_compare_literature --all

Exit codes:
    0 — no errors (warnings may be present), or file does not exist
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.frontmatter import (
    extract_frontmatter_and_body,
    parse_frontmatter,
)
from arf.scripts.verificators.common.markdown_sections import (
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    compare_literature_path,
    results_dir,
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

_PREFIX: str = "CL"

SECTION_SUMMARY: str = "Summary"
SECTION_COMPARISON_TABLE: str = "Comparison Table"
SECTION_METHODOLOGY_DIFFERENCES: str = "Methodology Differences"
SECTION_ANALYSIS: str = "Analysis"
SECTION_LIMITATIONS: str = "Limitations"

REQUIRED_SECTIONS: list[str] = [
    SECTION_SUMMARY,
    SECTION_COMPARISON_TABLE,
    SECTION_METHODOLOGY_DIFFERENCES,
    SECTION_ANALYSIS,
    SECTION_LIMITATIONS,
]

REQUIRED_FRONTMATTER_FIELDS: list[str] = [
    "spec_version",
    "task_id",
    "date_compared",
]

MIN_TOTAL_WORDS: int = 150
MIN_TABLE_DATA_ROWS: int = 2

TABLE_ROW_PATTERN: re.Pattern[str] = re.compile(r"^\s*\|.*\|")
TABLE_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(r"^\s*\|[\s\-:|]+\|")
NUMERIC_PATTERN: re.Pattern[str] = re.compile(r"\d+\.?\d*")
CITATION_PATTERN: re.Pattern[str] = re.compile(r"[A-Z][a-z]+\d{4}")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

CL_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
CL_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
CL_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
CL_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
CL_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)

CL_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
CL_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
CL_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------


def _count_table_data_rows(*, text: str) -> int:
    count: int = 0
    for line in text.splitlines():
        if TABLE_ROW_PATTERN.match(line) is None:
            continue
        if TABLE_SEPARATOR_PATTERN.match(line) is not None:
            continue
        count += 1
    # Subtract the header row (first matching non-separator line).
    if count > 0:
        count -= 1
    return count


def _check_table_numeric_values(
    *,
    text: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    in_table: bool = False
    header_seen: bool = False

    for line in text.splitlines():
        if TABLE_ROW_PATTERN.match(line) is None:
            if in_table:
                in_table = False
                header_seen = False
            continue

        in_table = True
        if TABLE_SEPARATOR_PATTERN.match(line) is not None:
            continue

        if not header_seen:
            header_seen = True
            continue

        # Data row: check Published Value and Our Value columns.
        cells: list[str] = [c.strip() for c in line.split("|")]
        # cells[0] is empty (before first |), so meaningful cells start at 1.
        # Expected columns: Method/Paper(1), Metric(2), Published(3),
        # Our Value(4), Delta(5), Notes(6).
        if len(cells) >= 5:
            published_cell: str = cells[3] if len(cells) > 3 else ""
            our_cell: str = cells[4] if len(cells) > 4 else ""
            published_has_num: bool = NUMERIC_PATTERN.search(published_cell) is not None
            our_has_num: bool = NUMERIC_PATTERN.search(our_cell) is not None
            if not published_has_num and not our_has_num:
                diagnostics.append(
                    Diagnostic(
                        code=CL_W002,
                        message=(
                            "Table data row missing numeric values in both "
                            f"Published Value and Our Value: {line.strip()}"
                        ),
                        file_path=file_path,
                    ),
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: frontmatter
# ---------------------------------------------------------------------------


def _check_frontmatter(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    fm_result = extract_frontmatter_and_body(content=content)
    if fm_result is None:
        diagnostics.append(
            Diagnostic(
                code=CL_E001,
                message="compare_literature.md has no YAML frontmatter",
                file_path=file_path,
            ),
        )
        return diagnostics

    parsed: dict[str, Any] | None = parse_frontmatter(raw_yaml=fm_result.raw_yaml)
    if parsed is None:
        diagnostics.append(
            Diagnostic(
                code=CL_E001,
                message="compare_literature.md YAML frontmatter is not valid YAML",
                file_path=file_path,
            ),
        )
        return diagnostics

    for field_name in REQUIRED_FRONTMATTER_FIELDS:
        if field_name not in parsed:
            diagnostics.append(
                Diagnostic(
                    code=CL_E002,
                    message=(f"Frontmatter missing required field: {field_name}"),
                    file_path=file_path,
                ),
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: mandatory sections
# ---------------------------------------------------------------------------


def _check_sections(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    sections = extract_sections(body=body, level=2)
    section_names: set[str] = {s.heading for s in sections}

    for required in REQUIRED_SECTIONS:
        if required not in section_names:
            diagnostics.append(
                Diagnostic(
                    code=CL_E003,
                    message=(f"compare_literature.md is missing mandatory section: ## {required}"),
                    file_path=file_path,
                ),
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: comparison table
# ---------------------------------------------------------------------------


def _check_comparison_table(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    sections = extract_sections(body=body, level=2)

    comparison_content: str | None = None
    for section in sections:
        if section.heading == SECTION_COMPARISON_TABLE:
            comparison_content = section.content
            break

    if comparison_content is None:
        # Section missing is already caught by _check_sections.
        return diagnostics

    # E004: no table found
    has_table: bool = False
    for line in comparison_content.splitlines():
        if TABLE_ROW_PATTERN.match(line) is not None:
            has_table = True
            break

    if not has_table:
        diagnostics.append(
            Diagnostic(
                code=CL_E004,
                message=("## Comparison Table section has no markdown table"),
                file_path=file_path,
            ),
        )
        return diagnostics

    # E005: fewer than 2 data rows
    data_rows: int = _count_table_data_rows(text=comparison_content)
    if data_rows < MIN_TABLE_DATA_ROWS:
        diagnostics.append(
            Diagnostic(
                code=CL_E005,
                message=(
                    f"Comparison table has {data_rows} data rows, "
                    f"fewer than minimum of {MIN_TABLE_DATA_ROWS}"
                ),
                file_path=file_path,
            ),
        )

    # W002: rows missing numeric values
    diagnostics.extend(
        _check_table_numeric_values(
            text=comparison_content,
            file_path=file_path,
        ),
    )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: quality
# ---------------------------------------------------------------------------


def _check_quality(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    # W001: word count
    total_words: int = count_words(text=content)
    if total_words < MIN_TOTAL_WORDS:
        diagnostics.append(
            Diagnostic(
                code=CL_W001,
                message=(
                    f"compare_literature.md word count is {total_words}, "
                    f"under minimum of {MIN_TOTAL_WORDS}"
                ),
                file_path=file_path,
            ),
        )

    # W003: no citations
    if CITATION_PATTERN.search(content) is None:
        diagnostics.append(
            Diagnostic(
                code=CL_W003,
                message=("No citation keys or paper references found in compare_literature.md"),
                file_path=file_path,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_compare_literature(
    *,
    task_id: str,
) -> VerificationResult | None:
    file_path: Path = compare_literature_path(task_id=task_id)

    if not file_path.exists():
        return None

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return VerificationResult(
            file_path=file_path,
            diagnostics=[
                Diagnostic(
                    code=CL_E001,
                    message=f"Cannot read compare_literature.md: {file_path}",
                    file_path=file_path,
                ),
            ],
        )

    diagnostics: list[Diagnostic] = []

    # Extract body (after frontmatter) for section checks.
    fm_result = extract_frontmatter_and_body(content=content)
    body: str = fm_result.body if fm_result is not None else content

    diagnostics.extend(
        _check_frontmatter(content=content, file_path=file_path),
    )
    diagnostics.extend(
        _check_sections(body=body, file_path=file_path),
    )
    diagnostics.extend(
        _check_comparison_table(body=body, file_path=file_path),
    )
    diagnostics.extend(
        _check_quality(content=content, file_path=file_path),
    )

    return VerificationResult(file_path=file_path, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_task_ids() -> list[str]:
    if not TASKS_DIR.exists():
        return []
    task_ids: list[str] = []
    for task_directory in sorted(TASKS_DIR.iterdir()):
        if not task_directory.is_dir() or task_directory.name.startswith("."):
            continue
        if results_dir(task_id=task_directory.name).is_dir():
            task_ids.append(task_directory.name)
    return task_ids


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=(
            "Verify compare_literature.md for a given task (or all tasks). "
            "Exits 0 when the file does not exist (optional file)."
        ),
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID (e.g. t0019_mfs_baseline_raganato)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all tasks with results/ directories",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.all:
        task_ids: list[str] = _discover_task_ids()
        if len(task_ids) == 0:
            print("No tasks with results/ directory found.")
            sys.exit(0)
        has_errors: bool = False
        found_any: bool = False
        for tid in task_ids:
            result: VerificationResult | None = verify_compare_literature(
                task_id=tid,
            )
            if result is None:
                continue
            found_any = True
            print_verification_result(result=result)
            if not result.passed:
                has_errors = True
        if not found_any:
            print("No tasks have compare_literature.md (optional file).")
        sys.exit(1 if has_errors else 0)

    if args.task_id is None:
        parser.error("Provide a task_id or use --all")

    result = verify_compare_literature(task_id=args.task_id)
    if result is None:
        print(
            f"compare_literature.md not found for {args.task_id} (optional file, skipping).",
        )
        sys.exit(0)

    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
