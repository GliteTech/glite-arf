import json
from pathlib import Path

import pytest

import meta.asset_types.answer.verificator as verify_answer_asset_module
import meta.asset_types.answer.verify_details as verify_answer_details_module
import meta.asset_types.answer.verify_full as verify_answer_full_module
import meta.asset_types.answer.verify_short as verify_answer_short_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.answer import (
    DEFAULT_ANSWER_ID,
    DEFAULT_TASK_ID,
    build_answer_asset,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from arf.tests.fixtures.writers import write_json

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERIFICATOR_MODULES = [
    verify_answer_asset_module,
    verify_answer_details_module,
    verify_answer_short_module,
    verify_answer_full_module,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _diagnostic_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _error_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.errors]


def _warning_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.warnings]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=_VERIFICATOR_MODULES,
    )
    build_complete_task(repo_root=tmp_path, task_id=DEFAULT_TASK_ID)
    return tmp_path


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_answer_passes(repo: Path) -> None:
    build_answer_asset(repo_root=repo)
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_wrapped_question_passes(repo: Path) -> None:
    long_question: str = (
        "What is the current state of the art for English all-words word sense "
        "disambiguation on the Raganato benchmark and how does it compare to "
        "earlier supervised and knowledge-based methods?"
    )
    wrapped_question: str = (
        "What is the current state of the art for English all-words word sense\n"
        "disambiguation on the Raganato benchmark and how does it compare to\n"
        "earlier supervised and knowledge-based methods?"
    )
    short_body: str = (
        "## Question\n\n" + wrapped_question + "\n\n"
        "## Answer\n\n"
        "The current SOTA for English all-words WSD on the Raganato "
        "benchmark achieves approximately 89.0 F1 using a bi-encoder "
        "approach with 44M parameters. Supervised methods consistently "
        "outperform knowledge-based approaches when training data is "
        "available.\n\n"
        "## Sources\n\n"
        "* SANDWiCH (2025) paper\n"
    )
    full_body: str = (
        "## Question\n\n" + wrapped_question + "\n\n"
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
    build_answer_asset(
        repo_root=repo,
        question=long_question,
        short_answer_body=short_body,
        full_answer_body=full_body,
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_e001_details_json_missing(repo: Path) -> None:
    build_answer_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import answer_details_path

    answer_details_path(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    ).unlink()
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E001" in _error_codes(result)


def test_e002_short_answer_missing(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        include_short_answer=False,
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E002" in _error_codes(result)


def test_e003_answer_id_mismatch(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        details_overrides={"answer_id": "wrong-id"},
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E003" in _error_codes(result)


def test_e004_answer_id_format_invalid(repo: Path) -> None:
    bad_id: str = "BAD_ID"
    build_answer_asset(
        repo_root=repo,
        answer_id=bad_id,
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=bad_id,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E004" in _error_codes(result)


def test_e005_required_field_missing(repo: Path) -> None:
    build_answer_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import answer_details_path

    details_path: Path = answer_details_path(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["question"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E005" in _error_codes(result)


def test_e006_invalid_answer_methods(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        answer_methods=["invalid-method"],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E006" in _error_codes(result)


def test_e007_invalid_confidence(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        confidence="very-high",
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E007" in _error_codes(result)


def test_e008_referenced_task_does_not_exist(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        source_task_ids=["t9999_nonexistent"],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E008" in _error_codes(result)


def test_e011_short_answer_missing_section(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        short_answer_body="## Question\n\nSome question?\n",
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E011" in _error_codes(result)


def test_e012_full_answer_missing_section(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        full_answer_body="## Question\n\nSome question?\n",
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E012" in _error_codes(result)


def test_e009_referenced_paper_does_not_exist(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        source_paper_ids=["nonexistent_paper_id"],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E009" in _error_codes(result)


def test_e010_invalid_source_url(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        source_urls=["ftp://not-http.example.com/file"],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E010" in _error_codes(result)


def test_e013_answer_section_wrong_sentence_count(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        short_answer_body=(
            "## Question\n\n"
            "What is the current state of the art for English all-words "
            "word sense disambiguation on the Raganato benchmark?\n\n"
            "## Answer\n\n"
            "One sentence only.\n\n"
            "## Sources\n\n"
            "* Some source\n"
        ),
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E013" in _error_codes(result)


def test_e014_no_evidence_references(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        source_paper_ids=[],
        source_urls=[],
        source_task_ids=[],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-E014" in _error_codes(result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_w001_nonexistent_category(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        categories=["nonexistent-category"],
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-W001" in _warning_codes(result)


def test_w002_question_too_short(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        question="Why?",
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-W002" in _warning_codes(result)


def test_w003_evidence_section_too_shallow(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        full_answer_body=(
            "## Question\n\n"
            "What is the current SOTA?\n\n"
            "## Short Answer\n\n"
            "The SOTA is approximately 89.0 F1.\n\n"
            "## Research Process\n\n" + ("Word " * 50) + "\n\n"
            "## Evidence from Papers\n\n"
            "Short.\n\n"
            "## Evidence from Internet Sources\n\n"
            "Not used for this answer.\n\n"
            "## Evidence from Code or Experiments\n\n"
            "Not used for this answer.\n\n"
            "## Synthesis\n\n" + ("Word " * 50) + "\n\n"
            "## Limitations\n\n" + ("Word " * 30) + "\n\n"
            "## Sources\n\n"
            "* Some source reference\n"
        ),
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-W003" in _warning_codes(result)


def test_w004_full_answer_too_short(repo: Path) -> None:
    build_answer_asset(
        repo_root=repo,
        full_answer_body=(
            "## Question\n\nQ?\n\n"
            "## Short Answer\n\nShort.\n\n"
            "## Research Process\n\nBrief.\n\n"
            "## Evidence from Papers\n\nBrief.\n\n"
            "## Evidence from Internet Sources\n\nBrief.\n\n"
            "## Evidence from Code or Experiments\n\nBrief.\n\n"
            "## Synthesis\n\nBrief.\n\n"
            "## Limitations\n\nBrief.\n\n"
            "## Sources\n\n* S\n"
        ),
    )
    result: VerificationResult = verify_answer_asset_module.verify_answer_asset(
        answer_id=DEFAULT_ANSWER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "AA-W004" in _warning_codes(result)
