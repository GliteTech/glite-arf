from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import (
    write_frontmatter_md,
    write_json,
    write_text,
)

SPEC_VERSION_RESULTS: str = "2"
DEFAULT_DATE_COMPLETED: str = "2026-04-01"

DEFAULT_RESULTS_SUMMARY: str = (
    "# Results Summary\n"
    "\n"
    "## Summary\n"
    "\n"
    "This task completed successfully and produced all expected outputs."
    " The primary objective was achieved with results that meet the"
    " verification criteria defined in the plan. All assets were"
    " generated and validated against the specification requirements.\n"
    "\n"
    "## Metrics\n"
    "\n"
    "* Overall accuracy reached the expected threshold for this task\n"
    "* Processing completed within the estimated time budget\n"
    "* All output files conform to the required format specifications\n"
    "\n"
    "## Verification\n"
    "\n"
    "All verificator checks passed without errors. Output files exist"
    " in the expected locations and contain valid data structures.\n"
)

DEFAULT_RESULTS_DETAILED_BODY: str = (
    "# Results Detailed\n"
    "\n"
    "## Summary\n"
    "\n"
    "This task was completed successfully. The implementation followed"
    " the approved plan and produced all expected assets. Results are"
    " documented below with full methodology and verification details.\n"
    "\n"
    "## Methodology\n"
    "\n"
    "The task was executed on a local development machine using Python"
    " 3.12 and the project's standard toolchain. Processing began at"
    " 2026-04-01T00:00:00Z and completed at 2026-04-01T01:00:00Z."
    " The approach followed the step-by-step plan without deviations."
    " All intermediate results were logged in the logs directory.\n"
    "\n"
    "## Verification\n"
    "\n"
    "All output files were validated against their respective"
    " specifications. The verificator script ran without errors."
    " File checksums and line counts were recorded for reproducibility.\n"
    "\n"
    "## Limitations\n"
    "\n"
    "No significant limitations were encountered during execution."
    " The results are representative of the expected output quality.\n"
    "\n"
    "## Files Created\n"
    "\n"
    "* `results/results_summary.md` — high-level summary\n"
    "* `results/results_detailed.md` — this file\n"
    "* `results/metrics.json` — quantitative metrics\n"
    "* `results/costs.json` — cost breakdown\n"
    "* `results/remote_machines_used.json` — machine usage\n"
    "\n"
    "## Task Requirement Coverage\n"
    "\n"
    "All task requirements from the original task description have been"
    " addressed. Each requirement was mapped to specific outputs and"
    " verified against the acceptance criteria in the plan.\n"
)

DEFAULT_COSTS_PAYLOAD: dict[str, object] = {
    "total_cost_usd": 0.0,
    "breakdown": {},
}


def build_results_summary(
    *,
    repo_root: Path,
    task_id: str,
    content: str | None = None,
) -> Path:
    summary_path: Path = paths.results_summary_path(task_id=task_id)
    write_text(
        path=summary_path,
        content=content if content is not None else DEFAULT_RESULTS_SUMMARY,
    )
    return summary_path


def build_results_detailed(
    *,
    repo_root: Path,
    task_id: str,
    body: str | None = None,
    frontmatter_overrides: dict[str, str | int] | None = None,
) -> Path:
    frontmatter: dict[str, str | int] = {
        "spec_version": SPEC_VERSION_RESULTS,
        "task_id": task_id,
    }
    if frontmatter_overrides is not None:
        frontmatter.update(frontmatter_overrides)

    detailed_path: Path = paths.results_detailed_path(task_id=task_id)
    write_frontmatter_md(
        path=detailed_path,
        frontmatter=frontmatter,
        body=(body if body is not None else DEFAULT_RESULTS_DETAILED_BODY),
    )
    return detailed_path


def build_metrics_file(
    *,
    repo_root: Path,
    task_id: str,
    payload: dict[str, object] | None = None,
) -> Path:
    metrics_path: Path = paths.metrics_path(task_id=task_id)
    write_json(
        path=metrics_path,
        data=payload if payload is not None else {},
    )
    return metrics_path


def build_costs_file(
    *,
    repo_root: Path,
    task_id: str,
    payload: dict[str, object] | None = None,
) -> Path:
    costs_path: Path = paths.costs_path(task_id=task_id)
    write_json(
        path=costs_path,
        data=payload if payload is not None else dict(DEFAULT_COSTS_PAYLOAD),
    )
    return costs_path


def build_remote_machines_file(
    *,
    repo_root: Path,
    task_id: str,
    payload: list[object] | None = None,
) -> Path:
    machines_path: Path = paths.remote_machines_path(task_id=task_id)
    write_json(
        path=machines_path,
        data=payload if payload is not None else [],
    )
    return machines_path


def build_results_images_dir(
    *,
    repo_root: Path,
    task_id: str,
) -> Path:
    images_path: Path = paths.results_images_dir(task_id=task_id)
    images_path.mkdir(parents=True, exist_ok=True)
    return images_path
