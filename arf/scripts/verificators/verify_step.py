"""Verificator for a single task step.

Checks the step folder contents against the step verification registry.
Each step type defines its own required files, optional files, and
markdown section requirements.

Usage:
    uv run python -m arf.scripts.verificators.verify_step <task_id> <step_id>
    uv run python -m arf.scripts.verificators.verify_step <task_id> --step-number 4

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    step_folder_path,
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
from arf.scripts.verificators.step_registry import (
    FileRequirement,
    StepVerificationSpec,
    build_default_spec,
    get_step_spec,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "SV"

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

SV_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
SV_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
SV_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
SV_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
SV_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)

SV_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
SV_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
SV_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)


# ---------------------------------------------------------------------------
# File resolution
# ---------------------------------------------------------------------------


def _resolve_file_path(
    *,
    requirement: FileRequirement,
    step_folder: Path,
    task_dir: Path,
) -> Path:
    if requirement.is_external:
        return task_dir / requirement.relative_path
    return step_folder / requirement.relative_path


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_step_folder_exists(
    *,
    step_folder: Path,
) -> list[Diagnostic]:
    if not step_folder.is_dir():
        return [
            Diagnostic(
                code=SV_E001,
                message=f"Step folder does not exist: {step_folder.name}",
                file_path=step_folder,
            ),
        ]
    return []


def _check_required_files(
    *,
    spec: StepVerificationSpec,
    step_folder: Path,
    task_dir: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for req in spec.required_files:
        file_path: Path = _resolve_file_path(
            requirement=req,
            step_folder=step_folder,
            task_dir=task_dir,
        )
        error_code: DiagnosticCode = SV_E003 if req.is_external else SV_E002
        if not file_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=error_code,
                    message=f"Required file missing: {req.relative_path}",
                    file_path=step_folder,
                ),
            )
    return diagnostics


def _check_optional_files(
    *,
    spec: StepVerificationSpec,
    step_folder: Path,
    task_dir: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for req in spec.optional_files:
        file_path: Path = _resolve_file_path(
            requirement=req,
            step_folder=step_folder,
            task_dir=task_dir,
        )
        if not file_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=SV_W002,
                    message=f"Optional file missing: {req.relative_path}",
                    file_path=step_folder,
                ),
            )
    return diagnostics


def _check_markdown_file(
    *,
    requirement: FileRequirement,
    step_folder: Path,
    task_dir: Path,
) -> list[Diagnostic]:
    if requirement.markdown is None:
        return []

    file_path: Path = _resolve_file_path(
        requirement=requirement,
        step_folder=step_folder,
        task_dir=task_dir,
    )
    if not file_path.exists():
        return []

    diagnostics: list[Diagnostic] = []
    md_req = requirement.markdown

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        diagnostics.append(
            Diagnostic(
                code=SV_E004,
                message=f"Cannot read markdown file: {md_req.relative_path}",
                file_path=file_path,
            ),
        )
        return diagnostics

    # For step_log.md, check frontmatter
    if requirement.relative_path == "step_log.md":
        fm_result: FrontmatterResult | None = extract_frontmatter_and_body(
            content=content,
        )
        if fm_result is None:
            diagnostics.append(
                Diagnostic(
                    code=SV_E004,
                    message="step_log.md missing YAML frontmatter",
                    file_path=file_path,
                ),
            )
            return diagnostics
        body: str = fm_result.body
    else:
        body = content

    # Check required sections
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )
    found_headings: set[str] = {s.heading for s in sections}
    for required_heading in md_req.required_sections:
        if required_heading not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=SV_E005,
                    message=(f"Missing section '## {required_heading}' in {md_req.relative_path}"),
                    file_path=file_path,
                ),
            )

    # Check minimum word count
    if md_req.min_total_words > 0:
        total_words: int = count_words(text=body)
        if total_words < md_req.min_total_words:
            diagnostics.append(
                Diagnostic(
                    code=SV_W001,
                    message=(
                        f"{md_req.relative_path} has {total_words} words "
                        f"(minimum: {md_req.min_total_words})"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


# ---------------------------------------------------------------------------
# Step ID resolution from step_tracker.json
# ---------------------------------------------------------------------------


def _load_tracker_steps(*, task_id: str) -> list[dict[str, object]] | None:
    """Load and return the steps list from step_tracker.json, or None."""
    tracker_path: Path = step_tracker_path(task_id=task_id)
    if not tracker_path.exists():
        return None

    try:
        raw: str = tracker_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    steps: object = data.get("steps")
    if not isinstance(steps, list):
        return None

    return [s for s in steps if isinstance(s, dict)]


@dataclass(frozen=True, slots=True)
class ResolvedStep:
    step_id: str
    step_number: int


def _resolve_step_from_tracker(
    *,
    task_id: str,
    step_number: int,
) -> ResolvedStep | None:
    steps: list[dict[str, object]] | None = _load_tracker_steps(task_id=task_id)
    if steps is None:
        return None

    for step in steps:
        if step.get("step") == step_number:
            name: object = step.get("name")
            if isinstance(name, str):
                return ResolvedStep(
                    step_id=name,
                    step_number=step_number,
                )

    return None


def _resolve_step_from_tracker_by_name(
    *,
    task_id: str,
    step_name: str,
) -> ResolvedStep | None:
    steps: list[dict[str, object]] | None = _load_tracker_steps(task_id=task_id)
    if steps is None:
        return None

    for step in steps:
        if step.get("name") == step_name:
            raw_number: object = step.get("step")
            if isinstance(raw_number, int):
                return ResolvedStep(
                    step_id=step_name,
                    step_number=raw_number,
                )

    return None


def _find_step_folder(
    *,
    task_id: str,
    step_id: str,
) -> Path | None:
    """Find an existing step folder matching the step_id pattern."""
    steps_dir: Path = TASKS_DIR / task_id / "logs" / "steps"
    if not steps_dir.is_dir():
        return None

    pattern: re.Pattern[str] = re.compile(
        rf"^\d{{3}}_{re.escape(step_id)}$",
    )
    for entry in sorted(steps_dir.iterdir()):
        if entry.is_dir() and pattern.match(entry.name) is not None:
            return entry

    return None


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_step(
    *,
    task_id: str,
    step_id: str,
    step_order: int,
) -> VerificationResult:
    step_folder: Path = step_folder_path(
        task_id=task_id,
        step_order=step_order,
        step_id=step_id,
    )
    task_dir: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []

    # Look up spec from registry
    spec: StepVerificationSpec | None = get_step_spec(step_id=step_id)
    if spec is None:
        diagnostics.append(
            Diagnostic(
                code=SV_W003,
                message=f"Step ID '{step_id}' is not in the canonical registry",
                file_path=step_folder,
            ),
        )
        spec = build_default_spec(
            step_id=step_id,
            step_order=step_order,
        )

    # E001: step folder exists
    folder_check: list[Diagnostic] = _check_step_folder_exists(
        step_folder=step_folder,
    )
    diagnostics.extend(folder_check)
    if len(folder_check) > 0:
        return VerificationResult(
            file_path=step_folder,
            diagnostics=diagnostics,
        )

    # E002, E003: required files
    diagnostics.extend(
        _check_required_files(
            spec=spec,
            step_folder=step_folder,
            task_dir=task_dir,
        ),
    )

    # W002: optional files
    diagnostics.extend(
        _check_optional_files(
            spec=spec,
            step_folder=step_folder,
            task_dir=task_dir,
        ),
    )

    # E004, E005, W001: markdown file checks
    all_files: list[FileRequirement] = spec.required_files + spec.optional_files
    for req in all_files:
        if req.markdown is not None:
            diagnostics.extend(
                _check_markdown_file(
                    requirement=req,
                    step_folder=step_folder,
                    task_dir=task_dir,
                ),
            )

    return VerificationResult(
        file_path=step_folder,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify a single step's log folder and outputs",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "step_id",
        nargs="?",
        default=None,
        help="Step ID (e.g. research-papers, implementation)",
    )
    parser.add_argument(
        "--step-number",
        type=int,
        default=None,
        help="Step number (alternative to step_id, looks up in step_tracker.json)",
    )
    args: argparse.Namespace = parser.parse_args()

    step_id: str | None = args.step_id
    step_order: int | None = args.step_number

    if step_id is None and step_order is None:
        parser.error("Provide step_id or --step-number")

    if step_id is not None and step_order is None:
        # 1. Try step_tracker.json first (actual task-local order)
        tracker_result: ResolvedStep | None = _resolve_step_from_tracker_by_name(
            task_id=args.task_id,
            step_name=step_id,
        )
        if tracker_result is not None:
            step_order = tracker_result.step_number
        else:
            # 2. Try existing folder on disk
            found: Path | None = _find_step_folder(
                task_id=args.task_id,
                step_id=step_id,
            )
            if found is not None:
                step_order = int(found.name[:3])
            else:
                # 3. Fall back to canonical registry
                spec: StepVerificationSpec | None = get_step_spec(step_id=step_id)
                if spec is not None:
                    step_order = spec.step_order
                else:
                    parser.error(
                        f"Cannot determine step order for '{step_id}'. Use --step-number.",
                    )

    if step_order is not None and step_id is None:
        resolved: ResolvedStep | None = _resolve_step_from_tracker(
            task_id=args.task_id,
            step_number=step_order,
        )
        if resolved is None:
            parser.error(
                f"Step number {step_order} not found in step_tracker.json",
            )
        step_id = resolved.step_id

    assert step_id is not None, "step_id is resolved"
    assert step_order is not None, "step_order is resolved"

    result: VerificationResult = verify_step(
        task_id=args.task_id,
        step_id=step_id,
        step_order=step_order,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
