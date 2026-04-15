"""Verificator for research_code.md files.

Usage:
    uv run python -m arf.scripts.verificators.verify_research_code <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.citation_utils import (
    SourceIndexEntry,
    extract_inline_citations,
    parse_source_index,
)
from arf.scripts.verificators.common.constants import (
    FRONTMATTER_FIELD_STATUS,
    FRONTMATTER_FIELD_TASK_ID,
    STATUS_PARTIAL,
)
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
    parse_frontmatter,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    research_code_path,
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
# Research-code-specific constants
# ---------------------------------------------------------------------------

FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
FRONTMATTER_FIELD_TASKS_CITED: str = "tasks_cited"
FRONTMATTER_FIELD_TASKS_REVIEWED: str = "tasks_reviewed"

TASK_INDEX_FIELD_TASK_ID: str = "task id"

SECTION_TASK_OBJECTIVE: str = "Task Objective"
SECTION_LIBRARY_LANDSCAPE: str = "Library Landscape"
SECTION_KEY_FINDINGS: str = "Key Findings"
SECTION_REUSABLE_CODE: str = "Reusable Code and Assets"
SECTION_LESSONS_LEARNED: str = "Lessons Learned"
SECTION_RECOMMENDATIONS: str = "Recommendations for This Task"
SECTION_TASK_INDEX: str = "Task Index"

MANDATORY_SECTIONS: list[str] = [
    SECTION_TASK_OBJECTIVE,
    SECTION_LIBRARY_LANDSCAPE,
    SECTION_KEY_FINDINGS,
    SECTION_REUSABLE_CODE,
    SECTION_LESSONS_LEARNED,
    SECTION_RECOMMENDATIONS,
    SECTION_TASK_INDEX,
]

MIN_WORDS_PER_SECTION: dict[str, int] = {
    SECTION_TASK_OBJECTIVE: 30,
    SECTION_LIBRARY_LANDSCAPE: 50,
    SECTION_KEY_FINDINGS: 200,
    SECTION_REUSABLE_CODE: 100,
    SECTION_LESSONS_LEARNED: 50,
    SECTION_RECOMMENDATIONS: 50,
    SECTION_TASK_INDEX: 0,
}

MIN_TOTAL_WORDS: int = 300

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "RC"

RC_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
RC_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
RC_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
RC_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
RC_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
RC_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
RC_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
RC_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
RC_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)

RC_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
RC_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
RC_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
RC_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
RC_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)

# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_spec_version(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    if FRONTMATTER_FIELD_SPEC_VERSION not in frontmatter:
        return [
            Diagnostic(
                code=RC_E008,
                message="Frontmatter is missing the 'spec_version' field",
                file_path=file_path,
            ),
        ]
    return []


def _check_task_id_match(
    *,
    frontmatter: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_task_id: object = frontmatter.get(FRONTMATTER_FIELD_TASK_ID)
    if fm_task_id is None:
        return [
            Diagnostic(
                code=RC_E003,
                message="Frontmatter is missing the 'task_id' field",
                file_path=file_path,
            ),
        ]
    if str(fm_task_id) != task_id:
        return [
            Diagnostic(
                code=RC_E003,
                message=(
                    f"Frontmatter task_id '{fm_task_id}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_mandatory_sections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    found_headings: set[str] = {s.heading for s in sections}
    diagnostics: list[Diagnostic] = []
    for required in MANDATORY_SECTIONS:
        if required not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=RC_E004,
                    message=f"Missing mandatory section: '## {required}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_tasks_cited(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    tasks_cited: object = frontmatter.get(FRONTMATTER_FIELD_TASKS_CITED)
    status: object = frontmatter.get(FRONTMATTER_FIELD_STATUS)
    if isinstance(tasks_cited, int) and tasks_cited < 1 and str(status) != STATUS_PARTIAL:
        return [
            Diagnostic(
                code=RC_E005,
                message="tasks_cited is 0 but status is not 'partial'",
                file_path=file_path,
            ),
        ]
    return []


def _check_inline_citations(
    *,
    body: str,
    task_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    task_keys: set[str] = {key for key in inline_keys if re.match(r"^t\d{4}$", key)}
    index_keys: set[str] = {entry.key for entry in task_entries}
    diagnostics: list[Diagnostic] = []
    for key in sorted(task_keys - index_keys):
        diagnostics.append(
            Diagnostic(
                code=RC_E006,
                message=(f"Inline citation [{key}] has no matching Task Index entry"),
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_task_index_entries(
    *,
    task_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in task_entries:
        if TASK_INDEX_FIELD_TASK_ID not in entry.fields:
            diagnostics.append(
                Diagnostic(
                    code=RC_E007,
                    message=(f"Task Index entry [{entry.key}] is missing the Task ID field"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_total_word_count(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    total: int = count_words(text=body)
    if total < MIN_TOTAL_WORDS:
        return [
            Diagnostic(
                code=RC_E009,
                message=(f"Total content has {total} words (minimum: {MIN_TOTAL_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_section_word_counts(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for section in sections:
        min_words: int | None = MIN_WORDS_PER_SECTION.get(section.heading)
        if min_words is None or min_words == 0:
            continue
        actual: int = count_words(text=section.content)
        if actual < min_words:
            diagnostics.append(
                Diagnostic(
                    code=RC_W001,
                    message=(
                        f"Section '{section.heading}' has {actual} words (minimum: {min_words})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_task_folder_exists(
    *,
    task_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in task_entries:
        raw_task_id: str | None = entry.fields.get(
            TASK_INDEX_FIELD_TASK_ID,
        )
        if raw_task_id is None:
            continue
        cleaned: str = raw_task_id.strip().strip("`")
        if len(cleaned) == 0:
            continue
        candidate: Path = TASKS_DIR / cleaned
        if not candidate.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=RC_W002,
                    message=(
                        f"Task Index entry [{entry.key}] references"
                        f" task '{cleaned}' which does not exist"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_key_findings_subsections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_KEY_FINDINGS:
            if re.search(r"^### ", section.content, re.MULTILINE) is None:
                return [
                    Diagnostic(
                        code=RC_W003,
                        message=("'## Key Findings' section contains no ### subsections"),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_uncited_tasks(
    *,
    body: str,
    task_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    diagnostics: list[Diagnostic] = []
    for entry in task_entries:
        if entry.key not in inline_keys:
            diagnostics.append(
                Diagnostic(
                    code=RC_W004,
                    message=(f"Task Index entry [{entry.key}] is never cited in body text"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_tasks_reviewed_vs_cited(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    tasks_reviewed: object = frontmatter.get(
        FRONTMATTER_FIELD_TASKS_REVIEWED,
    )
    tasks_cited: object = frontmatter.get(FRONTMATTER_FIELD_TASKS_CITED)
    if (
        isinstance(tasks_reviewed, int)
        and isinstance(tasks_cited, int)
        and tasks_reviewed < tasks_cited
    ):
        return [
            Diagnostic(
                code=RC_W005,
                message=(
                    f"tasks_reviewed ({tasks_reviewed}) < tasks_cited"
                    f" ({tasks_cited}) — likely a frontmatter error"
                ),
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_research_code(
    *,
    task_id: str,
) -> VerificationResult:
    file_path: Path = research_code_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: File existence
    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=RC_E001,
                message=f"File does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            Diagnostic(
                code=RC_E002,
                message=f"File is not valid UTF-8: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # E002: Frontmatter parsing
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        diagnostics.append(
            Diagnostic(
                code=RC_E002,
                message=("YAML frontmatter is missing or has invalid delimiters"),
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    raw_yaml: str = split_result.raw_yaml
    body: str = split_result.body
    frontmatter: dict[str, Any] | None = parse_frontmatter(
        raw_yaml=raw_yaml,
    )
    if frontmatter is None:
        diagnostics.append(
            Diagnostic(
                code=RC_E002,
                message="YAML frontmatter is not parseable",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # Extract sections and Task Index
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )
    task_index_content: str = ""
    for section in sections:
        if section.heading == SECTION_TASK_INDEX:
            task_index_content = section.content
            break
    task_entries: list[SourceIndexEntry] = parse_source_index(
        section_content=task_index_content,
    )

    # E008: spec_version
    diagnostics.extend(
        _check_spec_version(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E003: task_id match
    diagnostics.extend(
        _check_task_id_match(
            frontmatter=frontmatter,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E004: Mandatory sections
    diagnostics.extend(
        _check_mandatory_sections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # E005: tasks_cited < 1 with non-partial status
    diagnostics.extend(
        _check_tasks_cited(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E006: Inline citations without Task Index match
    diagnostics.extend(
        _check_inline_citations(
            body=body,
            task_entries=task_entries,
            file_path=file_path,
        ),
    )

    # E007: Task Index entries missing Task ID field
    diagnostics.extend(
        _check_task_index_entries(
            task_entries=task_entries,
            file_path=file_path,
        ),
    )

    # E009: Total word count
    diagnostics.extend(
        _check_total_word_count(
            body=body,
            file_path=file_path,
        ),
    )

    # W001: Section word counts
    diagnostics.extend(
        _check_section_word_counts(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W002: Task folder existence
    diagnostics.extend(
        _check_task_folder_exists(
            task_entries=task_entries,
            file_path=file_path,
        ),
    )

    # W003: Key Findings subsections
    diagnostics.extend(
        _check_key_findings_subsections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W004: Uncited Task Index entries
    diagnostics.extend(
        _check_uncited_tasks(
            body=body,
            task_entries=task_entries,
            file_path=file_path,
        ),
    )

    # W005: tasks_reviewed < tasks_cited
    diagnostics.extend(
        _check_tasks_reviewed_vs_cited(
            frontmatter=frontmatter,
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
        description="Verify research_code.md for a given task",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0016_baseline_wsd_with_bert)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_research_code(
        task_id=args.task_id,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
