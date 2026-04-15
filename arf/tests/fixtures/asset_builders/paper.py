from pathlib import Path

from arf.scripts.verificators.common.paths import (
    paper_asset_dir,
    paper_details_path,
    paper_files_dir,
    paper_summary_path,
)
from arf.tests.fixtures.writers import (
    write_frontmatter_md,
    write_json,
    write_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION_FIELD: str = "spec_version"
PAPER_ID_FIELD: str = "paper_id"
DOI_FIELD: str = "doi"
TITLE_FIELD: str = "title"
URL_FIELD: str = "url"
PDF_URL_FIELD: str = "pdf_url"
DATE_PUBLISHED_FIELD: str = "date_published"
YEAR_FIELD: str = "year"
AUTHORS_FIELD: str = "authors"
INSTITUTIONS_FIELD: str = "institutions"
JOURNAL_FIELD: str = "journal"
VENUE_TYPE_FIELD: str = "venue_type"
CATEGORIES_FIELD: str = "categories"
ABSTRACT_FIELD: str = "abstract"
CITATION_KEY_FIELD: str = "citation_key"
SUMMARY_PATH_FIELD: str = "summary_path"
FILES_FIELD: str = "files"
DOWNLOAD_STATUS_FIELD: str = "download_status"
DOWNLOAD_FAILURE_REASON_FIELD: str = "download_failure_reason"
ADDED_BY_TASK_FIELD: str = "added_by_task"
DATE_ADDED_FIELD: str = "date_added"

DEFAULT_SPEC_VERSION: str = "3"
DEFAULT_PAPER_ID: str = "10.1234_test_2026"
DEFAULT_TASK_ID: str = "t0001_test"
DEFAULT_TITLE: str = "Test Paper Title"
DEFAULT_YEAR: int = 2026
DEFAULT_DOI: str = "10.1234/test/2026"
DEFAULT_URL: str = "https://example.com/papers/test-2026"
DEFAULT_PDF_URL: str = "https://example.com/papers/test-2026.pdf"
DEFAULT_DATE_PUBLISHED: str = "2026-01-15"
DEFAULT_JOURNAL: str = "Test Conference 2026"
DEFAULT_VENUE_TYPE: str = "conference"
DEFAULT_ABSTRACT: str = (
    "This paper presents a comprehensive evaluation of word sense disambiguation "
    "methods across multiple standard benchmarks using a unified evaluation "
    "framework with consistent preprocessing and scoring conventions."
)
DEFAULT_CITATION_KEY: str = "Test2026"
DEFAULT_SUMMARY_PATH: str = "summary.md"
DEFAULT_DOWNLOAD_STATUS: str = "success"
DEFAULT_DATE_ADDED: str = "2026-01-20"
DEFAULT_PDF_FILENAME: str = "files/test_2026_test-paper.pdf"
DEFAULT_AUTHOR_NAME: str = "Alice Test"
DEFAULT_AUTHOR_COUNTRY: str = "US"
DEFAULT_AUTHOR_INSTITUTION: str = "Test University"
DEFAULT_INSTITUTION_NAME: str = "Test University"
DEFAULT_INSTITUTION_COUNTRY: str = "US"

# Filler text blocks that exceed minimum word-count requirements.

_OVERVIEW_TEXT: str = (
    "This paper investigates advanced methods for evaluating and comparing "
    "word sense disambiguation systems across diverse benchmarks. The authors "
    "introduce a novel framework that unifies five previously separate datasets "
    "into a single coherent benchmark suite. The evaluation methodology includes "
    "fine-grained analysis by part of speech, polysemy level, and domain, "
    "revealing patterns that aggregate metrics obscure. The framework provides "
    "an open-source scoring toolkit that eliminates discrepancies caused by "
    "different preprocessing and tokenization conventions."
)

_ARCHITECTURE_TEXT: str = (
    "The framework unifies five all-words WSD datasets: Senseval-2, Senseval-3, "
    "SemEval-2007 Task 17, SemEval-2013 Task 12, and SemEval-2015 Task 13. "
    "All datasets are converted to a common XML format with sense annotations "
    "mapped to WordNet 3.0 synsets. Evaluation uses standard precision, recall, "
    "and F1 over polysemous content words. The most frequent sense baseline from "
    "SemCor serves as the primary reference. Systems compared include SVM-based "
    "supervised models, graph-based knowledge approaches, and hybrid methods. "
    "Training uses SemCor with 226036 sense-annotated tokens. The scoring toolkit "
    "is implemented in Java and supports per-POS and per-domain breakdowns."
)

_RESULTS_TEXT: str = (
    "* MFS baseline achieves **65.5 F1** on the ALL concatenation\n"
    "* Best supervised system reaches **71.3 F1** on ALL\n"
    "* Knowledge-based approach achieves **63.7 F1** with WordNet only\n"
    "* Nouns are easiest at **72.1 F1** versus verbs at **57.4 F1**\n"
    "* Adjectives reach **78.5 F1** and adverbs reach **83.6 F1**\n"
    "* SemEval-2007 is the hardest dataset at **62.8 F1** for MFS\n"
)

_SUMMARY_TEXT: str = (
    "The paper addresses fragmentation in WSD evaluation by proposing a unified "
    "framework that standardizes five major all-words English WSD datasets. Prior "
    "to this work comparing systems required navigating inconsistent preprocessing "
    "and different WordNet versions.\n\n"
    "The framework maps all datasets to WordNet 3.0 and provides a common XML "
    "format with an open-source scorer. The authors evaluate dozens of systems "
    "spanning knowledge-based supervised and hybrid paradigms.\n\n"
    "The key finding is that supervised systems lead at 71.3 F1 but the MFS "
    "baseline at 65.5 F1 remains competitive especially on verbs where all "
    "systems struggle. POS breakdown shows nouns at 72.1 F1 while verbs lag.\n\n"
    "For this project the framework is essential as the standard benchmark and "
    "all experiments should use the unified evaluation with the provided scorer "
    "and the MFS baseline must be included as the minimum reference point."
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_paper_asset(
    *,
    repo_root: Path,
    paper_id: str = DEFAULT_PAPER_ID,
    task_id: str = DEFAULT_TASK_ID,
    spec_version: str = DEFAULT_SPEC_VERSION,
    title: str = DEFAULT_TITLE,
    year: int = DEFAULT_YEAR,
    doi: str | None = DEFAULT_DOI,
    url: str | None = DEFAULT_URL,
    pdf_url: str | None = DEFAULT_PDF_URL,
    date_published: str | None = DEFAULT_DATE_PUBLISHED,
    journal: str = DEFAULT_JOURNAL,
    venue_type: str = DEFAULT_VENUE_TYPE,
    categories: list[str] | None = None,
    abstract: str = DEFAULT_ABSTRACT,
    citation_key: str = DEFAULT_CITATION_KEY,
    summary_path: str = DEFAULT_SUMMARY_PATH,
    download_status: str = DEFAULT_DOWNLOAD_STATUS,
    download_failure_reason: str | None = None,
    date_added: str = DEFAULT_DATE_ADDED,
    include_summary: bool = True,
    include_files_dir: bool = True,
    details_overrides: dict[str, object] | None = None,
    summary_body: str | None = None,
) -> Path:
    asset_dir: Path = paper_asset_dir(
        paper_id=paper_id,
        task_id=task_id,
    )
    asset_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename: str = DEFAULT_PDF_FILENAME
    files_list: list[str] = [pdf_filename] if include_files_dir else []

    resolved_categories: list[str] = categories if categories is not None else []

    details: dict[str, object] = {
        SPEC_VERSION_FIELD: spec_version,
        PAPER_ID_FIELD: paper_id,
        DOI_FIELD: doi,
        TITLE_FIELD: title,
        URL_FIELD: url,
        PDF_URL_FIELD: pdf_url,
        DATE_PUBLISHED_FIELD: date_published,
        YEAR_FIELD: year,
        AUTHORS_FIELD: [
            {
                "name": DEFAULT_AUTHOR_NAME,
                "country": DEFAULT_AUTHOR_COUNTRY,
                "institution": DEFAULT_AUTHOR_INSTITUTION,
                "orcid": None,
            },
        ],
        INSTITUTIONS_FIELD: [
            {
                "name": DEFAULT_INSTITUTION_NAME,
                "country": DEFAULT_INSTITUTION_COUNTRY,
            },
        ],
        JOURNAL_FIELD: journal,
        VENUE_TYPE_FIELD: venue_type,
        CATEGORIES_FIELD: resolved_categories,
        ABSTRACT_FIELD: abstract,
        CITATION_KEY_FIELD: citation_key,
        SUMMARY_PATH_FIELD: summary_path,
        FILES_FIELD: files_list,
        DOWNLOAD_STATUS_FIELD: download_status,
        DOWNLOAD_FAILURE_REASON_FIELD: download_failure_reason,
        ADDED_BY_TASK_FIELD: task_id,
        DATE_ADDED_FIELD: date_added,
    }

    if details_overrides is not None:
        details.update(details_overrides)

    write_json(
        path=paper_details_path(paper_id=paper_id, task_id=task_id),
        data=details,
    )

    if include_summary:
        frontmatter: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            PAPER_ID_FIELD: paper_id,
            CITATION_KEY_FIELD: citation_key,
            "summarized_by_task": task_id,
            "date_summarized": date_added,
        }
        body: str = (
            summary_body
            if summary_body is not None
            else (
                f"# {title}\n\n"
                "## Metadata\n\n"
                f"* **File**: `{pdf_filename}`\n"
                f"* **Published**: {year}\n"
                f"* **Authors**: {DEFAULT_AUTHOR_NAME}\n"
                f"* **Venue**: {journal}\n"
                f"* **DOI**: `{doi}`\n\n"
                "## Abstract\n\n"
                f"{abstract}\n\n"
                "## Overview\n\n"
                f"{_OVERVIEW_TEXT}\n\n"
                "## Architecture, Models and Methods\n\n"
                f"{_ARCHITECTURE_TEXT}\n\n"
                "## Results\n\n"
                f"{_RESULTS_TEXT}\n"
                "## Innovations\n\n"
                "### Unified Evaluation Framework\n\n"
                "First standardized benchmark combining five all-words WSD "
                "datasets with consistent preprocessing.\n\n"
                "## Datasets\n\n"
                "* **Senseval-2**: 2282 instances, English all-words\n"
                "* **SemCor**: 226036 sense-annotated tokens\n\n"
                "## Main Ideas\n\n"
                "* The MFS baseline at 65.5 F1 is a strong reference point\n"
                "* Verb disambiguation is the hardest subproblem\n"
                "* Supervised approaches outperform knowledge-based ones\n\n"
                "## Summary\n\n"
                f"{_SUMMARY_TEXT}\n"
            )
        )
        write_frontmatter_md(
            path=paper_summary_path(
                paper_id=paper_id,
                task_id=task_id,
            ),
            frontmatter=frontmatter,
            body=body,
        )

    if include_files_dir:
        files_dir: Path = paper_files_dir(
            paper_id=paper_id,
            task_id=task_id,
        )
        files_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=asset_dir / pdf_filename,
            content="(placeholder PDF content)",
        )

    return asset_dir
