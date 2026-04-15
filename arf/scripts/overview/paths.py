"""Shared filesystem and relative path constants for overview materialization."""

from pathlib import Path

from arf.scripts.verificators.common.paths import OVERVIEW_DIR as BASE_OVERVIEW_DIR
from arf.scripts.verificators.common.paths import REPO_ROOT as BASE_REPO_ROOT

type SectionName = str
type ViewName = str
type TaskID = str

REPO_ROOT: Path = BASE_REPO_ROOT
OVERVIEW_DIR: Path = BASE_OVERVIEW_DIR

README_FILE_NAME: str = "README.md"
MARKDOWN_FILE_SUFFIX: str = ".md"
RESULTS_DETAILED_FILE_NAME: str = "results_detailed.md"
TASKS_SEGMENT: str = "tasks"
RESULTS_SEGMENT: str = "results"
PROJECT_SEGMENT: str = "project"
RESEARCH_SEGMENT: str = "research"
PROJECT_DESCRIPTION_REPO_PATH: Path = Path(PROJECT_SEGMENT) / "description.md"

DASHBOARD_README: Path = OVERVIEW_DIR / README_FILE_NAME
BY_CATEGORY_DIR: Path = OVERVIEW_DIR / "by-category"
LLM_CONTEXT_DIR: Path = OVERVIEW_DIR / "llm-context"
LLM_CONTEXT_README: Path = LLM_CONTEXT_DIR / README_FILE_NAME

ANSWERS_DIR: Path = OVERVIEW_DIR / "answers"
ANSWERS_README: Path = ANSWERS_DIR / README_FILE_NAME
ANSWERS_BY_CATEGORY_DIR: Path = ANSWERS_DIR / "by-category"
ANSWERS_BY_DATE_DIR: Path = ANSWERS_DIR / "by-date-added"
ANSWERS_BY_DATE_README: Path = ANSWERS_BY_DATE_DIR / README_FILE_NAME

PAPERS_DIR: Path = OVERVIEW_DIR / "papers"
PAPERS_README: Path = PAPERS_DIR / README_FILE_NAME
PAPERS_BY_CATEGORY_DIR: Path = PAPERS_DIR / "by-category"

OVERVIEW_REL: Path = Path("..")
SUBPAGE_REL: Path = OVERVIEW_REL / ".."
CATEGORY_PAGE_REL: Path = SUBPAGE_REL / ".."
DATE_PAGE_REL: Path = CATEGORY_PAGE_REL


def overview_section_dir(*, section_name: SectionName) -> Path:
    return OVERVIEW_DIR / section_name


def overview_section_readme(*, section_name: SectionName) -> Path:
    return overview_section_dir(section_name=section_name) / README_FILE_NAME


def overview_legacy_markdown_path(*, section_name: SectionName) -> Path:
    return OVERVIEW_DIR / f"{section_name}{MARKDOWN_FILE_SUFFIX}"


def overview_section_view_dir(*, section_name: SectionName, view_name: ViewName) -> Path:
    return overview_section_dir(section_name=section_name) / view_name


def overview_section_view_readme(*, section_name: SectionName, view_name: ViewName) -> Path:
    return (
        overview_section_view_dir(
            section_name=section_name,
            view_name=view_name,
        )
        / README_FILE_NAME
    )


def overview_repo_task_path(*, task_id: TaskID) -> Path:
    return REPO_ROOT / TASKS_SEGMENT / task_id


def results_detailed_path(*, task_id: TaskID) -> Path:
    return overview_repo_task_path(task_id=task_id) / RESULTS_SEGMENT / RESULTS_DETAILED_FILE_NAME


def results_detailed_repo_path(*, task_id: TaskID) -> Path:
    return Path(TASKS_SEGMENT) / task_id / RESULTS_SEGMENT / RESULTS_DETAILED_FILE_NAME


def task_research_repo_path(*, task_id: TaskID, file_name: str) -> Path:
    return Path(TASKS_SEGMENT) / task_id / RESEARCH_SEGMENT / file_name


def markdown_rel_prefix(*, relative_path: Path) -> str:
    return f"{relative_path.as_posix().rstrip('/')}/"
