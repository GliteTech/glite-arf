# Asset Types Reference

Asset types are defined per project under `meta/asset_types/`. The framework provides this
mechanism; the set of types is up to the project. The defaults below ship with most ARF projects as
boilerplate. Add, remove, or modify them as your project needs — see
[How to add an asset type](../howto/add_an_asset_type.md).

Every asset lives inside the task that produced it, under
`tasks/<task_id>/assets/<type>/<asset_id>/`. Each type has its own spec in
`meta/asset_types/<type>/specification.md`.

## Default Asset Types

### Paper

Spec: [`meta/asset_types/paper/specification.md`](../../../meta/asset_types/paper/specification.md)

```text
tasks/<task_id>/assets/paper/<paper_id>/
├── details.json       # Metadata (DOI, title, authors, year, venue, etc.)
├── summary.md         # Canonical summary document
└── files/             # PDF, markdown conversion, supporting files
```

Paper ID format: DOI-based (via `doi_to_slug`) or `no-doi_<Author><Year>_<slug>`.

### Dataset

Spec:
[`meta/asset_types/dataset/specification.md`](../../../meta/asset_types/dataset/specification.md)

```text
tasks/<task_id>/assets/dataset/<dataset_id>/
├── details.json       # Metadata (name, size, source, license, etc.)
├── description.md     # Canonical description document
└── files/             # Dataset files (required, at least one)
```

### Library

Spec:
[`meta/asset_types/library/specification.md`](../../../meta/asset_types/library/specification.md)

```text
tasks/<task_id>/assets/library/<library_id>/
├── details.json       # Metadata (module paths, entry points, etc.)
└── description.md     # Canonical description document
```

Library code lives in `tasks/<task_id>/code/` and is referenced via `module_paths` in
`details.json`. No `files/` directory.

### Model

Spec: [`meta/asset_types/model/specification.md`](../../../meta/asset_types/model/specification.md)

```text
tasks/<task_id>/assets/model/<model_id>/
├── details.json       # Metadata (architecture, training, metrics, etc.)
├── description.md     # Canonical description document
└── files/             # Weights, configs, tokenizer files (required)
```

### Answer

Spec:
[`meta/asset_types/answer/specification.md`](../../../meta/asset_types/answer/specification.md)

```text
tasks/<task_id>/assets/answer/<answer_id>/
├── details.json       # Metadata (question, sources, confidence, etc.)
├── short_answer.md    # Canonical short answer document
└── full_answer.md     # Canonical full answer document
```

### Predictions

Spec:
[`meta/asset_types/predictions/specification.md`](../../../meta/asset_types/predictions/specification.md)

```text
tasks/<task_id>/assets/predictions/<predictions_id>/
├── details.json       # Metadata (model, dataset, run config, etc.)
├── description.md     # Canonical description document
└── files/             # Prediction output files (required, at least one)
```

## Common Rules

* The top-level `assets/<type>/` directory is reserved for aggregator output — tasks must never
  write there directly.
* Every asset folder contains a `details.json` with a `spec_version` field.
* Canonical document paths are declared in `details.json` via `*_path` fields.
* Asset IDs must be valid folder names and stable across the project.
