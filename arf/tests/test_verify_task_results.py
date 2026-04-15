from pathlib import Path

import pytest

import arf.scripts.verificators.verify_task_results as verify_task_results_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_task_type
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.results_builders import (
    build_costs_file,
    build_metrics_file,
    build_remote_machines_file,
    build_results_detailed,
    build_results_images_dir,
    build_results_summary,
)
from arf.tests.fixtures.task_builder import build_task_folder, build_task_json
from arf.tests.fixtures.writers import write_frontmatter_md, write_json, write_text

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_task_results_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_task_results_module.verify_task_results(task_id=task_id)


def _build_all_results(*, repo_root: Path) -> None:
    build_task_folder(repo_root=repo_root, task_id=TASK_ID)
    build_task_json(
        repo_root=repo_root,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
    )
    build_results_summary(repo_root=repo_root, task_id=TASK_ID)
    build_results_detailed(repo_root=repo_root, task_id=TASK_ID)
    build_metrics_file(repo_root=repo_root, task_id=TASK_ID)
    build_costs_file(repo_root=repo_root, task_id=TASK_ID)
    build_remote_machines_file(repo_root=repo_root, task_id=TASK_ID)
    build_results_images_dir(repo_root=repo_root, task_id=TASK_ID)


# ---------------------------------------------------------------------------
# Valid results pass
# ---------------------------------------------------------------------------


def test_valid_results_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# results_summary.md errors
# ---------------------------------------------------------------------------


def test_tr_e001_missing_results_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    paths.results_summary_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "TR-E001" in _codes(result=result)


def test_tr_e006_missing_summary_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content="# Results\n\n## Summary\n\nDone.\n",
    )
    result: VerificationResult = _verify()
    assert "TR-E006" in _codes(result=result)


# ---------------------------------------------------------------------------
# results_detailed.md errors
# ---------------------------------------------------------------------------


def test_tr_e002_missing_results_detailed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    paths.results_detailed_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "TR-E002" in _codes(result=result)


def test_tr_e007_missing_detailed_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    # Write a detailed file missing mandatory sections (v2 requires
    # Task Requirement Coverage)
    from arf.tests.fixtures.writers import write_frontmatter_md

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body="# Detailed\n\n## Summary\n\nDone.\n",
    )
    result: VerificationResult = _verify()
    assert "TR-E007" in _codes(result=result)


# ---------------------------------------------------------------------------
# costs.json errors
# ---------------------------------------------------------------------------


def test_tr_e004_missing_costs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    paths.costs_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "TR-E004" in _codes(result=result)


def test_tr_e011_costs_missing_required_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={"some_field": 0},
    )
    result: VerificationResult = _verify()
    assert "TR-E011" in _codes(result=result)


def test_tr_e012_breakdown_not_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={"total_cost_usd": 0, "breakdown": "not-an-object"},
    )
    result: VerificationResult = _verify()
    assert "TR-E012" in _codes(result=result)


def test_tr_e012_breakdown_invalid_entry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={
            "total_cost_usd": 5.0,
            "breakdown": {"item": "invalid-not-number-or-dict"},
        },
    )
    result: VerificationResult = _verify()
    assert "TR-E012" in _codes(result=result)


def test_tr_e015_negative_total_cost(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={"total_cost_usd": -1.0, "breakdown": {}},
    )
    result: VerificationResult = _verify()
    assert "TR-E015" in _codes(result=result)


def test_tr_e016_services_not_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={
            "total_cost_usd": 0,
            "breakdown": {},
            "services": "not-an-object",
        },
    )
    result: VerificationResult = _verify()
    assert "TR-E016" in _codes(result=result)


def test_tr_e016_services_negative_value(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={
            "total_cost_usd": 0,
            "breakdown": {},
            "services": {"api": -5.0},
        },
    )
    result: VerificationResult = _verify()
    assert "TR-E016" in _codes(result=result)


def test_tr_e017_budget_limit_not_number(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={
            "total_cost_usd": 0,
            "breakdown": {},
            "budget_limit": "fifty",
        },
    )
    result: VerificationResult = _verify()
    assert "TR-E017" in _codes(result=result)


def test_tr_e018_note_not_string(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={"total_cost_usd": 0, "breakdown": {}, "note": 123},
    )
    result: VerificationResult = _verify()
    assert "TR-E018" in _codes(result=result)


# ---------------------------------------------------------------------------
# remote_machines_used.json errors
# ---------------------------------------------------------------------------


def test_tr_e005_missing_remote_machines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    paths.remote_machines_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "TR-E005" in _codes(result=result)


def test_tr_e013_remote_machines_not_array(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.remote_machines_path(task_id=TASK_ID),
        data={"not": "an array"},
    )
    result: VerificationResult = _verify()
    assert "TR-E013" in _codes(result=result)


def test_tr_e014_machine_missing_required_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.remote_machines_path(task_id=TASK_ID),
        data=[{"provider": "vast.ai"}],
    )
    result: VerificationResult = _verify()
    assert "TR-E014" in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_tr_w001_summary_low_word_count(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\nShort.\n\n"
            "## Metrics\n\n* A\n* B\n* C\n\n"
            "## Verification\n\nPassed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W001" in _codes(result=result)


def test_tr_w002_detailed_low_word_count(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "1", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\nShort.\n\n"
            "## Methodology\n\nDone.\n\n"
            "## Verification\n\nPassed.\n\n"
            "## Limitations\n\nNone.\n\n"
            "## Files Created\n\n* `results/file.json`\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W002" in _codes(result=result)


def test_tr_w003_few_metric_bullets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\n" + ("Word " * 80) + "\n\n"
            "## Metrics\n\n"
            "* Only one bullet\n\n"
            "## Verification\n\n"
            "All verificators passed without errors.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W003" in _codes(result=result)


def test_tr_w004_no_images_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
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
    result: VerificationResult = _verify()
    assert "TR-W004" in _codes(result=result)


def test_tr_w005_cost_sum_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.costs_path(task_id=TASK_ID),
        data={
            "total_cost_usd": 100.0,
            "breakdown": {"api": 10.0, "compute": 5.0},
        },
    )
    result: VerificationResult = _verify()
    assert "TR-W005" in _codes(result=result)


def test_tr_w007_verification_no_verificator_mention(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\n" + ("Word " * 80) + "\n\n"
            "## Metrics\n\n"
            "* Metric one is good\n"
            "* Metric two is better\n"
            "* Metric three is best\n\n"
            "## Verification\n\n"
            "No issues found.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W007" in _codes(result=result)


def test_tr_w007_not_triggered_by_verificator_keyword(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\n" + ("Word " * 80) + "\n\n"
            "## Metrics\n\n"
            "* Metric one is good\n"
            "* Metric two is better\n"
            "* Metric three is best\n\n"
            "## Verification\n\n"
            "Predictions verificator: PASSED\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W007" not in _codes(result=result)


def test_tr_w007_not_triggered_by_passed_keyword(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\n" + ("Word " * 80) + "\n\n"
            "## Metrics\n\n"
            "* Metric one is good\n"
            "* Metric two is better\n"
            "* Metric three is best\n\n"
            "## Verification\n\n"
            "All checks passed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W007" not in _codes(result=result)


def test_tr_w007_not_triggered_by_failed_keyword(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.results_summary_path(task_id=TASK_ID),
        content=(
            "# Results\n\n"
            "## Summary\n\n" + ("Word " * 80) + "\n\n"
            "## Metrics\n\n"
            "* Metric one is good\n"
            "* Metric two is better\n"
            "* Metric three is best\n\n"
            "## Verification\n\n"
            "Some checks failed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W007" not in _codes(result=result)


def test_tr_w008_files_created_no_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    body: str = (
        "# Detailed\n\n"
        "## Summary\n\n" + ("Word " * 100) + "\n\n"
        "## Methodology\n\n"
        "The task was executed on a local machine using Python 3.12. "
        "Processing began at 2026-04-01T00:00:00Z and completed at "
        "2026-04-01T01:00:00Z. Standard toolchain was used.\n\n"
        "## Verification\n\nPassed all checks.\n\n"
        "## Limitations\n\nNone significant.\n\n"
        "## Files Created\n\nSome files were created during this task.\n\n"
        "## Task Requirement Coverage\n\n"
        "REQ-1: Done. All requirements met.\n"
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=body,
    )
    result: VerificationResult = _verify()
    assert "TR-W008" in _codes(result=result)


def test_tr_w010_no_req_items_in_coverage(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    body: str = (
        "# Detailed\n\n"
        "## Summary\n\n" + ("Word " * 100) + "\n\n"
        "## Methodology\n\n"
        "The task was executed on a local machine using Python 3.12. "
        "Processing began at 2026-04-01T00:00:00Z and completed at "
        "2026-04-01T01:00:00Z. Standard toolchain was used.\n\n"
        "## Verification\n\nPassed all checks.\n\n"
        "## Limitations\n\nNone significant.\n\n"
        "## Files Created\n\n* `results/output.json`\n\n"
        "## Task Requirement Coverage\n\n"
        "All requirements were completed without issues.\n"
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=body,
    )
    result: VerificationResult = _verify()
    assert "TR-W010" in _codes(result=result)


def test_tr_w012_coverage_not_last_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    body: str = (
        "# Detailed\n\n"
        "## Summary\n\n" + ("Word " * 100) + "\n\n"
        "## Methodology\n\n"
        "The task was executed on a local machine using Python 3.12. "
        "Processing began at 2026-04-01T00:00:00Z and completed at "
        "2026-04-01T01:00:00Z. Standard toolchain was used.\n\n"
        "## Verification\n\nPassed all checks.\n\n"
        "## Limitations\n\nNone significant.\n\n"
        "## Files Created\n\n* `results/output.json`\n\n"
        "## Task Requirement Coverage\n\n"
        "* REQ-1: Done. All requirements met.\n\n"
        "## Extra Section After Coverage\n\n"
        "This section should not come after coverage.\n"
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=body,
    )
    result: VerificationResult = _verify()
    assert "TR-W012" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-E003: metrics.json missing
# ---------------------------------------------------------------------------


def test_tr_e003_missing_metrics_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    paths.metrics_path(task_id=TASK_ID).unlink()
    result: VerificationResult = _verify()
    assert "TR-E003" in _codes(result=result)


def test_tr_e003_invalid_metrics_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_text(
        path=paths.metrics_path(task_id=TASK_ID),
        content="{broken json",
    )
    result: VerificationResult = _verify()
    assert "TR-E003" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-E008: metrics.json top-level not an object
# ---------------------------------------------------------------------------


def test_tr_e008_metrics_array(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.metrics_path(task_id=TASK_ID),
        data=[1, 2, 3],
    )
    result: VerificationResult = _verify()
    assert "TR-E008" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-E010: metrics.json invalid payload shape
# ---------------------------------------------------------------------------


def test_tr_e010_empty_variants_array(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.metrics_path(task_id=TASK_ID),
        data={"variants": []},
    )
    result: VerificationResult = _verify()
    assert "TR-E010" in _codes(result=result)


def test_tr_e010_variant_missing_variant_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.metrics_path(task_id=TASK_ID),
        data={
            "variants": [
                {
                    "dimensions": {},
                    "metrics": {"f1_all": 0.65},
                },
            ],
        },
    )
    result: VerificationResult = _verify()
    assert "TR-E010" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-E019: results_detailed.md spec_version not recognized
# ---------------------------------------------------------------------------


def test_tr_e019_bad_spec_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "99", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\nDone.\n\n"
            "## Verification\n\nPassed.\n\n"
            "## Limitations\n\nNone.\n\n"
            "## Files Created\n\n* `results/file.json`\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-E019" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-W006: metrics.json key not snake_case
# ---------------------------------------------------------------------------


def test_tr_w006_non_snake_case_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    write_json(
        path=paths.metrics_path(task_id=TASK_ID),
        data={
            "variants": [
                {
                    "variant_id": "default",
                    "dimensions": {"Model-Name": "bert"},
                    "metrics": {"f1_all": 0.65},
                },
            ],
        },
    )
    result: VerificationResult = _verify()
    assert "TR-W006" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-W011: Task Requirement Coverage lacks status labels
# ---------------------------------------------------------------------------


def test_tr_w011_no_status_labels(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    from arf.tests.fixtures.writers import write_frontmatter_md

    body: str = (
        "# Detailed\n\n"
        "## Summary\n\n" + ("Word " * 100) + "\n\n"
        "## Methodology\n\n"
        "The task was executed on a local machine using Python 3.12. "
        "Processing began at 2026-04-01T00:00:00Z and completed at "
        "2026-04-01T01:00:00Z. Standard toolchain was used.\n\n"
        "## Verification\n\nPassed all checks.\n\n"
        "## Limitations\n\nNone significant.\n\n"
        "## Files Created\n\n* `results/output.json`\n\n"
        "## Task Requirement Coverage\n\n"
        "* REQ-1: Implemented the baseline model.\n"
        "* REQ-2: Evaluated on all datasets.\n"
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=body,
    )
    result: VerificationResult = _verify()
    assert "TR-W011" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-W013: Examples section missing for experiment-type task
# ---------------------------------------------------------------------------


def test_tr_w013_missing_examples_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="experiment-run",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["experiment-run"],
    )
    from arf.tests.fixtures.writers import write_frontmatter_md

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline model implemented.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W013" in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-W014: Examples section has fewer than 10 bullet points
# ---------------------------------------------------------------------------


def test_tr_w014_few_example_bullets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="experiment-run",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["experiment-run"],
    )
    from arf.tests.fixtures.writers import write_frontmatter_md

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Examples\n\n"
            "* Example 1\n"
            "* Example 2\n"
            "* Example 3\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline model implemented.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W014" in _codes(result=result)


def test_tr_w014_code_blocks_count_as_examples(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Code blocks should count as examples — 10 code blocks should pass."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="experiment-run",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["experiment-run"],
    )
    from arf.tests.fixtures.writers import write_frontmatter_md

    code_block_examples: str = ""
    for i in range(10):
        code_block_examples += (
            f"### Example {i + 1}\n\n```text\nInput: word {i}\nOutput: sense {i}\n```\n\n"
        )

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Examples\n\n"
            + code_block_examples
            + "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline model implemented.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W014" not in _codes(result=result)


def test_tr_w014_numbered_items_count_as_examples(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Numbered items should count as examples."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="experiment-run",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["experiment-run"],
    )
    from arf.tests.fixtures.writers import write_frontmatter_md

    numbered_examples: str = ""
    for i in range(10):
        numbered_examples += f"{i + 1}. Example item {i}\n"

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Examples\n\n"
            + numbered_examples
            + "\n"
            + "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline model implemented.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W014" not in _codes(result=result)


def test_tr_w014_mixed_bullets_and_code_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Mix of 5 bullets + 5 code blocks = 10 examples, should pass."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="experiment-run",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["experiment-run"],
    )
    mixed_examples: str = ""
    for i in range(5):
        mixed_examples += f"* Bullet example {i}\n"
    for i in range(5):
        mixed_examples += f"```text\nCode example {i}\n```\n\n"

    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Examples\n\n" + mixed_examples + "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline model implemented.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W014" not in _codes(result=result)


# ---------------------------------------------------------------------------
# TR-W013: Experiment-type classification scope
# ---------------------------------------------------------------------------


def test_tr_w013_not_emitted_for_comparative_analysis_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """comparative-analysis alone must not trip TR-W013 — it is not an experiment."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(repo_root=tmp_path, task_type_slug="comparative-analysis")
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["comparative-analysis"],
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Comparative analysis completed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W013" not in _codes(result=result)


def test_tr_w013_still_emitted_for_data_analysis(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """data-analysis remains an experiment type — TR-W013 must still fire."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="data-analysis",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["data-analysis"],
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Data analysis completed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W013" in _codes(result=result)


def test_tr_w013_still_emitted_for_baseline_evaluation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """baseline-evaluation remains an experiment type — TR-W013 must still fire."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(
        repo_root=tmp_path,
        task_type_slug="baseline-evaluation",
        overrides={"requires_result_examples": True},
    )
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["baseline-evaluation"],
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Baseline evaluation completed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W013" in _codes(result=result)


def test_tr_w013_not_emitted_for_comparative_analysis_with_other_nonexperiment_type(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """comparative-analysis + literature-review: neither is an experiment type."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_all_results(repo_root=tmp_path)
    build_task_type(repo_root=tmp_path, task_type_slug="comparative-analysis")
    build_task_type(repo_root=tmp_path, task_type_slug="literature-review")
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["comparative-analysis", "literature-review"],
    )
    write_frontmatter_md(
        path=paths.results_detailed_path(task_id=TASK_ID),
        frontmatter={"spec_version": "2", "task_id": TASK_ID},
        body=(
            "# Detailed\n\n"
            "## Summary\n\n" + ("Word " * 100) + "\n\n"
            "## Methodology\n\n"
            "The task was executed on a local machine using Python 3.12. "
            "Processing was done carefully.\n\n"
            "## Verification\n\nPassed all checks.\n\n"
            "## Limitations\n\nNone significant.\n\n"
            "## Files Created\n\n* `results/output.json`\n\n"
            "## Task Requirement Coverage\n\n"
            "* REQ-1: Done. Comparative literature review completed.\n"
        ),
    )
    result: VerificationResult = _verify()
    assert "TR-W013" not in _codes(result=result)
