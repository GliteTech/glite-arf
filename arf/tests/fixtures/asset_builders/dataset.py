from pathlib import Path

from arf.scripts.verificators.common.paths import (
    dataset_asset_dir,
    dataset_description_path,
    dataset_details_path,
    dataset_files_dir,
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
DATASET_ID_FIELD: str = "dataset_id"
NAME_FIELD: str = "name"
VERSION_FIELD: str = "version"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DESCRIPTION_PATH_FIELD: str = "description_path"
SOURCE_PAPER_ID_FIELD: str = "source_paper_id"
URL_FIELD: str = "url"
DOWNLOAD_URL_FIELD: str = "download_url"
YEAR_FIELD: str = "year"
DATE_PUBLISHED_FIELD: str = "date_published"
AUTHORS_FIELD: str = "authors"
INSTITUTIONS_FIELD: str = "institutions"
LICENSE_FIELD: str = "license"
ACCESS_KIND_FIELD: str = "access_kind"
SIZE_DESCRIPTION_FIELD: str = "size_description"
FILES_FIELD: str = "files"
CATEGORIES_FIELD: str = "categories"

DEFAULT_SPEC_VERSION: str = "2"
DEFAULT_DATASET_ID: str = "test-dataset"
DEFAULT_TASK_ID: str = "t0001_test"
DEFAULT_NAME: str = "Test Dataset"
DEFAULT_VERSION: str = "1.0"
DEFAULT_SHORT_DESCRIPTION: str = (
    "A test dataset containing sense-annotated English text for "
    "evaluating word sense disambiguation systems across standard "
    "benchmarks."
)
DEFAULT_DESCRIPTION_PATH: str = "description.md"
DEFAULT_URL: str = "https://example.com/datasets/test-dataset"
DEFAULT_YEAR: int = 2026
DEFAULT_DATE_PUBLISHED: str = "2026-01-15"
DEFAULT_LICENSE: str = "CC-BY-4.0"
DEFAULT_ACCESS_KIND: str = "public"
DEFAULT_SIZE_DESCRIPTION: str = "7253 sense-annotated instances"
DEFAULT_DATA_FILENAME: str = "files/data.jsonl"
DEFAULT_AUTHOR_NAME: str = "Alice Test"
DEFAULT_AUTHOR_COUNTRY: str = "US"
DEFAULT_AUTHOR_INSTITUTION: str = "Test University"
DEFAULT_INSTITUTION_NAME: str = "Test University"
DEFAULT_INSTITUTION_COUNTRY: str = "US"

_OVERVIEW_TEXT: str = (
    "This dataset provides sense-annotated English text for word sense "
    "disambiguation evaluation. It contains instances drawn from multiple "
    "domains with annotations mapped to WordNet 3.0 synsets. The dataset "
    "follows the unified format established by the Raganato evaluation "
    "framework and includes fine-grained part-of-speech annotations for "
    "each target word."
)

_DESCRIPTION_BODY: str = (
    "# Test Dataset\n\n"
    "## Metadata\n\n"
    "* **Name**: Test Dataset\n"
    "* **Version**: 1.0\n"
    "* **License**: CC-BY-4.0\n\n"
    "## Overview\n\n"
    f"{_OVERVIEW_TEXT}\n\n"
    "## Content & Annotation\n\n"
    "Each instance contains a target word in context with its gold-standard "
    "WordNet 3.0 sense key. Annotations cover nouns, verbs, adjectives, and "
    "adverbs. The annotation guidelines follow SemCor conventions.\n\n"
    "## Statistics\n\n"
    "* Total instances: 7253\n"
    "* Unique lemmas: 2154\n"
    "* Average polysemy: 4.2 senses per lemma\n\n"
    "## Usage Notes\n\n"
    "Load with the project WSD data loader. The dataset uses UTF-8 encoding "
    "and JSONL format with one instance per line.\n\n"
    "## Main Ideas\n\n"
    "* Provides a standard evaluation benchmark for WSD systems\n"
    "* Covers all four major parts of speech\n"
    "* Compatible with the Raganato unified evaluation framework\n\n"
    "## Summary\n\n"
    "This dataset is a test fixture for evaluating word sense disambiguation "
    "systems. It provides sense-annotated English text mapped to WordNet 3.0 "
    "synsets. The dataset follows standard conventions and can be loaded with "
    "the project data loader for consistent evaluation across experiments.\n"
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_dataset_asset(
    *,
    repo_root: Path,
    dataset_id: str = DEFAULT_DATASET_ID,
    task_id: str = DEFAULT_TASK_ID,
    spec_version: str = DEFAULT_SPEC_VERSION,
    name: str = DEFAULT_NAME,
    version: str | None = DEFAULT_VERSION,
    short_description: str = DEFAULT_SHORT_DESCRIPTION,
    description_path: str = DEFAULT_DESCRIPTION_PATH,
    source_paper_id: str | None = None,
    url: str | None = DEFAULT_URL,
    download_url: str | None = None,
    year: int = DEFAULT_YEAR,
    date_published: str | None = DEFAULT_DATE_PUBLISHED,
    license_str: str | None = DEFAULT_LICENSE,
    access_kind: str = DEFAULT_ACCESS_KIND,
    size_description: str = DEFAULT_SIZE_DESCRIPTION,
    categories: list[str] | None = None,
    include_description: bool = True,
    include_files_dir: bool = True,
    details_overrides: dict[str, object] | None = None,
    description_body: str | None = None,
) -> Path:
    asset_dir: Path = dataset_asset_dir(
        dataset_id=dataset_id,
        task_id=task_id,
    )
    asset_dir.mkdir(parents=True, exist_ok=True)

    resolved_categories: list[str] = categories if categories is not None else []

    files_list: list[dict[str, str]] = (
        [
            {
                "path": DEFAULT_DATA_FILENAME,
                "description": "Main dataset file in JSONL format",
                "format": "jsonl",
            },
        ]
        if include_files_dir
        else []
    )

    details: dict[str, object] = {
        SPEC_VERSION_FIELD: spec_version,
        DATASET_ID_FIELD: dataset_id,
        NAME_FIELD: name,
        VERSION_FIELD: version,
        SHORT_DESCRIPTION_FIELD: short_description,
        DESCRIPTION_PATH_FIELD: description_path,
        SOURCE_PAPER_ID_FIELD: source_paper_id,
        URL_FIELD: url,
        DOWNLOAD_URL_FIELD: download_url,
        YEAR_FIELD: year,
        DATE_PUBLISHED_FIELD: date_published,
        AUTHORS_FIELD: [
            {
                "name": DEFAULT_AUTHOR_NAME,
                "country": DEFAULT_AUTHOR_COUNTRY,
                "institution": DEFAULT_AUTHOR_INSTITUTION,
            },
        ],
        INSTITUTIONS_FIELD: [
            {
                "name": DEFAULT_INSTITUTION_NAME,
                "country": DEFAULT_INSTITUTION_COUNTRY,
            },
        ],
        LICENSE_FIELD: license_str,
        ACCESS_KIND_FIELD: access_kind,
        SIZE_DESCRIPTION_FIELD: size_description,
        FILES_FIELD: files_list,
        CATEGORIES_FIELD: resolved_categories,
    }

    if details_overrides is not None:
        details.update(details_overrides)

    write_json(
        path=dataset_details_path(
            dataset_id=dataset_id,
            task_id=task_id,
        ),
        data=details,
    )

    if include_description:
        frontmatter: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            DATASET_ID_FIELD: dataset_id,
            "summarized_by_task": task_id,
            "date_summarized": DEFAULT_DATE_PUBLISHED,
        }
        write_frontmatter_md(
            path=dataset_description_path(
                dataset_id=dataset_id,
                task_id=task_id,
            ),
            frontmatter=frontmatter,
            body=(description_body if description_body is not None else _DESCRIPTION_BODY),
        )

    if include_files_dir:
        files_dir: Path = dataset_files_dir(
            dataset_id=dataset_id,
            task_id=task_id,
        )
        files_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=asset_dir / DEFAULT_DATA_FILENAME,
            content='{"instance_id": 1, "token": "bank", "sense": "bank%1:17:01::"}\n',
        )

    return asset_dir
