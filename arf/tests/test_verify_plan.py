from pathlib import Path

import pytest

from arf.scripts.verificators import verify_plan as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.plan_builder import build_plan
from arf.tests.fixtures.task_builder import build_task_folder

TASK_ID: str = "t0001_test"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_mod.verify_plan(task_id=task_id)


class TestValidPasses:
    def test_valid_plan(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "PL-E001" in _codes(result=result)


class TestE002BadFrontmatter:
    def test_unparseable_frontmatter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        plan_dir: Path = tmp_path / "tasks" / TASK_ID / "plan"
        plan_dir.mkdir(parents=True, exist_ok=True)
        (plan_dir / "plan.md").write_text(
            "---\n: invalid yaml [\n---\n\n## Objective\nSome text.",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "PL-E002" in _codes(result=result)


class TestE003TaskIdMismatch:
    def test_task_id_mismatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={"task_id": "t9999_wrong"},
        )
        result: VerificationResult = _run()
        assert "PL-E003" in _codes(result=result)


class TestE004MissingSection:
    def test_missing_mandatory_section(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            omit_sections=["Risks & Fallbacks"],
        )
        result: VerificationResult = _run()
        assert "PL-E004" in _codes(result=result)


class TestE005Under200Words:
    def test_too_few_words(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        short_sections: dict[str, str] = {
            k: "X."
            for k in [
                "Objective",
                "Task Requirement Checklist",
                "Approach",
                "Cost Estimation",
                "Step by Step",
                "Remote Machines",
                "Assets Needed",
                "Expected Assets",
                "Time Estimation",
                "Risks & Fallbacks",
                "Verification Criteria",
            ]
        }
        short_sections["Step by Step"] = "1. Do thing."
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections=short_sections,
        )
        result: VerificationResult = _run()
        assert "PL-E005" in _codes(result=result)


class TestE006NoNumberedSteps:
    def test_no_numbered_items(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={"Step by Step": "* Do something\n* Do another"},
        )
        result: VerificationResult = _run()
        assert "PL-E006" in _codes(result=result)


class TestE007NoSpecVersion:
    def test_missing_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        plan_dir: Path = tmp_path / "tasks" / TASK_ID / "plan"
        plan_dir.mkdir(parents=True, exist_ok=True)
        (plan_dir / "plan.md").write_text(
            "---\n"
            f'task_id: "{TASK_ID}"\n'
            'date_completed: "2026-04-01"\n'
            'status: "complete"\n'
            "---\n\n"
            "# Plan\n\n"
            "## Objective\n\n" + "X " * 30 + "\n\n"
            "## Approach\n\n" + "X " * 50 + "\n\n"
            "## Cost Estimation\n\n$0 total cost.\n\n"
            "## Step by Step\n\n1. Do this\n2. Do that\n\n"
            "## Remote Machines\n\nNone required for this.\n\n"
            "## Assets Needed\n\nNo input assets.\n\n"
            "## Expected Assets\n\nOne output dataset asset.\n\n"
            "## Time Estimation\n\nAbout 1 hour total.\n\n"
            "## Risks & Fallbacks\n\n"
            "| Risk | Likelihood | Impact | Mitigation |\n"
            "|------|-----------|--------|------------|\n"
            "| Data missing | Low | High | Use backup |\n\n"
            "## Verification Criteria\n\n"
            "* Check A\n* Check B\n* Check C\n",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "PL-E007" in _codes(result=result)


class TestW001SectionBelowMinWords:
    def test_short_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={"Objective": "Short."},
        )
        result: VerificationResult = _run()
        assert "PL-W001" in _codes(result=result)


class TestW002NoRisksTable:
    def test_no_table(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Risks & Fallbacks": (
                    "There are some risks involved in this task"
                    " that we should consider carefully before"
                    " proceeding with the implementation."
                ),
            },
        )
        result: VerificationResult = _run()
        assert "PL-W002" in _codes(result=result)


class TestW003NoFrontmatter:
    def test_missing_frontmatter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        plan_dir: Path = tmp_path / "tasks" / TASK_ID / "plan"
        plan_dir.mkdir(parents=True, exist_ok=True)
        (plan_dir / "plan.md").write_text(
            "# Plan\n\n"
            "## Objective\n\n" + "X " * 30 + "\n\n"
            "## Approach\n\n" + "X " * 50 + "\n\n"
            "## Cost Estimation\n\n$0 total cost.\n\n"
            "## Step by Step\n\n1. Do step.\n\n"
            "## Remote Machines\n\nNone required for this.\n\n"
            "## Assets Needed\n\nNo input assets.\n\n"
            "## Expected Assets\n\nOne output dataset asset.\n\n"
            "## Time Estimation\n\nAbout 1 hour total.\n\n"
            "## Risks & Fallbacks\n\n"
            "| Risk | Likelihood | Impact | Mitigation |\n"
            "|------|-----------|--------|------------|\n"
            "| Data | Low | High | Backup |\n\n"
            "## Verification Criteria\n\n"
            "* Check A\n* Check B\n* Check C\n",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "PL-W003" in _codes(result=result)


class TestW004NoDollarInCost:
    def test_no_dollar(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Cost Estimation": "Zero cost, all free resources.",
            },
        )
        result: VerificationResult = _run()
        assert "PL-W004" in _codes(result=result)


class TestW005FewVerificationBullets:
    def test_fewer_than_3_bullets(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Verification Criteria": (
                    "* Check that output exists\nThat is the only verification needed."
                ),
            },
        )
        result: VerificationResult = _run()
        assert "PL-W005" in _codes(result=result)


class TestW006NoREQItems:
    def test_no_req_items(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Task Requirement Checklist": (
                    "* Train a model on SemCor\n"
                    "* Evaluate on Raganato benchmark\n"
                    "* Report per-POS F1 breakdown\n"
                    "* Document model architecture\n"
                    "These are the items for this task checklist."
                ),
            },
        )
        result: VerificationResult = _run()
        assert "PL-W006" in _codes(result=result)


class TestW007StepByStepNoREQRef:
    def test_no_req_reference_in_steps(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Step by Step": (
                    "1. Load and validate SemCor training data\n"
                    "2. Prepare sense definitions from WordNet\n"
                    "3. Train the bi-encoder model\n"
                    "4. Evaluate on all five Raganato datasets\n"
                    "5. Generate results summary and charts"
                ),
            },
        )
        result: VerificationResult = _run()
        assert "PL-W007" in _codes(result=result)


class TestW008ExpensiveOpsNoValidationGate:
    def test_expensive_ops_without_gate(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_plan(
            repo_root=tmp_path,
            task_id=TASK_ID,
            sections={
                "Step by Step": (
                    "1. Download training data\n"
                    "2. Train the model on GPU for 10 epochs\n"
                    "3. Run inference on evaluation set\n"
                    "4. Collect metrics and generate charts\n"
                    "5. Write results summary"
                ),
            },
        )
        result: VerificationResult = _run()
        assert "PL-W008" in _codes(result=result)
