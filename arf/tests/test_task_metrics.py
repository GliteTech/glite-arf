import json
from pathlib import Path

import pytest

import arf.scripts.verificators.verify_task_metrics as verify_task_metrics_module
from arf.scripts.common.task_metrics import (
    EXPLICIT_VARIANTS_FORMAT_KIND,
    IMPLICIT_VARIANT_ID,
    LEGACY_FORMAT_KIND,
    normalize_task_metrics_data,
)
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult

TASKS_SUBDIR: str = "tasks"
TASK_ID: str = "t0001_variant_metrics"


def _configure_repo_paths(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
) -> Path:
    tasks_dir = repo_root / TASKS_SUBDIR
    tasks_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(paths, "REPO_ROOT", repo_root)
    monkeypatch.setattr(paths, "TASKS_DIR", tasks_dir)
    monkeypatch.setattr(verify_task_metrics_module, "TASKS_DIR", tasks_dir)
    return tasks_dir


def _write_metrics_file(
    *,
    tasks_dir: Path,
    payload: dict[str, object],
) -> None:
    metrics_file: Path = tasks_dir / TASK_ID / "results" / "metrics.json"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _patch_registered_metric_keys(
    *,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        verify_task_metrics_module,
        "collect_registered_metric_keys",
        lambda: {
            "accuracy_all",
            "efficiency_inference_cost_per_item_usd",
            "f1_all",
            "f1_se2",
        },
    )


def _diagnostic_codes(result: VerificationResult) -> list[str]:
    return [diagnostic.code.text for diagnostic in result.diagnostics]


def test_normalize_task_metrics_data_legacy_format() -> None:
    normalized = normalize_task_metrics_data(
        data={
            "f1_all": 63.97,
            "f1_se2": 65.91,
        },
    )

    assert normalized.format_kind == LEGACY_FORMAT_KIND
    assert len(normalized.variants) == 1

    variant = normalized.variants[0]
    assert variant.variant_id == IMPLICIT_VARIANT_ID
    assert variant.label is None
    assert variant.dimensions == {}
    assert variant.metrics == {
        "f1_all": 63.97,
        "f1_se2": 65.91,
    }
    assert variant.is_implicit is True


def test_normalize_task_metrics_data_empty_legacy_format() -> None:
    normalized = normalize_task_metrics_data(data={})

    assert normalized.format_kind == LEGACY_FORMAT_KIND
    assert len(normalized.variants) == 1

    variant = normalized.variants[0]
    assert variant.variant_id == IMPLICIT_VARIANT_ID
    assert variant.label is None
    assert variant.dimensions == {}
    assert variant.metrics == {}
    assert variant.is_implicit is True


def test_normalize_task_metrics_data_explicit_variants() -> None:
    normalized = normalize_task_metrics_data(
        data={
            "variants": [
                {
                    "variant_id": "gpt-5.4_glosses-pos",
                    "label": "gpt-5.4 + glosses_pos",
                    "dimensions": {
                        "model": "gpt-5.4",
                        "prompt": "glosses_pos",
                    },
                    "metrics": {
                        "f1_all": 63.97,
                    },
                },
            ],
        },
    )

    assert normalized.format_kind == EXPLICIT_VARIANTS_FORMAT_KIND
    assert len(normalized.variants) == 1

    variant = normalized.variants[0]
    assert variant.variant_id == "gpt-5.4_glosses-pos"
    assert variant.label == "gpt-5.4 + glosses_pos"
    assert variant.dimensions == {
        "model": "gpt-5.4",
        "prompt": "glosses_pos",
    }
    assert variant.metrics == {
        "f1_all": 63.97,
    }
    assert variant.is_implicit is False


def test_verify_task_metrics_accepts_legacy_flat_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "f1_all": 63.97,
            "f1_se2": 65.91,
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is True
    assert result.diagnostics == []


def test_verify_task_metrics_accepts_explicit_variant_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "variants": [
                {
                    "variant_id": "gpt-5.4_glosses-pos",
                    "label": "gpt-5.4 + glosses_pos",
                    "dimensions": {
                        "model": "gpt-5.4",
                        "prompt": "glosses_pos",
                    },
                    "metrics": {
                        "f1_all": 63.97,
                        "f1_se2": 65.91,
                    },
                },
                {
                    "variant_id": "gpt-5.4_cot-glosses",
                    "label": "gpt-5.4 + cot_glosses",
                    "dimensions": {
                        "model": "gpt-5.4",
                        "prompt": "cot_glosses",
                    },
                    "metrics": {
                        "f1_all": 63.82,
                        "f1_se2": 65.10,
                    },
                },
            ],
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is True
    assert result.diagnostics == []


def test_verify_task_metrics_rejects_duplicate_variant_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "variants": [
                {
                    "variant_id": "same-id",
                    "label": "First",
                    "dimensions": {},
                    "metrics": {
                        "f1_all": 63.97,
                    },
                },
                {
                    "variant_id": "same-id",
                    "label": "Second",
                    "dimensions": {},
                    "metrics": {
                        "f1_all": 63.82,
                    },
                },
            ],
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is False
    assert "TM-E003" in _diagnostic_codes(result)


def test_verify_task_metrics_rejects_empty_explicit_variants_list(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "variants": [],
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is False
    assert "TM-E003" in _diagnostic_codes(result)


def test_verify_task_metrics_rejects_nested_variant_dimension_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "variants": [
                {
                    "variant_id": "prompt-a",
                    "label": "Prompt A",
                    "dimensions": {
                        "prompt": {
                            "name": "A",
                        },
                    },
                    "metrics": {
                        "f1_all": 63.97,
                    },
                },
            ],
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is False
    assert "TM-E004" in _diagnostic_codes(result)


def test_verify_task_metrics_rejects_unregistered_variant_metric_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    _patch_registered_metric_keys(monkeypatch=monkeypatch)
    _write_metrics_file(
        tasks_dir=tasks_dir,
        payload={
            "variants": [
                {
                    "variant_id": "prompt-a",
                    "label": "Prompt A",
                    "dimensions": {
                        "prompt": "A",
                    },
                    "metrics": {
                        "unknown_metric": 1.0,
                    },
                },
            ],
        },
    )

    result = verify_task_metrics_module.verify_task_metrics(task_id=TASK_ID)

    assert result.passed is False
    assert "TM-E005" in _diagnostic_codes(result)
