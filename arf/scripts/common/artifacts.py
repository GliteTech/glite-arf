"""Shared artifact loading and manifest helpers for corrections-aware scripts."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.json_utils import load_json_file

TARGET_KIND_SUGGESTION: str = "suggestion"
TARGET_KIND_PAPER: str = "paper"
TARGET_KIND_ANSWER: str = "answer"
TARGET_KIND_DATASET: str = "dataset"
TARGET_KIND_LIBRARY: str = "library"
TARGET_KIND_MODEL: str = "model"
TARGET_KIND_PREDICTIONS: str = "predictions"

ALL_TARGET_KINDS: set[str] = {
    TARGET_KIND_SUGGESTION,
    TARGET_KIND_PAPER,
    TARGET_KIND_ANSWER,
    TARGET_KIND_DATASET,
    TARGET_KIND_LIBRARY,
    TARGET_KIND_MODEL,
    TARGET_KIND_PREDICTIONS,
}

ASSET_TARGET_KINDS: set[str] = {
    TARGET_KIND_PAPER,
    TARGET_KIND_ANSWER,
    TARGET_KIND_DATASET,
    TARGET_KIND_LIBRARY,
    TARGET_KIND_MODEL,
    TARGET_KIND_PREDICTIONS,
}

SUMMARY_FILE_NAME: str = "summary.md"
SHORT_ANSWER_FILE_NAME: str = "short_answer.md"
FULL_ANSWER_FILE_NAME: str = "full_answer.md"
DESCRIPTION_FILE_NAME: str = "description.md"

STORAGE_KIND_ASSET: str = "asset"
STORAGE_KIND_TASK: str = "task"

SUGGESTIONS_FIELD_SUGGESTIONS: str = "suggestions"
FILE_ENTRY_FIELD_PATH: str = "path"
FILE_ENTRY_FIELD_DESCRIPTION: str = "description"
FILE_ENTRY_FIELD_FORMAT: str = "format"
DESCRIPTION_PATH_FIELD: str = "description_path"
SUMMARY_PATH_FIELD: str = "summary_path"
SHORT_ANSWER_PATH_FIELD: str = "short_answer_path"
FULL_ANSWER_PATH_FIELD: str = "full_answer_path"

LIBRARY_FIELD_MODULE_PATHS: str = "module_paths"
LIBRARY_FIELD_TEST_PATHS: str = "test_paths"
PAPER_FIELD_FILES: str = "files"

DOCUMENT_KIND_DESCRIPTION: str = "description"
DOCUMENT_KIND_SUMMARY: str = "summary"
DOCUMENT_KIND_SHORT_ANSWER: str = "short_answer"
DOCUMENT_KIND_FULL_ANSWER: str = "full_answer"


@dataclass(frozen=True, slots=True)
class TargetKey:
    task_id: str
    target_kind: str
    target_id: str


@dataclass(frozen=True, slots=True)
class ArtifactFileEntry:
    logical_path: str
    storage_kind: str
    description: str | None
    format: str | None


@dataclass(frozen=True, slots=True)
class CanonicalDocumentPathSelection:
    logical_path: str | None
    metadata_field: str
    field_present: bool
    used_fallback: bool


@dataclass(frozen=True, slots=True)
class CanonicalDocumentPathResolution:
    logical_path: str | None
    file_path: Path | None
    metadata_field: str
    field_present: bool
    used_fallback: bool


@dataclass(frozen=True, slots=True)
class TargetRecord:
    key: TargetKey
    payload: dict[str, Any]
    file_entries: list[ArtifactFileEntry]


def is_asset_kind(*, target_kind: str) -> bool:
    return target_kind in ASSET_TARGET_KINDS


def supports_file_changes(*, target_kind: str) -> bool:
    return target_kind in ASSET_TARGET_KINDS


def load_target_record(*, key: TargetKey) -> TargetRecord | None:
    if key.target_kind == TARGET_KIND_SUGGESTION:
        return _load_suggestion_record(key=key)
    if key.target_kind == TARGET_KIND_PAPER:
        return _load_paper_record(key=key)
    if key.target_kind == TARGET_KIND_ANSWER:
        return _load_answer_record(key=key)
    if key.target_kind == TARGET_KIND_DATASET:
        return _load_dataset_record(key=key)
    if key.target_kind == TARGET_KIND_LIBRARY:
        return _load_library_record(key=key)
    if key.target_kind == TARGET_KIND_MODEL:
        return _load_model_record(key=key)
    if key.target_kind == TARGET_KIND_PREDICTIONS:
        return _load_predictions_record(key=key)
    return None


def target_exists(*, key: TargetKey) -> bool:
    return load_target_record(key=key) is not None


def select_canonical_document_path(
    *,
    target_kind: str,
    payload: dict[str, Any],
    document_kind: str,
) -> CanonicalDocumentPathSelection | None:
    metadata_field: str
    fallback_logical_path: str
    if target_kind == TARGET_KIND_PAPER and document_kind == DOCUMENT_KIND_SUMMARY:
        metadata_field = SUMMARY_PATH_FIELD
        fallback_logical_path = SUMMARY_FILE_NAME
    elif target_kind == TARGET_KIND_ANSWER and document_kind == DOCUMENT_KIND_SHORT_ANSWER:
        metadata_field = SHORT_ANSWER_PATH_FIELD
        fallback_logical_path = SHORT_ANSWER_FILE_NAME
    elif target_kind == TARGET_KIND_ANSWER and document_kind == DOCUMENT_KIND_FULL_ANSWER:
        metadata_field = FULL_ANSWER_PATH_FIELD
        fallback_logical_path = FULL_ANSWER_FILE_NAME
    elif (
        target_kind
        in {
            TARGET_KIND_DATASET,
            TARGET_KIND_LIBRARY,
            TARGET_KIND_MODEL,
            TARGET_KIND_PREDICTIONS,
        }
        and document_kind == DOCUMENT_KIND_DESCRIPTION
    ):
        metadata_field = DESCRIPTION_PATH_FIELD
        fallback_logical_path = DESCRIPTION_FILE_NAME
    else:
        return None

    raw_value: object = payload.get(metadata_field)
    if raw_value is None:
        return CanonicalDocumentPathSelection(
            logical_path=fallback_logical_path,
            metadata_field=metadata_field,
            field_present=False,
            used_fallback=True,
        )
    if isinstance(raw_value, str) and len(raw_value.strip()) > 0:
        return CanonicalDocumentPathSelection(
            logical_path=raw_value,
            metadata_field=metadata_field,
            field_present=True,
            used_fallback=False,
        )
    return CanonicalDocumentPathSelection(
        logical_path=None,
        metadata_field=metadata_field,
        field_present=True,
        used_fallback=False,
    )


def find_file_entry(
    *,
    record: TargetRecord,
    logical_path: str,
) -> ArtifactFileEntry | None:
    for entry in record.file_entries:
        if entry.logical_path == logical_path:
            return entry
    return None


def resolve_asset_logical_path(
    *,
    key: TargetKey,
    logical_path: str,
) -> Path:
    return _asset_dir_for_target(key=key) / logical_path


def resolve_canonical_document_path(
    *,
    key: TargetKey,
    payload: dict[str, Any],
    document_kind: str,
) -> CanonicalDocumentPathResolution | None:
    selection = select_canonical_document_path(
        target_kind=key.target_kind,
        payload=payload,
        document_kind=document_kind,
    )
    if selection is None:
        return None
    file_path: Path | None = None
    if selection.logical_path is not None:
        file_path = resolve_asset_logical_path(
            key=key,
            logical_path=selection.logical_path,
        )
    return CanonicalDocumentPathResolution(
        logical_path=selection.logical_path,
        file_path=file_path,
        metadata_field=selection.metadata_field,
        field_present=selection.field_present,
        used_fallback=selection.used_fallback,
    )


def resolve_file_entry_path(
    *,
    record: TargetRecord,
    entry: ArtifactFileEntry,
) -> Path:
    if entry.storage_kind == STORAGE_KIND_TASK:
        return paths.TASKS_DIR / record.key.task_id / entry.logical_path
    return _asset_dir_for_target(key=record.key) / entry.logical_path


def to_repo_relative_path(*, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(paths.REPO_ROOT))
    except ValueError:
        return str(file_path)


def _load_suggestion_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.suggestions_path(task_id=key.task_id)
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    suggestions: object = data.get(SUGGESTIONS_FIELD_SUGGESTIONS)
    if not isinstance(suggestions, list):
        return None
    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            continue
        suggestion_id: object = suggestion.get("id")
        if suggestion_id == key.target_id:
            return TargetRecord(
                key=key,
                payload=suggestion,
                file_entries=[],
            )
    return None


def _load_paper_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.paper_details_path(
        paper_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    file_entries: list[ArtifactFileEntry] = []
    summary_selection = select_canonical_document_path(
        target_kind=TARGET_KIND_PAPER,
        payload=data,
        document_kind=DOCUMENT_KIND_SUMMARY,
    )
    if summary_selection is not None and summary_selection.logical_path is not None:
        file_entries.append(
            ArtifactFileEntry(
                logical_path=summary_selection.logical_path,
                storage_kind=STORAGE_KIND_ASSET,
                description="Paper summary",
                format="markdown",
            ),
        )
    files_value: object = data.get(PAPER_FIELD_FILES)
    if isinstance(files_value, list):
        for item in files_value:
            if isinstance(item, str):
                file_entries.append(
                    ArtifactFileEntry(
                        logical_path=item,
                        storage_kind=STORAGE_KIND_ASSET,
                        description=None,
                        format=None,
                    ),
                )
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=file_entries,
    )


def _load_answer_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.answer_details_path(
        answer_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    file_entries: list[ArtifactFileEntry] = []
    for document_kind, description in [
        (DOCUMENT_KIND_SHORT_ANSWER, "Short answer"),
        (DOCUMENT_KIND_FULL_ANSWER, "Full answer"),
    ]:
        selection = select_canonical_document_path(
            target_kind=TARGET_KIND_ANSWER,
            payload=data,
            document_kind=document_kind,
        )
        if selection is None or selection.logical_path is None:
            continue
        file_entries.append(
            ArtifactFileEntry(
                logical_path=selection.logical_path,
                storage_kind=STORAGE_KIND_ASSET,
                description=description,
                format="markdown",
            ),
        )
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=file_entries,
    )


def _load_dataset_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.dataset_details_path(
        dataset_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=_build_standard_asset_file_entries(
            data=data,
            description_label="Dataset description",
            target_kind=TARGET_KIND_DATASET,
        ),
    )


def _load_library_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.library_details_path(
        library_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    file_entries: list[ArtifactFileEntry] = []
    description_selection = select_canonical_document_path(
        target_kind=TARGET_KIND_LIBRARY,
        payload=data,
        document_kind=DOCUMENT_KIND_DESCRIPTION,
    )
    if description_selection is not None and description_selection.logical_path is not None:
        file_entries.append(
            ArtifactFileEntry(
                logical_path=description_selection.logical_path,
                storage_kind=STORAGE_KIND_ASSET,
                description="Library description",
                format="markdown",
            ),
        )
    file_entries.extend(
        _build_task_relative_entries(
            payload=data,
            field_name=LIBRARY_FIELD_MODULE_PATHS,
            description="Library module",
        ),
    )
    file_entries.extend(
        _build_task_relative_entries(
            payload=data,
            field_name=LIBRARY_FIELD_TEST_PATHS,
            description="Library test",
        ),
    )
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=file_entries,
    )


def _load_model_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.model_details_path(
        model_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=_build_standard_asset_file_entries(
            data=data,
            description_label="Model description",
            target_kind=TARGET_KIND_MODEL,
        ),
    )


def _load_predictions_record(*, key: TargetKey) -> TargetRecord | None:
    file_path: Path = paths.predictions_details_path(
        predictions_id=key.target_id,
        task_id=key.task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None
    return TargetRecord(
        key=key,
        payload=data,
        file_entries=_build_standard_asset_file_entries(
            data=data,
            description_label="Predictions description",
            target_kind=TARGET_KIND_PREDICTIONS,
        ),
    )


def _build_standard_asset_file_entries(
    *,
    data: dict[str, Any],
    description_label: str,
    target_kind: str,
) -> list[ArtifactFileEntry]:
    file_entries: list[ArtifactFileEntry] = []
    description_selection = select_canonical_document_path(
        target_kind=target_kind,
        payload=data,
        document_kind=DOCUMENT_KIND_DESCRIPTION,
    )
    if description_selection is not None and description_selection.logical_path is not None:
        file_entries.append(
            ArtifactFileEntry(
                logical_path=description_selection.logical_path,
                storage_kind=STORAGE_KIND_ASSET,
                description=description_label,
                format="markdown",
            ),
        )
    files_value: object = data.get(PAPER_FIELD_FILES)
    if isinstance(files_value, list):
        for item in files_value:
            if not isinstance(item, dict):
                continue
            path_value: object = item.get(FILE_ENTRY_FIELD_PATH)
            description_value: object = item.get(FILE_ENTRY_FIELD_DESCRIPTION)
            format_value: object = item.get(FILE_ENTRY_FIELD_FORMAT)
            if not isinstance(path_value, str):
                continue
            file_entries.append(
                ArtifactFileEntry(
                    logical_path=path_value,
                    storage_kind=STORAGE_KIND_ASSET,
                    description=description_value if isinstance(description_value, str) else None,
                    format=format_value if isinstance(format_value, str) else None,
                ),
            )
    return file_entries


def _build_task_relative_entries(
    *,
    payload: dict[str, Any],
    field_name: str,
    description: str,
) -> list[ArtifactFileEntry]:
    entries: list[ArtifactFileEntry] = []
    paths_value: object = payload.get(field_name)
    if not isinstance(paths_value, list):
        return entries
    for item in paths_value:
        if not isinstance(item, str):
            continue
        entries.append(
            ArtifactFileEntry(
                logical_path=item,
                storage_kind=STORAGE_KIND_TASK,
                description=description,
                format=item.rsplit(".", maxsplit=1)[-1] if "." in item else None,
            ),
        )
    return entries


def _asset_dir_for_target(*, key: TargetKey) -> Path:
    if key.target_kind == TARGET_KIND_PAPER:
        return paths.paper_asset_dir(
            paper_id=key.target_id,
            task_id=key.task_id,
        )
    if key.target_kind == TARGET_KIND_ANSWER:
        return paths.answer_asset_dir(
            answer_id=key.target_id,
            task_id=key.task_id,
        )
    if key.target_kind == TARGET_KIND_DATASET:
        return paths.dataset_asset_dir(
            dataset_id=key.target_id,
            task_id=key.task_id,
        )
    if key.target_kind == TARGET_KIND_LIBRARY:
        return paths.library_asset_dir(
            library_id=key.target_id,
            task_id=key.task_id,
        )
    if key.target_kind == TARGET_KIND_MODEL:
        return paths.model_asset_dir(
            model_id=key.target_id,
            task_id=key.task_id,
        )
    if key.target_kind == TARGET_KIND_PREDICTIONS:
        return paths.predictions_asset_dir(
            predictions_id=key.target_id,
            task_id=key.task_id,
        )
    raise ValueError(f"Unsupported asset target kind: {key.target_kind}")
