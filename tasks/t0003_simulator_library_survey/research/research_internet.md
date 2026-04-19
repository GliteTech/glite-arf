---
spec_version: "1"
task_id: "t0003_simulator_library_survey"
research_stage: "internet"
searches_conducted: 16
sources_cited: 20
papers_discovered: 4
date_completed: "2026-04-19"
status: "complete"
---
## Task Objective

Survey five candidate compartmental simulators (NEURON, NetPyNE, Brian2, MOOSE, Arbor) along five
axes — cable-model fidelity, Python ergonomics, speed and parallelism, availability of DSGC/RGC
examples, and long-term maintenance — to choose a primary simulator and a backup for the DSGC
project. The output is the evidence base behind one answer asset that recommends those two
libraries.

## Gaps Addressed

The `research_papers.md` step was deliberately skipped for this task: it is a tooling-comparison
survey rather than a literature review of biology, so there is no relevant paper corpus to summarise
upstream. Instead of inheriting a Gaps and Limitations section from `research_papers.md`, this
internet research treats the five evaluation axes from `task_description.md` as the gap list and
records resolution status for each.

* **Cable-model fidelity (full compartmental cable equation, voltage-gated conductances in arbitrary
  compartments, SWC/HOC/NeuroML morphologies)** — **Resolved** for NEURON, Arbor and MOOSE;
  **Partially resolved** for Brian2 (cable equation supported but the developers themselves describe
  multicompartment as "not yet as mature" as NEURON [Stimberg2019], and code generation for
  multicompartment is currently restricted to the C++ standalone target [Brian2-MC-Docs]).
* **Python ergonomics (pip install on `uv`, MOD/HOC vs pure Python)** — **Resolved**: NEURON,
  NetPyNE, Brian2, Arbor all ship pip wheels; MOOSE is the outlier (PyPI is not the primary
  distribution path).
* **Speed and parallelism (single-cell speed, parameter sweeps)** — **Resolved**: Arbor is **7-12x**
  faster than NEURON on single morphologically-detailed cells [Plastic-Arbor-2026, Arbor-RTD-2025],
  CoreNEURON+GPU gives **30-52x** over baseline on large networks [Awile2022], NetPyNE provides
  built-in batch/Optuna/inspyred sweep infrastructure [NetPyNE-Doc], MOOSE has no built-in batch
  layer.
* **DSGC/RGC examples available** — **Partially resolved**: A NEURON-based DSGC model is publicly
  released in ModelDB 189347 (Poleg-Polsky & Diamond 2016) [ModelDB-189347]; the Schachter et al.
  2010 PLoS CB DSGC model [Schachter2010] is published but not located in ModelDB by the searches;
  Brian2/Arbor/MOOSE have no published DSGC implementations and only generic RGC morphology examples
  [Berens-RGC-GH].
* **Long-term maintenance (last release, community activity)** — **Resolved**: NEURON (8.2.7 May
  2025, 9.0.1 Nov 2025) and Arbor (v0.12.0 Apr 2025) are actively released; NetPyNE released v1.1.1
  Sep 2025; MOOSE has only 22 GitHub stars and the latest visible tag is the chamcham 3.1.x series
  with no clearly dated 2024-2025 release surfaced [MOOSE-GH]; Brian2 ships continuously to PyPI
  (2.10.x) but uses no GitHub release tags [Brian2-GH].

## Search Strategy

**Sources searched**: Google web search, GitHub (project repositories and release pages), official
documentation sites (`docs.arbor-sim.org`, `nrn.readthedocs.io`, `brian2.readthedocs.io`,
`doc.netpyne.org`, `moose.ncbs.res.in/readthedocs`), PyPI, ModelDB (`modeldb.science` and
`senselab.med.yale.edu/ModelDB`), bioRxiv preprint server, eLife, PLOS Computational Biology, PMC.

**Date range**: 2010-2026 for foundational simulator references; 2024-2026 for release activity,
benchmarks, and Python packaging notes.

**Inclusion criteria**: Sources had to provide one of (a) primary documentation of one of the five
candidate libraries, (b) quantitative benchmark numbers across two or more candidates, (c) a
released DSGC/RGC compartmental model with downloadable code, or (d) packaging/maintenance evidence
(release dates, dependencies, GitHub activity). Excluded: blog posts about unrelated simulators
(NEST point-neuron, GENESIS legacy, BMTK without Python ergonomics info).

**Queries executed** (16 total):

*Pass 1 — gap-targeted (one per candidate library plus the DSGC example axis):*

1. `NEURON simulator 8.2 Python bindings cable equation reconstructed morphology benchmark 2025`
2. `NetPyNE NEURON wrapper documentation parameter sweep parallel batch 2025`
3. `Brian2 multicompartmental cable equation morphology spatial neuron extension`
4. `Arbor simulator multicompartmental neuron Python GPU performance benchmark 2025`
5. `MOOSE simulator multiscale Python compartmental model HHChannel rdesigneur 2025`
6. `retinal ganglion cell direction selective NEURON model GitHub Poleg-Polsky Schachter`
7. `NEURON simulator pip install uv Python packaging 2025`
8. `Arbor NEURON benchmark comparison single cell speed multi-compartment`

*Pass 2 — broadening (cross-simulator reviews, reproducibility, release status):*

9. `NEURON NEURON simulator latest release 8.2 9.0 changelog 2024 2025 stability`
10. `MOOSE simulator GitHub release 4.0 last update Bhalla 2024 2025`
11. `Brian2 spatialneuron NMDA voltage-gated channel example direction selectivity`
12. `ModelDB direction selective ganglion cell DSGC NEURON code download`
13. `"compartmental simulator" comparison "NEURON" "Arbor" "Brian2" review 2023 2024 2025`
14. `NetPyNE batch optuna inspyred parameter optimization NEURON cell tutorial 2024`

*Pass 3 — snowball (follow-ups on findings):*

15. `"NMODL" "MOD file" NEURON Arbor compatibility translation modcc 2024 2025`
16. `"NetPyNE" python "3.11" "3.12" requires NEURON installed pip install dependency`

**Deep reads via WebFetch**: Modernizing-NEURON paper (PMC9272742), Brian 2 eLife paper, MOOSE
release page, NetPyNE GitHub repository, Arbor release page, NEURON changelog, ModelDB DSGC entry,
MOOSE rdesigneur tutorial, jzlab/dsg repository.

## Key Findings

### Cable-Model Fidelity Across Candidates

NEURON, NetPyNE (which is a thin wrapper over NEURON, sharing its solver), Arbor and MOOSE all
implement the full compartmental cable equation, accept SWC morphologies, and let voltage-gated
conductances be placed in any compartment. NEURON 9.0 (released 30 September 2025) introduces a
Structure-Of-Arrays memory layout, replaces internal pointers with auto-updating `DataHandle`
objects, and migrates the codebase plus the MOD-file translator to C++
[NEURON-Changelog, Awile2022]. Arbor's `modcc` compiler accepts NMODL but uses a stricter dialect —
special variables must be declared `PARAMETER` rather than `ASSIGNED`, and not every NEURON MOD file
ports without edits [Arbor-NMODL-Doc].

Brian2's `SpatialNeuron` discretises the cable equation and reads SWC morphologies, but the
maintainers state explicitly that "Brian is used mostly for point neurons … this feature is not yet
as mature as those of specialised simulators such as NEURON and GENESIS, and is an important area
for future development" [Stimberg2019]. The documentation also restricts multicompartment code
generation to the C++ standalone target, ruling out the GPU/Cython paths [Brian2-MC-Docs].

MOOSE's `rdesigneur` interface loads SWC morphologies from NeuroMorpho.org-style files, distributes
HH channels via `chanDistrib` directives like `['Na', 'dend#', 'Gbar', '400']`, and supports
multiscale (electrical + biochemical) coupling [MOOSE-Rdes-Doc]. There is no documented built-in
batch driver — sweeps are written as Python loops around `buildModel()`.

### Speed and Parallelism

The most consistent across-simulator benchmark numbers come from the Arbor team and the BlueBrain
group. **Single-cell models** show Arbor running **7-12x faster** than NEURON on cerebellar
morphologies [Plastic-Arbor-2026]. On larger networks Arbor reports **roughly 5-8x speedup** over
NEURON when restricted to MPI parallelism, doubling when Arbor's HPC-tuned distribution scheme is
used [Arbor-RTD-2025]. The Plastic Arbor 2026 follow-up confirms that adding morphology to
point-neuron models incurs only "modest" runtime and memory overhead, and that Arbor is "markedly
more efficient" than NEURON even when computing additional plasticity dynamics [Plastic-Arbor-2026].

NEURON's own modernisation paper [Awile2022] documents big speedups on **large network** simulations
after enabling CoreNEURON: 191k-cell olfactory bulb model is **3.5x** faster on CPU and **30.4x**
faster on 8 NVIDIA V100 GPUs; 18k-cell rat CA1 model is **52x** on GPUs; mouse M1 cortex is **39x**.
RxD reaction-diffusion gains range from **4.2x** (1D pure diffusion) to **45.4x** (3D diffusion with
multi-threading).

NetPyNE wraps NEURON's MPI parallelism and adds an explicit `Batch` class, with parallel backends
for grid search, Optuna, and the `inspyred` evolutionary library — the latter is reported to "run
parallel simulations under the NEURON environment either on multiprocessor machines via MPI or
supercomputers via workload managers" [NetPyNE-Doc]. This is the most ergonomic parameter-sweep
layer found among the five candidates and is directly relevant to the project's optimisation step.

Brian2 is fastest at point-neuron CUBA-style network benchmarks, but its own paper notes the result
"does not mean that Brian 2 is faster than other simulators such as NEURON or NEST in general"
[Stimberg2019]; for multicompartment work it falls behind NEURON and Arbor.

### Python Ergonomics and Packaging

| Library | pip wheel | Python supported | Pure Python? |
| --- | --- | --- | --- |
| NEURON | yes (`neuron`), distributed since 7.8.1, "around 3000 downloads/month" reaching 17,000 in six months [Awile2022] | 3.9-3.13 (8.2.7); Python 3.14 added in 9.0.1 [NEURON-Changelog] | No — MOD files compile via `nrnivmodl` |
| NetPyNE | yes (`netpyne` v1.1.1 on 14 Sep 2025) [NetPyNE-GH] | Python 3.11 explicitly in `setup.py`; relies on NEURON [NetPyNE-Doc] | Yes for model description, but inherits NEURON's MOD step |
| Brian2 | yes (`brian2` 2.10.x continuous, no GitHub release tags) [Brian2-GH] | Python 3.9+ (current 2.10.x) | Yes — equation strings, code generation under the hood |
| Arbor | yes (`arbor`); v0.12.0 released 17 Apr 2025 [Arbor-Releases] | Python 3.7+, official wheels via `pip install arbor` [Arbor-Install-Doc] | Mostly — channel mechanisms still NMODL via `modcc` |
| MOOSE | partial; PyPI not the primary path; chamcham 3.1.x tagged via GitHub releases without explicit year on the page surfaced [MOOSE-GH, MOOSE-Releases] | Python 3 documented; less clear matrix | Yes for high-level scripting; channel definitions via Python objects |

`uv` integration was not explicitly tested by any source for any of these libraries, but pip wheels
are sufficient for `uv pip install` of NEURON and Brian2 in practice; Arbor wheels via
`pip install arbor` likewise integrate with `uv` (no special handling). NetPyNE's `setup.py` does
not pin NEURON, so an explicit `uv pip install neuron` step is required first [NetPyNE-Doc]. There
is an active issue about Python 3.13 wheels for NEURON [NEURON-Py313-Issue] which is now resolved in
8.2.7 and 9.0.1.

### Long-term Maintenance

NEURON shows the strongest activity: 8.2.7 (25 May 2025), 9.0.0 (30 Sep 2025) and 9.0.1 (17 Nov
2025\) [NEURON-Changelog]. The project transitioned to GitHub Actions and Azure CI, and the
modernisation paper documents an explicit shift "toward collaborative development" with rising
external contribution counts [Awile2022].

Arbor is also in active high-quality release cadence: v0.10.0 (8 Aug 2024), v0.11.0 (24 Apr 2024,
back-patched), and v0.12.0 (17 Apr 2025), with 2025 work focused on parallel performance via a
re-architected MPI algorithm [Arbor-Releases].

NetPyNE shipped v1.1.1 on 14 Sep 2025, has 169 GitHub stars, and offers active forum support
[NetPyNE-GH]. The maintenance footprint is smaller than NEURON's but the package is alive.

Brian2 has 1.2k GitHub stars, 176 open issues, 29 open PRs, and ships continuously to PyPI but uses
no GitHub release tags [Brian2-GH] — an unusual workflow that complicates "what version am I on"
checks.

MOOSE is the weakest on this axis: 22 stars, the latest visible tag is the chamcham `3.1.x` series
with no year displayed on the release page surfaced [MOOSE-GH, MOOSE-Releases]. The development is
concentrated in a single laboratory (BhallaLab at NCBS), and the Bhalla group is the de facto sole
maintainer.

### DSGC/RGC Code Availability

The single best DSGC asset found is **ModelDB 189347** (Poleg-Polsky & Diamond, 2016,
"Multiplication by NMDA receptors in Direction Selective Ganglion cells"), implemented in NEURON
[ModelDB-189347]. This matches the project's intended modelling approach (multi-compartmental DSGC,
distributed E and I, NMDA nonlinearity) and reuses our task `t0002` paper corpus (Poleg-Polsky &
Diamond 2016 is paper `10.1016_j.neuron.2016.02.013` in the corpus). The **Schachter et al. 2010**
PLoS CB DSGC model is published [Schachter2010] but a public ModelDB accession was not found via the
searches.

The `jzlab/dsg` repository [jzlab-DSG-GH] (Zylberberg, Cafaro, Turner et al., Neuron 2016) is
**MATLAB-only** and operates at the population/Fisher-information level rather than as a
compartmental simulator — useful as a downstream comparison but not a simulator-selection driver.
The `berenslab/rgc_dendrites` repository [Berens-RGC-GH] contains code for type-specific dendritic
integration in mouse RGCs but is not DSGC-specific. No published Brian2, Arbor, or MOOSE DSGC model
surfaced.

### NMODL Portability Caveat

The cleanest path to "build in NEURON, fall back to Arbor for speed" is mediated by NMODL. Arbor's
`modcc` accepts a strict subset of NMODL and explicitly disallows constructions that NEURON
tolerates [Arbor-NMODL-Doc]. NEURON 9.0's own C++ migration also requires updating MOD files
[NEURON-Changelog]. This means **MOD files written for NEURON 8.x are not guaranteed to compile in
either NEURON 9.0 or Arbor** without source edits — a moderate but real cost when planning a
multi-simulator strategy.

## Methodology Insights

* **Use NEURON as the primary simulator unless a hard performance bottleneck shows up.** It has the
  largest published model corpus (`Hines1997` foundational paper, ModelDB ecosystem), the only
  located DSGC model uses it, and 9.0/8.2 are both actively released
  [Awile2022, NEURON-Changelog, ModelDB-189347]. Pin to NEURON 8.2.7 first to maximise compatibility
  with the published DSGC model's MOD files; only move to 9.0 after a successful initial
  reproduction.
* **Wrap NEURON with NetPyNE for the optimisation/parameter-sweep stage.** The `Batch` class with
  Optuna and inspyred backends is the most ergonomic sweep layer available, and it inherits NEURON's
  MPI parallelism without rewriting the model [NetPyNE-Doc].
* **Treat Arbor as the backup**, not Brian2 or MOOSE. Arbor's measured **7-12x single-cell speedup**
  over NEURON [Plastic-Arbor-2026] is the only quantitative argument for a fallback that could
  matter at the optimisation stage; Brian2's multicompartment path is documented as immature by its
  own authors [Stimberg2019]; MOOSE's maintenance signal is too weak to bet a months-long project on
  it.
* **Budget MOD-file porting time when planning Arbor migration.** Arbor's NMODL dialect is stricter
  than NEURON's and POST_EVENT-style differences exist [Arbor-NMODL-Doc]. A fallback to Arbor is not
  free; expect several days of MOD-file translation before any speedup is realised.
* **Hypothesis (testable in t0002 follow-up)**: Reproducing the ModelDB 189347 DSGC model end-to-end
  in NEURON 8.2.7 takes <1 working day; porting the same MOD files to Arbor takes >3 days. If the
  port takes <1 day, Arbor becomes a viable primary; otherwise NEURON-as-primary is the dominant
  strategy.
* **Hypothesis (testable on hardware)**: For the project's expected sweep size (single DSGC, ~200
  parameter combinations of Na/K conductance, AMPA/GABA ratios, dendrite-active vs passive), one
  workstation running NEURON via NetPyNE Batch + 8 MPI ranks completes in <8 hours; CoreNEURON+GPU
  is overkill at this scale.
* **Best practice — pip wheels first.** All three of NEURON, Brian2, and Arbor have working pip
  wheels; do not build from source unless a wheel is missing for the target Python version
  [NEURON-Py313-Issue, Arbor-Install-Doc, Brian2-GH]. NetPyNE installs cleanly with pip but requires
  NEURON to be present first [NetPyNE-Doc].
* **Avoid MOOSE.** Without a public DSGC asset, a small contributor base (22 GitHub stars), and no
  built-in batch layer, the cost-benefit does not justify it for this project [MOOSE-GH].

## Discovered Papers

The four entries below are papers encountered during this search that are relevant to the project
(simulator characterisation or DSGC modelling) and not yet in the corpus enumerated under
`tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/`. The orchestrator should add
them via the standard add-paper flow.

### [Stimberg2019]

* **Title**: Brian 2, an intuitive and efficient neural simulator
* **Authors**: Marcel Stimberg, Romain Brette, Dan F. M. Goodman
* **Year**: 2019
* **DOI**: `10.7554/eLife.47314`
* **URL**: https://elifesciences.org/articles/47314
* **Suggested categories**: `simulator`, `python-tooling`
* **Why download**: Canonical Brian2 reference paper; explicitly states the multicompartment feature
  is "not yet as mature" as NEURON's, which is the cited evidence behind this task's decision to
  rule Brian2 out as a primary simulator.

### [Awile2022]

* **Title**: Modernizing the NEURON Simulator for Sustainability, Portability, and Performance
* **Authors**: Omar Awile, Pramod Kumbhar, Nicolas Cornu, Salvador Dura-Bernal, James G. King, Olli
  Lupton, Ioannis Magkanaris, Robert A. McDougal, Adam J. H. Newton, Fernando Pereira, Alexandru
  Săvulescu, Nicholas T. Carnevale, William W. Lytton, Michael L. Hines, Felix Schürmann
* **Year**: 2022
* **DOI**: `10.3389/fninf.2022.884046`
* **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9272742/
* **Suggested categories**: `simulator`, `python-tooling`
* **Why download**: Documents NEURON's CoreNEURON CPU/GPU benchmarks (3.5x to 52x speedups), pip
  wheel distribution model, and CI modernisation. Provides the NEURON side of the speed/maintenance
  evidence used to choose NEURON as primary.

### [Plastic-Arbor-2026]

* **Title**: Plastic Arbor: A modern simulation framework for synaptic plasticity—From single
  synapses to networks of morphological neurons
* **Authors**: Jannik Luboeinski, Sebastian Schmitt, Shadi Shafiee et al.
* **Year**: 2026 (PLOS CB; arXiv preprint 2024)
* **DOI**: `10.1371/journal.pcbi.1013926`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013926
* **Suggested categories**: `simulator`, `python-tooling`
* **Why download**: Cross-validates Arbor against Brian2 and reports the **7-12x single-cell
  speedup** of Arbor over NEURON that is the single strongest quantitative argument behind choosing
  Arbor as the project's backup simulator.

### [Schachter2010]

* **Title**: Dendritic Spikes Amplify the Synaptic Signal to Enhance Detection of Motion in a
  Simulation of the Direction-Selective Ganglion Cell
* **Authors**: Michael J. Schachter, Nicholas Oesch, Robert G. Smith, W. Rowland Taylor
* **Year**: 2010
* **DOI**: `10.1371/journal.pcbi.1000899`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000899
* **Suggested categories**: `dsgc`, `compartmental-modeling`
* **Why download**: This paper is already present in the t0002 corpus (paper folder
  `10.1371_journal.pcbi.1000899`) but only at the summary level; the cross-reference here flags that
  its NEURON model code is the second most relevant published DSGC simulator asset after ModelDB
  189347 and should be retrieved from supplementary materials in a downstream task. (No duplicate
  add needed; including here for traceability — the paper is already in the corpus.)

## Recommendations for This Task

1. **Primary simulator: NEURON 8.2.7 (Python wheel, MOD files via `nrnivmodl`).** Largest model
   corpus, only public DSGC asset (ModelDB 189347) is in NEURON, actively released, pip-installable.
   Pin to 8.2.x not 9.0 for the first months — 9.0's MOD-file C++ migration may break legacy models
   without warning [NEURON-Changelog, ModelDB-189347, Awile2022].
2. **Backup simulator: Arbor 0.12.0 (Python wheel `arbor`).** Largest measured single-cell speedup
   over NEURON (7-12x) and the only HPC-portable choice should the parameter sweep blow past local
   compute budget [Plastic-Arbor-2026, Arbor-RTD-2025, Arbor-Releases]. Budget several days for
   MOD-file dialect translation when activating the fallback [Arbor-NMODL-Doc].
3. **Wrap NEURON with NetPyNE 1.1.1 for the optimisation step**, not for the initial model build.
   Use NetPyNE's `Batch` class with the Optuna or inspyred backend for the Na/K conductance sweep
   that is the project's main optimisation target [NetPyNE-Doc, NetPyNE-GH].
4. **Reject Brian2** as either primary or backup: its own authors describe multicompartment as
   immature [Stimberg2019], and code generation for multicompartment models is restricted to the C++
   standalone target [Brian2-MC-Docs].
5. **Reject MOOSE** as either primary or backup: small maintainer base (22 GitHub stars), no public
   DSGC asset, no built-in batch layer [MOOSE-GH, MOOSE-Rdes-Doc].
6. **Concrete first-step task** (downstream): reproduce ModelDB 189347 end-to-end on the
   researcher's local machine with NEURON 8.2.7 + NetPyNE 1.1.1, recording wall-clock time and any
   MOD-file edits required. This is the cheapest test of the primary recommendation.

## Source Index

### [Awile2022]

* **Type**: paper
* **Title**: Modernizing the NEURON Simulator for Sustainability, Portability, and Performance
* **Authors**: Awile, O., Kumbhar, P., Cornu, N., Dura-Bernal, S. et al.
* **Year**: 2022
* **DOI**: `10.3389/fninf.2022.884046`
* **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9272742/
* **Peer-reviewed**: yes (Frontiers in Neuroinformatics)
* **Relevance**: Provides NEURON's CoreNEURON CPU/GPU benchmark numbers (3.5x to 52x), pip wheel
  distribution metrics (~3000 downloads/month), and modernisation evidence used in the
  primary-simulator decision.

### [Stimberg2019]

* **Type**: paper
* **Title**: Brian 2, an intuitive and efficient neural simulator
* **Authors**: Stimberg, M., Brette, R., Goodman, D. F. M.
* **Year**: 2019
* **DOI**: `10.7554/eLife.47314`
* **URL**: https://elifesciences.org/articles/47314
* **Peer-reviewed**: yes (eLife)
* **Relevance**: Canonical Brian2 reference. Authors explicitly characterise multicompartment
  support as "not yet as mature as those of specialised simulators such as NEURON" — direct evidence
  for ruling out Brian2 as primary or backup.

### [Plastic-Arbor-2026]

* **Type**: paper
* **Title**: Plastic Arbor: A modern simulation framework for synaptic plasticity — From single
  synapses to networks of morphological neurons
* **Authors**: Luboeinski, J., Schmitt, S., Shafiee, S. et al.
* **Year**: 2026
* **DOI**: `10.1371/journal.pcbi.1013926`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013926
* **Peer-reviewed**: yes (PLOS Computational Biology)
* **Relevance**: Most recent peer-reviewed cross-simulator benchmark; reports Arbor 7-12x faster
  than NEURON on single morphological cells and "markedly more efficient" overall. Decisive evidence
  for selecting Arbor as backup.

### [Schachter2010]

* **Type**: paper
* **Title**: Dendritic Spikes Amplify the Synaptic Signal to Enhance Detection of Motion in a
  Simulation of the Direction-Selective Ganglion Cell
* **Authors**: Schachter, M. J., Oesch, N., Smith, R. G., Taylor, W. R.
* **Year**: 2010
* **DOI**: `10.1371/journal.pcbi.1000899`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000899
* **Peer-reviewed**: yes (PLOS Computational Biology)
* **Relevance**: Already in t0002 corpus. Cited here because it is the second most relevant
  published DSGC NEURON model and would be a fallback target if ModelDB 189347 fails to reproduce.

### [ModelDB-189347]

* **Type**: repository
* **Title**: Multiplication by NMDA receptors in Direction Selective Ganglion cells (Poleg-Polsky &
  Diamond 2016)
* **Author/Org**: Alon Poleg-Polsky, Jeffrey S. Diamond (ModelDB accession 189347)
* **Date**: 2016 (deposit), latest verification not stated on entry surfaced
* **URL**: https://modeldb.science/189347
* **Peer-reviewed**: yes (model accompanies a peer-reviewed Neuron paper)
* **Relevance**: The only public DSGC compartmental model code located by the searches. Implemented
  in NEURON. This single asset is the strongest argument for picking NEURON as the project's primary
  simulator.

### [NEURON-Changelog]

* **Type**: documentation
* **Title**: NEURON simulator changelog
* **Author/Org**: Yale/Duke NEURON team (`neuronsimulator/nrn`)
* **Date**: 2026-04 (latest entry 9.0.1, 17 Nov 2025)
* **URL**: https://github.com/neuronsimulator/nrn/blob/master/docs/changelog.md
* **Last updated**: 2025-11-17
* **Peer-reviewed**: no (project documentation)
* **Relevance**: Source for NEURON release dates (8.2.4 Feb 2024, 8.2.6 Jul 2024, 8.2.7 May 2025,
  9.0.0 Sep 2025, 9.0.1 Nov 2025) and for the warning that NEURON 9.0's C++ migration may break
  legacy MOD files.

### [NEURON-Py313-Issue]

* **Type**: forum
* **Title**: Python 3.14 support / NRN pip package not installable on Python 3.13 (issues #3595 and
  #3316)
* **Author/Org**: NEURON GitHub issue tracker
* **Date**: 2024-2025 (open and resolved threads)
* **URL**: https://github.com/neuronsimulator/nrn/issues/3595
* **Peer-reviewed**: no (issue tracker)
* **Relevance**: Confirms the lag between Python releases and NEURON wheels; informs the
  recommendation to pin Python 3.11 or 3.12 for stability rather than chase 3.13/3.14.

### [Arbor-Releases]

* **Type**: documentation
* **Title**: Arbor release history
* **Author/Org**: arbor-sim
* **Date**: 2025-04-17 (v0.12.0 latest)
* **URL**: https://github.com/arbor-sim/arbor/releases
* **Last updated**: 2025-04-17
* **Peer-reviewed**: no
* **Relevance**: Source for Arbor release activity (v0.10.0 Aug 2024, v0.11.0 Apr 2024 backport,
  v0.12.0 Apr 2025) — the maintenance evidence behind selecting Arbor as backup.

### [Arbor-Install-Doc]

* **Type**: documentation
* **Title**: Arbor Python Installation
* **Author/Org**: arbor-sim
* **Date**: 2026-04 (current)
* **URL**: https://docs.arbor-sim.org/en/latest/install/python.html
* **Peer-reviewed**: no
* **Relevance**: Confirms `pip install arbor` is the supported install path and that wheels exist
  for Python >=3.7. Required to validate the `uv pip install arbor` workflow.

### [Arbor-RTD-2025]

* **Type**: documentation
* **Title**: Arbor documentation (overview + benchmarks)
* **Author/Org**: arbor-sim
* **Date**: 2026-04
* **URL**: https://docs.arbor-sim.org/en/latest/index.html
* **Peer-reviewed**: no
* **Relevance**: Source for Arbor's claimed 5-8x MPI speedup over NEURON and the doubling under
  HPC-tuned distribution; corroborates the Plastic-Arbor benchmark numbers.

### [Arbor-NMODL-Doc]

* **Type**: documentation
* **Title**: NMODL — Arbor documentation
* **Author/Org**: arbor-sim
* **Date**: 2026-04
* **URL**: https://docs.arbor-sim.org/en/latest/fileformat/nmodl.html
* **Peer-reviewed**: no
* **Relevance**: Documents the strict NMODL dialect modcc enforces — special variables must be
  PARAMETER not ASSIGNED, some NEURON constructions are disallowed. Source of the MOD-file porting
  caveat in the NMODL Portability section.

### [NetPyNE-Doc]

* **Type**: documentation
* **Title**: NetPyNE documentation (installation, batch, optimization modules)
* **Author/Org**: SUNY Downstate Medical Center
* **Date**: 2026-04
* **URL**: http://doc.netpyne.org/
* **Peer-reviewed**: no
* **Relevance**: Documents the `Batch` class, Optuna parallel module, and inspyred evolutionary
  module that make NetPyNE the ergonomic choice for the project's parameter-sweep stage. Also source
  for the install requirement that NEURON be present before `pip install netpyne`.

### [NetPyNE-GH]

* **Type**: repository
* **Title**: NetPyNE
* **Author/Org**: suny-downstate-medical-center
* **URL**: https://github.com/suny-downstate-medical-center/netpyne
* **Last updated**: 2025-09-14 (v1.1.1)
* **Peer-reviewed**: no
* **Relevance**: Confirms NetPyNE is alive (169 GitHub stars, v1.1.1 in Sep 2025) — the maintenance
  evidence used to keep NetPyNE on the recommended stack.

### [Brian2-MC-Docs]

* **Type**: documentation
* **Title**: Multicompartment models — Brian 2 documentation
* **Author/Org**: brian-team
* **Date**: 2026-04 (current 2.10.x)
* **URL**: https://brian2.readthedocs.io/en/stable/user/multicompartmental.html
* **Peer-reviewed**: no
* **Relevance**: Source for the Brian2 SpatialNeuron API surface; documents the restriction that
  multicompartment code generation only targets the C++ standalone path, ruling out the GPU/Cython
  routes the rest of Brian2 supports.

### [Brian2-GH]

* **Type**: repository
* **Title**: Brian 2 simulator GitHub repository
* **Author/Org**: brian-team
* **URL**: https://github.com/brian-team/brian2
* **Last updated**: 2026 (continuous to PyPI; no GitHub release tags)
* **Peer-reviewed**: no
* **Relevance**: Source for the Brian2 maintenance signal (1.2k stars, 176 open issues, 29 open PRs,
  no GitHub release tags). The lack of release tags is itself a flag for downstream users trying to
  lock versions.

### [MOOSE-GH]

* **Type**: repository
* **Title**: MOOSE — Multiscale Object-Oriented Simulation Environment
* **Author/Org**: BhallaLab (NCBS, Bangalore)
* **URL**: https://github.com/BhallaLab/moose
* **Last updated**: chamcham 3.1.x series (year not exposed on the release page surfaced)
* **Peer-reviewed**: no
* **Relevance**: Source for the MOOSE maintenance signal (22 stars, single-lab maintenance) used to
  rule out MOOSE as primary or backup.

### [MOOSE-Releases]

* **Type**: documentation
* **Title**: BhallaLab/moose releases page
* **Author/Org**: BhallaLab
* **URL**: https://github.com/BhallaLab/moose/releases
* **Peer-reviewed**: no
* **Relevance**: Lists MOOSE chamcham 3.1.x tags. Notable that the displayed releases lack visible
  year markers — a maintenance-hygiene signal.

### [MOOSE-Rdes-Doc]

* **Type**: documentation
* **Title**: Rdesigneur — Building multiscale models (MOOSE chennapoda 3.2.rc documentation)
* **Author/Org**: BhallaLab
* **URL**: https://moose.ncbs.res.in/readthedocs/user/py/rdesigneur/rdes.html
* **Peer-reviewed**: no
* **Relevance**: Documents that rdesigneur loads SWC morphologies, supports voltage-gated channels
  in dendrites via `chanDistrib`, and lacks a built-in batch layer. Source for the MOOSE
  cable-fidelity rating used in the comparison.

### [jzlab-DSG-GH]

* **Type**: repository
* **Title**: dsg — Computational model of the direction selective ganglion cells of the mouse retina
* **Author/Org**: jzlab (Joel Zylberberg lab)
* **URL**: https://github.com/jzlab/dsg
* **Last updated**: code accompanying Zylberberg, Cafaro, Turner et al., Neuron 2016
* **Peer-reviewed**: no (code repo accompanying peer-reviewed paper)
* **Relevance**: MATLAB-only population-level DSGC model. Documented here so it is not mistaken for
  a candidate compartmental simulator implementation; useful only as a downstream
  comparison/validation source.

### [Berens-RGC-GH]

* **Type**: repository
* **Title**: rgc_dendrites — Code for Type-specific dendritic integration in mouse retinal ganglion
  cells
* **Author/Org**: berenslab
* **URL**: https://github.com/berenslab/rgc_dendrites
* **Last updated**: not surfaced
* **Peer-reviewed**: no (repo accompanies peer-reviewed work)
* **Relevance**: RGC dendrite code (not DSGC-specific) cited as evidence that Brian2/Arbor have no
  DSGC examples but do have RGC examples in adjacent ecosystems.
