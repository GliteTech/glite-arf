# Download Paper Instructions

## Planning Guidelines

* List each paper to download with its DOI (preferred) or title and authors if no DOI is available.
* Read `meta/asset_types/paper/specification.md` before starting. The paper asset spec defines the
  exact folder structure, `details.json` schema, and canonical summary document section
  requirements.
* Generate paper IDs using `uv run python -u -m arf.scripts.utils.doi_to_slug <doi>` for DOI-based
  papers. For papers without a DOI, use the `no-doi_<AuthorYear>_<slug>` format defined in the spec.
* Check existing paper assets (run the paper aggregator) to avoid downloading duplicates.

## Implementation Guidelines

* Use the `/download_paper` or `/add-paper` skills for each paper. These skills handle the download,
  metadata extraction, and asset creation workflow.
* For each paper, create the asset folder at `assets/paper/<paper_id>/` containing `details.json`,
  the canonical summary document, and `files/` with the downloaded PDF.
* Fill `details.json` completely: all required fields including `spec_version`, `paper_id`, `doi`,
  `title`, `authors`, `institutions`, `venue_type`, `categories`, `abstract`, `citation_key`,
  `summary_path`, `files`, `download_status`, and `added_by_task`.
* Write the canonical summary document after reading the full paper, not just the abstract. The
  summary must contain all mandatory sections: Metadata, Abstract, Overview,
  Architecture/Models/Methods, Results, Innovations, Datasets, Main Ideas, and Summary.
* The Overview section must go beyond the abstract. It should reflect knowledge gained from reading
  the full paper text.
* The Results section must contain at least 5 bullet points with specific quantitative values (F1
  scores, accuracy, etc.).
* If a paper cannot be downloaded, set `download_status` to `"failed"`, provide
  `download_failure_reason`, and write the summary based on available information (abstract, related
  papers). State explicitly that the full paper was not available.

## Common Pitfalls

* **Wrong DOI format**: Always use `arf.scripts.utils.doi_to_slug` to convert DOIs to folder names.
  Manual conversion often misses edge cases like parentheses or multiple slashes.
* **Incomplete summaries**: Summaries that paraphrase only the abstract violate the spec. The
  Overview and Architecture sections must contain information from the full paper body.
* **Not running the paper verificator**: Run
  `uv run python -m arf.scripts.verificators.verify_paper_asset --task-id $TASK_ID <paper_id>` after
  creating each paper asset. It catches missing fields, format errors, and section omissions.
* **Missing quantitative results**: Vague statements like "results were good" are not acceptable.
  Extract specific numbers from the paper's results tables and include them in the Results section.
* **Forgetting `spec_version`**: Both `details.json` and the canonical summary document frontmatter
  must include `spec_version` matching the current paper asset specification version.

## Verification Additions

* Run `uv run python -m arf.scripts.verificators.verify_paper_asset --task-id $TASK_ID <paper_id>`
  for each paper.
* Confirm `details.json` passes schema validation with no errors.
* Confirm the canonical summary document contains all mandatory sections.
* Confirm `paper_id` in both files matches the folder name.
* Confirm `files/` contains the PDF when `download_status` is `"success"`.

## Related Skills

* `/download_paper` -- downloads and creates a paper asset from a URL
* `/add-paper` -- adds a paper asset with metadata and summary
