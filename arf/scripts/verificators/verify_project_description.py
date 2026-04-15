"""Verify that project/description.md conforms to the project description specification.

Specification: arf/specifications/project_description_specification.md
Verificator version: 1.0
"""

import argparse
import re
import sys
from pathlib import Path

from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    PROJECT_DESCRIPTION_PATH,
)
from arf.scripts.verificators.common.reporting import (
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

MANDATORY_SECTIONS: list[str] = [
    "Goal",
    "Scope",
    "Research Questions",
    "Success Criteria",
    "Key References",
    "Current Phase",
]

SCOPE_SUBSECTIONS: list[str] = [
    "In Scope",
    "Out of Scope",
]

MIN_GOAL_WORDS: int = 30
MIN_RESEARCH_QUESTIONS: int = 3
MAX_RESEARCH_QUESTIONS: int = 7
MIN_SUCCESS_CRITERIA: int = 3
MIN_KEY_REFERENCES: int = 3
MIN_CURRENT_PHASE_WORDS: int = 15

_NUMBERED_ITEM_PATTERN: re.Pattern[str] = re.compile(r"^\d+\.\s", re.MULTILINE)
_BULLET_ITEM_PATTERN: re.Pattern[str] = re.compile(r"^\*\s", re.MULTILINE)
_H1_PATTERN: re.Pattern[str] = re.compile(r"^# .+$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PD"

PD_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
PD_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
PD_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
PD_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)

PD_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
PD_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
PD_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
PD_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
PD_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
PD_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_h1_headings(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    h1_matches: list[re.Match[str]] = list(_H1_PATTERN.finditer(content))
    if len(h1_matches) == 0:
        return [
            Diagnostic(
                code=PD_E003,
                message="No # heading found in project description",
                file_path=file_path,
            ),
        ]
    if len(h1_matches) > 1:
        return [
            Diagnostic(
                code=PD_E003,
                message=(
                    f"Multiple # headings found ({len(h1_matches)}) — exactly one is required"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_mandatory_sections(
    *,
    section_headings: set[str],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for section_name in MANDATORY_SECTIONS:
        if section_name not in section_headings:
            diagnostics.append(
                Diagnostic(
                    code=PD_E002,
                    message=f"Missing mandatory section: '## {section_name}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_scope_subsections(
    *,
    scope_content: str,
    file_path: Path,
) -> list[Diagnostic]:
    h3_pattern: re.Pattern[str] = re.compile(r"^### (.+)$", re.MULTILINE)
    h3_headings: set[str] = {m.group(1).strip() for m in h3_pattern.finditer(scope_content)}
    diagnostics: list[Diagnostic] = []
    for subsection_name in SCOPE_SUBSECTIONS:
        if subsection_name not in h3_headings:
            diagnostics.append(
                Diagnostic(
                    code=PD_E004,
                    message=(f"Scope section missing subsection: '### {subsection_name}'"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_goal_word_count(
    *,
    goal_content: str,
    file_path: Path,
) -> list[Diagnostic]:
    word_count: int = count_words(text=goal_content)
    if word_count < MIN_GOAL_WORDS:
        return [
            Diagnostic(
                code=PD_W001,
                message=(f"Goal section has {word_count} words (minimum: {MIN_GOAL_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_research_questions_count(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    items: list[re.Match[str]] = list(
        _NUMBERED_ITEM_PATTERN.finditer(content),
    )
    count: int = len(items)
    diagnostics: list[Diagnostic] = []
    if count < MIN_RESEARCH_QUESTIONS:
        diagnostics.append(
            Diagnostic(
                code=PD_W002,
                message=(
                    f"Research Questions has {count} numbered items"
                    f" (minimum: {MIN_RESEARCH_QUESTIONS})"
                ),
                file_path=file_path,
            ),
        )
    if count > MAX_RESEARCH_QUESTIONS:
        diagnostics.append(
            Diagnostic(
                code=PD_W003,
                message=(
                    f"Research Questions has {count} numbered items"
                    f" (maximum: {MAX_RESEARCH_QUESTIONS})"
                ),
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_bullet_count(
    *,
    content: str,
    minimum: int,
    section_name: str,
    code: DiagnosticCode,
    file_path: Path,
) -> list[Diagnostic]:
    items: list[re.Match[str]] = list(
        _BULLET_ITEM_PATTERN.finditer(content),
    )
    count: int = len(items)
    if count < minimum:
        return [
            Diagnostic(
                code=code,
                message=(f"{section_name} has {count} bullet items (minimum: {minimum})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_current_phase_word_count(
    *,
    content: str,
    file_path: Path,
) -> list[Diagnostic]:
    word_count: int = count_words(text=content)
    if word_count < MIN_CURRENT_PHASE_WORDS:
        return [
            Diagnostic(
                code=PD_W006,
                message=(
                    f"Current Phase has {word_count} words (minimum: {MIN_CURRENT_PHASE_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def _get_section_content(
    *,
    sections: list[MarkdownSection],
    heading: str,
) -> str | None:
    for section in sections:
        if section.heading == heading:
            return section.content
    return None


def verify_project_description(
    *,
    file_path: Path | None = None,
) -> VerificationResult:
    path: Path = file_path if file_path is not None else PROJECT_DESCRIPTION_PATH
    diagnostics: list[Diagnostic] = []

    if not path.exists():
        diagnostics.append(
            Diagnostic(
                code=PD_E001,
                message=f"project/description.md does not exist: {path}",
                file_path=path,
            ),
        )
        return VerificationResult(
            file_path=path,
            diagnostics=diagnostics,
        )

    content: str = path.read_text(encoding="utf-8")

    # Check H1 headings
    diagnostics.extend(
        _check_h1_headings(content=content, file_path=path),
    )

    # Extract level-2 sections
    sections: list[MarkdownSection] = extract_sections(body=content, level=2)
    section_headings: set[str] = {s.heading for s in sections}

    # Check mandatory sections
    diagnostics.extend(
        _check_mandatory_sections(
            section_headings=section_headings,
            file_path=path,
        ),
    )

    # Scope subsections
    scope_content: str | None = _get_section_content(
        sections=sections,
        heading="Scope",
    )
    if scope_content is not None:
        diagnostics.extend(
            _check_scope_subsections(
                scope_content=scope_content,
                file_path=path,
            ),
        )

    # Goal word count
    goal_content: str | None = _get_section_content(
        sections=sections,
        heading="Goal",
    )
    if goal_content is not None:
        diagnostics.extend(
            _check_goal_word_count(
                goal_content=goal_content,
                file_path=path,
            ),
        )

    # Research Questions count
    rq_content: str | None = _get_section_content(
        sections=sections,
        heading="Research Questions",
    )
    if rq_content is not None:
        diagnostics.extend(
            _check_research_questions_count(
                content=rq_content,
                file_path=path,
            ),
        )

    # Success Criteria count
    sc_content: str | None = _get_section_content(
        sections=sections,
        heading="Success Criteria",
    )
    if sc_content is not None:
        diagnostics.extend(
            _check_bullet_count(
                content=sc_content,
                minimum=MIN_SUCCESS_CRITERIA,
                section_name="Success Criteria",
                code=PD_W004,
                file_path=path,
            ),
        )

    # Key References count
    kr_content: str | None = _get_section_content(
        sections=sections,
        heading="Key References",
    )
    if kr_content is not None:
        diagnostics.extend(
            _check_bullet_count(
                content=kr_content,
                minimum=MIN_KEY_REFERENCES,
                section_name="Key References",
                code=PD_W005,
                file_path=path,
            ),
        )

    # Current Phase word count
    cp_content: str | None = _get_section_content(
        sections=sections,
        heading="Current Phase",
    )
    if cp_content is not None:
        diagnostics.extend(
            _check_current_phase_word_count(
                content=cp_content,
                file_path=path,
            ),
        )

    return VerificationResult(
        file_path=path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify project/description.md",
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default=None,
        help=("Path to description.md to verify. If omitted, verifies project/description.md."),
    )
    args: argparse.Namespace = parser.parse_args()

    path: Path | None = None
    if args.file_path is not None:
        path = Path(args.file_path)

    result: VerificationResult = verify_project_description(
        file_path=path,
    )
    print_verification_result(result=result)

    if result.passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
