import types
from pathlib import Path

import pytest

from arf.scripts.verificators.common import paths

TASKS_SUBDIR: str = "tasks"
ASSETS_SUBDIR: str = "assets"
META_SUBDIR: str = "meta"
PROJECT_SUBDIR: str = "project"
OVERVIEW_SUBDIR: str = "overview"
NEWS_SUBDIR: str = "news"


def configure_repo_paths(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
    verificator_modules: list[types.ModuleType] | None = None,
    aggregator_modules: list[types.ModuleType] | None = None,
) -> Path:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    assets_dir: Path = repo_root / ASSETS_SUBDIR
    answer_assets_dir: Path = assets_dir / "answer"
    paper_assets_dir: Path = assets_dir / "paper"
    dataset_assets_dir: Path = assets_dir / "dataset"
    library_assets_dir: Path = assets_dir / "library"
    model_assets_dir: Path = assets_dir / "model"
    predictions_assets_dir: Path = assets_dir / "predictions"
    categories_dir: Path = repo_root / META_SUBDIR / "categories"
    metrics_dir: Path = repo_root / META_SUBDIR / "metrics"
    task_types_dir: Path = repo_root / META_SUBDIR / "task_types"
    project_dir: Path = repo_root / PROJECT_SUBDIR
    overview_dir: Path = repo_root / OVERVIEW_SUBDIR
    news_dir: Path = repo_root / NEWS_SUBDIR

    all_dirs: list[Path] = [
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
        project_dir,
        overview_dir,
        news_dir,
    ]
    for directory in all_dirs:
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
    monkeypatch.setattr(paths, "PROJECT_DIR", project_dir)
    monkeypatch.setattr(
        paths,
        "PROJECT_DESCRIPTION_PATH",
        project_dir / "description.md",
    )
    monkeypatch.setattr(paths, "PROJECT_BUDGET_PATH", project_dir / "budget.json")
    monkeypatch.setattr(paths, "OVERVIEW_DIR", overview_dir)
    monkeypatch.setattr(paths, "NEWS_DIR", news_dir)

    extra_modules: list[types.ModuleType] = []
    if verificator_modules is not None:
        extra_modules.extend(verificator_modules)
    if aggregator_modules is not None:
        extra_modules.extend(aggregator_modules)

    for module in extra_modules:
        if hasattr(module, "REPO_ROOT"):
            monkeypatch.setattr(module, "REPO_ROOT", repo_root)
        if hasattr(module, "TASKS_DIR"):
            monkeypatch.setattr(module, "TASKS_DIR", tasks_dir)
        if hasattr(module, "ASSETS_DIR"):
            monkeypatch.setattr(module, "ASSETS_DIR", assets_dir)
        if hasattr(module, "CATEGORIES_DIR"):
            monkeypatch.setattr(module, "CATEGORIES_DIR", categories_dir)
        if hasattr(module, "METRICS_DIR"):
            monkeypatch.setattr(module, "METRICS_DIR", metrics_dir)
        if hasattr(module, "TASK_TYPES_DIR"):
            monkeypatch.setattr(module, "TASK_TYPES_DIR", task_types_dir)
        if hasattr(module, "PROJECT_DIR"):
            monkeypatch.setattr(module, "PROJECT_DIR", project_dir)
        if hasattr(module, "PROJECT_DESCRIPTION_PATH"):
            monkeypatch.setattr(
                module,
                "PROJECT_DESCRIPTION_PATH",
                project_dir / "description.md",
            )
        if hasattr(module, "PROJECT_BUDGET_PATH"):
            monkeypatch.setattr(
                module,
                "PROJECT_BUDGET_PATH",
                project_dir / "budget.json",
            )
        if hasattr(module, "OVERVIEW_DIR"):
            monkeypatch.setattr(module, "OVERVIEW_DIR", overview_dir)
        if hasattr(module, "NEWS_DIR"):
            monkeypatch.setattr(module, "NEWS_DIR", news_dir)
        for asset_kind in [
            "ANSWER",
            "PAPER",
            "DATASET",
            "LIBRARY",
            "MODEL",
            "PREDICTIONS",
        ]:
            attr_name: str = f"{asset_kind}_ASSETS_DIR"
            if hasattr(module, attr_name):
                monkeypatch.setattr(module, attr_name, assets_dir / asset_kind.lower())

    return tasks_dir
