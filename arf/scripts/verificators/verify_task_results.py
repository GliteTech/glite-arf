"""Verificator for task results files.

Checks that the results/ directory contains all required files with correct
structure, as defined in the task results specification
(arf/specifications/task_results_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_task_results <task_id>
    uv run python -m arf.scripts.verificators.verify_task_results --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.frontmatter import (
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
    costs_path,
    metrics_path,
    remote_machines_path,
    results_detailed_path,
    results_dir,
    results_images_dir,
    results_summary_path,
    task_json_path,
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

_PREFIX: str = "TR"

SNAKE_CASE_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
LEGACY_DETAILED_RESULTS_SPEC_VERSION: str = "1"
VALID_DETAILED_SPEC_VERSIONS: frozenset[str] = frozenset({"1", "2"})

SECTION_SUMMARY: str = "Summary"
SECTION_METRICS: str = "Metrics"
SECTION_VERIFICATION: str = "Verification"
SECTION_METHODOLOGY: str = "Methodology"
SECTION_LIMITATIONS: str = "Limitations"
SECTION_FILES_CREATED: str = "Files Created"
SECTION_TASK_REQUIREMENT_COVERAGE: str = "Task Requirement Coverage"
SECTION_EXAMPLES: str = "Examples"

FIELD_TASK_TYPES: str = "task_types"

# Experiment task types are now discovered dynamically from
# ``meta/task_types/<slug>/description.json`` via the
# ``requires_result_examples`` field. No hardcoded list.
FIELD_REQUIRES_RESULT_EXAMPLES: str = "requires_result_examples"

MIN_EXAMPLES_COUNT: int = 10

VERIFY_KEYWORDS: tuple[str, ...] = ("verify", "verificat", "passed", "failed")
STATUS_KEYWORDS: tuple[str, ...] = ("done", "partial", "not done")
REQUIREMENT_ID_PATTERN: re.Pattern[str] = re.compile(r"\bREQ-\d+\b")
NUMBERED_ITEM_PATTERN: re.Pattern[str] = re.compile(r"^\s*\d+\.\s", re.MULTILINE)
TABLE_ROW_PATTERN: re.Pattern[str] = re.compile(r"^\|.+\|$", re.MULTILINE)

SUMMARY_REQUIRED_SECTIONS: list[str] = [
    SECTION_SUMMARY,
    SECTION_METRICS,
    SECTION_VERIFICATION,
]

DETAILED_REQUIRED_SECTIONS_V1: list[str] = [
    SECTION_SUMMARY,
    SECTION_METHODOLOGY,
    SECTION_VERIFICATION,
    SECTION_LIMITATIONS,
    SECTION_FILES_CREATED,
]
DETAILED_REQUIRED_SECTIONS_V2: list[str] = [
    *DETAILED_REQUIRED_SECTIONS_V1,
    SECTION_TASK_REQUIREMENT_COVERAGE,
]

BACKTICK_CHAR: str = "`"
SLASH_CHAR: str = "/"
COST_SUM_TOLERANCE: float = 0.01

MIN_SUMMARY_WORDS: int = 80
MIN_DETAILED_WORDS: int = 200
MIN_SUMMARY_METRIC_BULLETS: int = 3

COSTS_FIELD_TOTAL: str = "total_cost_usd"
COSTS_FIELD_BREAKDOWN: str = "breakdown"
COSTS_FIELD_COST_USD: str = "cost_usd"
COSTS_FIELD_SERVICES: str = "services"
COSTS_FIELD_BUDGET_LIMIT: str = "budget_limit"
COSTS_FIELD_NOTE: str = "note"

TASK_JSON_FIELD_NAME: str = "name"
TASK_JSON_FIELD_DESCRIPTION_SHORT: str = "description_short"

METRICS_FIELD_VARIANTS: str = "variants"
METRICS_FIELD_VARIANT_ID: str = "variant_id"
METRICS_FIELD_METRICS: str = "metrics"
METRICS_FIELD_DIMENSIONS: str = "dimensions"

MACHINE_REQUIRED_FIELDS: list[str] = [
    "provider",
    "machine_id",
    "gpu",
    "gpu_count",
    "ram_gb",
    "duration_hours",
    "cost_usd",
]

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

TR_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
TR_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
TR_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
TR_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
TR_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
TR_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
TR_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
TR_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
TR_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
TR_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
TR_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
TR_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
TR_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
TR_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)
TR_E015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=15,
)
TR_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
TR_E017: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=17,
)
TR_E018: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=18,
)
TR_E019: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=19,
)
TR_E020: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=20,
)

TR_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
TR_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
TR_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
TR_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
TR_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
TR_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
TR_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
TR_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
TR_W009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=9,
)
TR_W010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=10,
)
TR_W011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=11,
)
TR_W012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=12,
)
TR_W013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=13,
)
TR_W014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=14,
)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def _get_task_types(*, task_id: str) -> list[str]:
    """Read task_types from task.json. Return empty list on failure."""
    tj_path: Path = task_json_path(task_id=task_id)
    if not tj_path.exists():
        return []
    try:
        data: object = json.loads(tj_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    raw: object = data.get(FIELD_TASK_TYPES)
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, str)]


def _experiment_task_types() -> frozenset[str]:
    """Discover task types that require result examples.

    Reads ``requires_result_examples`` from each task type's
    ``description.json`` in ``meta/task_types/``.
    """
    from arf.scripts.verificators.common.paths import TASK_TYPES_DIR

    result: set[str] = set()
    if TASK_TYPES_DIR.is_dir() is False:
        return frozenset(result)
    for entry in TASK_TYPES_DIR.iterdir():
        if entry.is_dir() is False:
            continue
        desc_path: Path = entry / "description.json"
        if desc_path.is_file() is False:
            continue
        try:
            data: object = json.loads(desc_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get(FIELD_REQUIRES_RESULT_EXAMPLES) is True:
            result.add(entry.name)
    return frozenset(result)


def _is_experiment_task(*, task_id: str) -> bool:
    task_types: list[str] = _get_task_types(task_id=task_id)
    experiment_types: frozenset[str] = _experiment_task_types()
    return any(t in experiment_types for t in task_types)


_LLM_TASK_NAME_KEYWORDS: list[str] = [
    "llm",
    "prompt",
    "gpt",
    "claude",
    "reasoning_effort",
    "context_window",
    "fine-tun",
    "fine_tun",
]


def _is_llm_task(*, task_id: str) -> bool:
    """Heuristic: check if task name or description mentions LLM keywords."""
    tj_path: Path = task_json_path(task_id=task_id)
    if not tj_path.exists():
        return False
    try:
        data: object = json.loads(tj_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    name: object = data.get(TASK_JSON_FIELD_NAME, "")
    desc: object = data.get(TASK_JSON_FIELD_DESCRIPTION_SHORT, "")
    combined: str = f"{name} {desc} {task_id}".lower()
    return any(kw in combined for kw in _LLM_TASK_NAME_KEYWORDS)


def _has_fenced_code_blocks(*, text: str) -> bool:
    """Return True if text contains at least one fenced code block."""
    return "```" in text


def _read_markdown(*, file_path: Path) -> str | None:
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _count_bullet_points(*, text: str) -> int:
    count: int = 0
    for line in text.splitlines():
        stripped: str = line.strip()
        if stripped.startswith("* ") or stripped.startswith("- "):
            count += 1
    return count


def _count_fenced_code_blocks(*, text: str) -> int:
    count: int = 0
    for line in text.splitlines():
        if line.strip().startswith("```"):
            count += 1
    return count // 2


def _count_numbered_items(*, text: str) -> int:
    return len(NUMBERED_ITEM_PATTERN.findall(text))


_H3_EXAMPLE_PATTERN: re.Pattern[str] = re.compile(
    r"^###\s+(Example|Sample|Case)\b",
    re.MULTILINE,
)


def _count_h3_examples(*, text: str) -> int:
    return len(_H3_EXAMPLE_PATTERN.findall(text))


def _count_examples(*, text: str) -> int:
    return (
        _count_bullet_points(text=text)
        + _count_fenced_code_blocks(text=text)
        + _count_numbered_items(text=text)
        + _count_h3_examples(text=text)
    )


def _has_structured_items(*, text: str) -> bool:
    return (
        _count_bullet_points(text=text) > 0
        or NUMBERED_ITEM_PATTERN.search(text) is not None
        or TABLE_ROW_PATTERN.search(text) is not None
    )


# ---------------------------------------------------------------------------
# Internal types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _JsonLoadResult:
    data: Any | None = None
    error: str | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def _load_json(
    *,
    file_path: Path,
    error_code: DiagnosticCode,
    label: str,
) -> _JsonLoadResult:
    if not file_path.exists():
        return _JsonLoadResult(
            error="does not exist",
            diagnostics=[
                Diagnostic(
                    code=error_code,
                    message=f"{label} does not exist: {file_path}",
                    file_path=file_path,
                ),
            ],
        )
    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _JsonLoadResult(
            error=f"cannot read: {exc}",
            diagnostics=[
                Diagnostic(
                    code=error_code,
                    message=f"{label} cannot be read: {exc}",
                    file_path=file_path,
                ),
            ],
        )
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _JsonLoadResult(
            error=f"not valid JSON: {exc}",
            diagnostics=[
                Diagnostic(
                    code=error_code,
                    message=f"{label} is not valid JSON: {exc}",
                    file_path=file_path,
                ),
            ],
        )
    return _JsonLoadResult(data=data)


# ---------------------------------------------------------------------------
# Check: results_summary.md
# ---------------------------------------------------------------------------


def _check_results_summary(*, task_id: str) -> list[Diagnostic]:
    file_path: Path = results_summary_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    content: str | None = _read_markdown(file_path=file_path)
    if content is None:
        diagnostics.append(
            Diagnostic(
                code=TR_E001,
                message=f"results_summary.md does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return diagnostics

    # E006: mandatory sections
    sections: list[MarkdownSection] = extract_sections(body=content, level=2)
    section_names: set[str] = {s.heading for s in sections}
    for required in SUMMARY_REQUIRED_SECTIONS:
        if required not in section_names:
            diagnostics.append(
                Diagnostic(
                    code=TR_E006,
                    message=(f"results_summary.md is missing mandatory section: ## {required}"),
                    file_path=file_path,
                ),
            )

    # W001: word count
    total_words: int = count_words(text=content)
    if total_words < MIN_SUMMARY_WORDS:
        diagnostics.append(
            Diagnostic(
                code=TR_W001,
                message=(
                    f"results_summary.md word count is {total_words}, "
                    f"under minimum of {MIN_SUMMARY_WORDS}"
                ),
                file_path=file_path,
            ),
        )

    # W003: metrics bullet count
    for section in sections:
        if section.heading == SECTION_METRICS:
            bullet_count: int = _count_bullet_points(text=section.content)
            if bullet_count < MIN_SUMMARY_METRIC_BULLETS:
                diagnostics.append(
                    Diagnostic(
                        code=TR_W003,
                        message=(
                            f"## Metrics section has {bullet_count} bullet points, "
                            f"fewer than {MIN_SUMMARY_METRIC_BULLETS}"
                        ),
                        file_path=file_path,
                    ),
                )
            break

    # W007: verification section mentions verificator results
    for section in sections:
        if section.heading == SECTION_VERIFICATION:
            content_lower: str = section.content.lower()
            if not any(kw in content_lower for kw in VERIFY_KEYWORDS):
                diagnostics.append(
                    Diagnostic(
                        code=TR_W007,
                        message=(
                            "## Verification section does not mention any verificator results"
                        ),
                        file_path=file_path,
                    ),
                )
            break

    return diagnostics


# ---------------------------------------------------------------------------
# Check: results_detailed.md
# ---------------------------------------------------------------------------


def _check_results_detailed(*, task_id: str) -> list[Diagnostic]:
    file_path: Path = results_detailed_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    content: str | None = _read_markdown(file_path=file_path)
    if content is None:
        diagnostics.append(
            Diagnostic(
                code=TR_E002,
                message=f"results_detailed.md does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return diagnostics

    body: str = content
    detailed_spec_version: str | None = None
    split_result = extract_frontmatter_and_body(content=content)
    if split_result is not None:
        body = split_result.body
        frontmatter: dict[str, Any] | None = parse_frontmatter(raw_yaml=split_result.raw_yaml)
        if frontmatter is not None:
            raw_spec_version: object | None = frontmatter.get(FRONTMATTER_FIELD_SPEC_VERSION)
            if isinstance(raw_spec_version, str):
                detailed_spec_version = raw_spec_version

    # E019: spec_version must be a recognized value
    if (
        detailed_spec_version is not None
        and detailed_spec_version not in VALID_DETAILED_SPEC_VERSIONS
    ):
        diagnostics.append(
            Diagnostic(
                code=TR_E019,
                message=(
                    f"results_detailed.md spec_version is"
                    f" '{detailed_spec_version}', expected one of"
                    f" {sorted(VALID_DETAILED_SPEC_VERSIONS)}"
                ),
                file_path=file_path,
            ),
        )

    uses_requirement_coverage: bool = (
        detailed_spec_version is not None
        and detailed_spec_version != LEGACY_DETAILED_RESULTS_SPEC_VERSION
    )
    required_sections: list[str] = (
        DETAILED_REQUIRED_SECTIONS_V2
        if uses_requirement_coverage
        else DETAILED_REQUIRED_SECTIONS_V1
    )

    # E007: mandatory sections
    sections: list[MarkdownSection] = extract_sections(body=body, level=2)
    section_names: set[str] = {s.heading for s in sections}
    for required in required_sections:
        if required not in section_names:
            diagnostics.append(
                Diagnostic(
                    code=TR_E007,
                    message=(f"results_detailed.md is missing mandatory section: ## {required}"),
                    file_path=file_path,
                ),
            )

    # W013/W014: Examples section for experiment tasks
    if _is_experiment_task(task_id=task_id):
        if SECTION_EXAMPLES not in section_names:
            diagnostics.append(
                Diagnostic(
                    code=TR_W013,
                    message=(
                        "results_detailed.md is missing ## Examples section"
                        " (mandatory for experiment-type tasks)"
                    ),
                    file_path=file_path,
                ),
            )
        else:
            for section in sections:
                if section.heading == SECTION_EXAMPLES:
                    example_count: int = _count_examples(
                        text=section.content,
                    )
                    if example_count < MIN_EXAMPLES_COUNT:
                        diagnostics.append(
                            Diagnostic(
                                code=TR_W014,
                                message=(
                                    f"## Examples section has {example_count}"
                                    f" examples (bullets, code blocks,"
                                    f" numbered items), minimum is"
                                    f" {MIN_EXAMPLES_COUNT}"
                                ),
                                file_path=file_path,
                            ),
                        )
                    # E020: experiment examples must include code blocks
                    # showing actual inputs and outputs.
                    if not _has_fenced_code_blocks(
                        text=section.content,
                    ):
                        diagnostics.append(
                            Diagnostic(
                                code=TR_E020,
                                message=(
                                    "## Examples section contains no fenced"
                                    " code blocks — examples must show actual"
                                    " inputs and outputs in code blocks"
                                ),
                                file_path=file_path,
                            ),
                        )
                    break

    # W002: word count
    total_words: int = count_words(text=body)
    if total_words < MIN_DETAILED_WORDS:
        diagnostics.append(
            Diagnostic(
                code=TR_W002,
                message=(
                    f"results_detailed.md word count is {total_words}, "
                    f"under minimum of {MIN_DETAILED_WORDS}"
                ),
                file_path=file_path,
            ),
        )

    # W008: files created section lists paths
    for section in sections:
        if section.heading == SECTION_FILES_CREATED:
            if BACKTICK_CHAR not in section.content and SLASH_CHAR not in section.content:
                diagnostics.append(
                    Diagnostic(
                        code=TR_W008,
                        message=("## Files Created section does not appear to list any file paths"),
                        file_path=file_path,
                    ),
                )
            break

    if uses_requirement_coverage:
        for index, section in enumerate(sections):
            if section.heading == SECTION_TASK_REQUIREMENT_COVERAGE:
                has_requirement_id: bool = (
                    REQUIREMENT_ID_PATTERN.search(section.content) is not None
                )
                has_structured_items: bool = _has_structured_items(text=section.content)
                if not has_requirement_id or not has_structured_items:
                    diagnostics.append(
                        Diagnostic(
                            code=TR_W010,
                            message=(
                                "## Task Requirement Coverage does not appear to contain"
                                " structured `REQ-*` items"
                            ),
                            file_path=file_path,
                        ),
                    )

                lowered_content: str = section.content.lower()
                if not any(keyword in lowered_content for keyword in STATUS_KEYWORDS):
                    diagnostics.append(
                        Diagnostic(
                            code=TR_W011,
                            message=(
                                "## Task Requirement Coverage does not mention"
                                " `Done`, `Partial`, or `Not done` statuses"
                            ),
                            file_path=file_path,
                        ),
                    )

                if index != len(sections) - 1:
                    diagnostics.append(
                        Diagnostic(
                            code=TR_W012,
                            message=(
                                "## Task Requirement Coverage is not the final `##` section"
                                " in results_detailed.md"
                            ),
                            file_path=file_path,
                        ),
                    )
                break

    return diagnostics


# ---------------------------------------------------------------------------
# Check: costs.json
# ---------------------------------------------------------------------------


def _check_costs(*, task_id: str) -> list[Diagnostic]:
    file_path: Path = costs_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    load: _JsonLoadResult = _load_json(
        file_path=file_path,
        error_code=TR_E004,
        label="costs.json",
    )
    diagnostics.extend(load.diagnostics)
    if load.data is None:
        return diagnostics

    if not isinstance(load.data, dict):
        diagnostics.append(
            Diagnostic(
                code=TR_E004,
                message="costs.json top-level value is not a JSON object",
                file_path=file_path,
            ),
        )
        return diagnostics

    costs_data: dict[str, Any] = load.data

    # E011: required fields
    if COSTS_FIELD_TOTAL not in costs_data:
        diagnostics.append(
            Diagnostic(
                code=TR_E011,
                message=f"costs.json is missing '{COSTS_FIELD_TOTAL}'",
                file_path=file_path,
            ),
        )
    if COSTS_FIELD_BREAKDOWN not in costs_data:
        diagnostics.append(
            Diagnostic(
                code=TR_E011,
                message=f"costs.json is missing '{COSTS_FIELD_BREAKDOWN}'",
                file_path=file_path,
            ),
        )

    # E015: total_cost_usd must be a non-negative number
    total: object = costs_data.get(COSTS_FIELD_TOTAL)
    if total is not None and (
        not isinstance(total, int | float) or isinstance(total, bool) or float(total) < 0.0
    ):
        diagnostics.append(
            Diagnostic(
                code=TR_E015,
                message=f"costs.json '{COSTS_FIELD_TOTAL}' is not a non-negative number",
                file_path=file_path,
            ),
        )

    # E012: breakdown must be object
    breakdown: object = costs_data.get(COSTS_FIELD_BREAKDOWN)
    if breakdown is not None and not isinstance(breakdown, dict):
        diagnostics.append(
            Diagnostic(
                code=TR_E012,
                message=f"costs.json '{COSTS_FIELD_BREAKDOWN}' is not a JSON object",
                file_path=file_path,
            ),
        )

    # W005: total matches sum of breakdown
    if (
        isinstance(total, int | float)
        and not isinstance(total, bool)
        and float(total) >= 0.0
        and isinstance(breakdown, dict)
    ):
        breakdown_sum: float = 0.0
        for key, value in breakdown.items():
            if isinstance(value, int | float) and not isinstance(value, bool):
                numeric_value: float = float(value)
                if numeric_value < 0.0:
                    diagnostics.append(
                        Diagnostic(
                            code=TR_E012,
                            message=(
                                f"costs.json breakdown entry '{key}' is negative; "
                                "cost values must be non-negative"
                            ),
                            file_path=file_path,
                        ),
                    )
                    continue
                breakdown_sum += numeric_value
                continue

            if isinstance(value, dict):
                nested_cost: object = value.get(COSTS_FIELD_COST_USD)
                if isinstance(nested_cost, int | float) and not isinstance(nested_cost, bool):
                    numeric_nested_cost: float = float(nested_cost)
                    if numeric_nested_cost < 0.0:
                        diagnostics.append(
                            Diagnostic(
                                code=TR_E012,
                                message=(
                                    f"costs.json breakdown entry '{key}' has a negative "
                                    f"'{COSTS_FIELD_COST_USD}'"
                                ),
                                file_path=file_path,
                            ),
                        )
                        continue
                    breakdown_sum += numeric_nested_cost
                    continue

            diagnostics.append(
                Diagnostic(
                    code=TR_E012,
                    message=(
                        f"costs.json breakdown entry '{key}' is not a number and does not contain"
                        f" a numeric '{COSTS_FIELD_COST_USD}'"
                    ),
                    file_path=file_path,
                ),
            )
        if abs(float(total) - breakdown_sum) > COST_SUM_TOLERANCE:
            diagnostics.append(
                Diagnostic(
                    code=TR_W005,
                    message=(
                        f"costs.json total_cost_usd ({total}) does not match "
                        f"sum of breakdown values ({breakdown_sum:.2f})"
                    ),
                    file_path=file_path,
                ),
            )

    services: object = costs_data.get(COSTS_FIELD_SERVICES)
    if services is not None:
        if not isinstance(services, dict):
            diagnostics.append(
                Diagnostic(
                    code=TR_E016,
                    message=f"costs.json '{COSTS_FIELD_SERVICES}' is not a JSON object",
                    file_path=file_path,
                ),
            )
        else:
            for key, value in services.items():
                if (
                    not isinstance(value, int | float)
                    or isinstance(value, bool)
                    or float(value) < 0.0
                ):
                    diagnostics.append(
                        Diagnostic(
                            code=TR_E016,
                            message=(
                                f"costs.json services entry '{key}' is not a non-negative number"
                            ),
                            file_path=file_path,
                        ),
                    )

    budget_limit: object = costs_data.get(COSTS_FIELD_BUDGET_LIMIT)
    if budget_limit is not None and (
        not isinstance(budget_limit, int | float)
        or isinstance(budget_limit, bool)
        or float(budget_limit) < 0.0
    ):
        diagnostics.append(
            Diagnostic(
                code=TR_E017,
                message=f"costs.json '{COSTS_FIELD_BUDGET_LIMIT}' is not a non-negative number",
                file_path=file_path,
            ),
        )

    note: object = costs_data.get(COSTS_FIELD_NOTE)
    if note is not None and not isinstance(note, str):
        diagnostics.append(
            Diagnostic(
                code=TR_E018,
                message=f"costs.json '{COSTS_FIELD_NOTE}' is not a string",
                file_path=file_path,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: remote_machines_used.json
# ---------------------------------------------------------------------------


def _check_remote_machines(*, task_id: str) -> list[Diagnostic]:
    file_path: Path = remote_machines_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    load: _JsonLoadResult = _load_json(
        file_path=file_path,
        error_code=TR_E005,
        label="remote_machines_used.json",
    )
    diagnostics.extend(load.diagnostics)
    if load.data is None:
        return diagnostics

    # E013: top-level must be array
    if not isinstance(load.data, list):
        diagnostics.append(
            Diagnostic(
                code=TR_E013,
                message="remote_machines_used.json top-level value is not a JSON array",
                file_path=file_path,
            ),
        )
        return diagnostics

    # E014: each entry must have required fields
    for i, entry in enumerate(load.data):
        if not isinstance(entry, dict):
            diagnostics.append(
                Diagnostic(
                    code=TR_E014,
                    message=f"machines[{i}]: not a JSON object",
                    file_path=file_path,
                ),
            )
            continue
        for field_name in MACHINE_REQUIRED_FIELDS:
            if field_name not in entry:
                diagnostics.append(
                    Diagnostic(
                        code=TR_E014,
                        message=f"machines[{i}]: missing required field '{field_name}'",
                        file_path=file_path,
                    ),
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Check: images/ warning
# ---------------------------------------------------------------------------


def _check_images_dir(*, task_id: str) -> list[Diagnostic]:
    images: Path = results_images_dir(task_id=task_id)
    if not images.is_dir():
        return [
            Diagnostic(
                code=TR_W004,
                message="results/images/ directory does not exist",
                file_path=results_dir(task_id=task_id),
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Check: metrics.json
# ---------------------------------------------------------------------------


def _check_snake_case_keys(
    *,
    keys: list[str],
    label: str,
    file_path: Path,
    diagnostics: list[Diagnostic],
) -> None:
    for key in keys:
        if SNAKE_CASE_PATTERN.match(key) is None:
            diagnostics.append(
                Diagnostic(
                    code=TR_W006,
                    message=f"{label} key '{key}' is not snake_case",
                    file_path=file_path,
                ),
            )


def _check_variant_format(
    *,
    data: dict[str, Any],
    file_path: Path,
    diagnostics: list[Diagnostic],
) -> None:
    variants: object = data.get(METRICS_FIELD_VARIANTS)
    if not isinstance(variants, list):
        diagnostics.append(
            Diagnostic(
                code=TR_E010,
                message="metrics.json 'variants' is not a list",
                file_path=file_path,
            ),
        )
        return
    if len(variants) == 0:
        diagnostics.append(
            Diagnostic(
                code=TR_E010,
                message="metrics.json 'variants' is an empty array",
                file_path=file_path,
            ),
        )
        return
    for idx, variant in enumerate(variants):
        if not isinstance(variant, dict):
            diagnostics.append(
                Diagnostic(
                    code=TR_E010,
                    message=(f"metrics.json variant at index {idx} is not an object"),
                    file_path=file_path,
                ),
            )
            continue
        vid: object = variant.get(METRICS_FIELD_VARIANT_ID)
        if not isinstance(vid, str) or len(vid) == 0:
            diagnostics.append(
                Diagnostic(
                    code=TR_E010,
                    message=(f"variant at index {idx} missing or empty 'variant_id'"),
                    file_path=file_path,
                ),
            )
        vid_label: str = str(vid) if isinstance(vid, str) else f"index {idx}"
        m: object = variant.get(METRICS_FIELD_METRICS)
        if not isinstance(m, dict):
            diagnostics.append(
                Diagnostic(
                    code=TR_E010,
                    message=(f"variant '{vid_label}' missing or non-object 'metrics'"),
                    file_path=file_path,
                ),
            )
        else:
            _check_snake_case_keys(
                keys=list(m.keys()),
                label=f"variant '{vid_label}' metrics",
                file_path=file_path,
                diagnostics=diagnostics,
            )
        dims: object = variant.get(METRICS_FIELD_DIMENSIONS)
        if isinstance(dims, dict):
            _check_snake_case_keys(
                keys=list(dims.keys()),
                label=f"variant '{vid_label}' dimensions",
                file_path=file_path,
                diagnostics=diagnostics,
            )


def _check_legacy_format(
    *,
    data: dict[str, Any],
    file_path: Path,
    diagnostics: list[Diagnostic],
) -> None:
    for key, value in data.items():
        if isinstance(value, dict | list):
            diagnostics.append(
                Diagnostic(
                    code=TR_E010,
                    message=(f"metrics.json key '{key}' has non-scalar value"),
                    file_path=file_path,
                ),
            )
    _check_snake_case_keys(
        keys=list(data.keys()),
        label="metrics.json",
        file_path=file_path,
        diagnostics=diagnostics,
    )


def _check_metrics(*, task_id: str) -> list[Diagnostic]:
    file_path: Path = metrics_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    load_result: _JsonLoadResult = _load_json(
        file_path=file_path,
        error_code=TR_E003,
        label="metrics.json",
    )
    if load_result.data is None:
        return load_result.diagnostics

    data: Any = load_result.data

    if not isinstance(data, dict):
        return [
            Diagnostic(
                code=TR_E008,
                message=("metrics.json top-level value is not a JSON object"),
                file_path=file_path,
            ),
        ]

    if METRICS_FIELD_VARIANTS in data:
        _check_variant_format(
            data=data,
            file_path=file_path,
            diagnostics=diagnostics,
        )
    else:
        _check_legacy_format(
            data=data,
            file_path=file_path,
            diagnostics=diagnostics,
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_task_results(*, task_id: str) -> VerificationResult:
    file_path: Path = results_dir(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(_check_results_summary(task_id=task_id))
    diagnostics.extend(_check_results_detailed(task_id=task_id))
    diagnostics.extend(_check_metrics(task_id=task_id))
    diagnostics.extend(_check_costs(task_id=task_id))
    diagnostics.extend(_check_remote_machines(task_id=task_id))
    diagnostics.extend(_check_images_dir(task_id=task_id))

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
        description="Verify task results files for a given task (or all tasks)",
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID (e.g. t0003_download_training_corpus)",
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
        for tid in task_ids:
            result: VerificationResult = verify_task_results(task_id=tid)
            print_verification_result(result=result)
            if not result.passed:
                has_errors = True
        sys.exit(1 if has_errors else 0)

    if args.task_id is None:
        parser.error("Provide a task_id or use --all")

    result = verify_task_results(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
