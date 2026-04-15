"""Verify correction files against the corrections specification.

Usage:
    uv run python -m arf.scripts.verificators.verify_corrections <task_id>
    uv run python -m arf.scripts.verificators.verify_corrections --all

Exit codes:
    0 -- no errors (warnings may be present)
    1 -- one or more errors found
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    ALL_TARGET_KINDS,
    TARGET_KIND_SUGGESTION,
    TargetKey,
    find_file_entry,
    load_target_record,
    supports_file_changes,
)
from arf.scripts.common.corrections import (
    ACTION_DELETE,
    ACTION_REPLACE,
    ACTION_UPDATE,
    FILE_ACTION_ADD,
    FILE_ACTION_DELETE,
    FILE_ACTION_REPLACE,
    CorrectionCycleError,
    CorrectionSpec,
    build_correction_index,
    discover_corrections,
    load_effective_target_record,
    resolve_target,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    corrections_dir,
    task_json_path,
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

_PREFIX: str = "CR"

FIELD_SPEC_VERSION: str = "spec_version"
FIELD_CORRECTION_ID: str = "correction_id"
FIELD_CORRECTING_TASK: str = "correcting_task"
FIELD_TARGET_TASK: str = "target_task"
FIELD_TARGET_KIND: str = "target_kind"
FIELD_TARGET_ID: str = "target_id"
FIELD_ACTION: str = "action"
FIELD_CHANGES: str = "changes"
FIELD_FILE_CHANGES: str = "file_changes"
FIELD_RATIONALE: str = "rationale"
FIELD_PRIORITY: str = "priority"
FIELD_STATUS: str = "status"

FIELD_REPLACEMENT_TASK: str = "replacement_task"
FIELD_REPLACEMENT_ID: str = "replacement_id"
FIELD_REPLACEMENT_PATH: str = "replacement_path"
STATUS_COMPLETED: str = "completed"

REQUIRED_FIELDS: list[str] = [
    FIELD_SPEC_VERSION,
    FIELD_CORRECTION_ID,
    FIELD_CORRECTING_TASK,
    FIELD_TARGET_TASK,
    FIELD_TARGET_KIND,
    FIELD_TARGET_ID,
    FIELD_ACTION,
    FIELD_CHANGES,
    FIELD_RATIONALE,
]

ALLOWED_SPEC_VERSIONS: set[str] = {"1", "2", "3"}
ALLOWED_ACTIONS: set[str] = {
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_REPLACE,
}
ALLOWED_FILE_ACTIONS: set[str] = {
    FILE_ACTION_ADD,
    FILE_ACTION_DELETE,
    FILE_ACTION_REPLACE,
}
ALLOWED_SUGGESTION_PRIORITIES: set[str] = {"high", "medium", "low"}
ALLOWED_SUGGESTION_STATUSES: set[str] = {"active", "rejected"}
CORRECTION_ID_PATTERN: re.Pattern[str] = re.compile(r"^C-\d{4}-\d{2}$")
MIN_RATIONALE_LENGTH: int = 10

IMMUTABLE_ID_FIELDS: dict[str, str] = {
    "suggestion": "id",
    "paper": "paper_id",
    "answer": "answer_id",
    "dataset": "dataset_id",
    "library": "library_id",
    "model": "model_id",
    "predictions": "predictions_id",
}
SUGGESTION_UPDATE_FIELDS: set[str] = {
    "title",
    "description",
    "kind",
    "priority",
    "source_task",
    "source_paper",
    "categories",
    "status",
}

CR_E001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=1)
CR_E002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=2)
CR_E003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=3)
CR_E004: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=4)
CR_E005: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=5)
CR_E006: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=6)
CR_E007: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=7)
CR_E008: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=8)
CR_E009: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=9)
CR_E010: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=10)
CR_E011: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=11)
CR_E012: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=12)
CR_E013: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=13)
CR_E014: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=14)
CR_E015: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=15)
CR_E016: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=16)
CR_E017: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=17)
CR_E018: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=18)
CR_E019: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=19)
CR_E020: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=20)

CR_W001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=1)
CR_W002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=2)
CR_W003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=3)


@dataclass(frozen=True, slots=True)
class LoadedJsonObject:
    data: dict[str, Any] | None
    diagnostics: list[Diagnostic]


def _discover_correction_files(*, task_id: str) -> list[Path]:
    dir_path: Path = corrections_dir(task_id=task_id)
    if not dir_path.exists():
        return []
    return sorted(path for path in dir_path.iterdir() if path.is_file() and path.suffix == ".json")


def _load_json_object(*, file_path: Path) -> LoadedJsonObject:
    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return LoadedJsonObject(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=CR_E001,
                    message=f"Cannot read correction file: {exc}",
                    file_path=file_path,
                ),
            ],
        )

    try:
        data: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        return LoadedJsonObject(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=CR_E001,
                    message=f"Correction file is not valid JSON: {exc}",
                    file_path=file_path,
                ),
            ],
        )

    if not isinstance(data, dict):
        return LoadedJsonObject(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=CR_E002,
                    message="Top-level value is not a JSON object",
                    file_path=file_path,
                ),
            ],
        )

    return LoadedJsonObject(data=data, diagnostics=[])


def _task_index_from_task_id(*, task_id: str) -> str | None:
    if len(task_id) < 5 or not task_id.startswith("t"):
        return None
    task_index: str = task_id[1:5]
    if not task_index.isdigit():
        return None
    return task_index


def _load_task_status(*, task_id: str) -> str | None:
    file_path: Path = task_json_path(task_id=task_id)
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    status: object = data.get(FIELD_STATUS)
    if not isinstance(status, str):
        return None
    return status


def _allowed_update_fields(*, target_key: TargetKey) -> set[str]:
    target_record = load_target_record(key=target_key)
    if target_record is None:
        return set()
    if target_key.target_kind == TARGET_KIND_SUGGESTION:
        return set(SUGGESTION_UPDATE_FIELDS)
    immutable_id_field: str | None = IMMUTABLE_ID_FIELDS.get(target_key.target_kind)
    allowed_fields: set[str] = {key for key in target_record.payload if key != FIELD_SPEC_VERSION}
    if immutable_id_field is not None:
        allowed_fields.discard(immutable_id_field)
    return allowed_fields


def _validate_update_changes(
    *,
    changes: object,
    file_path: Path,
    target_key: TargetKey,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if changes is None:
        return diagnostics
    if not isinstance(changes, dict):
        return [
            Diagnostic(
                code=CR_E010,
                message="changes must be an object or null for action 'update'",
                file_path=file_path,
            ),
        ]

    allowed_fields: set[str] = _allowed_update_fields(target_key=target_key)
    for field_name, value in changes.items():
        if field_name not in allowed_fields:
            diagnostics.append(
                Diagnostic(
                    code=CR_E014,
                    message=(
                        f"Field '{field_name}' is not allowed in update changes for "
                        f"target kind '{target_key.target_kind}'"
                    ),
                    file_path=file_path,
                ),
            )
            continue
        if target_key.target_kind != TARGET_KIND_SUGGESTION:
            continue
        if field_name == FIELD_PRIORITY and value not in ALLOWED_SUGGESTION_PRIORITIES:
            diagnostics.append(
                Diagnostic(
                    code=CR_E015,
                    message=(
                        f"Invalid suggestion priority '{value}'; allowed: "
                        f"{', '.join(sorted(ALLOWED_SUGGESTION_PRIORITIES))}"
                    ),
                    file_path=file_path,
                ),
            )
        if field_name == FIELD_STATUS and value not in ALLOWED_SUGGESTION_STATUSES:
            diagnostics.append(
                Diagnostic(
                    code=CR_E015,
                    message=(
                        f"Invalid suggestion status '{value}'; allowed: "
                        f"{', '.join(sorted(ALLOWED_SUGGESTION_STATUSES))}"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _validate_replace_changes(
    *,
    changes: object,
    file_path: Path,
    target_key: TargetKey,
) -> list[Diagnostic]:
    if not isinstance(changes, dict):
        return [
            Diagnostic(
                code=CR_E010,
                message="changes must be an object when action is 'replace'",
                file_path=file_path,
            ),
        ]

    replacement_task: object = changes.get(FIELD_REPLACEMENT_TASK)
    replacement_id: object = changes.get(FIELD_REPLACEMENT_ID)
    if not isinstance(replacement_task, str) or not isinstance(replacement_id, str):
        return [
            Diagnostic(
                code=CR_E016,
                message=(
                    "replace corrections must set string fields "
                    "'replacement_task' and 'replacement_id'"
                ),
                file_path=file_path,
            ),
        ]

    replacement_key = TargetKey(
        task_id=replacement_task,
        target_kind=target_key.target_kind,
        target_id=replacement_id,
    )
    if replacement_key == target_key:
        return [
            Diagnostic(
                code=CR_E019,
                message="replace correction cannot point to the same target",
                file_path=file_path,
            ),
        ]

    if load_target_record(key=replacement_key) is None:
        return [
            Diagnostic(
                code=CR_E016,
                message=(
                    f"Replacement target '{replacement_key.target_kind}:{replacement_key.task_id}:"
                    f"{replacement_key.target_id}' does not exist"
                ),
                file_path=file_path,
            ),
        ]

    return []


def _validate_file_changes(
    *,
    action: str,
    file_changes_value: object,
    file_path: Path,
    target_key: TargetKey,
) -> list[Diagnostic]:
    if file_changes_value is None:
        return []

    diagnostics: list[Diagnostic] = []
    if action != ACTION_UPDATE:
        diagnostics.append(
            Diagnostic(
                code=CR_E011,
                message="file_changes is only allowed when action is 'update'",
                file_path=file_path,
            ),
        )
        return diagnostics

    if not supports_file_changes(target_kind=target_key.target_kind):
        diagnostics.append(
            Diagnostic(
                code=CR_E011,
                message=f"file_changes is not supported for target kind '{target_key.target_kind}'",
                file_path=file_path,
            ),
        )
        return diagnostics

    if not isinstance(file_changes_value, dict):
        diagnostics.append(
            Diagnostic(
                code=CR_E011,
                message="file_changes must be a JSON object keyed by target path",
                file_path=file_path,
            ),
        )
        return diagnostics

    target_record = load_target_record(key=target_key)
    for target_path, raw_change in file_changes_value.items():
        if not isinstance(target_path, str) or not isinstance(raw_change, dict):
            diagnostics.append(
                Diagnostic(
                    code=CR_E017,
                    message=(
                        "Each file_changes entry must use a string path key and an object value"
                    ),
                    file_path=file_path,
                ),
            )
            continue

        file_action: object = raw_change.get(FIELD_ACTION)
        if not isinstance(file_action, str) or file_action not in ALLOWED_FILE_ACTIONS:
            diagnostics.append(
                Diagnostic(
                    code=CR_E017,
                    message=(
                        f"file_changes['{target_path}'].action must be one of: "
                        f"{', '.join(sorted(ALLOWED_FILE_ACTIONS))}"
                    ),
                    file_path=file_path,
                ),
            )
            continue

        target_entry_exists: bool = False
        if target_record is not None:
            target_entry_exists = (
                find_file_entry(record=target_record, logical_path=target_path) is not None
            )

        if file_action == FILE_ACTION_ADD and target_entry_exists:
            diagnostics.append(
                Diagnostic(
                    code=CR_E018,
                    message=(
                        f"file_changes['{target_path}'] uses action 'add' but the target path "
                        "already exists; use 'replace' instead"
                    ),
                    file_path=file_path,
                ),
            )
        if file_action in {FILE_ACTION_DELETE, FILE_ACTION_REPLACE} and not target_entry_exists:
            diagnostics.append(
                Diagnostic(
                    code=CR_E018,
                    message=(
                        f"file_changes['{target_path}'] targets a path that does not exist in "
                        "the target artifact"
                    ),
                    file_path=file_path,
                ),
            )

        replacement_task: object = raw_change.get(FIELD_REPLACEMENT_TASK)
        replacement_id: object = raw_change.get(FIELD_REPLACEMENT_ID)
        replacement_path: object = raw_change.get(FIELD_REPLACEMENT_PATH)

        if file_action == FILE_ACTION_DELETE:
            if (
                replacement_task is not None
                or replacement_id is not None
                or replacement_path is not None
            ):
                diagnostics.append(
                    Diagnostic(
                        code=CR_E017,
                        message=(
                            f"file_changes['{target_path}'] with action 'delete' must not set "
                            "replacement fields"
                        ),
                        file_path=file_path,
                    ),
                )
            continue

        if not isinstance(replacement_task, str):
            diagnostics.append(
                Diagnostic(
                    code=CR_E017,
                    message=(
                        f"file_changes['{target_path}'] must set string field 'replacement_task'"
                    ),
                    file_path=file_path,
                ),
            )
            continue
        if not isinstance(replacement_id, str):
            diagnostics.append(
                Diagnostic(
                    code=CR_E017,
                    message=(
                        f"file_changes['{target_path}'] must set string field 'replacement_id'"
                    ),
                    file_path=file_path,
                ),
            )
            continue
        if not isinstance(replacement_path, str):
            diagnostics.append(
                Diagnostic(
                    code=CR_E017,
                    message=(
                        f"file_changes['{target_path}'] must set string field 'replacement_path'"
                    ),
                    file_path=file_path,
                ),
            )
            continue

        replacement_key = TargetKey(
            task_id=replacement_task,
            target_kind=target_key.target_kind,
            target_id=replacement_id,
        )
        if replacement_key == target_key and replacement_path == target_path:
            diagnostics.append(
                Diagnostic(
                    code=CR_E019,
                    message=(
                        f"file_changes['{target_path}'] cannot reference the same target file"
                    ),
                    file_path=file_path,
                ),
            )
            continue

        replacement_record = load_target_record(key=replacement_key)
        if replacement_record is None:
            diagnostics.append(
                Diagnostic(
                    code=CR_E016,
                    message=(
                        "Replacement target "
                        f"'{replacement_key.target_kind}:{replacement_key.task_id}:"
                        f"{replacement_key.target_id}' does not exist"
                    ),
                    file_path=file_path,
                ),
            )
            continue
        if find_file_entry(record=replacement_record, logical_path=replacement_path) is None:
            diagnostics.append(
                Diagnostic(
                    code=CR_E018,
                    message=(
                        f"Replacement file '{replacement_path}' does not exist in "
                        f"'{replacement_key.target_kind}:{replacement_key.task_id}:"
                        f"{replacement_key.target_id}'"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _validate_cycle_free(
    *,
    correction_spec: CorrectionSpec,
    correction_index: dict[TargetKey, list[CorrectionSpec]],
) -> list[Diagnostic]:
    try:
        resolution = resolve_target(
            original_key=correction_spec.target_key,
            correction_index=correction_index,
        )
        if not resolution.deleted:
            _ = load_effective_target_record(
                resolution=resolution,
                correction_index=correction_index,
            )
    except CorrectionCycleError as exc:
        return [
            Diagnostic(
                code=CR_E020,
                message="Correction replacement chain contains a cycle",
                detail=str(exc),
                file_path=correction_spec.source_file,
            ),
        ]
    return []


def _verify_correction_file(
    *,
    file_path: Path,
    task_id: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    loaded_json_object: LoadedJsonObject = _load_json_object(file_path=file_path)
    diagnostics.extend(loaded_json_object.diagnostics)
    data: dict[str, Any] | None = loaded_json_object.data
    if data is None:
        return diagnostics

    for field_name in REQUIRED_FIELDS:
        if field_name not in data:
            diagnostics.append(
                Diagnostic(
                    code=CR_E003,
                    message=f"Missing required field '{field_name}'",
                    file_path=file_path,
                ),
            )

    spec_version: object = data.get(FIELD_SPEC_VERSION)
    if isinstance(spec_version, str) and spec_version not in ALLOWED_SPEC_VERSIONS:
        diagnostics.append(
            Diagnostic(
                code=CR_E004,
                message=(
                    f"spec_version '{spec_version}' is not supported; allowed: "
                    f"{', '.join(sorted(ALLOWED_SPEC_VERSIONS))}"
                ),
                file_path=file_path,
            ),
        )

    correction_id: object = data.get(FIELD_CORRECTION_ID)
    if isinstance(correction_id, str):
        if CORRECTION_ID_PATTERN.match(correction_id) is None:
            diagnostics.append(
                Diagnostic(
                    code=CR_E005,
                    message=f"correction_id '{correction_id}' does not match C-XXXX-NN",
                    file_path=file_path,
                ),
            )
        else:
            expected_task_index: str | None = _task_index_from_task_id(task_id=task_id)
            actual_task_index: str = correction_id[2:6]
            if expected_task_index is not None and actual_task_index != expected_task_index:
                diagnostics.append(
                    Diagnostic(
                        code=CR_E005,
                        message=(
                            f"correction_id '{correction_id}' does not use task index "
                            f"'{expected_task_index}' from task '{task_id}'"
                        ),
                        file_path=file_path,
                    ),
                )

    correcting_task: object = data.get(FIELD_CORRECTING_TASK)
    if isinstance(correcting_task, str) and correcting_task != task_id:
        diagnostics.append(
            Diagnostic(
                code=CR_E006,
                message=(
                    f"correcting_task '{correcting_task}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        )

    target_task: object = data.get(FIELD_TARGET_TASK)
    if isinstance(target_task, str) and not (TASKS_DIR / target_task).is_dir():
        diagnostics.append(
            Diagnostic(
                code=CR_E007,
                message=f"target_task '{target_task}' does not exist",
                file_path=file_path,
            ),
        )

    target_kind: object = data.get(FIELD_TARGET_KIND)
    if isinstance(target_kind, str) and target_kind not in ALL_TARGET_KINDS:
        diagnostics.append(
            Diagnostic(
                code=CR_E008,
                message=(
                    f"target_kind '{target_kind}' is not allowed; expected one of: "
                    f"{', '.join(sorted(ALL_TARGET_KINDS))}"
                ),
                file_path=file_path,
            ),
        )

    action: object = data.get(FIELD_ACTION)
    if isinstance(action, str) and action not in ALLOWED_ACTIONS:
        diagnostics.append(
            Diagnostic(
                code=CR_E009,
                message=(
                    f"action '{action}' is not allowed; expected one of: "
                    f"{', '.join(sorted(ALLOWED_ACTIONS))}"
                ),
                file_path=file_path,
            ),
        )

    rationale: object = data.get(FIELD_RATIONALE)
    if isinstance(rationale, str) and len(rationale.strip()) == 0:
        diagnostics.append(
            Diagnostic(
                code=CR_E012,
                message="rationale is empty or whitespace-only",
                file_path=file_path,
            ),
        )

    target_id: object = data.get(FIELD_TARGET_ID)
    if (
        isinstance(target_task, str)
        and isinstance(target_kind, str)
        and isinstance(target_id, str)
        and target_kind in ALL_TARGET_KINDS
        and (TASKS_DIR / target_task).is_dir()
    ):
        target_key = TargetKey(
            task_id=target_task,
            target_kind=target_kind,
            target_id=target_id,
        )
        if load_target_record(key=target_key) is None:
            diagnostics.append(
                Diagnostic(
                    code=CR_E013,
                    message=(f"Target '{target_kind}:{target_task}:{target_id}' does not exist"),
                    file_path=file_path,
                ),
            )

        changes: object = data.get(FIELD_CHANGES)
        file_changes_value: object = data.get(FIELD_FILE_CHANGES)

        if isinstance(action, str):
            if action == ACTION_UPDATE:
                if changes is not None and not isinstance(changes, dict):
                    diagnostics.append(
                        Diagnostic(
                            code=CR_E010,
                            message=("changes must be an object or null when action is 'update'"),
                            file_path=file_path,
                        ),
                    )
                if changes is None and file_changes_value is None:
                    diagnostics.append(
                        Diagnostic(
                            code=CR_E010,
                            message=(
                                "update corrections must define at least one of changes or "
                                "file_changes"
                            ),
                            file_path=file_path,
                        ),
                    )
                diagnostics.extend(
                    _validate_update_changes(
                        changes=changes,
                        file_path=file_path,
                        target_key=target_key,
                    ),
                )
                diagnostics.extend(
                    _validate_file_changes(
                        action=action,
                        file_changes_value=file_changes_value,
                        file_path=file_path,
                        target_key=target_key,
                    ),
                )

            if action == ACTION_DELETE:
                if changes is not None:
                    diagnostics.append(
                        Diagnostic(
                            code=CR_E010,
                            message="changes must be null when action is 'delete'",
                            file_path=file_path,
                        ),
                    )
                if file_changes_value is not None:
                    diagnostics.append(
                        Diagnostic(
                            code=CR_E011,
                            message="file_changes is not allowed when action is 'delete'",
                            file_path=file_path,
                        ),
                    )

            if action == ACTION_REPLACE:
                diagnostics.extend(
                    _validate_replace_changes(
                        changes=changes,
                        file_path=file_path,
                        target_key=target_key,
                    ),
                )
                if file_changes_value is not None:
                    diagnostics.append(
                        Diagnostic(
                            code=CR_E011,
                            message="file_changes is not allowed when action is 'replace'",
                            file_path=file_path,
                        ),
                    )

    if isinstance(target_task, str) and (TASKS_DIR / target_task).is_dir():
        target_status: str | None = _load_task_status(task_id=target_task)
        if target_status is not None and target_status != STATUS_COMPLETED:
            diagnostics.append(
                Diagnostic(
                    code=CR_W001,
                    message=(
                        f"target_task '{target_task}' has status "
                        f"'{target_status}', not '{STATUS_COMPLETED}'"
                    ),
                    file_path=file_path,
                ),
            )

    if isinstance(target_kind, str) and isinstance(target_id, str):
        expected_file_name: str = f"{target_kind}_{target_id}.json"
        if file_path.name != expected_file_name:
            diagnostics.append(
                Diagnostic(
                    code=CR_W002,
                    message=(
                        f"Filename '{file_path.name}' does not match convention "
                        f"'{expected_file_name}'"
                    ),
                    file_path=file_path,
                ),
            )

    if (
        isinstance(rationale, str)
        and len(rationale.strip()) > 0
        and len(rationale.strip()) < MIN_RATIONALE_LENGTH
    ):
        diagnostics.append(
            Diagnostic(
                code=CR_W003,
                message=(
                    f"rationale is {len(rationale.strip())} characters, under "
                    f"{MIN_RATIONALE_LENGTH}"
                ),
                file_path=file_path,
            ),
        )

    return diagnostics


def verify_corrections(*, task_id: str) -> VerificationResult:
    dir_path: Path = corrections_dir(task_id=task_id)
    diagnostics: list[Diagnostic] = []
    correction_files: list[Path] = _discover_correction_files(task_id=task_id)

    for file_path in correction_files:
        diagnostics.extend(
            _verify_correction_file(
                file_path=file_path,
                task_id=task_id,
            ),
        )

    correction_specs: list[CorrectionSpec] = discover_corrections()
    correction_index = build_correction_index(correction_specs=correction_specs)
    for correction_spec in correction_specs:
        if correction_spec.correcting_task != task_id:
            continue
        diagnostics.extend(
            _validate_cycle_free(
                correction_spec=correction_spec,
                correction_index=correction_index,
            ),
        )

    return VerificationResult(file_path=dir_path, diagnostics=diagnostics)


def _discover_task_ids_with_corrections() -> list[str]:
    if not TASKS_DIR.exists():
        return []

    task_ids: list[str] = []
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        correction_files = _discover_correction_files(task_id=task_dir.name)
        if len(correction_files) == 0:
            continue
        task_ids.append(task_dir.name)
    return task_ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify correction files in task corrections/ folders",
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
        help="Verify corrections in all task folders.",
    )
    args = parser.parse_args()

    task_ids: list[str]
    if args.task_id is not None:
        task_ids = [args.task_id]
    elif args.all:
        task_ids = _discover_task_ids_with_corrections()
        if len(task_ids) == 0:
            print("No tasks with correction files found.")
            sys.exit(0)
    else:
        parser.error("Provide a task_id or use --all")
        return

    all_passed: bool = True
    for task_id in task_ids:
        result = verify_corrections(task_id=task_id)
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
