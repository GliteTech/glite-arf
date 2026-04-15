from pathlib import Path

from arf.scripts.verificators.common.paths import (
    answer_asset_dir,
    answer_details_path,
    answer_full_answer_path,
    answer_short_answer_path,
)
from arf.tests.fixtures.writers import write_frontmatter_md, write_json

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION_FIELD: str = "spec_version"
ANSWER_ID_FIELD: str = "answer_id"
QUESTION_FIELD: str = "question"
SHORT_TITLE_FIELD: str = "short_title"
SHORT_ANSWER_PATH_FIELD: str = "short_answer_path"
FULL_ANSWER_PATH_FIELD: str = "full_answer_path"
CATEGORIES_FIELD: str = "categories"
ANSWER_METHODS_FIELD: str = "answer_methods"
SOURCE_PAPER_IDS_FIELD: str = "source_paper_ids"
SOURCE_URLS_FIELD: str = "source_urls"
SOURCE_TASK_IDS_FIELD: str = "source_task_ids"
CONFIDENCE_FIELD: str = "confidence"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"

DEFAULT_SPEC_VERSION: str = "2"
DEFAULT_ANSWER_ID: str = "test-answer"
DEFAULT_TASK_ID: str = "t0001_test"
DEFAULT_QUESTION: str = (
    "What is the current state of the art for English all-words "
    "word sense disambiguation on the Raganato benchmark?"
)
DEFAULT_SHORT_TITLE: str = "WSD SOTA Raganato"
DEFAULT_SHORT_ANSWER_PATH: str = "short_answer.md"
DEFAULT_FULL_ANSWER_PATH: str = "full_answer.md"
DEFAULT_ANSWER_METHOD: str = "papers"
DEFAULT_CONFIDENCE: str = "high"
DEFAULT_DATE_CREATED: str = "2026-01-20"
DEFAULT_SOURCE_URL: str = "https://example.com/wsd-survey"

_SHORT_ANSWER_BODY: str = (
    "## Question\n\n"
    "What is the current state of the art for English all-words "
    "word sense disambiguation on the Raganato benchmark?\n\n"
    "## Answer\n\n"
    "The current SOTA for English all-words WSD on the Raganato "
    "benchmark achieves approximately 89.0 F1 using a bi-encoder "
    "approach with 44M parameters. Supervised methods consistently "
    "outperform knowledge-based approaches when training data is "
    "available.\n\n"
    "## Sources\n\n"
    "* SANDWiCH (2025) paper\n"
    "* Raganato unified evaluation framework\n"
)

_FULL_ANSWER_BODY: str = (
    "## Question\n\n"
    "What is the current state of the art for English all-words "
    "word sense disambiguation on the Raganato benchmark?\n\n"
    "## Short Answer\n\n"
    "The current SOTA achieves approximately 89.0 F1 using a "
    "bi-encoder approach.\n\n"
    "## Research Process\n\n"
    "We reviewed published results on the Raganato unified benchmark "
    "including results from supervised, knowledge-based, and "
    "LLM-based methods across all five evaluation datasets.\n\n"
    "## Evidence from Papers\n\n"
    "The SANDWiCH model (2025) achieves 89.0 F1 on the ALL "
    "concatenation with only 44M parameters using a bi-encoder "
    "architecture trained on SemCor.\n\n"
    "## Evidence from Internet Sources\n\n"
    "Recent leaderboard results confirm the SANDWiCH numbers and "
    "show that LLM-based approaches are competitive but slower.\n\n"
    "## Evidence from Code or Experiments\n\n"
    "No code experiments were conducted for this answer.\n\n"
    "## Synthesis\n\n"
    "The evidence converges on supervised bi-encoder methods as "
    "the current SOTA for WSD. The MFS baseline at 65.5 F1 remains "
    "the minimum reference. The gap between SOTA and MFS has grown "
    "steadily over the past decade of research.\n\n"
    "## Limitations\n\n"
    "This answer is based on published benchmarks only and does not "
    "include unpublished or in-progress methods. LLM-based approaches "
    "are evolving rapidly and may surpass current SOTA soon.\n\n"
    "## Sources\n\n"
    "* SANDWiCH (2025) paper\n"
    "* Raganato unified evaluation framework\n"
    "* https://example.com/wsd-survey\n"
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_answer_asset(
    *,
    repo_root: Path,
    answer_id: str = DEFAULT_ANSWER_ID,
    task_id: str = DEFAULT_TASK_ID,
    spec_version: str = DEFAULT_SPEC_VERSION,
    question: str = DEFAULT_QUESTION,
    short_title: str = DEFAULT_SHORT_TITLE,
    short_answer_path: str = DEFAULT_SHORT_ANSWER_PATH,
    full_answer_path: str = DEFAULT_FULL_ANSWER_PATH,
    answer_methods: list[str] | None = None,
    source_paper_ids: list[str] | None = None,
    source_urls: list[str] | None = None,
    source_task_ids: list[str] | None = None,
    confidence: str = DEFAULT_CONFIDENCE,
    categories: list[str] | None = None,
    date_created: str = DEFAULT_DATE_CREATED,
    include_short_answer: bool = True,
    include_full_answer: bool = True,
    details_overrides: dict[str, object] | None = None,
    short_answer_body: str | None = None,
    full_answer_body: str | None = None,
) -> Path:
    asset_dir: Path = answer_asset_dir(
        answer_id=answer_id,
        task_id=task_id,
    )
    asset_dir.mkdir(parents=True, exist_ok=True)

    resolved_methods: list[str] = (
        answer_methods if answer_methods is not None else [DEFAULT_ANSWER_METHOD]
    )
    resolved_paper_ids: list[str] = source_paper_ids if source_paper_ids is not None else []
    resolved_urls: list[str] = source_urls if source_urls is not None else [DEFAULT_SOURCE_URL]
    resolved_task_ids: list[str] = source_task_ids if source_task_ids is not None else []
    resolved_categories: list[str] = categories if categories is not None else []

    details: dict[str, object] = {
        SPEC_VERSION_FIELD: spec_version,
        ANSWER_ID_FIELD: answer_id,
        QUESTION_FIELD: question,
        SHORT_TITLE_FIELD: short_title,
        SHORT_ANSWER_PATH_FIELD: short_answer_path,
        FULL_ANSWER_PATH_FIELD: full_answer_path,
        CATEGORIES_FIELD: resolved_categories,
        ANSWER_METHODS_FIELD: resolved_methods,
        SOURCE_PAPER_IDS_FIELD: resolved_paper_ids,
        SOURCE_URLS_FIELD: resolved_urls,
        SOURCE_TASK_IDS_FIELD: resolved_task_ids,
        CONFIDENCE_FIELD: confidence,
        CREATED_BY_TASK_FIELD: task_id,
        DATE_CREATED_FIELD: date_created,
    }

    if details_overrides is not None:
        details.update(details_overrides)

    write_json(
        path=answer_details_path(
            answer_id=answer_id,
            task_id=task_id,
        ),
        data=details,
    )

    if include_short_answer:
        short_fm: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            ANSWER_ID_FIELD: answer_id,
            "answered_by_task": task_id,
            "date_answered": date_created,
        }
        write_frontmatter_md(
            path=answer_short_answer_path(
                answer_id=answer_id,
                task_id=task_id,
            ),
            frontmatter=short_fm,
            body=(short_answer_body if short_answer_body is not None else _SHORT_ANSWER_BODY),
        )

    if include_full_answer:
        full_fm: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            ANSWER_ID_FIELD: answer_id,
            "answered_by_task": task_id,
            "date_answered": date_created,
            CONFIDENCE_FIELD: confidence,
        }
        write_frontmatter_md(
            path=answer_full_answer_path(
                answer_id=answer_id,
                task_id=task_id,
            ),
            frontmatter=full_fm,
            body=(full_answer_body if full_answer_body is not None else _FULL_ANSWER_BODY),
        )

    return asset_dir
