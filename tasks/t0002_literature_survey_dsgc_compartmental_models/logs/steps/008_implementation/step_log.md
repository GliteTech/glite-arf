---
spec_version: "3"
task_id: "t0002_literature_survey_dsgc_compartmental_models"
step_number: 8
step_name: "implementation"
status: "completed"
started_at: "2026-04-18T23:37:33Z"
completed_at: "2026-04-18T23:59:00Z"
---
# Step 8: implementation

## Summary

Executed milestone M1 (paper downloads) and milestone M2 (synthesis answer asset) of the
plan. M1 produced exactly 20 paper assets under `assets/paper/<paper_id>/` split into
four batches: 6 seeds (BarlowLevick1965, Hines1997, Vaney2012, PolegPolsky2016,
Oesch2005, Branco2010), 4 RQ1+RQ4 compartmental modelling papers (Schachter2010,
Fohlmeister2010, Koren2017, ElQuessny2021), 6 RQ3+RQ5 E/I and tuning-curve papers
(Taylor2002, Chen2009, Park2014, Sivyer2010, Jain2020, Hanson2019), 3 RQ3
circuit/structure papers (Briggman2011, Ding2016, Sethuramanujam2016), and 1 RQ2
morphology paper (Hoshi2011). Each paper asset has a `details.json` conforming to paper
asset specification v3, a canonical `summary.md` with all nine mandatory sections, and
either the actual PDF/XML/markdown under `files/` or a `.gitkeep` plus
`download_status: "failed"` for the three paywalled papers (Chen2009, Sivyer2010,
Sethuramanujam2016). M2 produced exactly one answer asset at
`assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/` with
`details.json`, `short_answer.md`, and `full_answer.md`. The full answer document's
`## Synthesis` section contains the five mandatory `### RQ` subheadings with
quantitative targets per RQ (Na/K conductances 0.04-0.10 S/cm^2, 177 AMPA + 177 GABA
synapses, active-dendrite DSI gain from 0.3 to 0.7, mouse ON-OFF DSGC tuning-curve
targets DSI 0.7-0.85 and peak 40-80 Hz). The answer asset verificator reported
`PASSED - no errors or warnings`.

## Actions Taken

1. Spawned `/add-paper` subagents in four batches (seed batch of 6, batch A of 4, batch
   B of 6, batch C+D of 4) with one subagent per paper. Subagents ran the 6-phase
   `/add-paper` workflow (identify, metadata collection, download, details.json
   construction, summary writing, verification) and each printed the paper asset
   verificator's `PASSED` line before returning.
2. Resolved paywalled papers by recording `download_status: "failed"` with concrete
   `download_failure_reason`, placing `.gitkeep` in `files/`, and retaining the abstract
   and metadata — exactly as the paper asset specification v3 allows.
3. Worked around Windows MAX_PATH limitations on ElQuessny2021 by shortening its PDF
   filename from `el-quessny_2021_dsgc-morphology-synaptic-distribution.pdf` to
   `el-quessny_2021_dsgc-morph.pdf` and updating `details.json` `files` and `summary.md`
   Metadata accordingly.
4. Committed the four paper batches as separate commits: `a46dba7` (6 seeds), `846c334`
   (4 RQ1+RQ4), `da536f8` + `cc668ce` + `10dca6a` (RQ3+RQ5 batch B), `b7152d3` (RQ2
   batch C+D).
5. Created the answer asset folder and wrote `details.json` with the 20 paper IDs in the
   order of the plan's Paper Selection table, `spec_version: "2"`,
   `answer_id: "how-does-dsgc-literature-structure-the-five-research-questions"`,
   `confidence: "medium"`, `answer_methods: ["papers","internet"]`, six category slugs,
   and `date_created: "2026-04-18"`.
6. Wrote `short_answer.md` with YAML frontmatter and the three mandatory sections
   (Question, Answer, Sources). The `## Answer` section is 4 sentences, no inline
   citations.
7. Wrote `full_answer.md` with YAML frontmatter (including `confidence: "medium"`) and
   the nine mandatory sections (Question, Short Answer, Research Process, Evidence from
   Papers, Evidence from Internet Sources, Evidence from Code or Experiments, Synthesis,
   Limitations, Sources). The `## Synthesis` section contains five `### RQ` subheadings
   with numerical targets. The `## Sources` section lists 20 paper asset IDs with
   markdown reference link definitions resolving to each paper's `summary.md`. The
   `## Evidence from Code or Experiments` section explicitly states the method was not
   used.
8. Ran `flowmark --inplace` on `short_answer.md` and `full_answer.md` to normalize
   formatting.
9. Ran
   `uv run python -u -m meta.asset_types.answer.verificator how-does-dsgc-literature-structure-the-five-research-questions --task-id t0002_literature_survey_dsgc_compartmental_models`
   and confirmed `PASSED - no errors or warnings`.
10. Ran `grep -c "^### RQ" full_answer.md` and confirmed count is `5` (VC-5 of plan).

## Outputs

* 20 paper assets under
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/`
* 1 answer asset at
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/steps/008_implementation/step_log.md`

## Issues

Three papers (Chen2009, Sivyer2010, Sethuramanujam2016) were paywalled and could not be
downloaded from open-access mirrors; they have `download_status: "failed"` with
`download_failure_reason` populated and `.gitkeep` in `files/`. These remain valid
metadata-only paper assets under paper asset specification v3. Their abstracts were
extracted from journal landing pages and are sufficient to support the synthesis
answer's quantitative claims on RQ5 (Chen2009, Sivyer2010) and on RQ3
(Sethuramanujam2016). Flowmark's Windows temp-file name exceeds MAX_PATH inside the
worktree, so the answer markdown files were copied to `$HOME/tmp_flowmark/`, formatted
in place there, and copied back — the resulting files are byte-identical to what
flowmark would have produced in place.
