---
spec_version: "2"
task_id: "t0002_literature_survey_dsgc_compartmental_models"
date_completed: "2026-04-19"
status: "complete"
---
# Plan: Literature Survey of Compartmental Models of DS Retinal Ganglion Cells

## Objective

Produce a self-contained literature survey of compartmental models of direction-selective retinal
ganglion cells (DSGCs) that covers all five project research questions (RQ1 Na/K conductances, RQ2
morphology sensitivity, RQ3 AMPA/GABA balance, RQ4 active vs passive dendrites, RQ5
angle-to-AP-frequency tuning curves). The deliverable is 20 paper assets under
`assets/paper/<paper_id>/` plus exactly one synthesis answer asset under
`assets/answer/<answer_id>/` that explicitly answers each RQ with quantitative targets and
model-design guidance. "Done" means every paper asset passes the paper asset verificator with zero
errors, the answer asset passes the answer asset verificator with zero errors and addresses each of
the five RQs in its canonical full answer document, and the six seed references from
`project/description.md` are among the downloaded papers. Downstream tasks (t0004 target tuning
curve generator, t0005 morphology download, later Na/K optimisation and active-vs-passive dendrite
experiments) depend on these assets.

## Task Requirement Checklist

The operative task text from `tasks/t0002_literature_survey_dsgc_compartmental_models/task.json`
plus the long description file `task_description.md` is:

```text
Name: "Literature survey: compartmental models of DS retinal ganglion cells"
Short description: "Survey published compartmental models of direction-selective retinal ganglion
cells to inform all five project research questions."
Task types: ["literature-survey"]
Expected assets: paper=20, answer=1
Dependencies: []

Scope (from task_description.md):
- Cover all five project research questions at survey level:
  1. RQ1 Na/K combinations
  2. RQ2 morphology sensitivity
  3. RQ3 AMPA/GABA balance
  4. RQ4 active vs passive dendrites
  5. RQ5 angle-to-AP-frequency tuning curves
- Include the six references already listed in project/description.md (Barlow & Levick 1965,
  Hines & Carnevale 1997, Vaney/Sivyer/Taylor 2012, Poleg-Polsky & Diamond 2016,
  Oesch/Euler/Taylor 2005, Branco/Clark/Häusser 2010).
- Add at least 14 more papers found by internet search, spread across the five RQs.
- Prefer papers with a clearly described compartmental model, published morphology, or
  quantitative angle-to-rate measurements.

Expected outputs:
- ~20 paper assets under assets/paper/ (each with details.json, summary.md, and the paper file
  under files/).
- One answer asset under assets/answer/ synthesising all five RQs.

Compute and budget: No external cost. Local LLM CLI only; no paid APIs or remote machines.
Verification: ≥20 paper assets pass verify_paper_asset; answer asset passes verify_answer_asset
and explicitly addresses each of the five RQs.
```

### Requirement items

* **REQ-1** — Produce exactly 20 paper assets under
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/<paper_id>/`, each with
  `details.json`, a canonical summary document (default `summary.md`), and the paper file under
  `files/` (or `.gitkeep` plus `download_status: "failed"` when the PDF is unavailable). Evidence:
  `ls assets/paper/` shows 20 subfolders and the paper verificator passes for each. Satisfied by
  Steps 3-7 (milestone M1) and Step 10 (verification).

* **REQ-2** — Include all six seed references from `project/description.md` among the 20 paper
  assets: BarlowLevick1965, Hines1997, Vaney2012, PolegPolsky2016, Oesch2005, Branco2010. Evidence:
  each of the six expected paper IDs (`10.1113_jphysiol.1965.sp007638`,
  `10.1162_neco.1997.9.6.1179`, `10.1038_nrn3165`, `10.1016_j.neuron.2016.02.013`,
  `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664`) is present in `assets/paper/`.
  Satisfied by Step 3 (milestone M1 seed batch).

* **REQ-3** — Add at least 14 additional peer-reviewed papers beyond the six seeds (14 + 6 = 20
  total). The full candidate list of 22 discovered papers is catalogued in
  `tasks/t0002_literature_survey_dsgc_compartmental_models/research/research_internet.md` under
  `## Discovered Papers`. The 14 chosen for download are listed in the Approach section's Paper
  Selection table. Evidence: `ls assets/paper/` returns exactly 20 folders; the 14 non-seed IDs
  match the Approach selection. Satisfied by Steps 4-7 (milestone M1 non-seed batches).

* **REQ-4** — Spread the 14 non-seed papers across all five RQs. Each RQ must be covered by at
  least two non-seed papers (seeds already cover RQ1, RQ4, RQ5 via Fohlmeister-like parameters in
  PolegPolsky2016 and Oesch2005; RQ2 and RQ3 need explicit non-seed coverage). Evidence: the Paper
  Selection table in the Approach section maps each paper to one or more RQs and shows ≥2 non-seed
  papers per RQ. Satisfied by the Approach selection and verified at Step 10.

* **REQ-5** — Prefer papers with (a) a clearly described compartmental model, (b) a published
  morphology, or (c) quantitative angle-to-rate measurements. Every selected paper must satisfy at
  least one criterion; this is documented in the "selection criterion" column of the Paper Selection
  table. Evidence: the Paper Selection table shows each paper's criterion. Satisfied by the Approach
  selection and confirmed by each paper's summary document.

* **REQ-6** — Each paper asset must conform to `meta/asset_types/paper/specification.md` v3:
  folder is `assets/paper/<paper_id>/`, `details.json` has every required field (including
  `spec_version: "3"`, `summary_path`, `files`, `download_status`), the canonical summary document
  contains all mandatory sections (Metadata, Abstract, Overview, Architecture/Models/Methods,
  Results, Innovations, Datasets, Main Ideas, Summary), and the paper file in `files/` is the real
  PDF when downloadable. Evidence: `verify_paper_asset.py` reports zero errors. Satisfied by Steps
  3-7 (creation) and Step 10 (verification).

* **REQ-7** — Produce exactly one answer asset under
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/<answer_id>/` that
  synthesises findings across all five RQs. The answer ID will be
  `how-does-dsgc-literature-structure-the-five-research-questions`. The canonical full answer
  document must have a dedicated subsection for each of RQ1, RQ2, RQ3, RQ4, RQ5 inside
  `## Synthesis`, each with quantitative targets or model-design conclusions drawn from the 20
  papers. Evidence: `verify_answer_asset.py` passes and the full answer document has five RQ
  subsections. Satisfied by Steps 8-9 and Step 10.

* **REQ-8** — The answer asset must conform to `meta/asset_types/answer/specification.md` v2:
  `details.json` has `spec_version: "2"`, the question, `short_title`, `short_answer_path`,
  `full_answer_path`, categories from `meta/categories/`, `answer_methods`, evidence lists
  (`source_paper_ids` containing the 20 paper IDs from REQ-1), `confidence`, `created_by_task`,
  `date_created`; the short answer has Question/Answer/Sources; the full answer has Question, Short
  Answer, Research Process, Evidence from Papers, Evidence from Internet Sources, Evidence from Code
  or Experiments, Synthesis, Limitations, Sources. Evidence: `verify_answer_asset.py` passes.
  Satisfied by Steps 8-9 and Step 10.

* **REQ-9** — Zero external cost (no paid APIs, no remote machines, no GPU). Only public paper
  downloads and local LLM CLI use. Evidence: `results/costs.json` reports `$0.00`. Satisfied by the
  Cost Estimation section; the orchestrator writes `costs.json` after Step 10 finishes.

## Approach

### Strategy

This is the project's first research task, so there are no prior paper assets to reuse. Paper
selection draws the full candidate list from `research/research_internet.md`'s
`## Discovered Papers` section, which catalogues 22 peer-reviewed candidates across the five RQs.
Two of the 22 are downgraded to "not downloaded this task" so the total lands at exactly 20 (see
Paper Selection table below). Each selected paper is downloaded and turned into a paper asset via
the `/add-paper` skill, one paper per `/add-paper` invocation. Each invocation runs in its own
subagent so the 20 papers can proceed in batches without polluting the orchestrator's context.

The synthesis answer asset is produced last, after all 20 paper assets exist, so its
`## Evidence from Papers` section can cite real asset IDs (not drafts).

### Paper selection

The 20 papers to download are selected from the 22 candidates in `research/research_internet.md`.
The two candidates held back are [ModelDB-PP2016] (a ModelDB database entry, not a peer-reviewed
paper — it is a code asset and belongs to a later task) and [Branco2010-MDB] (same reason). This
leaves 20 peer-reviewed papers: the 6 seeds plus 14 additional papers. The 14 additional papers are
spread across the five RQs, with every RQ covered by at least two non-seed papers.

| Paper ID (slug) | Citation | RQ(s) covered | Selection criterion (a/b/c per REQ-5) |
| --- | --- | --- | --- |
| `10.1113_jphysiol.1965.sp007638` | BarlowLevick1965 (seed) | RQ3, RQ5 | c quantitative DS measurements |
| `10.1162_neco.1997.9.6.1179` | Hines1997 (seed) | (methods) | a compartmental model simulator |
| `10.1038_nrn3165` | Vaney2012 (seed) | RQ1-RQ5 | review grounding every RQ |
| `10.1016_j.neuron.2016.02.013` | PolegPolsky2016 (seed) | RQ1, RQ3, RQ4 | a compartmental DSGC model, b published morphology |
| `10.1016_j.neuron.2005.06.036` | Oesch2005 (seed) | RQ4, RQ5 | c dendritic-spike patch-clamp data |
| `10.1126_science.1189664` | Branco2010 (seed) | RQ2, RQ4 | a cable-theory model |
| `10.1371_journal.pcbi.1000899` | Schachter2010 | RQ1, RQ4 | a compartmental DSGC model with active dendrites |
| `10.1152_jn.00123.2009` | Fohlmeister2010 | RQ1 | a ion-channel model with densities |
| `10.1523_JNEUROSCI.22-17-07712.2002` | Taylor2002 | RQ3, RQ5 | c voltage-clamp E/I measurements |
| `10.1113_jphysiol.2008.161240` | Chen2009 | RQ5 | c tuning-curve and DSI data |
| `10.1523_JNEUROSCI.5017-13.2014` | Park2014 | RQ3, RQ5 | c E/I and tuning-curve data |
| `10.1038_nature09818` | Briggman2011 | RQ3 | b SBEM morphology reconstruction |
| `10.1038_nature18609` | Ding2016 | RQ3 | b cross-species morphology + network model |
| `10.1113_jphysiol.2010.192716` | Sivyer2010 | RQ5 | c velocity-dependent tuning curves |
| `10.1002_cne.22678` | Hoshi2011 | RQ2 | b morphological ON DSGC characterisation |
| `10.1016_j.neuron.2017.07.020` | Koren2017 | RQ2, RQ4 | a cross-compartmental DSGC model |
| `10.1523_ENEURO.0261-21.2021` | ElQuessny2021 | RQ2 | a morphology-swap simulation |
| `10.7554_eLife.52949` | Jain2020 | RQ3, RQ4 | c dendritic Ca2+ and E/I imaging |
| `10.7554_eLife.42392` | Hanson2019 | RQ3 | c circuit-level DS without SAC asymmetry |
| `10.1016_j.neuron.2016.04.041` | Sethuramanujam2016 | RQ3 | c mixed ACh/GABA transmission data |

Non-seed RQ coverage (14 papers): RQ1 has 2 (Schachter2010, Fohlmeister2010); RQ2 has 4 (Hoshi2011,
Koren2017, ElQuessny2021, Branco2010 via cable theory also covers it via seed — counting only
non-seeds gives 3); RQ3 has 7 (Taylor2002, Park2014, Briggman2011, Ding2016, Jain2020, Hanson2019,
Sethuramanujam2016); RQ4 has 3 (Schachter2010, Koren2017, Jain2020); RQ5 has 4 (Taylor2002,
Chen2009, Park2014, Sivyer2010). Every RQ has ≥2 non-seed papers. REQ-4 is satisfied.

### Answer asset design

Exactly one answer asset is produced:

* **answer_id**: `how-does-dsgc-literature-structure-the-five-research-questions`
* **question**: "How does the existing peer-reviewed literature on compartmental models of
  direction-selective retinal ganglion cells structure the five project research questions (Na/K
  conductances, morphology sensitivity, AMPA/GABA balance, active vs passive dendrites, and
  angle-to-AP-frequency tuning curves), and what quantitative targets does it provide?"
* **short_title**: "DSGC literature structure of the five RQs"
* **answer_methods**: `["papers", "internet"]` — the evidence comes from the 20 paper assets plus
  the internet research document.
* **categories**:
  `["direction-selectivity", "compartmental-modeling", "retinal-ganglion-cell", "dendritic-computation", "synaptic-integration", "voltage-gated-channels"]`.
* **confidence**: `medium` — evidence is strong for RQ3-RQ5 but sparse for an explicit (g_Na, g_K)
  grid (RQ1) and for a factorial morphology sweep (RQ2).
* **source_paper_ids**: all 20 paper IDs from REQ-1.
* **source_urls**: 0-2 ModelDB URLs that the research document references for code availability.

The canonical full answer document's `## Synthesis` section will contain five subheadings —
`### RQ1 Na/K conductances`, `### RQ2 morphology sensitivity`, `### RQ3 AMPA/GABA balance`,
`### RQ4 active vs passive dendrites`, `### RQ5 angle-to-AP-frequency tuning curves` — each with
the quantitative targets surfaced by `research/research_internet.md` (DSI 0.7-0.85, peak rate 40-80
Hz, null residual < 10 Hz, half-width 60-90 deg, 177 AMPA + 177 GABA synapses, g_Na peak 0.04-0.10
S/cm^2, etc.). This directly addresses REQ-7.

### Alternatives considered

* **Separate answer asset per RQ (5 answers).** Rejected because `task.json`'s
  `expected_assets.answer` is `1` and the orchestrator-level metrics and verificator expect one
  answer asset. A single synthesis answer with five clearly titled subsections satisfies the same
  browseability goal without violating the expected-assets count.
* **Downloading all 22 candidates from `research/research_internet.md` for a total of 22 paper
  assets.** Rejected because `task.json`'s `expected_assets.paper` is exactly `20` and because the
  two excluded items ([ModelDB-PP2016], [Branco2010-MDB]) are ModelDB database entries, not
  peer-reviewed papers — they are better modelled as code/model assets in a later implementation
  task.
* **Using a spreadsheet or standalone markdown table in `research/` instead of paper assets.**
  Rejected because downstream tasks (t0004 target tuning-curve generator, t0005 morphology download)
  consume paper assets via aggregators, not ad-hoc markdown. The paper asset format is the project's
  canonical distribution mechanism.

### Task type and type guidance

The task type is `literature-survey` (already set in `task.json`). The type's Planning Guidelines at
`meta/task_types/literature-survey/instruction.md` required: (a) setting a target number of papers
— done at 20; (b) defining search scope — done in `research/research_internet.md`; (c) checking
existing paper assets via `aggregate_papers.py` — done in the research document (corpus is empty);
(d) using `/add-paper` for each selected paper — step 3 onward in Step by Step. The type's Common
Pitfalls list flagged citation fabrication and shallow coverage; both are mitigated by reading every
downloaded PDF in full before writing the summary and by the Paper Selection table requiring ≥2
non-seed papers per RQ.

### Grounding in research findings

Key numbers from `research/research_internet.md` that drive the answer asset's Synthesis:

* RQ1: Fohlmeister-Miller 2010 parameter set with peak somatic g_Na ~0.04-0.10 S/cm^2, g_K (delayed
  rectifier) ~0.012 S/cm^2, g_K,A ~0.036 S/cm^2, g_K,Ca ~0.001 S/cm^2 calibrated at 7-37 deg C from
  [Fohlmeister2010]. No published grid search of (g_Na, g_K) pairs for DSGC.
* RQ2: ElQuessny2021 simulation result — global DSGC dendritic morphology has only a minor effect
  on E/I distribution; local dendritic electrotonics still matter per Schachter2010.
* RQ3: Mouse ON-OFF DSGC null-direction inhibition is 3-5x larger than preferred inhibition
  ([Park2014, Taylor2002]); 177 AMPA + 177 GABA synapses on a reconstructed DSGC in
  [PolegPolsky2016].
* RQ4: Active dendrites (with Fohlmeister-like densities) boost DSI from ~0.3 to ~0.7 in
  [Schachter2010]; TTX-sensitive dendritic Na+ spikes in [Oesch2005].
* RQ5: Adult mouse ON-OFF DSGC preferred peak 40-80 Hz, null 3-10 Hz, DSI 0.6-0.9, half-width 60-90
  deg ([Chen2009, Park2014]).

## Cost Estimation

Total estimated cost: **$0.00**, which is at or under the project's `per_task_default_limit` of
`$0.00` defined in `project/budget.json`.

Itemized breakdown:

* **External paper downloads**: $0.00. All 20 papers are either open-access or reachable via journal
  URLs that `research/research_internet.md` has already verified. When a paper is behind a paywall,
  the task will mark `download_status: "failed"` with a `download_failure_reason` and retain only
  the abstract (per `meta/asset_types/paper/specification.md` v3). No paid subscription will be
  used.
* **LLM API calls**: $0.00. The `/add-paper` skill and all summary generation run on the local
  Claude Code CLI inside the user's existing subscription — no paid API calls are triggered. No
  Anthropic SDK or third-party model API is invoked.
* **Remote compute**: $0.00. See `## Remote Machines` for reasoning.
* **Storage**: $0.00. 20 PDFs + metadata fit well within local disk.

Compared against `project/budget.json` `total_budget` of $0.00, the task is on-budget.

## Step by Step

The steps below are grouped into three milestones: **M1 Paper downloads** (Steps 3-7), **M2
Synthesis answer** (Steps 8-9), **M3 Verification** (Step 10). Steps 1-2 are setup.

Steps 1-2 assume the orchestrator has already produced the research stage outputs at
`tasks/t0002_literature_survey_dsgc_compartmental_models/research/research_internet.md`; if that
file is missing, stop and create an intervention file — do not proceed.

1. **Confirm research inputs and category list.** Read
   `tasks/t0002_literature_survey_dsgc_compartmental_models/research/research_internet.md` and
   confirm the `## Discovered Papers` section contains 22 entries. Run
   `uv run python -u -m arf.scripts.aggregators.aggregate_categories --format json` and confirm all
   of `direction-selectivity`, `compartmental-modeling`, `retinal-ganglion-cell`,
   `dendritic-computation`, `synaptic-integration`, `voltage-gated-channels`, `patch-clamp`,
   `cable-theory` are present (eight categories total). Expected output: the aggregator returns
   these eight category slugs. If a category is missing, stop and create an intervention file under
   `intervention/` — do not invent or substitute categories. Satisfies REQ-6, REQ-8.

2. **Confirm the paper corpus is empty.** Instead of running `aggregate_papers.py` (the aggregator
   script does not exist in this worktree), list `assets/paper/` in every prior task:
   `ls tasks/*/assets/paper/ 2>/dev/null`. Expected output: empty. If any prior paper asset exists,
   cross-check its `details.json` `paper_id` against the 20 target IDs in the Approach's Paper
   Selection table and drop any already-downloaded paper from the download list before Step 3.
   Satisfies REQ-1 (prevents duplicates).

3. **Download the six seed papers (milestone M1 seed batch).** For each of the six seed paper IDs
   (`10.1113_jphysiol.1965.sp007638`, `10.1162_neco.1997.9.6.1179`, `10.1038_nrn3165`,
   `10.1016_j.neuron.2016.02.013`, `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664`), spawn
   a separate subagent running the `/add-paper` skill once per paper with the paper's DOI passed as
   `$ARGUMENTS`. Each subagent creates
   `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/<paper_id>/` with
   `details.json`, `summary.md`, and `files/<author>_<year>_<slug>.pdf` (or a `.gitkeep` plus
   `download_status: "failed"` if the PDF is paywalled). Expected observable output: six new
   subfolders under `assets/paper/`, each with the three required artifacts. The subagent prints a
   PASS message from the paper asset verificator for each folder before returning. Satisfies REQ-1,
   REQ-2, REQ-6.

4. **Download the four RQ1+RQ4 compartmental-modelling non-seed papers (milestone M1 batch A).** For
   each of `10.1371_journal.pcbi.1000899` (Schachter2010), `10.1152_jn.00123.2009`
   (Fohlmeister2010), `10.1016_j.neuron.2017.07.020` (Koren2017), `10.1523_ENEURO.0261-21.2021`
   (ElQuessny2021), spawn a `/add-paper` subagent with the DOI as `$ARGUMENTS`. Expected: four new
   subfolders under `assets/paper/`, each passing the paper verificator. Satisfies REQ-3, REQ-4
   (RQ1, RQ2, RQ4 coverage), REQ-5 (criterion a), REQ-6.

5. **Download the six RQ3+RQ5 E/I and tuning-curve non-seed papers (milestone M1 batch B).** For
   each of `10.1523_JNEUROSCI.22-17-07712.2002` (Taylor2002), `10.1113_jphysiol.2008.161240`
   (Chen2009), `10.1523_JNEUROSCI.5017-13.2014` (Park2014), `10.1113_jphysiol.2010.192716`
   (Sivyer2010), `10.7554_eLife.52949` (Jain2020), `10.7554_eLife.42392` (Hanson2019), spawn a
   `/add-paper` subagent with the DOI as `$ARGUMENTS`. Expected: six new subfolders under
   `assets/paper/`, each passing the paper verificator. Satisfies REQ-3, REQ-4 (RQ3, RQ5 coverage),
   REQ-5 (criterion c), REQ-6.

6. **Download the three RQ3 circuit/structure non-seed papers (milestone M1 batch C).** For each of
   `10.1038_nature09818` (Briggman2011), `10.1038_nature18609` (Ding2016),
   `10.1016_j.neuron.2016.04.041` (Sethuramanujam2016), spawn a `/add-paper` subagent with the DOI
   as `$ARGUMENTS`. Expected: three new subfolders under `assets/paper/`, each passing the paper
   verificator. Satisfies REQ-3, REQ-4 (RQ3 coverage), REQ-5 (criteria b and c), REQ-6.

7. **Download the remaining non-seed paper (milestone M1 batch D).** For `10.1002_cne.22678`
   (Hoshi2011), spawn a `/add-paper` subagent. Expected: one new subfolder under `assets/paper/`
   passing the paper verificator. At the end of milestone M1, running
   `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/ | wc -l` must print
   `20`. Satisfies REQ-1, REQ-3, REQ-4 (RQ2 coverage), REQ-5 (criterion b), REQ-6.

8. **Create the answer asset folder and details.json (milestone M2).** Create
   `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/`.
   Write `details.json` with `spec_version: "2"`,
   `answer_id: "how-does-dsgc-literature-structure-the-five-research-questions"`, the question
   string (see Approach section), `short_title: "DSGC literature structure of the five RQs"`,
   `short_answer_path: "short_answer.md"`, `full_answer_path: "full_answer.md"`,
   `categories: ["direction-selectivity","compartmental-modeling","retinal-ganglion-cell", "dendritic-computation","synaptic-integration","voltage-gated-channels"]`,
   `answer_methods: ["papers","internet"]`, `source_paper_ids` equal to the 20 paper IDs from
   milestone M1 in the order of the Paper Selection table, `source_urls: []` (ModelDB entries live
   in the research document citations, not the answer asset), `source_task_ids: []` (no prior task
   dependencies), `confidence: "medium"`,
   `created_by_task: "t0002_literature_survey_dsgc_compartmental_models"`, `date_created` set to
   today's ISO 8601 date. Validate the file by eyeballing every required field against
   `meta/asset_types/answer/specification.md` v2. Satisfies REQ-7, REQ-8.

9. **Write the short and full answer documents (milestone M2).** Write `short_answer.md` with YAML
   frontmatter (`spec_version: "2"`, `answer_id`, `answered_by_task`, `date_answered`) and three
   sections (`## Question` verbatim from `details.json`, `## Answer` as 2-5 sentences stating "The
   20 reviewed papers converge on the Fohlmeister-Miller ion-channel complement, the Poleg-Polsky
   177 AMPA + 177 GABA synaptic budget, the Schachter active-dendrite DSI gain, and the Chen/Park
   mouse ON-OFF DSGC tuning-curve targets of DSI 0.7-0.85, peak 40-80 Hz, null < 10 Hz, half-width
   60-90 deg", no inline citations, and `## Sources` listing the five most load-bearing paper asset
   IDs plus the research document URL). Write `full_answer.md` with YAML frontmatter (same five
   fields plus `confidence: "medium"`) and nine sections in order: `## Question`, `## Short Answer`,
   `## Research Process`, `## Evidence from Papers`, `## Evidence from Internet Sources`,
   `## Evidence from Code or Experiments`, `## Synthesis`, `## Limitations`, `## Sources`. The
   `## Synthesis` section must have five `###` subheadings — one per RQ — each stating the
   quantitative target and the paper IDs that support it. The `## Evidence from Code or Experiments`
   section must state explicitly that the code-experiment method was not used for this task, per the
   specification's instruction when a method is skipped. The `## Sources` section must list every
   one of the 20 paper IDs with markdown reference links pointing to each paper's `summary.md`.
   Satisfies REQ-7, REQ-8.

10. **Verify every paper asset and the answer asset (milestone M3).** Run
    `uv run python -u -m meta.asset_types.paper.verificator --task-id t0002_literature_survey_dsgc_compartmental_models`
    and confirm the final line is `0 errors` for every paper. Run
    `uv run python -u -m meta.asset_types.answer.verificator --task-id t0002_literature_survey_dsgc_compartmental_models`
    and confirm the final line is `0 errors`. Run
    `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/ | wc -l` and confirm
    the count is `20`. Run
    `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/ | wc -l` and confirm
    the count is `1`. Read the `## Synthesis` section of `full_answer.md` and confirm five `###`
    subheadings (one per RQ). Satisfies REQ-1, REQ-2, REQ-3, REQ-4, REQ-6, REQ-7, REQ-8.

**Metric measurement (registered metrics audit).** The project has four registered metrics in
`meta/metrics/`: `direction_selectivity_index`, `tuning_curve_hwhm_deg`, `tuning_curve_reliability`,
`tuning_curve_rmse`. Every one of these metrics measures a quantitative property of a compartmental
model simulation (a DSI, a tuning-curve half-width, a reproducibility score, a target-curve RMSE).
This task is a pure literature survey and produces no simulation output — it downloads and
summarises existing papers, it does not run any simulation. Therefore **none of the four registered
metrics applies to this task**, and `results/metrics.json` will be written as an empty object `{}`
by the orchestrator during its poststep. This is a deliberate omission, not an oversight. The
numerical targets extracted from the literature (DSI 0.7-0.85, peak 40-80 Hz, etc.) are recorded as
prose in the answer asset's `## Synthesis` section and will seed the metric-measuring tasks t0004,
t0005, and the later Na/K optimisation task.

## Remote Machines

**None required.** The task runs locally on the developer's workstation. No compartmental model is
simulated, no training or inference is performed, and no large-scale data processing is needed. The
only compute activity is downloading ~20 PDFs (a few hundred MB in total) and running the local
Claude Code CLI — both well within a standard laptop. `project/budget.json` `available_services`
is empty, which independently confirms that no remote compute is provisioned for this project. Any
attempt to provision a GPU or a cloud VM would be a direct violation of the task's Cost Estimation
and must be refused.

## Assets Needed

Input assets required by this task:

* **`project/description.md`** — source of the six seed references (BarlowLevick1965, Hines1997,
  Vaney2012, PolegPolsky2016, Oesch2005, Branco2010) and of the five research questions.
* **`tasks/t0002_literature_survey_dsgc_compartmental_models/research/research_internet.md`** —
  catalogue of the 22 discovered paper candidates with DOIs, URLs, suggested categories, and per-RQ
  coverage; produced in the preceding research stage of this same task.
* **`meta/categories/`** — the eight category folders listed in Step 1, used as tags on both paper
  and answer assets.
* **`meta/asset_types/paper/specification.md` v3** — paper asset format.
* **`meta/asset_types/answer/specification.md` v2** — answer asset format.
* **Journal/preprint URLs listed in `research/research_internet.md`** — source URLs for each
  paper's PDF.

No dependency task assets are required — this task has `dependencies: []` and is the project's
first research task.

## Expected Assets

This task produces exactly 21 assets total, matching `task.json`'s `expected_assets` of
`paper: 20, answer: 1`:

* **20 paper assets** under
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/<paper_id>/`, one per row of
  the Approach section's Paper Selection table. Each asset contains `details.json` conforming to
  `meta/asset_types/paper/specification.md` v3 (with `spec_version: "3"`, `summary_path`, `files`,
  `download_status`), a canonical summary document with all nine mandatory sections, and a PDF under
  `files/` (or `.gitkeep` plus `download_status: "failed"` if the PDF is unavailable). Paper IDs are
  DOI slugs generated by `arf.scripts.utils.doi_to_slug`.
* **1 answer asset** at
  `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/`
  with `details.json`, `short_answer.md`, and `full_answer.md` conforming to
  `meta/asset_types/answer/specification.md` v2. The full answer document's `## Synthesis` section
  has exactly five `###` subheadings (one per research question).

No new datasets, libraries, models, or predictions are produced.

## Time Estimation

* Research phase (already complete): `research_internet.md` and `research_papers.md` were produced
  in the earlier research stage of this task; `research_code.md` is skipped by design (first
  research task, no prior code to review).
* Planning phase (current): ~45 min.
* Implementation milestone M1 (20 paper downloads via `/add-paper` subagents): ~6-8 h of wall-clock
  work (~20-25 min per paper including download, abstract extraction, full-text read, and summary
  drafting; some papers run in parallel sub-agents).
* Implementation milestone M2 (answer asset): ~1.5 h (drafting `short_answer.md` and
  `full_answer.md` after all 20 paper summaries are available).
* Milestone M3 (verification): ~10 min.
* Remote compute: 0 h (none).
* Total: ~8-10 h wall-clock after planning.

## Risks & Fallbacks

Pre-mortem: if this task failed, the most likely failure mode is that several target PDFs are
paywalled, leaving fewer than 20 downloadable papers and forcing the task into either a substitution
loop or an intervention. Secondary failure modes are DOI-to-slug collisions between the 20 selected
papers and author/institution country metadata that the paper specification flags as warnings.

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| One or more target PDFs are paywalled or permanently offline | Medium | Moderate — blocks REQ-1 REQ-6 for the affected paper | Mark the affected paper with `download_status: "failed"` and a concrete `download_failure_reason` per spec v3, place `.gitkeep` in `files/`, reuse the abstract from the journal landing page, and proceed. The paper specification explicitly allows metadata-only assets. If three or more papers fail, create an intervention file under `intervention/` requesting a librarian-mediated PDF fetch before Step 10. |
| DOI-to-slug collision with a future or concurrent task paper | Low | Moderate — two different papers would write to the same folder, corrupting one asset | All 20 DOIs in the Paper Selection table are distinct. Before Step 3 through Step 7, run `uv run python -u -m arf.scripts.utils.doi_to_slug "<doi>"` for every DOI and confirm the 20 slugs are unique. `ls tasks/*/assets/paper/` must return no collision before each `/add-paper` invocation. |
| Author/institution country or ORCID metadata missing for older papers (BarlowLevick1965, Taylor2002) | High | Low — triggers warnings `PA-W007` or `PA-W010`, never blocks the verificator | Accept these warnings rather than fabricate values. For each missing country, set the field to `null` (allowed by spec v3 for authors, triggers `PA-W007` if no author has a country, `PA-W010` when institution country is `null`). Document the warnings in `logs/` and carry them through. The task's verification criteria only require zero errors, not zero warnings. |
| `/add-paper` subagent exhausts its context window while summarising a long paper | Low | Moderate — partial summary blocks the paper verificator | Spawn each `/add-paper` as an independent subagent in its own context (one paper per invocation). If a summary stops mid-section, re-run the subagent with an explicit instruction to read only the results section first and then expand — the summary is regeneratable. |

## Verification Criteria

Every criterion below is an exact shell command and the expected observable output. The task is
complete only when all six pass.

* **VC-1 — Paper asset verificator passes for every paper (covers REQ-1, REQ-2, REQ-3, REQ-6).**
  Run
  `uv run python -u -m meta.asset_types.paper.verificator --task-id t0002_literature_survey_dsgc_compartmental_models`.
  Expected output: for each of the 20 paper IDs, a `PASSED` line; final exit code `0`. If any paper
  returns a non-zero exit, stop and fix the asset before proceeding.

* **VC-2 — Answer asset verificator passes (covers REQ-7, REQ-8).** Run
  `uv run python -u -m meta.asset_types.answer.verificator --task-id t0002_literature_survey_dsgc_compartmental_models`.
  Expected output: one `PASSED` line for
  `how-does-dsgc-literature-structure-the-five-research-questions`; exit code `0`.

* **VC-3 — Paper count is exactly 20 (covers REQ-1, REQ-3).** Run
  `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/ | wc -l`. Expected
  output: `20`. If the count is 19 or 21, the Paper Selection table is out of sync and must be
  reconciled before proceeding.

* **VC-4 — Six seed references are present (covers REQ-2).** For each of the six seed paper IDs
  (`10.1113_jphysiol.1965.sp007638`, `10.1162_neco.1997.9.6.1179`, `10.1038_nrn3165`,
  `10.1016_j.neuron.2016.02.013`, `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664`),
  confirm the folder exists by running
  `test -d tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/<paper_id> && echo PRESENT`.
  Expected output: `PRESENT` six times.

* **VC-5 — Answer full document has five per-RQ subsections (covers REQ-4, REQ-7).** Run
  `grep -c "^### RQ" tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/full_answer.md`.
  Expected output: `5`.

* **VC-6 — Categories referenced by assets all exist in `meta/categories/` (covers REQ-6,
  REQ-8).** Run `uv run python -u -m arf.scripts.aggregators.aggregate_categories --format ids` and
  confirm that every category slug listed in any paper's `details.json` `categories` field and in
  the answer asset's `categories` field is one of the returned IDs. Expected output: all referenced
  slugs appear in the aggregator output; no `PA-W005` warnings in VC-1 output for unknown
  categories.
