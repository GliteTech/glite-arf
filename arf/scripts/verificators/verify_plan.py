"""Verificator for plan/plan.md files.

Usage:
    uv run python -m arf.scripts.verificators.verify_plan <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.constants import (
    FRONTMATTER_FIELD_TASK_ID,
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
    plan_path,
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
# Plan-specific constants
# ---------------------------------------------------------------------------

FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
LEGACY_PLAN_SPEC_VERSION: str = "1"

SECTION_OBJECTIVE: str = "Objective"
SECTION_TASK_REQUIREMENT_CHECKLIST: str = "Task Requirement Checklist"
SECTION_APPROACH: str = "Approach"
SECTION_COST_ESTIMATION: str = "Cost Estimation"
SECTION_STEP_BY_STEP: str = "Step by Step"
SECTION_REMOTE_MACHINES: str = "Remote Machines"
SECTION_ASSETS_NEEDED: str = "Assets Needed"
SECTION_EXPECTED_ASSETS: str = "Expected Assets"
SECTION_TIME_ESTIMATION: str = "Time Estimation"
SECTION_RISKS: str = "Risks & Fallbacks"
SECTION_VERIFICATION: str = "Verification Criteria"

MANDATORY_SECTIONS_V1: list[str] = [
    SECTION_OBJECTIVE,
    SECTION_APPROACH,
    SECTION_COST_ESTIMATION,
    SECTION_STEP_BY_STEP,
    SECTION_REMOTE_MACHINES,
    SECTION_ASSETS_NEEDED,
    SECTION_EXPECTED_ASSETS,
    SECTION_TIME_ESTIMATION,
    SECTION_RISKS,
    SECTION_VERIFICATION,
]

MANDATORY_SECTIONS_V2: list[str] = [
    SECTION_OBJECTIVE,
    SECTION_TASK_REQUIREMENT_CHECKLIST,
    *MANDATORY_SECTIONS_V1[1:],
]

MIN_WORDS_PER_SECTION_V1: dict[str, int] = {
    SECTION_OBJECTIVE: 30,
    SECTION_APPROACH: 50,
    SECTION_COST_ESTIMATION: 20,
    SECTION_STEP_BY_STEP: 100,
    SECTION_REMOTE_MACHINES: 10,
    SECTION_ASSETS_NEEDED: 10,
    SECTION_EXPECTED_ASSETS: 20,
    SECTION_TIME_ESTIMATION: 10,
    SECTION_RISKS: 30,
    SECTION_VERIFICATION: 30,
}

MIN_WORDS_PER_SECTION_V2: dict[str, int] = {
    SECTION_TASK_REQUIREMENT_CHECKLIST: 60,
    **MIN_WORDS_PER_SECTION_V1,
}

MIN_TOTAL_WORDS: int = 200
MIN_VERIFICATION_BULLETS: int = 3

_NUMBERED_ITEM_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\d+\.\s",
    re.MULTILINE,
)
_TABLE_ROW_PATTERN: re.Pattern[str] = re.compile(
    r"^\|.+\|$",
    re.MULTILINE,
)
_DOLLAR_PATTERN: re.Pattern[str] = re.compile(r"\$\d")
_BULLET_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\*\s",
    re.MULTILINE,
)
_REQUIREMENT_ID_PATTERN: re.Pattern[str] = re.compile(r"\bREQ-\d+\b")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PL"

PL_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
PL_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
PL_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
PL_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
PL_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
PL_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
PL_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)

PL_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
PL_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
PL_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
PL_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
PL_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
PL_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
PL_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
PL_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
PL_W009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=9,
)

_EXPENSIVE_OPERATION_KEYWORDS: list[str] = [
    "inference",
    "train",
    "api call",
    "api key",
    "remote machine",
    "gpu",
]
_VALIDATION_GATE_KEYWORDS: list[str] = [
    "baseline",
    "validation gate",
    "preflight",
    "--limit",
]

# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_frontmatter_task_id(
    *,
    frontmatter: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_task_id: object = frontmatter.get(FRONTMATTER_FIELD_TASK_ID)
    if fm_task_id is None:
        return []
    if str(fm_task_id) != task_id:
        return [
            Diagnostic(
                code=PL_E003,
                message=(
                    f"Frontmatter task_id '{fm_task_id}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_frontmatter_spec_version(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    if FRONTMATTER_FIELD_SPEC_VERSION not in frontmatter:
        return [
            Diagnostic(
                code=PL_E007,
                message="Frontmatter is missing the 'spec_version' field",
                file_path=file_path,
            ),
        ]
    return []


def _check_mandatory_sections(
    *,
    sections: list[MarkdownSection],
    mandatory_sections: list[str],
    file_path: Path,
) -> list[Diagnostic]:
    found_headings: set[str] = {s.heading for s in sections}
    diagnostics: list[Diagnostic] = []
    for required in mandatory_sections:
        if required not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=PL_E004,
                    message=f"Missing mandatory section: '## {required}'",
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
                code=PL_E005,
                message=f"Total content has {total} words (minimum: {MIN_TOTAL_WORDS})",
                file_path=file_path,
            ),
        ]
    return []


def _check_step_by_step_numbered(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_STEP_BY_STEP:
            if _NUMBERED_ITEM_PATTERN.search(section.content) is None:
                return [
                    Diagnostic(
                        code=PL_E006,
                        message=(
                            "'## Step by Step' section has no numbered items"
                            " (expected '1.' pattern)"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_section_word_counts(
    *,
    sections: list[MarkdownSection],
    min_words_per_section: dict[str, int],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for section in sections:
        min_words: int | None = min_words_per_section.get(section.heading)
        if min_words is None or min_words == 0:
            continue
        actual: int = count_words(text=section.content)
        if actual < min_words:
            diagnostics.append(
                Diagnostic(
                    code=PL_W001,
                    message=(
                        f"Section '{section.heading}' has {actual} words (minimum: {min_words})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_risks_table(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_RISKS:
            if _TABLE_ROW_PATTERN.search(section.content) is None:
                return [
                    Diagnostic(
                        code=PL_W002,
                        message="'## Risks & Fallbacks' section contains no markdown table",
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_cost_dollar(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_COST_ESTIMATION:
            if _DOLLAR_PATTERN.search(section.content) is None:
                return [
                    Diagnostic(
                        code=PL_W004,
                        message=(
                            "'## Cost Estimation' does not mention a dollar amount (e.g., $0)"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_verification_bullets(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_VERIFICATION:
            bullet_count: int = len(_BULLET_PATTERN.findall(section.content))
            if bullet_count < MIN_VERIFICATION_BULLETS:
                return [
                    Diagnostic(
                        code=PL_W005,
                        message=(
                            f"'## Verification Criteria' has {bullet_count}"
                            f" bullet points (minimum: {MIN_VERIFICATION_BULLETS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_task_requirement_checklist(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_TASK_REQUIREMENT_CHECKLIST:
            has_requirement_ids: bool = _REQUIREMENT_ID_PATTERN.search(section.content) is not None
            has_structure: bool = (
                has_requirement_ids
                or _BULLET_PATTERN.search(section.content) is not None
                or _NUMBERED_ITEM_PATTERN.search(section.content) is not None
                or _TABLE_ROW_PATTERN.search(section.content) is not None
            )
            if not has_structure or not has_requirement_ids:
                return [
                    Diagnostic(
                        code=PL_W006,
                        message=(
                            "'## Task Requirement Checklist' does not appear to contain"
                            " structured `REQ-*` checklist items"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_step_by_step_requirement_ids(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_STEP_BY_STEP:
            if _REQUIREMENT_ID_PATTERN.search(section.content) is None:
                return [
                    Diagnostic(
                        code=PL_W007,
                        message="'## Step by Step' does not reference any `REQ-*` items",
                        file_path=file_path,
                    ),
                ]
            return []
    return []


_ORCHESTRATOR_FILENAMES: list[str] = [
    "results_summary.md",
    "results_detailed.md",
    "costs.json",
    "suggestions.json",
    "compare_literature.md",
]


_ZERO_TOTAL_RE: re.Pattern[str] = re.compile(
    r"(?:total|estimated)\s+(?:cost[:\s]*)?\$0(?:\.00)?(?:\b|$)",
    re.IGNORECASE,
)


def _cost_estimation_is_zero(*, sections: list[MarkdownSection]) -> bool:
    """Return True when Cost Estimation explicitly states $0 total."""
    for section in sections:
        if section.heading == SECTION_COST_ESTIMATION:
            return _ZERO_TOTAL_RE.search(section.content) is not None
    return False


def _check_validation_gates(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    step_by_step: str | None = None
    for section in sections:
        if section.heading == SECTION_STEP_BY_STEP:
            step_by_step = section.content
            break
    if step_by_step is None:
        return diagnostics

    lowered: str = step_by_step.lower()
    has_expensive_step: bool = any(kw in lowered for kw in _EXPENSIVE_OPERATION_KEYWORDS)
    if not has_expensive_step:
        return diagnostics

    # Suppress when cost estimation is $0 — no actual expensive operations.
    if _cost_estimation_is_zero(sections=sections):
        return diagnostics

    has_validation_reference: bool = any(kw in lowered for kw in _VALIDATION_GATE_KEYWORDS)
    if not has_validation_reference:
        diagnostics.append(
            Diagnostic(
                code=PL_W008,
                message=(
                    "Step by Step contains expensive operations "
                    "(inference, training, API calls) but does not "
                    "reference a baseline comparison or validation gate"
                ),
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_plan_scope_boundary(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    """Warn if Step by Step mentions orchestrator-managed files."""
    diagnostics: list[Diagnostic] = []
    step_by_step: str | None = None
    for section in sections:
        if section.heading == SECTION_STEP_BY_STEP:
            step_by_step = section.content
            break
    if step_by_step is None:
        return diagnostics

    lowered: str = step_by_step.lower()
    found: list[str] = [name for name in _ORCHESTRATOR_FILENAMES if name.lower() in lowered]
    if len(found) > 0:
        diagnostics.append(
            Diagnostic(
                code=PL_W009,
                message=(
                    "Step by Step mentions orchestrator-managed files: "
                    f"{', '.join(found)}. "
                    "The plan should cover only implementation work — "
                    "results writing, suggestions, and compare-literature "
                    "are orchestrator steps managed by execute-task"
                ),
                file_path=file_path,
            ),
        )
    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_plan(
    *,
    task_id: str,
) -> VerificationResult:
    file_path: Path = plan_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: File existence
    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=PL_E001,
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
                code=PL_E002,
                message=f"File is not valid UTF-8: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # Try to parse frontmatter (optional for backwards compatibility)
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )

    body: str
    has_frontmatter: bool = False
    plan_spec_version: str | None = None

    if split_result is not None:
        raw_yaml: str = split_result.raw_yaml
        body = split_result.body
        frontmatter: dict[str, Any] | None = parse_frontmatter(
            raw_yaml=raw_yaml,
        )
        if frontmatter is None and len(raw_yaml.strip()) > 0:
            # Frontmatter delimiters present but content not parseable
            diagnostics.append(
                Diagnostic(
                    code=PL_E002,
                    message="YAML frontmatter is present but not parseable",
                    file_path=file_path,
                ),
            )
        elif frontmatter is not None:
            has_frontmatter = True
            plan_spec_version = str(frontmatter.get(FRONTMATTER_FIELD_SPEC_VERSION, ""))
            # E003: task_id match
            diagnostics.extend(
                _check_frontmatter_task_id(
                    frontmatter=frontmatter,
                    task_id=task_id,
                    file_path=file_path,
                ),
            )
            # E007: spec_version
            diagnostics.extend(
                _check_frontmatter_spec_version(
                    frontmatter=frontmatter,
                    file_path=file_path,
                ),
            )
    else:
        body = content

    uses_requirement_checklist: bool = (
        plan_spec_version is not None and plan_spec_version != LEGACY_PLAN_SPEC_VERSION
    )
    mandatory_sections: list[str] = (
        MANDATORY_SECTIONS_V2 if uses_requirement_checklist else MANDATORY_SECTIONS_V1
    )
    min_words_per_section: dict[str, int] = (
        MIN_WORDS_PER_SECTION_V2 if uses_requirement_checklist else MIN_WORDS_PER_SECTION_V1
    )

    # W003: Missing frontmatter (backwards compat warning)
    if not has_frontmatter:
        diagnostics.append(
            Diagnostic(
                code=PL_W003,
                message=(
                    "YAML frontmatter is missing — new plans should include"
                    " frontmatter per plan_specification.md"
                ),
                file_path=file_path,
            ),
        )

    # Extract sections
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )

    # E004: Mandatory sections
    diagnostics.extend(
        _check_mandatory_sections(
            sections=sections,
            mandatory_sections=mandatory_sections,
            file_path=file_path,
        ),
    )

    # E005: Total word count
    diagnostics.extend(
        _check_total_word_count(
            body=body,
            file_path=file_path,
        ),
    )

    # E006: Step by Step numbered items
    diagnostics.extend(
        _check_step_by_step_numbered(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W001: Section word counts
    diagnostics.extend(
        _check_section_word_counts(
            sections=sections,
            min_words_per_section=min_words_per_section,
            file_path=file_path,
        ),
    )

    # W002: Risks table
    diagnostics.extend(
        _check_risks_table(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W004: Cost dollar amount
    diagnostics.extend(
        _check_cost_dollar(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W005: Verification bullet count
    diagnostics.extend(
        _check_verification_bullets(
            sections=sections,
            file_path=file_path,
        ),
    )
    if uses_requirement_checklist:
        diagnostics.extend(
            _check_task_requirement_checklist(
                sections=sections,
                file_path=file_path,
            ),
        )
        diagnostics.extend(
            _check_step_by_step_requirement_ids(
                sections=sections,
                file_path=file_path,
            ),
        )

    # W008: Validation gates for expensive operations
    diagnostics.extend(
        _check_validation_gates(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W009: Plan scope boundary — Step by Step should not include orchestrator steps
    diagnostics.extend(
        _check_plan_scope_boundary(
            sections=sections,
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
        description="Verify plan/plan.md for a given task",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0016_baseline_wsd_with_bert)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_plan(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
