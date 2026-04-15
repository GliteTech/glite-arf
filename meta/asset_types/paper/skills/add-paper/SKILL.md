---
name: "add-paper"
description: "Download a paper, create metadata assets, and register it in the current task."
---
# Add Paper

**Version**: 2

## Goal

Download a research paper, create its structured metadata (`details.json`) and canonical summary
document, and verify the result passes all paper asset checks.

## Inputs

* `$ARGUMENTS` — any combination of: paper title, DOI, authors, year, arXiv ID. At least one of
  title, DOI, or arXiv ID is required.

## Context

Read before starting:

* `project/description.md` — project goals (guides Main Ideas and Summary sections)
* `meta/asset_types/paper/specification.md` — the authoritative paper asset format (details.json
  schema, summary document sections, folder layout)
* `arf/styleguide/markdown_styleguide.md` — formatting rules for the summary (100-char lines, `*`
  bullets, heading hierarchy, etc.)

Before assigning categories, run the category aggregator to get the full list of available
categories with their descriptions:

```bash
uv run python -u -m arf.scripts.aggregators.aggregate_categories --format json
```

## Steps

### Phase 1: Resolve Paper Identity

1. Parse `$ARGUMENTS` to extract available identifiers (title, DOI, authors, year, arXiv ID).

2. If a DOI is provided, generate the paper ID using the canonical script:

   ```bash
   uv run python -u -m arf.scripts.utils.doi_to_slug "<doi>"
   ```

3. If no DOI is provided, search for the paper using available identifiers (title + authors + year)
   via CrossRef, Semantic Scholar, or OpenAlex to resolve the DOI. Then generate the paper ID as
   above.

4. If the paper has no DOI (preprints, working papers), construct the paper ID manually:
   `no-doi_<FirstAuthorLastName><Year>_<slug>` where slug is 2-5 lowercase hyphenated words from the
   title.

5. Check if this paper already exists in the project by running:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_papers --format json --detail short
   ```
   Compare the resolved paper ID against every `paper_id` in the output. Also compare the resolved
   DOI (if any) and the normalized title (lowercase, stripped punctuation) against the `title`
   fields. If any match is found, stop and report that the paper is already in the project,
   including the matching citation key and task that added it.

### Phase 2: Collect Full Metadata

1. Query CrossRef API (`https://api.crossref.org/works/{doi}`) to get: title, authors (with
   affiliations and ORCID when available), year, journal/venue, publisher, abstract, publication
   date.
2. Query Semantic Scholar and OpenAlex for additional metadata (country affiliations, ORCID IDs,
   venue type classification).
3. Determine `venue_type` from the metadata: one of `journal`, `conference`, `workshop`, `preprint`,
   `book`, `thesis`, `technical_report`, `other`.
4. Look up author country codes (ISO 3166-1 alpha-2) from their institutional affiliations. If an
   affiliation mentions a university or organization, map it to the country. Leave as `null` when
   uncertain — do not guess.
5. For institutions that are not well-known universities (e.g., small companies, startups, labs),
   perform a web search to determine their country before giving up. If the country still cannot be
   determined after searching, omit the institution from the `institutions` list entirely rather
   than fabricating a country code. The author's `institution` field can still reference it — only
   the top-level `institutions` array requires a country.
6. Build the complete metadata record mentally. Do not write files yet.

### Phase 3: Download Paper File

1. Determine the current task ID from the task folder you are working in (e.g.,
   `0001-initial-survey`). If running outside a task context, use `manual` and place files in
   `assets/paper/<paper_id>/`.

2. Create the asset folder structure inside the task folder:

   ```text
   tasks/<task_id>/assets/paper/<paper_id>/
   └── files/
   ```

3. Invoke the `/download_paper` skill with:
   * The resolved identifiers (DOI, title, authors, year, arXiv ID)
   * `output_dir` set to `tasks/<task_id>/assets/paper/<paper_id>/files/`

4. Verify the download succeeded and the file passes basic validation (file exists, size > 10 KB,
   correct content type).

5. If the download fails, retry with alternate identifiers. If all attempts fail:
   * Keep the asset folder. Create a `.gitkeep` file in the `files/` directory so git preserves the
     empty directory.
   * Record the failure: set `download_status` to `"failed"` and `download_failure_reason` to a
     detailed explanation (which sources were tried, what errors occurred, whether the paper is
     paywalled, retracted, or simply not found online).
   * The paper asset still has value — proceed with metadata and abstract-based summary.

### Phase 4: Write details.json

1. Create `tasks/<task_id>/assets/paper/<paper_id>/details.json` following the schema in
   `meta/asset_types/paper/specification.md`.
2. Required fields — include ALL of these:
   * `spec_version` — set to `"3"`
   * `paper_id` — must match the folder name exactly
   * `doi` — original DOI with slashes, or `null`
   * `title` — full paper title
   * `url` — landing page URL (not the PDF URL)
   * `pdf_url` — direct PDF URL if known, or `null`
   * `date_published` — ISO 8601 date as precise as known, or `null`
   * `year` — publication year (integer)
   * `authors` — ordered list with `name`, `country`, `institution`, `orcid` fields per author
   * `institutions` — deduplicated list of all institutions with countries
   * `journal` — journal or conference name
   * `venue_type` — one of the allowed values
   * `categories` — category slugs from the aggregator output. Read each category's description and
     assign all categories whose scope matches the paper's topic. Use at least one category. If no
     existing category fits, use an empty list — do not invent category slugs.
   * `abstract` — full abstract text
   * `citation_key` — `FirstAuthorLastNameYear` format (e.g., `Raganato2017`); append `a`, `b` if
     another paper by the same first author in the same year already exists in the project
   * `summary_path` — canonical summary document path relative to the asset root; use `"summary.md"`
     unless there is a strong reason to choose a different name
   * `files` — relative paths to downloaded files (e.g.,
     `["files/raganato_2017_wsd-unified-eval.pdf"]`); empty list `[]` when download failed
   * `download_status` — `"success"` if file was downloaded, `"failed"` if all attempts failed
   * `download_failure_reason` — `null` when `download_status` is `"success"`; detailed explanation
     when `"failed"` (sources tried, errors encountered, paywall status)
   * `added_by_task` — the current task ID, or `"manual"` if run outside a task context
   * `date_added` — today's date in ISO 8601 format
3. Use `null` for optional fields that cannot be determined. Do not fabricate values.

### Phase 5: Read Paper and Write the Canonical Summary Document

1. Read the downloaded paper file. If PDF, extract and read the full text. If markdown or HTML, read
   directly.

2. If the paper could not be downloaded (`download_status` is `"failed"`), write the summary based
   on the abstract and any information found during metadata collection. State this limitation
   explicitly in the Overview section: "This summary is based on the abstract and publicly available
   information only; the full paper could not be downloaded."

3. Create the summary document at the path declared by `details.json` `summary_path`. The default is
   `tasks/<task_id>/assets/paper/<paper_id>/summary.md`. Use YAML frontmatter:

   ```yaml
   ---
   spec_version: "3"
   paper_id: "<paper_id>"
   citation_key: "<citation_key>"
   summarized_by_task: "<task_id or manual>"
   date_summarized: "<today>"
   ---
   ```

4. Write all 9 mandatory sections in this order. Follow the markdown style guide
   (`arf/styleguide/markdown_styleguide.md`) throughout — 100-char line length, `*` bullets, proper
   heading hierarchy, no skipped heading levels.

   `## Metadata` — quick-reference block:

   ```markdown
   * File: `files/<filename>` (or "Download failed" if no file)
   * Published: <year>
   * Authors: <names with Unicode emoji country flags (e.g., 🇮🇹 🇺🇸 🇪🇸), not
     markdown shortcodes like :flag_it:>
   * Venue: <journal/conference>
   * DOI: `<doi>` or N/A
   ```

   `## Abstract` — the paper's abstract, copied verbatim from the original paper. Do not paraphrase,
   reword, or summarize. If the paper could not be downloaded, copy the abstract from
   `details.json`.

   `## Overview` — 2-5 paragraphs in your own words describing what the paper does and finds. This
   section must be written after reading the full paper, not just the abstract. It must cover
   methodology, key results, and significance — information that goes well beyond what the paper's
   abstract contains. Do NOT paraphrase or reword the paper's abstract — write an original overview
   based on the full paper content. If the paper could not be downloaded, this must be explicitly
   stated and the section should acknowledge its limitations. Minimum 100 words.

   `## Architecture, Models and Methods` — detailed methodology: algorithms, architectures, training
   procedures, hyperparameters, sample sizes, evaluation metrics, hardware specs. Include specific
   numbers. Minimum 150 words. If the paper was not downloaded, write what can be inferred from the
   abstract and note "Full methodology not available — paper not downloaded."

   `## Results` — bullet points with specific quantitative values. Every metric the paper reports
   that matters. Minimum 5 bullet points. Use bold for numbers such as `\*\*71.3 F1\*\*`. If the
   paper was not downloaded and results are unavailable, write "Results not available — paper not
   downloaded. Abstract reports: <whatever the abstract says>."

   `## Innovations` — named `###` subheadings for each novel contribution. Explain what is new and
   why it matters.

   `## Datasets` — dataset names, sizes, languages, licenses, availability. For theoretical papers:
   "This is a theoretical paper; no datasets were used."

   `## Main Ideas` — bullet points of actionable takeaways for this project. Minimum 3 bullet
   points.

   `## Summary` — exactly 4 paragraphs:
   1. What the paper does (research question, scope, motivation)
   2. How it does it (methodology, key design decisions)
   3. What it finds (headline results, significance)
   4. Why it matters for this project (practical implications) Minimum 200 words total.

5. **NEVER** fabricate results, metrics, or claims. If you cannot determine a value from the paper,
   write "Not reported in the paper."

6. **NEVER** use vague language ("good results", "improved significantly"). Use specific numbers.

### Phase 6: Verify

1. Run the paper asset verificator with the task ID:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_paper_asset "<paper_id>" \
     --task-id "<task_id>"
   ```

2. If there are errors, fix them and re-run until all errors are resolved.

3. Warnings are acceptable but review each one — fix any that are easy to address (e.g., missing
   author countries that can be looked up).

## Done When

* `tasks/<task_id>/assets/paper/<paper_id>/details.json` exists with all required fields populated.
* The canonical summary document exists with all 9 mandatory sections, YAML frontmatter, and minimum
  word/bullet counts met.
* `tasks/<task_id>/assets/paper/<paper_id>/files/` contains at least one paper file when
  `download_status` is `"success"`, or is empty with `download_failure_reason` populated when
  `"failed"`.
* The verificator (`verify_paper_asset.py`) passes with zero errors.
* The `citation_key` in the canonical summary document frontmatter matches `details.json`.
* The `paper_id` in both files matches the folder name.

## Forbidden

* NEVER fabricate metadata (authors, DOI, year, institutions). Use `null` for unknown values.
* NEVER fabricate paper results or metrics. Quote only what the paper reports.
* NEVER skip reading the paper before writing the summary. If the paper cannot be downloaded, state
  this explicitly in the summary.
* NEVER write summary sections with vague qualifiers instead of specific numbers ("results were
  good" instead of "achieved \*\*71.3 F1\*\*").
* NEVER skip the verification step (Phase 6).
* NEVER use `-` for bullet points in the canonical summary document. Use `*` per the markdown style
  guide.
* NEVER exceed 100 characters per line in the canonical summary document (except URLs and table
  rows).
* NEVER set `download_status` to `"failed"` without providing a `download_failure_reason`.
