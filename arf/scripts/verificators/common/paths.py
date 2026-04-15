from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[4]
TASKS_DIR: Path = REPO_ROOT / "tasks"
ASSETS_DIR: Path = REPO_ROOT / "assets"
ANSWER_ASSETS_DIR: Path = ASSETS_DIR / "answer"
PAPER_ASSETS_DIR: Path = ASSETS_DIR / "paper"
DATASET_ASSETS_DIR: Path = ASSETS_DIR / "dataset"
LIBRARY_ASSETS_DIR: Path = ASSETS_DIR / "library"
MODEL_ASSETS_DIR: Path = ASSETS_DIR / "model"
PREDICTIONS_ASSETS_DIR: Path = ASSETS_DIR / "predictions"
ASSET_TYPES_DIR: Path = REPO_ROOT / "meta" / "asset_types"
CATEGORIES_DIR: Path = REPO_ROOT / "meta" / "categories"
METRICS_DIR: Path = REPO_ROOT / "meta" / "metrics"
TASK_TYPES_DIR: Path = REPO_ROOT / "meta" / "task_types"
PROJECT_DIR: Path = REPO_ROOT / "project"
PROJECT_DESCRIPTION_PATH: Path = PROJECT_DIR / "description.md"
PROJECT_BUDGET_PATH: Path = PROJECT_DIR / "budget.json"
OVERVIEW_DIR: Path = REPO_ROOT / "overview"
NEWS_DIR: Path = REPO_ROOT / "news"


# ---------------------------------------------------------------------------
# Generic asset path helpers (used by the plugin architecture)
# ---------------------------------------------------------------------------


def asset_base_dir(*, task_id: str | None, asset_type: str) -> Path:
    """Return the base directory for an asset type, optionally scoped to a task."""
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / asset_type
    return ASSETS_DIR / asset_type


def asset_dir(*, asset_id: str, asset_type: str, task_id: str | None = None) -> Path:
    """Return the directory for a single asset instance."""
    return asset_base_dir(task_id=task_id, asset_type=asset_type) / asset_id


def asset_details_path(
    *,
    asset_id: str,
    asset_type: str,
    task_id: str | None = None,
) -> Path:
    """Return the ``details.json`` path for a single asset instance."""
    return asset_dir(asset_id=asset_id, asset_type=asset_type, task_id=task_id) / "details.json"


def asset_files_dir(
    *,
    asset_id: str,
    asset_type: str,
    task_id: str | None = None,
) -> Path:
    """Return the ``files/`` subdirectory for a single asset instance."""
    return asset_dir(asset_id=asset_id, asset_type=asset_type, task_id=task_id) / "files"


# ---------------------------------------------------------------------------
# Task-level paths
# ---------------------------------------------------------------------------


def research_internet_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "research" / "research_internet.md"


def research_papers_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "research" / "research_papers.md"


def research_code_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "research" / "research_code.md"


def paper_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "paper"
    return PAPER_ASSETS_DIR


def answer_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "answer"
    return ANSWER_ASSETS_DIR


def answer_asset_dir(*, answer_id: str, task_id: str | None = None) -> Path:
    return answer_base_dir(task_id=task_id) / answer_id


def answer_details_path(*, answer_id: str, task_id: str | None = None) -> Path:
    return answer_base_dir(task_id=task_id) / answer_id / "details.json"


def answer_short_answer_path(*, answer_id: str, task_id: str | None = None) -> Path:
    return answer_base_dir(task_id=task_id) / answer_id / "short_answer.md"


def answer_full_answer_path(*, answer_id: str, task_id: str | None = None) -> Path:
    return answer_base_dir(task_id=task_id) / answer_id / "full_answer.md"


def paper_asset_dir(*, paper_id: str, task_id: str | None = None) -> Path:
    return paper_base_dir(task_id=task_id) / paper_id


def paper_details_path(*, paper_id: str, task_id: str | None = None) -> Path:
    return paper_base_dir(task_id=task_id) / paper_id / "details.json"


def paper_summary_path(*, paper_id: str, task_id: str | None = None) -> Path:
    return paper_base_dir(task_id=task_id) / paper_id / "summary.md"


def paper_files_dir(*, paper_id: str, task_id: str | None = None) -> Path:
    return paper_base_dir(task_id=task_id) / paper_id / "files"


def dataset_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "dataset"
    return DATASET_ASSETS_DIR


def dataset_asset_dir(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> Path:
    return dataset_base_dir(task_id=task_id) / dataset_id


def dataset_details_path(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> Path:
    return dataset_base_dir(task_id=task_id) / dataset_id / "details.json"


def dataset_description_path(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> Path:
    return dataset_base_dir(task_id=task_id) / dataset_id / "description.md"


def dataset_files_dir(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> Path:
    return dataset_base_dir(task_id=task_id) / dataset_id / "files"


def library_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "library"
    return LIBRARY_ASSETS_DIR


def library_asset_dir(
    *,
    library_id: str,
    task_id: str | None = None,
) -> Path:
    return library_base_dir(task_id=task_id) / library_id


def library_details_path(
    *,
    library_id: str,
    task_id: str | None = None,
) -> Path:
    return library_base_dir(task_id=task_id) / library_id / "details.json"


def library_description_path(
    *,
    library_id: str,
    task_id: str | None = None,
) -> Path:
    return library_base_dir(task_id=task_id) / library_id / "description.md"


def model_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "model"
    return MODEL_ASSETS_DIR


def model_asset_dir(
    *,
    model_id: str,
    task_id: str | None = None,
) -> Path:
    return model_base_dir(task_id=task_id) / model_id


def model_details_path(
    *,
    model_id: str,
    task_id: str | None = None,
) -> Path:
    return model_base_dir(task_id=task_id) / model_id / "details.json"


def model_description_path(
    *,
    model_id: str,
    task_id: str | None = None,
) -> Path:
    return model_base_dir(task_id=task_id) / model_id / "description.md"


def model_files_dir(
    *,
    model_id: str,
    task_id: str | None = None,
) -> Path:
    return model_base_dir(task_id=task_id) / model_id / "files"


def predictions_base_dir(*, task_id: str | None) -> Path:
    if task_id is not None:
        return TASKS_DIR / task_id / "assets" / "predictions"
    return PREDICTIONS_ASSETS_DIR


def predictions_asset_dir(
    *,
    predictions_id: str,
    task_id: str | None = None,
) -> Path:
    return predictions_base_dir(task_id=task_id) / predictions_id


def predictions_details_path(
    *,
    predictions_id: str,
    task_id: str | None = None,
) -> Path:
    return predictions_base_dir(task_id=task_id) / predictions_id / "details.json"


def predictions_description_path(
    *,
    predictions_id: str,
    task_id: str | None = None,
) -> Path:
    return predictions_base_dir(task_id=task_id) / predictions_id / "description.md"


def predictions_files_dir(
    *,
    predictions_id: str,
    task_id: str | None = None,
) -> Path:
    return predictions_base_dir(task_id=task_id) / predictions_id / "files"


def category_description_path(*, category_slug: str) -> Path:
    return CATEGORIES_DIR / category_slug / "description.json"


def logs_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "logs"


def command_logs_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "logs" / "commands"


def step_logs_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "logs" / "steps"


def search_logs_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "logs" / "searches"


def session_logs_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "logs" / "sessions"


def session_capture_report_path(*, task_id: str) -> Path:
    return session_logs_dir(task_id=task_id) / "capture_report.json"


def step_tracker_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "step_tracker.json"


def task_json_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "task.json"


def suggestions_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "suggestions.json"


def corrections_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "corrections"


def results_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results"


def results_summary_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "results_summary.md"


def results_detailed_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "results_detailed.md"


def metrics_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "metrics.json"


def costs_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "costs.json"


def remote_machines_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "remote_machines_used.json"


def results_images_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "images"


def compare_literature_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "results" / "compare_literature.md"


def task_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id


def plan_path(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "plan" / "plan.md"


def intervention_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "intervention"


def assets_dir(*, task_id: str) -> Path:
    return TASKS_DIR / task_id / "assets"


def step_folder_path(
    *,
    task_id: str,
    step_order: int,
    step_id: str,
) -> Path:
    folder_name: str = f"{step_order:03d}_{step_id}"
    return TASKS_DIR / task_id / "logs" / "steps" / folder_name


def metric_definition_path(*, metric_key: str) -> Path:
    return METRICS_DIR / metric_key / "description.json"


def task_type_description_path(*, task_type_slug: str) -> Path:
    return TASK_TYPES_DIR / task_type_slug / "description.json"


def task_type_instruction_path(*, task_type_slug: str) -> Path:
    return TASK_TYPES_DIR / task_type_slug / "instruction.md"


def news_md_path(*, date: str) -> Path:
    return NEWS_DIR / f"{date}.md"


def news_json_path(*, date: str) -> Path:
    return NEWS_DIR / f"{date}.json"
