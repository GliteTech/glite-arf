# Verificators Reference

Verificators validate artifacts against specifications. They live in `arf/scripts/verificators/`.
Each one returns structured diagnostics with codes. Errors block step completion. Warnings advise.

## Diagnostic Code Convention

* Format: `<PREFIX>-E<NNN>` for errors, `<PREFIX>-W<NNN>` for warnings
* Prefix: 2-3 letters identifying the artifact (e.g., `PA` = paper asset, `TG` = task git)
* Errors block step completion via prestep/poststep
* Warnings are logged but do not block

## All Verificators

| Script | Code Prefix | What It Checks |
| --- | --- | --- |
| [`verify_answer_asset.py`](../../scripts/verificators/verify_answer_asset.py) | —[^composite] | Answer asset folder structure and metadata |
| [`verify_answer_details.py`](../../scripts/verificators/verify_answer_details.py) | AA | Answer `details.json` schema and fields |
| [`verify_answer_full.py`](../../scripts/verificators/verify_answer_full.py) | AA | Canonical full answer document structure |
| [`verify_answer_short.py`](../../scripts/verificators/verify_answer_short.py) | AA | Canonical short answer document structure |
| [`verify_categories.py`](../../scripts/verificators/verify_categories.py) | CA | Category folder definitions under `meta/categories/` |
| [`verify_compare_literature.py`](../../scripts/verificators/verify_compare_literature.py) | CL | `compare_literature.md` structure and sections |
| [`verify_corrections.py`](../../scripts/verificators/verify_corrections.py) | CR | Correction files against the corrections specification |
| [`verify_daily_news.py`](../../scripts/verificators/verify_daily_news.py) | DN | Daily news files against the daily news specification |
| [`verify_dataset_asset.py`](../../scripts/verificators/verify_dataset_asset.py) | DA | Dataset asset folder structure and metadata |
| [`verify_dataset_description.py`](../../scripts/verificators/verify_dataset_description.py) | DA | Dataset canonical description document |
| [`verify_dataset_details.py`](../../scripts/verificators/verify_dataset_details.py) | DA | Dataset `details.json` schema and fields |
| [`verify_library_asset.py`](../../scripts/verificators/verify_library_asset.py) | —[^composite] | Library asset folder structure and metadata |
| [`verify_library_description.py`](../../scripts/verificators/verify_library_description.py) | LA | Library canonical description document |
| [`verify_library_details.py`](../../scripts/verificators/verify_library_details.py) | LA | Library `details.json` schema and fields |
| [`verify_logs.py`](../../scripts/verificators/verify_logs.py) | LG | Task log files against the logs specification |
| [`verify_machines_destroyed.py`](../../scripts/verificators/verify_machines_destroyed.py) | —[^composite] | Remote machine destruction and cost reconciliation |
| [`verify_metrics.py`](../../scripts/verificators/verify_metrics.py) | MT | Metric definition files under `meta/metrics/` |
| [`verify_model_asset.py`](../../scripts/verificators/verify_model_asset.py) | MA | Model asset folder structure and metadata |
| [`verify_model_description.py`](../../scripts/verificators/verify_model_description.py) | MA | Model canonical description document |
| [`verify_model_details.py`](../../scripts/verificators/verify_model_details.py) | MA | Model `details.json` schema and fields |
| [`verify_paper_asset.py`](../../scripts/verificators/verify_paper_asset.py) | PA | Paper asset folder structure and metadata |
| [`verify_paper_details.py`](../../scripts/verificators/verify_paper_details.py) | PA | Paper `details.json` schema and fields |
| [`verify_paper_summary.py`](../../scripts/verificators/verify_paper_summary.py) | PA | Paper canonical summary document structure |
| [`verify_plan.py`](../../scripts/verificators/verify_plan.py) | PL | `plan/plan.md` structure and mandatory sections |
| [`verify_pr_premerge.py`](../../scripts/verificators/verify_pr_premerge.py) | PM | Pre-merge PR readiness checks |
| [`verify_predictions_asset.py`](../../scripts/verificators/verify_predictions_asset.py) | PR | Predictions asset folder structure and metadata |
| [`verify_predictions_description.py`](../../scripts/verificators/verify_predictions_description.py) | PR | Predictions canonical description document |
| [`verify_predictions_details.py`](../../scripts/verificators/verify_predictions_details.py) | PR | Predictions `details.json` schema and fields |
| [`verify_project_budget.py`](../../scripts/verificators/verify_project_budget.py) | PB | `project/budget.json` against the project budget specification |
| [`verify_project_description.py`](../../scripts/verificators/verify_project_description.py) | PD | `project/description.md` against the project description specification |
| [`verify_research_code.py`](../../scripts/verificators/verify_research_code.py) | RC | `research/research_code.md` structure and sections |
| [`verify_research_internet.py`](../../scripts/verificators/verify_research_internet.py) | RI | `research/research_internet.md` structure and sections |
| [`verify_research_papers.py`](../../scripts/verificators/verify_research_papers.py) | RP | `research/research_papers.md` structure and sections |
| [`verify_step.py`](../../scripts/verificators/verify_step.py) | SV | A single task step against the step specification |
| [`verify_suggestions.py`](../../scripts/verificators/verify_suggestions.py) | SG | `suggestions.json` files against the suggestions specification |
| [`verify_task_complete.py`](../../scripts/verificators/verify_task_complete.py) | TC | Overall task completion readiness |
| [`verify_task_dependencies.py`](../../scripts/verificators/verify_task_dependencies.py) | TD | Task dependency existence, status, and corrections |
| [`verify_task_file.py`](../../scripts/verificators/verify_task_file.py) | TF | `task.json` schema and fields |
| [`verify_task_folder.py`](../../scripts/verificators/verify_task_folder.py) | FD | Mandatory task folder structure |
| [`verify_task_metrics.py`](../../scripts/verificators/verify_task_metrics.py) | TM | Task `metrics.json` against registered metrics |
| [`verify_task_results.py`](../../scripts/verificators/verify_task_results.py) | TR | Task result files and mandatory sections |
| [`verify_task_types.py`](../../scripts/verificators/verify_task_types.py) | TY | Task type folder definitions under `meta/task_types/` |

[^composite]: Composite verificators that delegate to per-document verificators and emit no codes of
    their own.

## Running a Verificator

```bash
uv run python -m arf.scripts.verificators.<script_name> <task_id>
```

Most verificators take a task ID. Some take additional arguments — check the script's `--help`.

## Exit Codes

* `0` — pass (no errors; warnings allowed)
* `1` — fail (one or more errors)
