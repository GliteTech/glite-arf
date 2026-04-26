# 2. Review meta/

The `/setup-project` skill populated asset types, categories, metrics, and task types under
[`meta/`](../../../meta/). Everything in `meta/` is **project-specific**. Review what setup created
before you start real work, and adjust anything that does not match the project.

## Why Customize Before Running Tasks

Every task you run will tag its outputs with these values. Metrics reported in
`results/metrics.json` must be registered in [`meta/metrics/`](../../../meta/metrics/). Papers and
tasks are filtered by [`meta/categories/`](../../../meta/categories/). Task types in
[`meta/task_types/`](../../../meta/task_types/) control which stages a task runs and include
task-type-specific instructions. Assets are validated against
[`meta/asset_types/`](../../../meta/asset_types/).

If you start running tasks with the wrong set, every result will need a correction later. Cheap
twenty minutes now, expensive backlog later.

## Step 1: Review What Setup Created

Open each subdirectory and read what is there:

```bash
ls meta/asset_types/
ls meta/categories/
ls meta/metrics/
ls meta/task_types/
```

Read at least one `description.json` from each to see the shape. Then ask yourself, for each entry:
**does this fit my project?**

## Step 2: Asset Types

The built-in asset types are `paper`, `dataset`, `library`, `model`, `answer`, `predictions`. Most
research projects keep all six. `/setup-project` may also have added project-specific asset types
through `/add-asset-type`.

* **paper** — academic papers downloaded and summarized during research. Each paper asset holds
  structured metadata (`details.json`), the PDF or markdown source, and a detailed summary written
  after reading the full text. Papers feed every later task's research stage.

* **dataset** — downloaded or generated datasets with documentation and statistics. Holds the actual
  data files (XML, CSV, JSON), a `details.json` with provenance, and a description covering content,
  annotations, splits, and usage notes. Training corpora, evaluation benchmarks, challenge sets.

* **library** — reusable Python code registered as a named asset. The code itself lives in the
  task's `code/` directory; the asset records entry points, dependencies, and API documentation so
  downstream tasks can import it. Data loaders, scorers, preprocessing utilities.

* **model** — trained machine-learning model with weights, config, and training metadata. Stores
  architecture details, hyperparameters, base-model lineage, training metrics, and the actual weight
  files (PyTorch, safetensors, ONNX). Large files tracked via Git LFS.

* **answer** — a structured response to an explicit research question. Contains a short answer (2-5
  sentences) and a full answer (a researched mini-paper with evidence from papers, internet sources,
  or code experiments). Answers are traceable back to their sources.

* **predictions** — model outputs on evaluation datasets. Stores prediction files (JSONL, CSV, TSV),
  the model and dataset that produced them, per-instance outputs, and metrics computed at creation
  time. Enables reproducible comparison and error analysis across models.

Reasons to customize:

* **Remove** a type your project will never produce (a survey project may not need `model`)
* **Add** a type for outputs the defaults do not cover (e.g., `experiment-log` for wet-lab projects,
  `figure` for a paper-writing project)

To add one, follow [How to add an asset type](../howto/add_an_asset_type.md).

## Step 3: Categories

Categories tag papers, tasks, and assets for filtering. Edit `meta/categories/` so the set matches
your project's subfields. For the tutorial project (image augmentation on CIFAR-10), you might want:

* `augmentation` — any work on data augmentation
* `baseline` — reference/baseline experiments
* `architecture` — model architecture work
* `survey` — literature surveys and reading lists

Delete any category setup added that does not apply. Add missing categories via
[How to add a category](../howto/add_a_category.md).

## Step 4: Metrics

Metrics in `results/metrics.json` must be registered in `meta/metrics/`. If you report an
unregistered key, verification fails. For MyResearch you need at least:

* `accuracy_cifar10_test` — top-1 accuracy on CIFAR-10 test set
* `efficiency_training_time_seconds` — wall-clock training time (likely already in the defaults)
* `efficiency_inference_time_per_item_seconds` — per-item inference time (likely already in the
  defaults)

Add missing metrics via [How to add a metric](../howto/add_a_metric.md). Delete metrics you will
never use.

## Step 5: Task Types

Task types control which stages `/execute-task` runs. The defaults:

* **answer-question** — answer one or more research questions with evidence-backed response assets
* **baseline-evaluation** — run a baseline or benchmark evaluation to establish reference points
* **brainstorming** — record outcomes from a human-AI brainstorming session as suggestions
* **build-model** — design, train, and evaluate a machine-learning model (often needs GPU)
* **code-reproduction** — reproduce published results by running or reimplementing original code
* **comparative-analysis** — systematically compare multiple approaches along defined dimensions
* **correction** — fix mistakes in aggregated artifacts from earlier completed tasks
* **data-analysis** — analyze existing data to extract insights, statistics, and visualizations
* **deduplication** — find and resolve duplicate assets accumulated from parallel execution
* **download-dataset** — download a dataset, verify integrity, and register it as an asset
* **download-paper** — find, download, and summarize a specific set of identified papers
* **experiment-run** — execute a complete experimental pipeline from data prep through evaluation
* **feature-engineering** — extract or generate features from data for downstream model training
* **infrastructure-setup** — set up environments, tools, or dependencies needed by other tasks
* **internet-research** — answer research questions using web sources and online documentation
* **literature-survey** — cast a wide net to discover, download, and synthesize papers on a topic
* **write-library** — create reusable Python library code registered as a library asset

Usually the defaults are fine. Reasons to add one:

* Your project has a recurring workflow the defaults do not capture (e.g., `wet-lab-run` for biology
  projects, `annotation-batch` for dataset-curation projects)
* An existing task type has instructions that conflict with your project's conventions — fork it

See [How to add a task type](../howto/add_a_task_type.md) for the recipe.

## Step 6: Commit the Changes

The how-tos run the relevant verificators but do not commit for you. After editing `meta/`:

```bash
git add meta/
git commit -m "meta: customize asset types, categories, metrics, task types for MyResearch"
git push
```

## Verification

From the repo root, run each aggregator that reads `meta/`:

```bash
uv run python -m arf.scripts.aggregators.aggregate_categories --format ids
uv run python -m arf.scripts.aggregators.aggregate_metrics --format ids
uv run python -m arf.scripts.aggregators.aggregate_task_types --format ids
```

Each should list exactly the set you intend. No more, no less.

## Next

Meta is tuned to the project. Continue to [3. Run Your First Task](03_run_your_first_task.md) to
execute the first task planned by `/setup-project`, or create a literature-survey task if setup
explicitly deferred task creation.
