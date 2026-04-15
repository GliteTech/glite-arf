"""Verificator for task metrics.json files.

Validates that results/metrics.json uses either the legacy flat format or the
explicit multi-variant format defined in the task results specification
(arf/specifications/task_results_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_task_metrics <task_id>
    uv run python -m arf.scripts.verificators.verify_task_metrics --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from arf.scripts.common.task_metrics import (
    ALLOWED_VARIANT_FIELDS,
    DIMENSIONS_FIELD,
    IMPLICIT_VARIANT_ID,
    LABEL_FIELD,
    METRICS_FIELD,
    SNAKE_CASE_PATTERN,
    VARIANT_ID_FIELD,
    VARIANT_ID_PATTERN,
    VARIANTS_FIELD,
    is_scalar_metric_value,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    metrics_path,
    results_dir,
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
from arf.scripts.verificators.verify_metrics import (
    collect_registered_metric_keys,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "TM"

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

TM_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
TM_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
TM_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
TM_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
TM_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)

TM_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
TM_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)


# ---------------------------------------------------------------------------
# Verification logic
# ---------------------------------------------------------------------------


def _load_metrics_payload(*, file_path: Path) -> VerificationResult | dict[str, Any]:
    diagnostics: list[Diagnostic] = []

    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=TM_E001,
                message=f"metrics.json does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code=TM_E001,
                message=f"metrics.json cannot be read: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    try:
        parsed: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        diagnostics.append(
            Diagnostic(
                code=TM_E001,
                message=f"metrics.json is not valid JSON: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    if not isinstance(parsed, dict):
        diagnostics.append(
            Diagnostic(
                code=TM_E002,
                message="metrics.json top-level value is not a JSON object",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    return parsed


def _check_metric_map(
    *,
    data: dict[str, Any],
    file_path: Path,
    map_label: str,
    registered_keys: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for key, value in data.items():
        if not is_scalar_metric_value(value=value):
            diagnostics.append(
                Diagnostic(
                    code=TM_E004,
                    message=(f"{map_label} key '{key}' has a nested object or array value"),
                    file_path=file_path,
                ),
            )
        if SNAKE_CASE_PATTERN.match(key) is None:
            diagnostics.append(
                Diagnostic(
                    code=TM_W001,
                    message=f"{map_label} key '{key}' is not snake_case",
                    file_path=file_path,
                ),
            )
        if key not in registered_keys:
            diagnostics.append(
                Diagnostic(
                    code=TM_E005,
                    message=(
                        f"{map_label} key '{key}' is not registered in meta/metrics/. "
                        f"Only registered project metrics are allowed in metrics.json. "
                        f"Task-specific data belongs in results_detailed.md."
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_dimensions_map(
    *,
    data: dict[str, Any],
    file_path: Path,
    variant_id: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for key, value in data.items():
        if not is_scalar_metric_value(value=value):
            diagnostics.append(
                Diagnostic(
                    code=TM_E004,
                    message=(
                        f"Variant '{variant_id}' {DIMENSIONS_FIELD} key '{key}' has a nested"
                        f" object or array value"
                    ),
                    file_path=file_path,
                ),
            )
        if SNAKE_CASE_PATTERN.match(key) is None:
            diagnostics.append(
                Diagnostic(
                    code=TM_W001,
                    message=(
                        f"Variant '{variant_id}' {DIMENSIONS_FIELD} key '{key}' is not snake_case"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_explicit_variants(
    *,
    data: dict[str, Any],
    file_path: Path,
    registered_keys: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if set(data.keys()) != {VARIANTS_FIELD}:
        diagnostics.append(
            Diagnostic(
                code=TM_E003,
                message=(
                    f"Explicit variant format only allows the top-level '{VARIANTS_FIELD}' field"
                ),
                file_path=file_path,
            ),
        )
        return diagnostics

    variants_value: object = data.get(VARIANTS_FIELD)
    if not isinstance(variants_value, list):
        diagnostics.append(
            Diagnostic(
                code=TM_E003,
                message=f"'{VARIANTS_FIELD}' must be a JSON array",
                file_path=file_path,
            ),
        )
        return diagnostics

    if len(variants_value) == 0:
        diagnostics.append(
            Diagnostic(
                code=TM_E003,
                message=(
                    f"'{VARIANTS_FIELD}' must contain at least one variant; use {{}} for no metrics"
                ),
                file_path=file_path,
            ),
        )
        return diagnostics

    seen_variant_ids: set[str] = set()
    for index, raw_variant in enumerate(variants_value):
        variant_label: str = f"Variant #{index + 1}"

        if not isinstance(raw_variant, dict):
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"{variant_label} is not a JSON object",
                    file_path=file_path,
                ),
            )
            continue

        if set(raw_variant.keys()) != ALLOWED_VARIANT_FIELDS:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=(
                        f"{variant_label} must define exactly these fields: "
                        f"{', '.join(sorted(ALLOWED_VARIANT_FIELDS))}"
                    ),
                    file_path=file_path,
                ),
            )

        variant_id: object = raw_variant.get(VARIANT_ID_FIELD)
        if not isinstance(variant_id, str) or len(variant_id) == 0:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"{variant_label} has an invalid '{VARIANT_ID_FIELD}'",
                    file_path=file_path,
                ),
            )
            continue

        if VARIANT_ID_PATTERN.match(variant_id) is None:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=(
                        f"Variant '{variant_id}' has an invalid '{VARIANT_ID_FIELD}'. Use"
                        " lowercase letters, digits, dots, hyphens, and underscores."
                    ),
                    file_path=file_path,
                ),
            )

        if variant_id == IMPLICIT_VARIANT_ID:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=(
                        f"Variant #{index + 1} uses the reserved implicit variant id"
                        " ''. Use a non-empty explicit id."
                    ),
                    file_path=file_path,
                ),
            )

        if variant_id in seen_variant_ids:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"Duplicate '{VARIANT_ID_FIELD}' value '{variant_id}'",
                    file_path=file_path,
                ),
            )
        else:
            seen_variant_ids.add(variant_id)

        label: object = raw_variant.get(LABEL_FIELD)
        if not isinstance(label, str) or len(label.strip()) == 0:
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"Variant '{variant_id}' has an invalid '{LABEL_FIELD}'",
                    file_path=file_path,
                ),
            )

        dimensions: object = raw_variant.get(DIMENSIONS_FIELD)
        if not isinstance(dimensions, dict):
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"Variant '{variant_id}' has an invalid '{DIMENSIONS_FIELD}'",
                    file_path=file_path,
                ),
            )
        else:
            diagnostics.extend(
                _check_dimensions_map(
                    data=dimensions,
                    file_path=file_path,
                    variant_id=variant_id,
                ),
            )

        metrics: object = raw_variant.get(METRICS_FIELD)
        if not isinstance(metrics, dict):
            diagnostics.append(
                Diagnostic(
                    code=TM_E003,
                    message=f"Variant '{variant_id}' has an invalid '{METRICS_FIELD}'",
                    file_path=file_path,
                ),
            )
        else:
            diagnostics.extend(
                _check_metric_map(
                    data=metrics,
                    file_path=file_path,
                    map_label=f"Variant '{variant_id}' {METRICS_FIELD}",
                    registered_keys=registered_keys,
                ),
            )

    return diagnostics


def verify_task_metrics(*, task_id: str) -> VerificationResult:
    file_path: Path = metrics_path(task_id=task_id)
    loaded: VerificationResult | dict[str, Any] = _load_metrics_payload(
        file_path=file_path,
    )
    if isinstance(loaded, VerificationResult):
        return loaded

    data: dict[str, Any] = loaded
    registered_keys: set[str] = collect_registered_metric_keys()
    diagnostics: list[Diagnostic] = []

    if VARIANTS_FIELD in data:
        diagnostics.extend(
            _check_explicit_variants(
                data=data,
                file_path=file_path,
                registered_keys=registered_keys,
            ),
        )
    else:
        diagnostics.extend(
            _check_metric_map(
                data=data,
                file_path=file_path,
                map_label="metrics.json",
                registered_keys=registered_keys,
            ),
        )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


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
        description="Verify task metrics.json file(s)",
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID to verify. If omitted, use --all.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Verify metrics.json in all task folders.",
    )
    args: argparse.Namespace = parser.parse_args()

    task_ids: list[str]
    if args.task_id is not None:
        task_ids = [args.task_id]
    elif args.all:
        task_ids = _discover_task_ids()
        if len(task_ids) == 0:
            print("No tasks with results/ directory found.")
            sys.exit(0)
    else:
        parser.error("Provide a task_id or use --all")
        return

    all_passed: bool = True
    for task_id in task_ids:
        result: VerificationResult = verify_task_metrics(task_id=task_id)
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
