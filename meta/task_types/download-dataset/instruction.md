# Download Dataset Instructions

## Planning Guidelines

* Record the exact download URL(s) in the plan. If the dataset requires navigating a web page to
  find the link, document the steps.
* Check whether the dataset requires authentication, account creation, or acceptance of terms of
  use. If so, create an intervention file in `intervention/` describing what the human must do.
* Identify the expected file format (ZIP, tar.gz, CSV, XML, etc.) and approximate size. Plan disk
  space accordingly.
* If the dataset has a known checksum (SHA256, MD5), record it in the plan for verification after
  download.
* Determine which dataset asset specification version to follow by reading
  `meta/asset_types/dataset/specification.md`.

## Implementation Guidelines

* Download files using `curl` or `wget` wrapped in `run_with_logs.py`. Log the HTTP status code and
  file size after download.
* Verify file integrity immediately after download: check file size is nonzero, verify checksums if
  available, and confirm the file can be decompressed or parsed.
* Extract and inspect the dataset structure. Document the number of files, records, columns, and any
  splits (train/dev/test).
* Compute basic statistics: total instances, unique labels, class distribution, average sequence
  length, or other relevant measures.
* Create the dataset asset folder under `assets/dataset/<dataset_id>/` containing `details.json`,
  the canonical description document, and `files/` following the dataset asset specification. Set
  `description_path` in `details.json`.
* Store raw downloaded files in the asset's `files/` subdirectory. Do not modify the original files;
  create processed versions separately if needed.
* Record download metadata: source URL, download date, file sizes, checksums, and any preprocessing
  applied.

## Common Pitfalls

* **Not verifying checksums**: A corrupted download produces silent errors downstream. Always verify
  file integrity before proceeding.
* **Not documenting structure**: Future tasks depend on understanding the dataset layout. Document
  column names, file formats, encoding, and any quirks (missing values, inconsistent delimiters).
* **Forgetting intervention files**: Datasets behind authentication walls or license agreements
  require human action. Create an intervention file immediately when you encounter access
  restrictions rather than trying to work around them.
* **Not recording statistics**: Raw file counts and sizes are not enough. Compute and report
  domain-relevant statistics (instance counts, label distributions, vocabulary size).
* **Modifying original files**: Keep raw downloads untouched. Apply any transformations to copies,
  and document what was changed.

## Verification Additions

* Confirm each dataset asset folder contains `details.json`, the canonical description document, and
  at least one file in `files/`.
* Verify `details.json` matches the dataset asset specification schema.
* Confirm reported file sizes and record counts match actual files.
* Run the dataset verificator if one exists.

## Related Skills

* `/implementation` -- for the download and processing steps
