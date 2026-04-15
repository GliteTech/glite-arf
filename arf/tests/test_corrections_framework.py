import json
from pathlib import Path

import pytest

import arf.scripts.verificators.verify_corrections as verify_corrections_module
import meta.asset_types.library.aggregator as aggregate_libraries_module
from arf.scripts.common.artifacts import (
    FULL_ANSWER_FILE_NAME,
    TARGET_KIND_ANSWER,
    TARGET_KIND_LIBRARY,
    TARGET_KIND_MODEL,
    TARGET_KIND_PAPER,
    TargetKey,
)
from arf.scripts.common.corrections import (
    build_correction_index,
    discover_corrections,
    find_resolved_file,
    load_effective_target_record,
    resolve_target,
)
from arf.scripts.verificators.common import paths

STATUS_COMPLETED: str = "completed"
START_TIME_UTC: str = "2026-04-02T00:00:00Z"
DATE_CREATED: str = "2026-04-02"
SPEC_VERSION_1: str = "1"
SPEC_VERSION_2: str = "2"
SPEC_VERSION_3: str = "3"

TASKS_SUBDIR: str = "tasks"
ASSETS_SUBDIR: str = "assets"
ANSWER_SUBDIR: str = "answer"
PAPER_SUBDIR: str = "paper"
DATASET_SUBDIR: str = "dataset"
LIBRARY_SUBDIR: str = "library"
MODEL_SUBDIR: str = "model"
PREDICTIONS_SUBDIR: str = "predictions"
META_SUBDIR: str = "meta"
CATEGORIES_SUBDIR: str = "categories"
METRICS_SUBDIR: str = "metrics"
TASK_TYPES_SUBDIR: str = "task_types"
FILES_SUBDIR: str = "files"
CORRECTIONS_SUBDIR: str = "corrections"
TASK_JSON_FILE: str = "task.json"
DETAILS_JSON_FILE: str = "details.json"
DESCRIPTION_FILE_NAME: str = "description.md"
SHORT_ANSWER_FILE_NAME: str = "short_answer.md"
SUMMARY_FILE_NAME: str = "summary.md"
PAPER_FILE_NAME: str = "paper.pdf"
ACTION_UPDATE: str = "update"
ACTION_REPLACE: str = "replace"
CUSTOM_SHORT_ANSWER_PATH: str = "docs/short-answer.md"
CUSTOM_FULL_ANSWER_PATH: str = "docs/full-answer.md"
CUSTOM_LIBRARY_DESCRIPTION_PATH: str = "docs/library-guide.md"
CUSTOM_PAPER_SUMMARY_PATH: str = "notes/paper-summary.md"

QUESTION_REMOTE_MACHINES: str = "When should a task use remote machines?"
SHORT_TITLE_REMOTE_MACHINES: str = "Remote machine use"
CATEGORY_INFRA: str = "infra"
CATEGORY_LIBRARY: str = "library"
CATEGORY_MODELS: str = "models"
MODEL_FRAMEWORK: str = "pytorch"
MODEL_VERSION: str = "1.0.0"
MODEL_SHORT_DESCRIPTION: str = "Model"
LIBRARY_SHORT_DESCRIPTION: str = "Library"
LIBRARY_ENTRY_POINT_NAME: str = "main"
LIBRARY_ENTRY_POINT_KIND: str = "function"
LIBRARY_ENTRY_POINT_DESCRIPTION: str = "Main entry point"
MODEL_ARCHITECTURE: str = "Test architecture"
MODEL_FILE_DESCRIPTION: str = "Weights"
MODEL_FILE_FORMAT: str = "bin"

TASK_BASE_ANSWER: str = "t0001_base_answer"
TASK_FIX_ANSWER: str = "t0002_fix_answer"
ANSWER_ID_REMOTE_MACHINES: str = "remote-machines"
ANSWER_ID_REMOTE_MACHINES_FIX: str = "remote-machines-fix"
ANSWER_CORRECTION_FILE_NAME: str = "answer_remote-machines.json"
REMOTE_SHORT_ANSWER: str = "Use them when local compute is insufficient."
REMOTE_FULL_ANSWER_ORIGINAL: str = "Original long answer."
REMOTE_FULL_ANSWER_CORRECTED: str = "Corrected long answer."
CONFIDENCE_MEDIUM: str = "medium"
CONFIDENCE_HIGH: str = "high"

TASK_BASE_MODEL: str = "t0001_base_model"
TASK_MID_MODEL: str = "t0002_mid_model"
TASK_FINAL_MODEL: str = "t0003_final_model"
TASK_CORRECT_MID_MODEL: str = "t0004_correct_mid"
TASK_CORRECT_BASE_MODEL: str = "t0005_correct_base"
MODEL_ID_BASE: str = "model-a"
MODEL_ID_MID: str = "model-b"
MODEL_ID_FINAL: str = "model-c"
MODEL_FILE_NAME: str = "model.bin"
FINAL_MODEL_FILE_NAME: str = "final.bin"
MODEL_FILE_PATH: str = f"{FILES_SUBDIR}/{MODEL_FILE_NAME}"
FINAL_MODEL_FILE_PATH: str = f"{FILES_SUBDIR}/{FINAL_MODEL_FILE_NAME}"

TASK_BASE_LIBRARY: str = "t0001_base_library"
TASK_FIX_LIBRARY: str = "t0002_fix_library"
LIBRARY_ID_LOADER: str = "loader"
LIBRARY_ID_LOADER_PATCH: str = "loader-patch"
LIBRARY_CORRECTION_FILE_NAME: str = "library_loader.json"
BASE_MODULE_PATH: str = "code/base.py"
MISSING_FILE_PATH: str = "missing.md"


def _task_dir(*, repo_root: Path, task_id: str) -> Path:
    return repo_root / TASKS_SUBDIR / task_id


def _task_asset_dir(*, repo_root: Path, task_id: str, asset_kind: str, asset_id: str) -> Path:
    return _task_dir(repo_root=repo_root, task_id=task_id) / ASSETS_SUBDIR / asset_kind / asset_id


def _write_json(*, path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _frontmatter_markdown(*, key: str, value: str, body: str) -> str:
    return f'---\n{key}: "{value}"\nspec_version: "{SPEC_VERSION_1}"\n---\n\n{body}'


def _create_task(*, repo_root: Path, task_id: str, status: str = STATUS_COMPLETED) -> Path:
    task_dir = _task_dir(repo_root=repo_root, task_id=task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        path=task_dir / TASK_JSON_FILE,
        data={
            "status": status,
            "start_time": START_TIME_UTC,
        },
    )
    return task_dir


def _configure_repo_paths(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
) -> None:
    tasks_dir = repo_root / TASKS_SUBDIR
    assets_dir = repo_root / ASSETS_SUBDIR
    answer_assets_dir = assets_dir / ANSWER_SUBDIR
    paper_assets_dir = assets_dir / PAPER_SUBDIR
    dataset_assets_dir = assets_dir / DATASET_SUBDIR
    library_assets_dir = assets_dir / LIBRARY_SUBDIR
    model_assets_dir = assets_dir / MODEL_SUBDIR
    predictions_assets_dir = assets_dir / PREDICTIONS_SUBDIR
    categories_dir = repo_root / META_SUBDIR / CATEGORIES_SUBDIR
    metrics_dir = repo_root / META_SUBDIR / METRICS_SUBDIR
    task_types_dir = repo_root / META_SUBDIR / TASK_TYPES_SUBDIR

    for directory in [
        tasks_dir,
        answer_assets_dir,
        paper_assets_dir,
        dataset_assets_dir,
        library_assets_dir,
        model_assets_dir,
        predictions_assets_dir,
        categories_dir,
        metrics_dir,
        task_types_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(paths, "REPO_ROOT", repo_root)
    monkeypatch.setattr(paths, "TASKS_DIR", tasks_dir)
    monkeypatch.setattr(paths, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(paths, "ANSWER_ASSETS_DIR", answer_assets_dir)
    monkeypatch.setattr(paths, "PAPER_ASSETS_DIR", paper_assets_dir)
    monkeypatch.setattr(paths, "DATASET_ASSETS_DIR", dataset_assets_dir)
    monkeypatch.setattr(paths, "LIBRARY_ASSETS_DIR", library_assets_dir)
    monkeypatch.setattr(paths, "MODEL_ASSETS_DIR", model_assets_dir)
    monkeypatch.setattr(paths, "PREDICTIONS_ASSETS_DIR", predictions_assets_dir)
    monkeypatch.setattr(paths, "CATEGORIES_DIR", categories_dir)
    monkeypatch.setattr(paths, "METRICS_DIR", metrics_dir)
    monkeypatch.setattr(paths, "TASK_TYPES_DIR", task_types_dir)
    monkeypatch.setattr(verify_corrections_module, "TASKS_DIR", tasks_dir)
    monkeypatch.setattr(aggregate_libraries_module, "TASKS_DIR", tasks_dir)


def _create_answer_asset(
    *,
    repo_root: Path,
    task_id: str,
    answer_id: str,
    confidence: str,
    short_answer: str,
    full_answer: str,
    short_answer_path: str = SHORT_ANSWER_FILE_NAME,
    full_answer_path: str = FULL_ANSWER_FILE_NAME,
) -> None:
    asset_dir = _task_asset_dir(
        repo_root=repo_root,
        task_id=task_id,
        asset_kind=ANSWER_SUBDIR,
        asset_id=answer_id,
    )
    _write_json(
        path=asset_dir / DETAILS_JSON_FILE,
        data={
            "spec_version": SPEC_VERSION_2,
            "answer_id": answer_id,
            "question": QUESTION_REMOTE_MACHINES,
            "short_title": SHORT_TITLE_REMOTE_MACHINES,
            "short_answer_path": short_answer_path,
            "full_answer_path": full_answer_path,
            "categories": [CATEGORY_INFRA],
            "answer_methods": ["code"],
            "source_paper_ids": [],
            "source_urls": [],
            "source_task_ids": [],
            "confidence": confidence,
            "created_by_task": task_id,
            "date_created": DATE_CREATED,
        },
    )
    _write_text(
        path=asset_dir / short_answer_path,
        content=_frontmatter_markdown(
            key="answer_id",
            value=answer_id,
            body=f"## Question\n\nQ\n\n## Answer\n\n{short_answer}\n",
        ),
    )
    _write_text(
        path=asset_dir / full_answer_path,
        content=_frontmatter_markdown(
            key="answer_id",
            value=answer_id,
            body=f"## Question\n\nQ\n\n## Short Answer\n\n{full_answer}\n",
        ),
    )


def _create_model_asset(
    *,
    repo_root: Path,
    task_id: str,
    model_id: str,
    file_name: str,
) -> None:
    asset_dir = _task_asset_dir(
        repo_root=repo_root,
        task_id=task_id,
        asset_kind=MODEL_SUBDIR,
        asset_id=model_id,
    )
    _write_json(
        path=asset_dir / DETAILS_JSON_FILE,
        data={
            "spec_version": SPEC_VERSION_1,
            "model_id": model_id,
            "name": model_id,
            "version": MODEL_VERSION,
            "short_description": MODEL_SHORT_DESCRIPTION,
            "framework": MODEL_FRAMEWORK,
            "base_model": None,
            "base_model_source": None,
            "architecture": MODEL_ARCHITECTURE,
            "training_task_id": task_id,
            "training_dataset_ids": [],
            "hyperparameters": None,
            "training_metrics": None,
            "files": [
                {
                    "path": f"{FILES_SUBDIR}/{file_name}",
                    "description": MODEL_FILE_DESCRIPTION,
                    "format": MODEL_FILE_FORMAT,
                }
            ],
            "categories": [CATEGORY_MODELS],
            "created_by_task": task_id,
            "date_created": DATE_CREATED,
        },
    )
    _write_text(
        path=asset_dir / DESCRIPTION_FILE_NAME,
        content=_frontmatter_markdown(
            key="model_id",
            value=model_id,
            body="## Summary\n\nModel summary.\n",
        ),
    )
    _write_text(
        path=asset_dir / FILES_SUBDIR / file_name,
        content=f"{task_id}:{model_id}:{file_name}\n",
    )


def _create_library_asset(
    *,
    repo_root: Path,
    task_id: str,
    library_id: str,
    module_path: str,
    description_path: str = DESCRIPTION_FILE_NAME,
    spec_version: str = SPEC_VERSION_1,
) -> None:
    asset_dir = _task_asset_dir(
        repo_root=repo_root,
        task_id=task_id,
        asset_kind=LIBRARY_SUBDIR,
        asset_id=library_id,
    )
    _write_json(
        path=asset_dir / DETAILS_JSON_FILE,
        data={
            "spec_version": spec_version,
            "library_id": library_id,
            "name": library_id,
            "version": MODEL_VERSION,
            "short_description": LIBRARY_SHORT_DESCRIPTION,
            "description_path": description_path if spec_version != SPEC_VERSION_1 else None,
            "module_paths": [module_path],
            "entry_points": [
                {
                    "name": LIBRARY_ENTRY_POINT_NAME,
                    "kind": LIBRARY_ENTRY_POINT_KIND,
                    "module": module_path,
                    "description": LIBRARY_ENTRY_POINT_DESCRIPTION,
                }
            ],
            "dependencies": [],
            "test_paths": [],
            "categories": [CATEGORY_LIBRARY],
            "created_by_task": task_id,
            "date_created": DATE_CREATED,
        },
    )
    _write_text(
        path=asset_dir / description_path,
        content=_frontmatter_markdown(
            key="library_id",
            value=library_id,
            body="## Summary\n\nLibrary summary.\n",
        ),
    )
    _write_text(
        path=_task_dir(repo_root=repo_root, task_id=task_id) / module_path,
        content=f"{task_id}:{module_path}\n",
    )


def _create_paper_asset(
    *,
    repo_root: Path,
    task_id: str,
    paper_id: str,
    summary_path: str = SUMMARY_FILE_NAME,
) -> None:
    asset_dir = _task_asset_dir(
        repo_root=repo_root,
        task_id=task_id,
        asset_kind=PAPER_SUBDIR,
        asset_id=paper_id,
    )
    _write_json(
        path=asset_dir / DETAILS_JSON_FILE,
        data={
            "spec_version": SPEC_VERSION_3,
            "paper_id": paper_id,
            "doi": None,
            "title": paper_id,
            "url": None,
            "pdf_url": None,
            "year": 2026,
            "authors": [],
            "institutions": [],
            "journal": "preprint",
            "venue_type": "preprint",
            "categories": [CATEGORY_INFRA],
            "abstract": "Abstract text with enough words to be treated as present.",
            "citation_key": "Test2026",
            "summary_path": summary_path,
            "files": [f"{FILES_SUBDIR}/{PAPER_FILE_NAME}"],
            "download_status": "success",
            "download_failure_reason": None,
            "added_by_task": task_id,
            "date_added": DATE_CREATED,
        },
    )
    _write_text(
        path=asset_dir / summary_path,
        content=_frontmatter_markdown(
            key="paper_id",
            value=paper_id,
            body="## Summary\n\nPaper summary.\n",
        ),
    )
    _write_text(
        path=asset_dir / FILES_SUBDIR / PAPER_FILE_NAME,
        content="pdf\n",
    )


def _create_correction(
    *,
    repo_root: Path,
    correcting_task: str,
    file_name: str,
    payload: dict[str, object],
) -> None:
    _write_json(
        path=_task_dir(repo_root=repo_root, task_id=correcting_task)
        / CORRECTIONS_SUBDIR
        / file_name,
        data=payload,
    )


def test_partial_answer_file_correction_updates_effective_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_ANSWER)
    _create_task(repo_root=tmp_path, task_id=TASK_FIX_ANSWER)
    _create_answer_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_ANSWER,
        answer_id=ANSWER_ID_REMOTE_MACHINES,
        confidence=CONFIDENCE_MEDIUM,
        short_answer=REMOTE_SHORT_ANSWER,
        full_answer=REMOTE_FULL_ANSWER_ORIGINAL,
        short_answer_path=CUSTOM_SHORT_ANSWER_PATH,
        full_answer_path=CUSTOM_FULL_ANSWER_PATH,
    )
    _create_answer_asset(
        repo_root=tmp_path,
        task_id=TASK_FIX_ANSWER,
        answer_id=ANSWER_ID_REMOTE_MACHINES_FIX,
        confidence=CONFIDENCE_HIGH,
        short_answer=REMOTE_SHORT_ANSWER,
        full_answer=REMOTE_FULL_ANSWER_CORRECTED,
        short_answer_path=CUSTOM_SHORT_ANSWER_PATH,
        full_answer_path=CUSTOM_FULL_ANSWER_PATH,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_FIX_ANSWER,
        file_name=ANSWER_CORRECTION_FILE_NAME,
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0002-01",
            "correcting_task": TASK_FIX_ANSWER,
            "target_task": TASK_BASE_ANSWER,
            "target_kind": TARGET_KIND_ANSWER,
            "target_id": ANSWER_ID_REMOTE_MACHINES,
            "action": ACTION_UPDATE,
            "changes": {"confidence": CONFIDENCE_HIGH},
            "file_changes": {
                CUSTOM_FULL_ANSWER_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FIX_ANSWER,
                    "replacement_id": ANSWER_ID_REMOTE_MACHINES_FIX,
                    "replacement_path": CUSTOM_FULL_ANSWER_PATH,
                }
            },
            "rationale": "Only the long answer needed correction.",
        },
    )

    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    resolution = resolve_target(
        original_key=TargetKey(
            task_id=TASK_BASE_ANSWER,
            target_kind=TARGET_KIND_ANSWER,
            target_id=ANSWER_ID_REMOTE_MACHINES,
        ),
        correction_index=correction_index,
    )
    record = load_effective_target_record(
        resolution=resolution,
        correction_index=correction_index,
    )

    assert record is not None
    assert record.payload["confidence"] == CONFIDENCE_HIGH
    short_answer_ref = find_resolved_file(
        record=record,
        logical_path=CUSTOM_SHORT_ANSWER_PATH,
    )
    full_answer_ref = find_resolved_file(
        record=record,
        logical_path=CUSTOM_FULL_ANSWER_PATH,
    )
    assert short_answer_ref is not None
    assert full_answer_ref is not None
    assert short_answer_ref.source_task == TASK_BASE_ANSWER
    assert full_answer_ref.source_task == TASK_FIX_ANSWER
    assert full_answer_ref.source_id == ANSWER_ID_REMOTE_MACHINES_FIX


def test_library_aggregator_uses_corrected_metadata_defined_description_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_LIBRARY)
    _create_task(repo_root=tmp_path, task_id=TASK_FIX_LIBRARY)
    _create_library_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_LIBRARY,
        library_id=LIBRARY_ID_LOADER,
        module_path=BASE_MODULE_PATH,
        description_path=CUSTOM_LIBRARY_DESCRIPTION_PATH,
        spec_version=SPEC_VERSION_2,
    )
    _create_library_asset(
        repo_root=tmp_path,
        task_id=TASK_FIX_LIBRARY,
        library_id=LIBRARY_ID_LOADER_PATCH,
        module_path=BASE_MODULE_PATH,
        description_path=CUSTOM_LIBRARY_DESCRIPTION_PATH,
        spec_version=SPEC_VERSION_2,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_FIX_LIBRARY,
        file_name=LIBRARY_CORRECTION_FILE_NAME,
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0002-01",
            "correcting_task": TASK_FIX_LIBRARY,
            "target_task": TASK_BASE_LIBRARY,
            "target_kind": TARGET_KIND_LIBRARY,
            "target_id": LIBRARY_ID_LOADER,
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                CUSTOM_LIBRARY_DESCRIPTION_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FIX_LIBRARY,
                    "replacement_id": LIBRARY_ID_LOADER_PATCH,
                    "replacement_path": CUSTOM_LIBRARY_DESCRIPTION_PATH,
                }
            },
            "rationale": "Replace the library guide with the corrected version.",
        },
    )

    libraries = aggregate_libraries_module.aggregate_libraries_full(
        include_full_description=False,
        filter_ids=[LIBRARY_ID_LOADER],
        filter_categories=None,
    )

    assert len(libraries) == 1
    assert (
        libraries[0].description_path == f"{TASKS_SUBDIR}/"
        f"{TASK_FIX_LIBRARY}/assets/library/{LIBRARY_ID_LOADER_PATCH}/"
        f"{CUSTOM_LIBRARY_DESCRIPTION_PATH}"
    )


def test_paper_file_correction_supports_metadata_defined_summary_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_ANSWER)
    _create_task(repo_root=tmp_path, task_id=TASK_FIX_ANSWER)
    _create_paper_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_ANSWER,
        paper_id="paper-a",
        summary_path=CUSTOM_PAPER_SUMMARY_PATH,
    )
    _create_paper_asset(
        repo_root=tmp_path,
        task_id=TASK_FIX_ANSWER,
        paper_id="paper-b",
        summary_path=CUSTOM_PAPER_SUMMARY_PATH,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_FIX_ANSWER,
        file_name="paper_paper-a.json",
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0002-02",
            "correcting_task": TASK_FIX_ANSWER,
            "target_task": TASK_BASE_ANSWER,
            "target_kind": TARGET_KIND_PAPER,
            "target_id": "paper-a",
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                CUSTOM_PAPER_SUMMARY_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FIX_ANSWER,
                    "replacement_id": "paper-b",
                    "replacement_path": CUSTOM_PAPER_SUMMARY_PATH,
                }
            },
            "rationale": "Replace the paper summary with the corrected one.",
        },
    )

    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    resolution = resolve_target(
        original_key=TargetKey(
            task_id=TASK_BASE_ANSWER,
            target_kind=TARGET_KIND_PAPER,
            target_id="paper-a",
        ),
        correction_index=correction_index,
    )
    record = load_effective_target_record(
        resolution=resolution,
        correction_index=correction_index,
    )

    assert record is not None
    summary_ref = find_resolved_file(
        record=record,
        logical_path=CUSTOM_PAPER_SUMMARY_PATH,
    )
    assert summary_ref is not None
    assert summary_ref.source_task == TASK_FIX_ANSWER
    assert summary_ref.source_id == "paper-b"


def test_transitive_model_file_replacement_uses_final_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_MODEL)
    _create_task(repo_root=tmp_path, task_id=TASK_MID_MODEL)
    _create_task(repo_root=tmp_path, task_id=TASK_FINAL_MODEL)
    _create_task(repo_root=tmp_path, task_id=TASK_CORRECT_MID_MODEL)
    _create_task(repo_root=tmp_path, task_id=TASK_CORRECT_BASE_MODEL)
    _create_model_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_MODEL,
        model_id=MODEL_ID_BASE,
        file_name=MODEL_FILE_NAME,
    )
    _create_model_asset(
        repo_root=tmp_path,
        task_id=TASK_MID_MODEL,
        model_id=MODEL_ID_MID,
        file_name=MODEL_FILE_NAME,
    )
    _create_model_asset(
        repo_root=tmp_path,
        task_id=TASK_FINAL_MODEL,
        model_id=MODEL_ID_FINAL,
        file_name=FINAL_MODEL_FILE_NAME,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_CORRECT_MID_MODEL,
        file_name="model_model-b.json",
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0004-01",
            "correcting_task": TASK_CORRECT_MID_MODEL,
            "target_task": TASK_MID_MODEL,
            "target_kind": TARGET_KIND_MODEL,
            "target_id": MODEL_ID_MID,
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                MODEL_FILE_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FINAL_MODEL,
                    "replacement_id": MODEL_ID_FINAL,
                    "replacement_path": FINAL_MODEL_FILE_PATH,
                }
            },
            "rationale": "The mid model should source the final weights file.",
        },
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_CORRECT_BASE_MODEL,
        file_name="model_model-a.json",
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0005-01",
            "correcting_task": TASK_CORRECT_BASE_MODEL,
            "target_task": TASK_BASE_MODEL,
            "target_kind": TARGET_KIND_MODEL,
            "target_id": MODEL_ID_BASE,
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                MODEL_FILE_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_MID_MODEL,
                    "replacement_id": MODEL_ID_MID,
                    "replacement_path": MODEL_FILE_PATH,
                }
            },
            "rationale": "The base model should follow the corrected mid model.",
        },
    )

    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    resolution = resolve_target(
        original_key=TargetKey(
            task_id=TASK_BASE_MODEL,
            target_kind=TARGET_KIND_MODEL,
            target_id=MODEL_ID_BASE,
        ),
        correction_index=correction_index,
    )
    record = load_effective_target_record(
        resolution=resolution,
        correction_index=correction_index,
    )

    assert record is not None
    file_ref = find_resolved_file(
        record=record,
        logical_path=MODEL_FILE_PATH,
    )
    assert file_ref is not None
    assert file_ref.source_task == TASK_FINAL_MODEL
    assert file_ref.source_id == MODEL_ID_FINAL
    assert file_ref.source_logical_path == FINAL_MODEL_FILE_PATH


def test_verify_corrections_reports_missing_replacement_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_ANSWER)
    _create_task(repo_root=tmp_path, task_id=TASK_FIX_ANSWER)
    _create_answer_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_ANSWER,
        answer_id=ANSWER_ID_REMOTE_MACHINES,
        confidence=CONFIDENCE_MEDIUM,
        short_answer=REMOTE_SHORT_ANSWER,
        full_answer=REMOTE_FULL_ANSWER_ORIGINAL,
    )
    _create_answer_asset(
        repo_root=tmp_path,
        task_id=TASK_FIX_ANSWER,
        answer_id=ANSWER_ID_REMOTE_MACHINES_FIX,
        confidence=CONFIDENCE_HIGH,
        short_answer=REMOTE_SHORT_ANSWER,
        full_answer=REMOTE_FULL_ANSWER_CORRECTED,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_FIX_ANSWER,
        file_name=ANSWER_CORRECTION_FILE_NAME,
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0002-01",
            "correcting_task": TASK_FIX_ANSWER,
            "target_task": TASK_BASE_ANSWER,
            "target_kind": TARGET_KIND_ANSWER,
            "target_id": ANSWER_ID_REMOTE_MACHINES,
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                FULL_ANSWER_FILE_NAME: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FIX_ANSWER,
                    "replacement_id": ANSWER_ID_REMOTE_MACHINES_FIX,
                    "replacement_path": MISSING_FILE_PATH,
                }
            },
            "rationale": "This replacement path is intentionally invalid.",
        },
    )

    result = verify_corrections_module.verify_corrections(
        task_id=TASK_FIX_ANSWER,
    )

    assert any(diagnostic.code.text == "CR-E018" for diagnostic in result.errors)


def test_library_aggregator_returns_effective_module_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _create_task(repo_root=tmp_path, task_id=TASK_BASE_LIBRARY)
    _create_task(repo_root=tmp_path, task_id=TASK_FIX_LIBRARY)
    _create_library_asset(
        repo_root=tmp_path,
        task_id=TASK_BASE_LIBRARY,
        library_id=LIBRARY_ID_LOADER,
        module_path=BASE_MODULE_PATH,
    )
    _create_library_asset(
        repo_root=tmp_path,
        task_id=TASK_FIX_LIBRARY,
        library_id=LIBRARY_ID_LOADER_PATCH,
        module_path=BASE_MODULE_PATH,
    )
    _create_correction(
        repo_root=tmp_path,
        correcting_task=TASK_FIX_LIBRARY,
        file_name=LIBRARY_CORRECTION_FILE_NAME,
        payload={
            "spec_version": SPEC_VERSION_3,
            "correction_id": "C-0002-01",
            "correcting_task": TASK_FIX_LIBRARY,
            "target_task": TASK_BASE_LIBRARY,
            "target_kind": TARGET_KIND_LIBRARY,
            "target_id": LIBRARY_ID_LOADER,
            "action": ACTION_UPDATE,
            "changes": None,
            "file_changes": {
                BASE_MODULE_PATH: {
                    "action": ACTION_REPLACE,
                    "replacement_task": TASK_FIX_LIBRARY,
                    "replacement_id": LIBRARY_ID_LOADER_PATCH,
                    "replacement_path": BASE_MODULE_PATH,
                }
            },
            "rationale": "Use the patched module implementation.",
        },
    )

    libraries = aggregate_libraries_module.aggregate_libraries_full(
        filter_ids=[LIBRARY_ID_LOADER],
    )

    assert len(libraries) == 1
    assert libraries[0].module_paths == [f"{TASKS_SUBDIR}/{TASK_FIX_LIBRARY}/{BASE_MODULE_PATH}"]
