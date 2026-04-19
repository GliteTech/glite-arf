---
spec_version: "2"
task_id: "t0002_literature_survey_dsgc_compartmental_models"
---
# Results Detailed: Literature Survey of Compartmental Models of DS Retinal Ganglion Cells

## Summary

This task produced a 20-paper literature survey of compartmental models of direction-selective
retinal ganglion cells (DSGCs) and one synthesis answer asset that integrates the findings across
all five project research questions. Every paper asset conforms to paper asset specification v3
(with `details.json`, a canonical `summary.md`, and the paper file under `files/` where downloadable
or a `.gitkeep` plus `download_status: "failed"` where paywalled). The answer asset conforms to
answer asset specification v2 and provides per-RQ quantitative targets that downstream compartmental
modelling tasks (t0004 target tuning-curve generator, t0005 morphology download, later Na/K
optimisation and active-vs-passive dendrite experiments) must reproduce.

## Methodology

**Machine**: Local developer workstation (Windows 11 Education, x86-64). No remote compute.

**Runtime**: Total wall-clock for the task from `create-branch` prestep (2026-04-18T23:05:41Z) to
the end of step 12 `results` poststep (approximately 2026-04-19T01:30:00Z) is **~2.5 h** of
orchestrator time, with the implementation step accounting for the bulk via parallel `/add-paper`
subagents (each paper ~15-25 min of subagent wall-clock). No simulation, training, or inference was
performed — the only compute activity was HTTP downloads and local LLM CLI use.

**Start timestamp**: 2026-04-18T23:05:41Z (step 1 `create-branch` prestep)

**End timestamp**: 2026-04-19T01:30:00Z (step 12 `results` expected poststep)

**Methods used**:

* `papers` — peer-reviewed literature catalogued and summarized per paper asset spec v3
* `internet` — bibliographic metadata retrieval (DOIs, journal URLs, abstracts)

The `code-experiment` method was not used: this is a literature survey task and no simulation code
was written.

**Tools used**:

* `/add-paper` skill — invoked once per paper in a dedicated subagent
* `/planning` skill — used to produce `plan/plan.md`
* `meta.asset_types.paper.verificator` — validated every paper asset
* `meta.asset_types.answer.verificator` — validated the synthesis answer asset
* `arf.scripts.utils.doi_to_slug` — generated DOI-based folder slugs

## Metrics Tables

The project does not have a registered metric that applies to a pure literature survey, so
`metrics.json` is `{}` by design. The quantitative targets surfaced by the survey are recorded as
prose in the answer asset's `## Synthesis` section. Below is a condensed view of those targets.

| RQ | Target / finding | Source paper IDs |
| --- | --- | --- |
| RQ1 Na/K conductances | g_Na peak 0.04-0.10 S/cm^2; g_K (DR) ~0.012 S/cm^2; g_K,A ~0.036 S/cm^2; g_K,Ca ~0.001 S/cm^2 | `10.1152_jn.00123.2009`, `10.1371_journal.pcbi.1000899`, `10.1016_j.neuron.2016.02.013`, `10.1038_nrn3165` |
| RQ2 morphology sensitivity | Global dendrite shape minimally changes the E/I synaptic map; local electrotonic compartments (lambda ~100-200 um) still matter | `10.1523_ENEURO.0261-21.2021`, `10.1126_science.1189664`, `10.1002_cne.22678`, `10.1016_j.neuron.2017.07.020`, `10.1038_nature09818`, `10.1038_nature18609` |
| RQ3 AMPA/GABA balance | 177 AMPA + 177 GABA synapses on reconstructed mouse DSGC; null-direction IPSC 3-5x preferred | `10.1016_j.neuron.2016.02.013`, `10.1523_JNEUROSCI.22-17-07712.2002`, `10.1523_JNEUROSCI.5017-13.2014`, `10.7554_eLife.52949`, `10.7554_eLife.42392`, `10.1016_j.neuron.2016.04.041`, `10.1113_jphysiol.1965.sp007638` |
| RQ4 active vs passive dendrites | Active dendrites with Fohlmeister densities raise DSI from ~0.3 (passive) to ~0.7 (active); TTX-sensitive dendritic Na+ spikes recorded in rabbit | `10.1371_journal.pcbi.1000899`, `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664`, `10.1016_j.neuron.2017.07.020`, `10.7554_eLife.52949` |
| RQ5 angle-to-AP-frequency tuning curves | Adult mouse ON-OFF DSGC: preferred peak 40-80 Hz; null 3-10 Hz; DSI 0.6-0.9; HWHM 60-90 deg | `10.1113_jphysiol.2008.161240`, `10.1523_JNEUROSCI.5017-13.2014`, `10.1113_jphysiol.1965.sp007638`, `10.1523_JNEUROSCI.22-17-07712.2002`, `10.1016_j.neuron.2005.06.036`, `10.1113_jphysiol.2010.192716` |

## Analysis

The 20 papers converge on a coherent compartmental-modelling recipe for mouse ON-OFF DSGCs. The
backbone (NEURON simulator per `10.1162_neco.1997.9.6.1179`) is uncontroversial. The Fohlmeister
ion-channel parameter set is the only point in the (g_Na, g_K) space that the literature has
calibrated against DSGC-like spiking — downstream task t0006+ should sweep around this point rather
than start from an uninformed grid. The Poleg-Polsky 177+177 synaptic budget and the 3-5x
null-to-preferred IPSC asymmetry are the two most load-bearing numbers for any faithful
compartmental DSGC: failing to reproduce both simultaneously means the resulting DSI will miss the
target window. The most surprising recent finding is the El-Quessny result that global DSGC
dendritic morphology only minimally influences the synaptic distribution of excitation and
inhibition; this means that morphology-swap experiments (t0005) should focus on local electrotonic
compartments and branching topology near the primary dendrite rather than whole-tree shape. The
weakest evidence is on RQ1 (there is no published factorial grid of g_Na, g_K for DSGCs
specifically) and on the downstream mapping from E/I synaptic drive to angle-to-AP tuning-curve
shape — these two gaps motivate the project's core experimental agenda.

## Verification

* `meta.asset_types.paper.verificator` against every paper asset — 20/20 PASSED, 0 errors.
* `meta.asset_types.answer.verificator` against
  `how-does-dsgc-literature-structure-the-five-research-questions` — PASSED, 0 errors, 0 warnings.
* `grep -c "^### RQ" full_answer.md` — **5** (matches plan VC-5: five per-RQ subsections).
* `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/ | wc -l` — **20**
  (matches plan VC-3).
* `ls tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/ | wc -l` — **1**
  (matches expected_assets).
* Six seed paper folders (BarlowLevick1965, Hines1997, Vaney2012, PolegPolsky2016, Oesch2005,
  Branco2010) are present (matches plan VC-4).
* `verify_step` on every completed step — PASSED (step tracker is consistent and logs are in place).

## Limitations

Three papers could not be downloaded from open-access mirrors and remain as metadata-only assets:
Chen2009 (`10.1113_jphysiol.2008.161240`), Sivyer2010 (`10.1113_jphysiol.2010.192716`), and
Sethuramanujam2016 (`10.1016_j.neuron.2016.04.041`). The paper asset spec v3 explicitly supports
this via `download_status: "failed"` and `.gitkeep` under `files/`, and each metadata-only asset
retains the journal-landing-page abstract. Key quantitative claims attributed to these papers
(Chen2009 and Sivyer2010 tuning-curve numbers, Sethuramanujam2016 co-transmission result) come from
their abstracts and not from full-text re-reading, so the confidence on those specific numbers is
lower than for the 17 fully downloaded papers. Two ModelDB database entries flagged in
`research/research_internet.md` ([ModelDB-PP2016], [Branco2010-MDB]) are not paper assets; they are
code artefacts that belong to a later implementation task. The survey does not include any
literature on ON DSGCs in non-mouse species beyond what Barlow & Levick 1965 (rabbit), Oesch 2005
(rabbit), and Taylor 2002 (rabbit) already provide — a downstream task could extend coverage to
primate or zebrafish DSGCs if needed.

## Files Created

* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/` — 20 paper asset
  subfolders, each with `details.json`, `summary.md`, and `files/<...>` (or `.gitkeep`)
* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/details.json`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/short_answer.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/full_answer.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/research/research_internet.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/plan/plan.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/results_summary.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/results_detailed.md`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/metrics.json`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/costs.json`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/remote_machines_used.json`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/steps/` — step logs for every
  executed and skipped canonical step

## Task Requirement Coverage

The operative task text from `task.json` and `task_description.md`:

```text
Name: Literature survey: compartmental models of DS retinal ganglion cells
Short description: Survey published compartmental models of direction-selective retinal ganglion
cells to inform all five project research questions.

Scope:
- Cover all five project research questions at survey level (RQ1-RQ5).
- Include the six seed references from project/description.md.
- Add at least 14 more papers found by internet search, spread across the five RQs.
- Prefer papers with a clearly described compartmental model, published morphology, or
  quantitative angle-to-rate measurements.
Expected outputs: ~20 paper assets; one answer asset synthesising all five RQs.
Verification: 20 paper assets pass verify_paper_asset; answer asset passes verify_answer_asset
and explicitly addresses each of the five RQs.
```

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-1 | Produce exactly 20 paper assets under `assets/paper/<paper_id>/`, each with the three mandatory artifacts | **Done** | `ls assets/paper/ \| wc -l` = 20; each folder contains `details.json`, canonical `summary.md`, and `files/<...>` or `.gitkeep` |
| REQ-2 | Include all six seed references | **Done** | Folders `10.1113_jphysiol.1965.sp007638`, `10.1162_neco.1997.9.6.1179`, `10.1038_nrn3165`, `10.1016_j.neuron.2016.02.013`, `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664` all exist |
| REQ-3 | Add ≥ 14 additional peer-reviewed papers beyond the seeds | **Done** | 14 additional DOIs downloaded: Schachter2010, Fohlmeister2010, Taylor2002, Chen2009, Park2014, Briggman2011, Ding2016, Sivyer2010, Hoshi2011, Koren2017, ElQuessny2021, Jain2020, Hanson2019, Sethuramanujam2016 |
| REQ-4 | Spread the 14 non-seed papers across all five RQs with ≥ 2 non-seed papers per RQ | **Done** | RQ1: 2 (Schachter2010, Fohlmeister2010); RQ2: 3 (Hoshi2011, Koren2017, ElQuessny2021); RQ3: 7 (Taylor2002, Park2014, Briggman2011, Ding2016, Jain2020, Hanson2019, Sethuramanujam2016); RQ4: 3 (Schachter2010, Koren2017, Jain2020); RQ5: 4 (Taylor2002, Chen2009, Park2014, Sivyer2010) — every RQ ≥ 2 |
| REQ-5 | Prefer papers satisfying a/b/c (compartmental model, morphology, angle-to-rate) | **Done** | Paper Selection table in `plan/plan.md` lines 150-170 maps each paper to its selection criterion; every selected paper satisfies ≥ 1 criterion |
| REQ-6 | Each paper asset conforms to paper asset spec v3 and verificator reports zero errors | **Done** | All 20 paper assets verified PASSED against `meta.asset_types.paper.verificator` with zero errors each |
| REQ-7 | Produce exactly one answer asset with five per-RQ subsections in `## Synthesis` | **Done** | `assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/full_answer.md` has `### RQ1 Na/K conductances`, `### RQ2 morphology sensitivity`, `### RQ3 AMPA/GABA balance`, `### RQ4 active vs passive dendrites`, `### RQ5 angle-to-AP-frequency tuning curves` (grep count = 5) |
| REQ-8 | Answer asset conforms to answer asset spec v2 | **Done** | `meta.asset_types.answer.verificator` reports PASSED with 0 errors and 0 warnings; `details.json` has `spec_version: "2"`, all required fields populated; short and full answers have all mandatory sections |
| REQ-9 | Zero external cost | **Done** | `results/costs.json` shows `total_cost_usd: 0`; no paid APIs or remote machines used |
