import argparse
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    answer_asset_dir,
    answer_base_dir,
    answer_details_path,
)
from arf.scripts.verificators.common.reporting import (
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    VerificationResult,
)
from meta.asset_types.answer.verify_details import verify_answer_details
from meta.asset_types.answer.verify_full import verify_answer_full
from meta.asset_types.answer.verify_short import verify_answer_short


def verify_answer_asset(
    *,
    answer_id: str,
    task_id: str | None = None,
) -> VerificationResult:
    asset_dir: Path = answer_asset_dir(answer_id=answer_id, task_id=task_id)
    diagnostics: list[Diagnostic] = []
    details_path: Path = answer_details_path(answer_id=answer_id, task_id=task_id)
    details: dict[str, Any] | None = load_json_file(file_path=details_path)
    expected_question: str | None = None
    expected_confidence: str | None = None
    if details is not None:
        question_value: object = details.get("question")
        confidence_value: object = details.get("confidence")
        if isinstance(question_value, str):
            expected_question = question_value
        if isinstance(confidence_value, str):
            expected_confidence = confidence_value

    diagnostics.extend(
        verify_answer_details(
            answer_id=answer_id,
            task_id=task_id,
        ),
    )
    diagnostics.extend(
        verify_answer_short(
            answer_id=answer_id,
            expected_question=expected_question,
            task_id=task_id,
        ),
    )
    diagnostics.extend(
        verify_answer_full(
            answer_id=answer_id,
            expected_confidence=expected_confidence,
            expected_question=expected_question,
            task_id=task_id,
        ),
    )

    return VerificationResult(
        file_path=asset_dir,
        diagnostics=diagnostics,
    )


def _discover_answer_ids(*, task_id: str | None) -> list[str]:
    base_dir: Path = answer_base_dir(task_id=task_id)
    if not base_dir.exists():
        return []
    return sorted(
        directory.name
        for directory in base_dir.iterdir()
        if directory.is_dir() and not directory.name.startswith(".")
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify answer asset folder(s)",
    )
    parser.add_argument(
        "answer_id",
        nargs="?",
        default=None,
        help=(
            "Answer ID (folder name) to verify. If omitted, verifies all answers in the "
            "target directory."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "Task ID to locate answers in tasks/<task_id>/assets/answer/. If omitted, "
            "looks in top-level assets/answer/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_id: str | None = args.task_id
    answer_ids: list[str]
    if args.answer_id is not None:
        answer_ids = [args.answer_id]
    else:
        answer_ids = _discover_answer_ids(task_id=task_id)
        if len(answer_ids) == 0:
            base_dir: Path = answer_base_dir(task_id=task_id)
            print(f"No answer assets found in {base_dir}")
            sys.exit(0)

    all_passed: bool = True
    for answer_id in answer_ids:
        result: VerificationResult = verify_answer_asset(
            answer_id=answer_id,
            task_id=task_id,
        )
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
