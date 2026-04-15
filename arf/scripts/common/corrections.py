"""Shared correction discovery and effective-state resolution."""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    ALL_TARGET_KINDS,
    TargetKey,
    TargetRecord,
    find_file_entry,
    load_target_record,
    resolve_file_entry_path,
    to_repo_relative_path,
)
from arf.scripts.verificators.common import paths

ACTION_UPDATE: str = "update"
ACTION_DELETE: str = "delete"
ACTION_REPLACE: str = "replace"

FILE_ACTION_ADD: str = "add"
FILE_ACTION_DELETE: str = "delete"
FILE_ACTION_REPLACE: str = "replace"

FIELD_CORRECTION_ID: str = "correction_id"
FIELD_CORRECTING_TASK: str = "correcting_task"
FIELD_TARGET_TASK: str = "target_task"
FIELD_TARGET_KIND: str = "target_kind"
FIELD_TARGET_ID: str = "target_id"
FIELD_ACTION: str = "action"
FIELD_CHANGES: str = "changes"
FIELD_FILE_CHANGES: str = "file_changes"

REPLACEMENT_TASK_FIELD: str = "replacement_task"
REPLACEMENT_ID_FIELD: str = "replacement_id"
REPLACEMENT_PATH_FIELD: str = "replacement_path"


@dataclass(frozen=True, slots=True)
class FileChangeSpec:
    target_path: str
    action: str
    replacement_task: str | None
    replacement_id: str | None
    replacement_path: str | None


@dataclass(frozen=True, slots=True)
class CorrectionSpec:
    correction_id: str
    correcting_task: str
    source_file: Path
    target_key: TargetKey
    action: str
    changes: dict[str, Any] | None
    file_changes: list[FileChangeSpec]


@dataclass(frozen=True, slots=True)
class TargetResolution:
    original_key: TargetKey
    effective_key: TargetKey
    deleted: bool
    metadata_overrides: dict[str, Any]
    file_changes: list[FileChangeSpec]


@dataclass(frozen=True, slots=True)
class ResolvedFileReference:
    logical_path: str
    repo_relative_path: str
    source_task: str
    source_id: str
    source_logical_path: str
    description: str | None
    format: str | None


@dataclass(frozen=True, slots=True)
class EffectiveTargetRecord:
    original_key: TargetKey
    effective_key: TargetKey
    payload: dict[str, Any]
    file_references: list[ResolvedFileReference]


@dataclass(frozen=True, slots=True)
class FileCorrectionKey:
    target_key: TargetKey
    logical_path: str


@dataclass(frozen=True, slots=True, order=True)
class CorrectionSortKey:
    task_index: int
    correction_id: str
    source_file_name: str


class CorrectionCycleError(RuntimeError):
    """Raised when correction replacement chains contain a cycle."""


def discover_corrections() -> list[CorrectionSpec]:
    correction_specs: list[CorrectionSpec] = []
    if not paths.TASKS_DIR.exists():
        return correction_specs

    for task_dir in sorted(paths.TASKS_DIR.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        corrections_path: Path = paths.corrections_dir(task_id=task_dir.name)
        if not corrections_path.exists():
            continue
        for file_path in sorted(corrections_path.iterdir()):
            if not file_path.is_file() or file_path.suffix != ".json":
                continue
            spec: CorrectionSpec | None = _load_correction_spec(
                file_path=file_path,
            )
            if spec is not None:
                correction_specs.append(spec)

    correction_specs.sort(key=_correction_sort_key)
    return correction_specs


def build_correction_index(
    *,
    correction_specs: list[CorrectionSpec],
) -> dict[TargetKey, list[CorrectionSpec]]:
    index: dict[TargetKey, list[CorrectionSpec]] = defaultdict(list)
    for correction_spec in correction_specs:
        index[correction_spec.target_key].append(correction_spec)
    return index


def resolve_target(
    *,
    original_key: TargetKey,
    correction_index: dict[TargetKey, list[CorrectionSpec]],
    active_keys: set[TargetKey] | None = None,
) -> TargetResolution:
    if active_keys is None:
        active_keys = set()
    if original_key in active_keys:
        raise CorrectionCycleError(f"Correction cycle detected for {original_key}")

    active_keys.add(original_key)
    correction_specs: list[CorrectionSpec] = correction_index.get(original_key, [])

    effective_key: TargetKey = original_key
    deleted: bool = False
    metadata_overrides: dict[str, Any] = {}
    file_changes_by_path: dict[str, FileChangeSpec] = {}

    for correction_spec in correction_specs:
        if correction_spec.action == ACTION_DELETE:
            deleted = True
            effective_key = original_key
            metadata_overrides = {}
            file_changes_by_path = {}
            continue
        if correction_spec.action == ACTION_REPLACE:
            replacement_key: TargetKey | None = _replacement_key_from_changes(
                changes=correction_spec.changes,
                target_kind=original_key.target_kind,
            )
            if replacement_key is None:
                continue
            deleted = False
            effective_key = replacement_key
            metadata_overrides = {}
            file_changes_by_path = {}
            continue
        if correction_spec.action == ACTION_UPDATE:
            deleted = False
            if correction_spec.changes is not None:
                metadata_overrides.update(correction_spec.changes)
            for file_change in correction_spec.file_changes:
                file_changes_by_path[file_change.target_path] = file_change

    if deleted:
        active_keys.remove(original_key)
        return TargetResolution(
            original_key=original_key,
            effective_key=original_key,
            deleted=True,
            metadata_overrides={},
            file_changes=[],
        )

    if effective_key != original_key:
        base_resolution: TargetResolution = resolve_target(
            original_key=effective_key,
            correction_index=correction_index,
            active_keys=active_keys,
        )
        active_keys.remove(original_key)
        if base_resolution.deleted:
            return TargetResolution(
                original_key=original_key,
                effective_key=base_resolution.effective_key,
                deleted=True,
                metadata_overrides={},
                file_changes=[],
            )
        merged_metadata: dict[str, Any] = dict(base_resolution.metadata_overrides)
        merged_metadata.update(metadata_overrides)
        merged_file_changes: dict[str, FileChangeSpec] = {
            item.target_path: item for item in base_resolution.file_changes
        }
        merged_file_changes.update(file_changes_by_path)
        return TargetResolution(
            original_key=original_key,
            effective_key=base_resolution.effective_key,
            deleted=False,
            metadata_overrides=merged_metadata,
            file_changes=list(merged_file_changes.values()),
        )

    active_keys.remove(original_key)
    return TargetResolution(
        original_key=original_key,
        effective_key=effective_key,
        deleted=False,
        metadata_overrides=metadata_overrides,
        file_changes=list(file_changes_by_path.values()),
    )


def load_effective_target_record(
    *,
    resolution: TargetResolution,
    correction_index: dict[TargetKey, list[CorrectionSpec]],
) -> EffectiveTargetRecord | None:
    if resolution.deleted:
        return None
    base_record: TargetRecord | None = load_target_record(
        key=resolution.effective_key,
    )
    if base_record is None:
        return None

    payload: dict[str, Any] = dict(base_record.payload)
    payload.update(resolution.metadata_overrides)
    file_references: list[ResolvedFileReference] = _resolve_effective_file_references(
        record=base_record,
        correction_index=correction_index,
        resolution=resolution,
    )
    return EffectiveTargetRecord(
        original_key=resolution.original_key,
        effective_key=resolution.effective_key,
        payload=payload,
        file_references=file_references,
    )


def dedupe_effective_records(
    *,
    records: list[EffectiveTargetRecord],
) -> list[EffectiveTargetRecord]:
    grouped: dict[TargetKey, list[EffectiveTargetRecord]] = defaultdict(list)
    for record in records:
        grouped[record.effective_key].append(record)

    deduped: list[EffectiveTargetRecord] = []
    for effective_key in sorted(
        grouped.keys(),
        key=lambda item: (item.task_id, item.target_id, item.target_kind),
    ):
        group: list[EffectiveTargetRecord] = grouped[effective_key]
        preferred: EffectiveTargetRecord | None = None
        for record in group:
            if record.original_key == record.effective_key:
                preferred = record
                break
        if preferred is None:
            preferred = group[0]
        deduped.append(preferred)
    return deduped


def find_resolved_file(
    *,
    record: EffectiveTargetRecord,
    logical_path: str,
) -> ResolvedFileReference | None:
    for reference in record.file_references:
        if reference.logical_path == logical_path:
            return reference
    return None


def _resolve_effective_file_references(
    *,
    record: TargetRecord,
    correction_index: dict[TargetKey, list[CorrectionSpec]],
    resolution: TargetResolution,
) -> list[ResolvedFileReference]:
    file_changes_by_path: dict[str, FileChangeSpec] = {
        file_change.target_path: file_change for file_change in resolution.file_changes
    }
    ordered_logical_paths: list[str] = [entry.logical_path for entry in record.file_entries]
    for file_change in resolution.file_changes:
        if (
            file_change.action == FILE_ACTION_ADD
            and file_change.target_path not in ordered_logical_paths
        ):
            ordered_logical_paths.append(file_change.target_path)

    file_references: list[ResolvedFileReference] = []
    for logical_path in ordered_logical_paths:
        resolved_reference = _resolve_effective_file_reference(
            correction_index=correction_index,
            file_changes_by_path=file_changes_by_path,
            logical_path=logical_path,
            record=record,
        )
        if resolved_reference is None:
            continue
        file_references.append(resolved_reference)

    return file_references


def _resolve_effective_file_reference(
    *,
    correction_index: dict[TargetKey, list[CorrectionSpec]],
    file_changes_by_path: dict[str, FileChangeSpec],
    logical_path: str,
    record: TargetRecord,
    active_pairs: set[FileCorrectionKey] | None = None,
) -> ResolvedFileReference | None:
    if active_pairs is None:
        active_pairs = set()

    pair: FileCorrectionKey = FileCorrectionKey(
        target_key=record.key,
        logical_path=logical_path,
    )
    if pair in active_pairs:
        raise CorrectionCycleError(
            f"File correction cycle detected for {record.key}::{logical_path}",
        )

    active_pairs.add(pair)
    file_change: FileChangeSpec | None = file_changes_by_path.get(logical_path)
    if file_change is not None:
        if file_change.action == FILE_ACTION_DELETE:
            active_pairs.remove(pair)
            return None
        replacement_key: TargetKey | None = _replacement_key_from_file_change(
            file_change=file_change,
            target_kind=record.key.target_kind,
        )
        if replacement_key is not None and file_change.replacement_path is not None:
            replacement_resolution: TargetResolution = resolve_target(
                original_key=replacement_key,
                correction_index=correction_index,
            )
            if replacement_resolution.deleted:
                active_pairs.remove(pair)
                return None
            replacement_record: TargetRecord | None = load_target_record(
                key=replacement_resolution.effective_key,
            )
            if replacement_record is None:
                active_pairs.remove(pair)
                return None
            replacement_file_changes_by_path: dict[str, FileChangeSpec] = {
                item.target_path: item for item in replacement_resolution.file_changes
            }
            resolved_reference = _resolve_effective_file_reference(
                correction_index=correction_index,
                file_changes_by_path=replacement_file_changes_by_path,
                logical_path=file_change.replacement_path,
                record=replacement_record,
                active_pairs=active_pairs,
            )
            active_pairs.remove(pair)
            if resolved_reference is None:
                return None
            return ResolvedFileReference(
                logical_path=logical_path,
                repo_relative_path=resolved_reference.repo_relative_path,
                source_task=resolved_reference.source_task,
                source_id=resolved_reference.source_id,
                source_logical_path=resolved_reference.source_logical_path,
                description=resolved_reference.description,
                format=resolved_reference.format,
            )

    entry = find_file_entry(
        record=record,
        logical_path=logical_path,
    )
    active_pairs.remove(pair)
    if entry is None:
        return None
    repo_path: Path = resolve_file_entry_path(
        record=record,
        entry=entry,
    )
    return ResolvedFileReference(
        logical_path=logical_path,
        repo_relative_path=to_repo_relative_path(file_path=repo_path),
        source_task=record.key.task_id,
        source_id=record.key.target_id,
        source_logical_path=logical_path,
        description=entry.description,
        format=entry.format,
    )


def _load_correction_spec(*, file_path: Path) -> CorrectionSpec | None:
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None

    correction_id: object = data.get(FIELD_CORRECTION_ID)
    correcting_task: object = data.get(FIELD_CORRECTING_TASK)
    target_task: object = data.get(FIELD_TARGET_TASK)
    target_kind: object = data.get(FIELD_TARGET_KIND)
    target_id: object = data.get(FIELD_TARGET_ID)
    action: object = data.get(FIELD_ACTION)
    changes: object = data.get(FIELD_CHANGES)
    file_changes_value: object = data.get(FIELD_FILE_CHANGES)

    if not isinstance(correction_id, str):
        return None
    if not isinstance(correcting_task, str):
        return None
    if not isinstance(target_task, str):
        return None
    if not isinstance(target_kind, str) or target_kind not in ALL_TARGET_KINDS:
        return None
    if not isinstance(target_id, str):
        return None
    if not isinstance(action, str):
        return None

    file_changes: list[FileChangeSpec] = _parse_file_changes(
        file_changes_value=file_changes_value,
    )

    return CorrectionSpec(
        correction_id=correction_id,
        correcting_task=correcting_task,
        source_file=file_path,
        target_key=TargetKey(
            task_id=target_task,
            target_kind=target_kind,
            target_id=target_id,
        ),
        action=action,
        changes=changes if isinstance(changes, dict) else None,
        file_changes=file_changes,
    )


def _parse_file_changes(*, file_changes_value: object) -> list[FileChangeSpec]:
    if not isinstance(file_changes_value, dict):
        return []
    file_changes: list[FileChangeSpec] = []
    for target_path, raw_value in file_changes_value.items():
        if not isinstance(target_path, str):
            continue
        if not isinstance(raw_value, dict):
            continue
        action_value: object = raw_value.get(FIELD_ACTION)
        if not isinstance(action_value, str):
            continue
        replacement_task: object = raw_value.get(REPLACEMENT_TASK_FIELD)
        replacement_id: object = raw_value.get(REPLACEMENT_ID_FIELD)
        replacement_path: object = raw_value.get(REPLACEMENT_PATH_FIELD)
        file_changes.append(
            FileChangeSpec(
                target_path=target_path,
                action=action_value,
                replacement_task=replacement_task if isinstance(replacement_task, str) else None,
                replacement_id=replacement_id if isinstance(replacement_id, str) else None,
                replacement_path=replacement_path if isinstance(replacement_path, str) else None,
            ),
        )
    return file_changes


def _replacement_key_from_changes(
    *,
    changes: dict[str, Any] | None,
    target_kind: str,
) -> TargetKey | None:
    if changes is None:
        return None
    replacement_task: object = changes.get(REPLACEMENT_TASK_FIELD)
    replacement_id: object = changes.get(REPLACEMENT_ID_FIELD)
    if not isinstance(replacement_task, str) or not isinstance(replacement_id, str):
        return None
    return TargetKey(
        task_id=replacement_task,
        target_kind=target_kind,
        target_id=replacement_id,
    )


def _replacement_key_from_file_change(
    *,
    file_change: FileChangeSpec,
    target_kind: str,
) -> TargetKey | None:
    if file_change.replacement_task is None or file_change.replacement_id is None:
        return None
    return TargetKey(
        task_id=file_change.replacement_task,
        target_kind=target_kind,
        target_id=file_change.replacement_id,
    )


def _correction_sort_key(correction_spec: CorrectionSpec) -> CorrectionSortKey:
    return CorrectionSortKey(
        task_index=_task_index_from_task_id(task_id=correction_spec.correcting_task),
        correction_id=correction_spec.correction_id,
        source_file_name=correction_spec.source_file.name,
    )


def _task_index_from_task_id(*, task_id: str) -> int:
    if len(task_id) >= 5 and task_id.startswith("t"):
        numeric_part: str = task_id[1:5]
        if numeric_part.isdigit():
            return int(numeric_part)
    return 0
