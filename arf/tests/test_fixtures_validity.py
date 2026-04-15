"""Meta-tests: every fixture builder's defaults must pass its verificator.

If a builder produces data that fails verification, happy-path tests in
individual verificator test files will fail for the wrong reason (builder
bug, not verificator bug). This file catches that explicitly.
"""

from pathlib import Path

import pytest

import arf.scripts.common.artifacts as artifacts_module
import arf.scripts.common.corrections as corrections_module
import arf.scripts.common.task_description as task_description_module
import arf.scripts.verificators.verify_categories as verify_categories_mod
import arf.scripts.verificators.verify_corrections as verify_corrections_mod
import arf.scripts.verificators.verify_logs as verify_logs_mod
import arf.scripts.verificators.verify_metrics as verify_metrics_mod
import arf.scripts.verificators.verify_plan as verify_plan_mod
import arf.scripts.verificators.verify_project_budget as verify_project_budget_mod
import arf.scripts.verificators.verify_project_description as verify_proj_desc_mod
import arf.scripts.verificators.verify_research_code as verify_research_code_mod
import arf.scripts.verificators.verify_research_internet as verify_research_inet_mod
import arf.scripts.verificators.verify_research_papers as verify_research_papers_mod
import arf.scripts.verificators.verify_suggestions as verify_suggestions_mod
import arf.scripts.verificators.verify_task_file as verify_task_file_mod
import arf.scripts.verificators.verify_task_folder as verify_task_folder_mod
import arf.scripts.verificators.verify_task_results as verify_task_results_mod
import arf.scripts.verificators.verify_task_types as verify_task_types_mod
import arf.tests.fixtures.asset_builders.library as library_builder_mod
import meta.asset_types.answer.verificator as verify_answer_mod
import meta.asset_types.answer.verify_details as verify_answer_details_mod
import meta.asset_types.answer.verify_full as verify_answer_full_mod
import meta.asset_types.answer.verify_short as verify_answer_short_mod
import meta.asset_types.dataset.verificator as verify_dataset_mod
import meta.asset_types.dataset.verify_details as verify_dataset_details_mod
import meta.asset_types.library.verificator as verify_library_mod
import meta.asset_types.library.verify_details as verify_library_details_mod
import meta.asset_types.model.verificator as verify_model_mod
import meta.asset_types.model.verify_details as verify_model_details_mod
import meta.asset_types.paper.verificator as verify_paper_mod
import meta.asset_types.paper.verify_details as verify_paper_details_mod
import meta.asset_types.paper.verify_summary as verify_paper_summary_mod
import meta.asset_types.predictions.verificator as verify_predictions_mod
import meta.asset_types.predictions.verify_details as verify_pred_det_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.answer import (
    DEFAULT_ANSWER_ID as ANSWER_ID,
)
from arf.tests.fixtures.asset_builders.answer import (
    DEFAULT_TASK_ID as ANSWER_TASK_ID,
)
from arf.tests.fixtures.asset_builders.answer import (
    build_answer_asset,
)
from arf.tests.fixtures.asset_builders.dataset import (
    DEFAULT_DATASET_ID as DATASET_ID,
)
from arf.tests.fixtures.asset_builders.dataset import (
    DEFAULT_TASK_ID as DATASET_TASK_ID,
)
from arf.tests.fixtures.asset_builders.dataset import (
    build_dataset_asset,
)
from arf.tests.fixtures.asset_builders.library import (
    DEFAULT_LIBRARY_ID as LIBRARY_ID,
)
from arf.tests.fixtures.asset_builders.library import (
    DEFAULT_TASK_ID as LIBRARY_TASK_ID,
)
from arf.tests.fixtures.asset_builders.library import (
    build_library_asset,
)
from arf.tests.fixtures.asset_builders.model import (
    DEFAULT_MODEL_ID as MODEL_ID,
)
from arf.tests.fixtures.asset_builders.model import (
    DEFAULT_TASK_ID as MODEL_TASK_ID,
)
from arf.tests.fixtures.asset_builders.model import (
    build_model_asset,
)
from arf.tests.fixtures.asset_builders.paper import (
    DEFAULT_PAPER_ID as PAPER_ID,
)
from arf.tests.fixtures.asset_builders.paper import (
    DEFAULT_TASK_ID as PAPER_TASK_ID,
)
from arf.tests.fixtures.asset_builders.paper import (
    build_paper_asset,
)
from arf.tests.fixtures.asset_builders.predictions import (
    DEFAULT_PREDICTIONS_ID as PREDICTIONS_ID,
)
from arf.tests.fixtures.asset_builders.predictions import (
    DEFAULT_TASK_ID as PREDICTIONS_TASK_ID,
)
from arf.tests.fixtures.asset_builders.predictions import (
    build_predictions_asset,
)
from arf.tests.fixtures.correction_builder import build_correction
from arf.tests.fixtures.log_builders import (
    build_command_log,
    build_step_log,
)
from arf.tests.fixtures.metadata_builders import (
    build_category,
    build_metric,
    build_task_type,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.plan_builder import build_plan
from arf.tests.fixtures.project_builder import (
    build_project_budget,
    build_project_description,
)
from arf.tests.fixtures.research_builders import (
    build_research_code,
    build_research_internet,
    build_research_papers,
)
from arf.tests.fixtures.results_builders import (
    build_costs_file,
    build_metrics_file,
    build_remote_machines_file,
    build_results_detailed,
    build_results_images_dir,
    build_results_summary,
)
from arf.tests.fixtures.suggestion_builder import (
    build_suggestion,
    build_suggestions_file,
)
from arf.tests.fixtures.task_builder import (
    build_complete_task,
    build_step_tracker,
    build_task_folder,
    build_task_json,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1
CATEGORY_SLUG: str = "test-category"
METRIC_KEY: str = "test_metric"
TASK_TYPE_SLUG: str = "test-task-type"

CORRECTING_TASK: str = "t0002_fixup"
CORRECTING_INDEX: int = 2
TARGET_TASK: str = "t0001_original"
TARGET_INDEX: int = 1
SUGGESTION_ID: str = "S-0001-01"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _diagnostic_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


# ---------------------------------------------------------------------------
# Task structure: build_complete_task -> verify_task_file
# ---------------------------------------------------------------------------


def test_build_complete_task_passes_verify_task_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_task_file_mod,
            task_description_module,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_task_file_mod.verify_task_file(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Task structure: build_complete_task -> verify_task_folder
# (in_progress status avoids requiring all completed-task files)
# ---------------------------------------------------------------------------


def test_build_complete_task_passes_verify_task_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_task_folder_mod,
            task_description_module,
        ],
    )
    build_complete_task(
        repo_root=tmp_path,
        task_id=TASK_ID,
        status="in_progress",
    )
    result: VerificationResult = verify_task_folder_mod.verify_task_folder(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Suggestions: build_suggestions_file -> verify_suggestions
# ---------------------------------------------------------------------------


def test_build_suggestions_file_passes_verify_suggestions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_suggestions_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
    )
    build_category(
        repo_root=tmp_path,
        category_slug=CATEGORY_SLUG,
    )
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[build_suggestion()],
    )
    result: VerificationResult = verify_suggestions_mod.verify_suggestions(task_id=TASK_ID)
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Plan: build_plan -> verify_plan
# ---------------------------------------------------------------------------


def test_build_plan_passes_verify_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_plan_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_plan(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_plan_mod.verify_plan(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Research: build_research_* -> verify_research_*
# ---------------------------------------------------------------------------


def test_build_research_papers_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_research_papers_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_research_papers(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_research_papers_mod.verify_research_papers(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


def test_build_research_internet_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_research_inet_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_research_internet(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_research_inet_mod.verify_research_internet(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


def test_build_research_code_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_research_code_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_research_code(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_research_code_mod.verify_research_code(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Results: build_results_* -> verify_task_results
# ---------------------------------------------------------------------------


def test_build_results_passes_verify_task_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_task_results_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
    )
    build_results_summary(repo_root=tmp_path, task_id=TASK_ID)
    build_results_detailed(repo_root=tmp_path, task_id=TASK_ID)
    build_metrics_file(repo_root=tmp_path, task_id=TASK_ID)
    build_costs_file(repo_root=tmp_path, task_id=TASK_ID)
    build_remote_machines_file(repo_root=tmp_path, task_id=TASK_ID)
    build_results_images_dir(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = verify_task_results_mod.verify_task_results(task_id=TASK_ID)
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Categories: build_category -> verify_category
# ---------------------------------------------------------------------------


def test_build_category_passes_verify_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_categories_mod],
    )
    build_category(repo_root=tmp_path, category_slug=CATEGORY_SLUG)
    result: VerificationResult = verify_categories_mod.verify_category(
        category_slug=CATEGORY_SLUG,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Metrics: build_metric -> verify_metric
# ---------------------------------------------------------------------------


def test_build_metric_passes_verify_metric(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_metrics_mod],
    )
    build_metric(repo_root=tmp_path, metric_key=METRIC_KEY)
    result: VerificationResult = verify_metrics_mod.verify_metric(
        metric_key=METRIC_KEY,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Task types: build_task_type -> verify_task_type
# ---------------------------------------------------------------------------


def test_build_task_type_passes_verify_task_type(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_task_types_mod],
    )
    build_task_type(repo_root=tmp_path, task_type_slug=TASK_TYPE_SLUG)
    result: VerificationResult = verify_task_types_mod.verify_task_type(
        task_type_slug=TASK_TYPE_SLUG,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Project: build_project_description -> verify_project_description
# ---------------------------------------------------------------------------


def test_build_project_description_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_proj_desc_mod],
    )
    build_project_description(repo_root=tmp_path)
    result: VerificationResult = verify_proj_desc_mod.verify_project_description()
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Project: build_project_budget -> verify_project_budget
# ---------------------------------------------------------------------------


def test_build_project_budget_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_project_budget_mod],
    )
    build_project_budget(repo_root=tmp_path)
    result: VerificationResult = verify_project_budget_mod.verify_project_budget()
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Paper asset: build_paper_asset -> verify_paper_asset
# ---------------------------------------------------------------------------


def test_build_paper_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_paper_mod,
            verify_paper_details_mod,
            verify_paper_summary_mod,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=PAPER_TASK_ID)
    build_paper_asset(repo_root=tmp_path)
    result: VerificationResult = verify_paper_mod.verify_paper_asset(
        paper_id=PAPER_ID,
        task_id=PAPER_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Answer asset: build_answer_asset -> verify_answer_asset
# ---------------------------------------------------------------------------


def test_build_answer_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_answer_mod,
            verify_answer_details_mod,
            verify_answer_short_mod,
            verify_answer_full_mod,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=ANSWER_TASK_ID)
    build_answer_asset(repo_root=tmp_path)
    result: VerificationResult = verify_answer_mod.verify_answer_asset(
        answer_id=ANSWER_ID,
        task_id=ANSWER_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Dataset asset: build_dataset_asset -> verify_dataset_asset
# ---------------------------------------------------------------------------


def test_build_dataset_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_dataset_mod,
            verify_dataset_details_mod,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=DATASET_TASK_ID)
    build_dataset_asset(repo_root=tmp_path)
    result: VerificationResult = verify_dataset_mod.verify_dataset_asset(
        dataset_id=DATASET_ID,
        task_id=DATASET_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Library asset: build_library_asset -> verify_library_asset
# ---------------------------------------------------------------------------


def test_build_library_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_library_mod,
            verify_library_details_mod,
            library_builder_mod,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=LIBRARY_TASK_ID)
    build_library_asset(repo_root=tmp_path)
    result: VerificationResult = verify_library_mod.verify_library_asset(
        library_id=LIBRARY_ID,
        task_id=LIBRARY_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Model asset: build_model_asset -> verify_model_asset
# ---------------------------------------------------------------------------


def test_build_model_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_model_mod,
            verify_model_details_mod,
        ],
    )
    build_complete_task(repo_root=tmp_path, task_id=MODEL_TASK_ID)
    build_model_asset(repo_root=tmp_path)
    result: VerificationResult = verify_model_mod.verify_model_asset(
        model_id=MODEL_ID,
        task_id=MODEL_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Predictions asset: build_predictions_asset -> verify_predictions_asset
# ---------------------------------------------------------------------------


def test_build_predictions_asset_passes_verify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_predictions_mod,
            verify_pred_det_mod,
        ],
    )
    build_complete_task(
        repo_root=tmp_path,
        task_id=PREDICTIONS_TASK_ID,
    )
    build_predictions_asset(repo_root=tmp_path)
    result: VerificationResult = verify_predictions_mod.verify_predictions_asset(
        predictions_id=PREDICTIONS_ID,
        task_id=PREDICTIONS_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Logs: build_command_log + build_step_log -> verify_logs
# ---------------------------------------------------------------------------


def test_build_logs_passes_verify_logs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[verify_logs_mod],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_step_tracker(
        repo_root=tmp_path,
        task_id=TASK_ID,
        steps=[
            {
                "step": 4,
                "status": "completed",
                "log_file": "step_log.md",
            },
        ],
    )
    build_command_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        log_index=1,
    )
    build_step_log(
        repo_root=tmp_path,
        task_id=TASK_ID,
        step_order=4,
        step_id="research-papers",
    )
    result: VerificationResult = verify_logs_mod.verify_logs(
        task_id=TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Corrections: build_correction -> verify_corrections
#
# ---------------------------------------------------------------------------


def test_build_correction_passes_verify_corrections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=[
            verify_corrections_mod,
            artifacts_module,
            corrections_module,
        ],
    )
    # Set up the target task with a suggestion to correct.
    build_task_folder(repo_root=tmp_path, task_id=TARGET_TASK)
    build_task_json(
        repo_root=tmp_path,
        task_id=TARGET_TASK,
        task_index=TARGET_INDEX,
        status="completed",
    )
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TARGET_TASK,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_ID,
                source_task=TARGET_TASK,
            ),
        ],
    )
    # Set up the correcting task and write the correction.
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    build_task_json(
        repo_root=tmp_path,
        task_id=CORRECTING_TASK,
        task_index=CORRECTING_INDEX,
    )
    build_correction(
        repo_root=tmp_path,
        correcting_task=CORRECTING_TASK,
        file_name="suggestion_S-0001-01",
        correction_id="C-0002-01",
        target_task=TARGET_TASK,
        target_kind="suggestion",
        target_id=SUGGESTION_ID,
        action="update",
        changes={"priority": "high"},
        rationale="New evidence supports higher priority.",
    )
    result: VerificationResult = verify_corrections_mod.verify_corrections(
        task_id=CORRECTING_TASK,
    )
    assert result.passed is True, _diagnostic_codes(result)
