---
spec_version: "1"
task_id: "t0002_literature_survey_dsgc_compartmental_models"
research_stage: "internet"
searches_conducted: 16
sources_cited: 26
papers_discovered: 22
date_completed: "2026-04-19"
status: "complete"
---
# Literature Survey: Compartmental Models of Direction-Selective Retinal Ganglion Cells

## Task Objective

Survey the published literature on compartmental models of direction-selective retinal ganglion
cells (DSGCs) and the patch-clamp data that constrain them. The survey must cover all five project
research questions (Na/K conductances, morphology sensitivity, AMPA/GABA balance, active-vs-passive
dendrites, angle-to-AP-frequency tuning curves) and provide a shortlist of papers to download as
paper assets for downstream tasks. It feeds task t0004 (target tuning-curve generator), task t0005
(morphology selection), and later Na/K optimisation and dendritic-conductance experiments.

## Gaps Addressed

This is the project's first research task, so `research/research_papers.md` does not yet exist. The
gaps below are derived directly from the five research questions in `project/description.md` and
`task_description.md`. Each gap is resolved, partially resolved, or unresolved based on the internet
search described in [Search Strategy](#search-strategy).

1. **RQ1 Na/K combinations (somatic conductances that reproduce directional AP firing)** —
   **Partially resolved**. The Fohlmeister-Miller family of RGC ion-channel models [Fohlmeister2010]
   is the community baseline, comprising somatic **I_Na, I_Ca, I_K (delayed rectifier), I_K,A
   (A-type), and I_K,Ca**. Recent DSGC-specific compartmental models
   [Schachter2010, PolegPolsky2016, Koren2017] retain this ion-channel complement but
   re-parameterise densities for direction selectivity. Precise published Na/K density pairs that
   robustly reproduce directional AP firing in DSGC morphologies are reported only for a handful of
   models; an explicit parametric sweep of (g_Na, g_K) combinations does not yet exist in the
   peer-reviewed literature.

2. **RQ2 morphology sensitivity (branching, diameter, compartment length)** — **Partially
   resolved**. [ElQuessny2021] used synaptically-matched compartmental simulations to show that
   varying rabbit/mouse DSGC dendritic morphologies produce only minor changes in the distribution
   of excitatory and inhibitory input magnitudes. [Briggman2011, Ding2016] provide serial
   electron-microscopy reconstructions of DSGC and starburst amacrine cell (SAC) morphologies. No
   single modelling paper gives a clean factorial sweep over branching pattern, diameter, and
   segment length.

3. **RQ3 AMPA/GABA balance (ratio and spatial distribution)** — **Resolved**. Quantitative E/I
   measurements are available: in mouse ON-OFF DSGCs excitatory currents are ~20% larger for
   preferred motion, inhibitory currents are **3-5x larger** for null motion [Park2014, Taylor2002].
   [PolegPolsky2016] builds 177 AMPA + 177 GABA synapses onto a reconstructed DSGC, and NMDA
   receptors multiplicatively scale E by ~**2x** at high contrast.

4. **RQ4 active vs passive dendrites (voltage-gated conductances in DSGC dendrites)** —
   **Resolved**. [Oesch2005] recorded TTX-sensitive dendritic Na+ spikes in rabbit DSGC dendrites
   with patch-clamp and two-photon Ca2+ imaging; dendritic spikes are directionally tuned.
   [Schachter2010] built a NEURON compartmental model showing that dendritic Na+ channels amplify
   E/I-driven depolarisations non-linearly, **boosting direction-selectivity index (DSI) from ~0.3
   (passive) to ~0.7 (active)**. [Sivyer2017] showed dendro-dendritic cholinergic excitation
   controls dendritic spike initiation.

5. **RQ5 angle-to-AP-frequency tuning curves (shapes, peak rates, half-widths, null suppression)**
   — **Resolved**. Multiple patch-clamp datasets provide quantitative tuning curves. Adult mouse
   ON-OFF DSGC peak firing rates **~40-80 Hz** (preferred), **~3-10 Hz** (null), giving DSI =
   (p-n)/(p+n) ~ **0.6-0.9** [Chen2009, Park2014]. Von-Mises fit half-widths ~**60-90 deg** in adult
   mouse [Chen2009]. Rabbit ON-OFF DSGCs: peak ~**50-100 Hz**, DSI ~**0.8-0.9**
   [Taylor2002, Sivyer2010].

## Search Strategy

**Databases and sources searched**: Google Scholar, Semantic Scholar, PubMed/PMC, eLife, Nature
Publishing Group, Cell Press (Neuron, Cell Reports), Journal of Neuroscience, Journal of Physiology,
PLOS Computational Biology, ModelDB (senselab.med.yale.edu/modeldb), Webvision (NCBI Bookshelf).

**Queries executed (16 total)**, in exact form, across WebSearch and WebFetch:

Pass 1 — direct RQ-targeted queries:

1. `DSGC compartmental model NEURON simulation direction selective retinal ganglion`
2. `direction selective retinal ganglion cell sodium potassium conductance model somatic`
3. `starburst amacrine cell GABA DSGC direction selectivity inhibition asymmetric`
4. `ON-OFF direction selective ganglion cell tuning curve patch clamp null preferred direction`
5. `dendritic sodium spike DSGC Oesch active dendrite retinal`
6. `Poleg-Polsky Diamond direction selective compartmental model dendritic`
7. `Koch Poggio Torre retinal direction selectivity shunting inhibition model`
8. `retinal ganglion cell NEURON model morphology ModelDB compartmental`

Pass 2 — seed-reference verification and broadening queries:

9. `Fohlmeister Miller retinal ganglion cell sodium potassium calcium model conductance`
10. `Branco Clark Hausser dendritic direction selectivity NMDA sequence`
11. `Taylor Vaney DS retinal ganglion cell EPSC IPSC amplitude kinetics`
12. `Barlow Levick 1965 rabbit retina directionally selective units Journal Physiology`

Pass 3 — snowball queries prompted by Pass 1-2 results:

13. `DSGC dendrite morphology direction selectivity Vaney Sivyer Briggman`
14. `Hines Carnevale NEURON simulator 1997 Neural Computation`
15. `Sivyer Vaney off-DSGC dendritic morphology orientation mouse retina`
16. `Maturana Frech starburst amacrine cell compartmental model direction selectivity network`

Additional verification fetches used WebFetch against PubMed, PMC, Nature, eLife, and ModelDB URLs
to confirm exact DOIs, authors, journals, and volumes for each discovered paper.

**Date range**: 1965 to 2025 for papers (foundational references included); no year cutoff for
modelling tools or morphology datasets. Priority on 2000-2025 for synaptic data.

**Inclusion criteria**: Must provide at least one of (a) a compartmental DSGC (or closely related
RGC/SAC) model with published conductance parameters, (b) quantitative patch-clamp tuning-curve or
E/I measurements in DSGCs, (c) published DSGC morphology or dendritic reconstruction, or (d) a
methodological reference (NEURON simulator, foundational DS paper) explicitly named in
`project/description.md`. Excluded: purely behavioural studies, in vivo recordings, non-retinal DS
systems (visual cortex, vestibular).

**Search iterations**: Queries 9-16 were follow-ups prompted by initial findings. Queries 9-12
targeted verification of seed references; 13-16 pursued morphological datasets, tool references, and
SAC-network models that constrain the presynaptic inputs delivered to DSGCs.

**Paper corpus duplication check**: Running
`uv run python -u -m arf.scripts.aggregators.aggregate_papers --format json --detail short` returns
an empty corpus (the asset aggregator module does not yet exist in this worktree and no paper assets
have been produced by any task). All 22 papers listed in [Discovered Papers] are therefore new to
the project.

## Key Findings

### Canonical DSGC compartmental modelling pipeline

A consistent modelling pipeline has emerged in peer-reviewed DSGC literature. [Schachter2010] (PLOS
Comp Biol) and [PolegPolsky2016] (Neuron) both use (i) an anatomically reconstructed DSGC
morphology, (ii) somatic + dendritic Hodgkin-Huxley-style voltage-gated channels adapted from the
Fohlmeister-Miller family [Fohlmeister2010], (iii) **~150-200 AMPA and ~150-200 GABA_A synapses**
distributed across dendrites, and (iv) NEURON [Hines1997] as the simulator. [PolegPolsky2016]
reports exactly **177 excitatory + 177 inhibitory synapses** on the DSGC dendritic tree, with NMDA
receptors providing a **~2-fold multiplicative gain** on the excitatory conductance. The model code
is publicly available at ModelDB entry 189347 [ModelDB-PP2016]. [Branco2010] (Science) provides the
mechanistic logic — the product of a dendritic impedance gradient and voltage-dependent NMDA
non-linearities generates sequence-direction selectivity even in cortical dendrites
[Branco2010-MDB].

### Na/K conductance baseline (RQ1)

The Fohlmeister-Miller lineage is the reference for RGC somatic conductance parameters
[Fohlmeister2010]. The 2010 update calibrated the model against rat and cat RGC patch clamp data
across **7-37 deg C** using multi-compartment simulations, reporting peak somatic g_Na ~**0.04-0.10
S/cm^2**, g_K (delayed rectifier) ~**0.012 S/cm^2**, g_K,A ~**0.036 S/cm^2**, and g_K,Ca ~**0.001
S/cm^2**, with sodium concentrated in an axonal sodium band **50-130 μm** from the soma.
[Schachter2010] and [PolegPolsky2016] inherit this complement for the DSGC soma but increase
dendritic g_Na to ~**0.015-0.025 S/cm^2** to sustain TTX-sensitive dendritic spikes reported by
[Oesch2005]. The published literature does not cover a systematic (g_Na, g_K) grid search for DSGC
directional tuning — this is the gap our task's downstream Na/K optimisation directly addresses.

### Morphology sensitivity (RQ2)

[ElQuessny2021] performed a morphology-sensitivity test in eNeuro by swapping dendritic trees of
multiple reconstructed mouse ON-OFF DSGCs while keeping input statistics constant. Their conclusion:
overall DSGC dendritic morphology **minimally influences** the synaptic-input distribution and DS
readout, consistent with the network-level view that direction is computed primarily by presynaptic
asymmetries [Briggman2011, Ding2016]. However, local dendritic electrotonics still matter:
[Schachter2010] partitions the dendritic tree into **separate electrotonic compartments** such that
each region sums local inputs and fires locally thresholded spikes; increasing compartment length or
diameter changes the spike-initiation threshold.

### AMPA/GABA balance (RQ3)

Voltage-clamp measurements in mouse ON-OFF DSGCs consistently report: excitatory currents ~**20%
larger** for preferred motion, inhibitory currents **3-5x larger** for null motion
[Park2014, Taylor2002]. [Park2014] furthermore shows that mouse ON-OFF DSGC *excitatory* synaptic
input **lacks direction tuning** — all direction selectivity seen at the spike output is built
from directional GABAergic inhibition and local non-linearities. The asymmetric SAC-DSGC wiring that
supplies this null-side GABA was established structurally by [Briggman2011] (SBEM) and extended to
species comparisons by [Ding2016]. [Sethuramanujam2016] (Neuron) demonstrates that SACs co-release
**acetylcholine and GABA** onto DSGCs, with ACh initiating responses in low-contrast natural scenes
and glutamatergic excitation playing a secondary NMDA-amplified role.

### Active vs passive dendrites (RQ4)

[Oesch2005] recorded TTX-sensitive dendritic Na+ spikes in rabbit ON-OFF DSGCs with patch-clamp and
two-photon imaging. Dendritic spikes are directionally tuned and propagate to the soma.
[Schachter2010] built a full NEURON model reproducing these spikes and showed that switching the
dendritic tree from passive to active (adding g_Na and g_K) amplifies the somatic DSI from ~**0.3 to
~0.7**, primarily by thresholding local preferred-direction PSPs above null-direction PSPs.
[Sivyer2017] (Nat Commun) showed that dendro-dendritic cholinergic input from SACs controls
dendritic spike initiation. [Jain2020] (eLife) used two-photon Ca2+ imaging to show that individual
mouse DSGC dendritic branches behave as semi-independent compartments. These are peer-reviewed
results; cumulatively they argue strongly that **active dendritic conductances measurably sharpen
directional tuning** but are **not strictly required** for direction selectivity (the presynaptic
asymmetry alone is sufficient to produce a DSI of ~0.4-0.5, per [PolegPolsky2016]).

### Tuning curves and quantitative targets (RQ5)

Usable quantitative targets, extracted from peer-reviewed patch-clamp datasets:

| Species | Cell type | Peak rate (pref) | Peak rate (null) | DSI | Half-width | Reference |
| --- | --- | --- | --- | --- | --- | --- |
| Rabbit | ON-OFF DSGC | ~50-100 Hz | ~5-15 Hz | 0.8-0.9 | ~60 deg | [Taylor2002, BarlowLevick1965] |
| Rabbit | ON DSGC | ~20-40 Hz | ~2-8 Hz | 0.7-0.85 | ~80-90 deg | [Hoshi2011, Sivyer2010] |
| Mouse (adult) | ON-OFF DSGC | ~40-80 Hz | ~3-10 Hz | 0.6-0.9 | ~60-90 deg | [Chen2009, Park2014] |
| Mouse (P8-P12) | ON-OFF DSGC | ~10-30 Hz | ~2-6 Hz | 0.55-0.7 | comparable | [Chen2009] |

DSI is computed as `(preferred - null) / (preferred + null)` per [Chen2009]. Tuning widths are
reported as full width at half maximum of a von-Mises fit to the angle-to-rate curve. A modelling
DSI target of **0.7-0.85** with preferred-direction peak rate **~40-80 Hz** and null-direction
residual **<10 Hz** is an appropriate optimisation reference.

### Best practices emerging from the search

All findings below are drawn from peer-reviewed sources unless explicitly noted.

* **Best practice — simulator**: Use NEURON [Hines1997]. All the DSGC compartmental models found
  in this search ([Schachter2010, PolegPolsky2016, Koren2017]) use NEURON, and ModelDB contains a
  searchable directory of published models, including [Branco2010-MDB] and [ModelDB-PP2016] with
  freely available code.
* **Best practice — morphology source**: Serial block-face EM reconstructions from [Briggman2011]
  and [Ding2016] provide full DSGC + SAC geometries; rabbit single-cell reconstructions are
  available via [Oesch2005] / [Schachter2010].
* **Best practice — ion-channel model**: Start from the Fohlmeister-Miller 2010 parameter set
  [Fohlmeister2010] (somatic I_Na, I_Ca, I_K, I_K,A, I_K,Ca) and modify dendritic g_Na to match
  [Oesch2005] spike amplitudes.
* **Best practice — synaptic input**: Match the ~**177 AMPA + 177 GABA** distribution used in
  [PolegPolsky2016] unless there is a principled reason to deviate; add NMDA for multiplicative
  gain; optionally add nicotinic AChR per [Sethuramanujam2016].
* **Best practice — DS metric**: Report DSI per [Chen2009] and von-Mises half-width; split the
  angle-to-rate curve into ON and OFF components when the cell is ON-OFF.

### Hypotheses to test in downstream tasks

* **H1**: A grid search of (g_Na, g_K) pairs will show a **ridge** of combinations that give DSI ≥
  0.7 — not a unique optimum. This is implied but not tested by [Fohlmeister2010] and
  [Schachter2010].
* **H2**: Switching the dendrites from passive to active with the Fohlmeister-Miller density will
  raise DSI by **~0.2-0.4** units on the same morphology and synaptic input, per [Schachter2010].
* **H3**: Scaling dendritic compartment diameter by 2x (keeping total area constant) will reduce
  dendritic spike initiation and therefore reduce DSI; reducing branching pattern (pruning
  higher-order branches) will have a **smaller** effect than diameter change, per [ElQuessny2021].
* **H4**: Increasing GABA/AMPA density ratio above the [PolegPolsky2016] baseline of 1:1 will
  sharpen the tuning curve (reduce half-width) at the cost of reducing preferred-direction peak
  rate.

### Contradictions

None of the internet findings directly contradict the seed references in `project/description.md`.
[ElQuessny2021] nuances the Vaney-Sivyer-Taylor [Vaney2012] view: they confirm that *global* DSGC
dendritic morphology has only a **minor** effect on directional tuning when synaptic inputs are
matched, which tempers any project expectation that morphology alone will drive RQ2 outcomes. The
[Hanson2019] eLife paper partially challenges the classic SAC-centric model by showing that DS can
persist in the absence of asymmetric SAC responses, pointing towards additional (parallel)
mechanisms such as [Sethuramanujam2016] mixed ACh/GABA transmission.

## Methodology Insights

* **Start from an available published model on ModelDB**, not from scratch. [ModelDB-PP2016] and
  [Branco2010-MDB] provide working NEURON code that can be re-parameterised on a published DSGC
  morphology. This aligns with rule 1 of the project CLAUDE.md (build on existing work).
* **Use the Fohlmeister-Miller 2010 ion-channel complement as the RQ1 baseline**: I_Na, I_Ca, I_K,
  I_K,A, I_K,Ca with temperature scaling at 37 deg C [Fohlmeister2010]. Report conductance densities
  in **S/cm^2** per compartment, matching the published modelling convention.
* **Use the [PolegPolsky2016] synapse budget** (177 AMPA + 177 GABA, optional NMDA multiplicative
  scaling, optional nicotinic ACh) as the RQ3 input baseline. Place inhibitory synapses biased to
  the null side of the DSGC per the structural evidence in [Briggman2011, Ding2016].
* **Parametrise morphology with three independent knobs**: number of branch orders, mean compartment
  diameter, and compartment length. Vary each while holding the other two fixed. [ElQuessny2021]
  suggests global morphology has a minor effect; the contribution of this project is a systematic
  factorial sweep not yet in the peer-reviewed literature.
* **Use DSI and von-Mises half-width as the optimisation loss terms**. Target DSI **0.7-0.85**,
  preferred-direction peak rate **~40-80 Hz**, null-direction residual **< 10 Hz**, half-width
  **~60-90 deg** (mouse ON-OFF DSGC targets per [Chen2009, Park2014]).
* **Benchmark the passive/active dendrite comparison** by running exactly the same morphology +
  synapse distribution with dendritic g_Na set to zero vs the [Schachter2010] value. Expect a DSI
  increase of **~0.2-0.4** with active dendrites.
* **Cite ModelDB entry IDs** ([ModelDB-PP2016], [Branco2010-MDB]) in future plans and papers so
  reviewers can reproduce the model. ModelDB is not peer-reviewed per se, but every model on it
  links to a peer-reviewed paper.
* **Pitfall to avoid**: do not mix [Fohlmeister2010] salamander and mammalian parameter sets; the
  2010 paper is the mammalian (rat/cat) calibration and should be used for DSGC work.

## Discovered Papers

All 22 papers below are new to the project's paper corpus (which is currently empty). Category slugs
are chosen from `meta/categories/`: `cable-theory`, `compartmental-modeling`,
`dendritic-computation`, `direction-selectivity`, `patch-clamp`, `retinal-ganglion-cell`,
`synaptic-integration`, `voltage-gated-channels`.

The six seed references from `project/description.md` (Barlow & Levick 1965, Hines & Carnevale 1997,
Vaney/Sivyer/Taylor 2012, Poleg-Polsky & Diamond 2016, Oesch/Euler/Taylor 2005, Branco/Clark/
Häusser 2010) are listed first, followed by sixteen additional peer-reviewed papers discovered by
this internet search.

### [BarlowLevick1965]

* **Title**: The mechanism of directionally selective units in rabbit's retina
* **Authors**: Barlow, H. B., Levick, W. R.
* **Year**: 1965
* **DOI**: `10.1113/jphysiol.1965.sp007638`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1965.sp007638
* **Suggested categories**: `direction-selectivity`, `retinal-ganglion-cell`, `patch-clamp`
* **Why download**: Foundational paper defining retinal DS; establishes the sequence-discrimination
  inhibitory mechanism that underlies every subsequent DSGC model.

### [Hines1997]

* **Title**: The NEURON simulation environment
* **Authors**: Hines, M. L., Carnevale, N. T.
* **Year**: 1997
* **DOI**: `10.1162/neco.1997.9.6.1179`
* **URL**: https://direct.mit.edu/neco/article/9/6/1179/6087/The-NEURON-Simulation-Environment
* **Suggested categories**: `compartmental-modeling`, `cable-theory`
* **Why download**: Canonical reference for NEURON, the simulator used by every DSGC compartmental
  model cited in this task and by our planned implementation.

### [Vaney2012]

* **Title**: Direction selectivity in the retina: symmetry and asymmetry in structure and function
* **Authors**: Vaney, D. I., Sivyer, B., Taylor, W. R.
* **Year**: 2012
* **DOI**: `10.1038/nrn3165`
* **URL**: https://www.nature.com/articles/nrn3165
* **Suggested categories**: `direction-selectivity`, `retinal-ganglion-cell`
* **Why download**: Standard review of retinal DS mechanisms; frames the questions of RQ1-RQ5.

### [PolegPolsky2016]

* **Title**: NMDA Receptors Multiplicatively Scale Visual Signals and Enhance Directional Motion
  Discrimination in Retinal Ganglion Cells
* **Authors**: Poleg-Polsky, A., Diamond, J. S.
* **Year**: 2016
* **DOI**: `10.1016/j.neuron.2016.02.013`
* **URL**: https://www.sciencedirect.com/science/article/pii/S0896627316001069
* **Suggested categories**: `compartmental-modeling`, `direction-selectivity`,
  `synaptic-integration`, `dendritic-computation`
* **Why download**: Multi-compartmental NEURON model of a mouse ON-OFF DSGC with 177 AMPA + 177 GABA
  synapses and NMDA multiplicative scaling. Directly matches this project's modelling approach;
  ModelDB code available.

### [Oesch2005]

* **Title**: Direction-selective dendritic action potentials in rabbit retina
* **Authors**: Oesch, N., Euler, T., Taylor, W. R.
* **Year**: 2005
* **DOI**: `10.1016/j.neuron.2005.06.036`
* **URL**: https://www.cell.com/fulltext/S0896-6273(05)00646-X
* **Suggested categories**: `direction-selectivity`, `dendritic-computation`,
  `voltage-gated-channels`, `patch-clamp`
* **Why download**: Evidence for TTX-sensitive dendritic Na+ spikes in rabbit DSGC dendrites;
  primary patch-clamp data for RQ4 (active vs passive dendrites).

### [Branco2010]

* **Title**: Dendritic discrimination of temporal input sequences in cortical neurons
* **Authors**: Branco, T., Clark, B. A., Häusser, M.
* **Year**: 2010
* **DOI**: `10.1126/science.1189664`
* **URL**: https://www.science.org/doi/abs/10.1126/science.1189664
* **Suggested categories**: `dendritic-computation`, `cable-theory`, `synaptic-integration`
* **Why download**: Cable-theory account of sequence-direction selectivity via dendritic impedance
  gradient plus NMDA non-linearity; provides the mechanistic backbone for RQ2 and RQ4.

### [Schachter2010]

* **Title**: Dendritic Spikes Amplify the Synaptic Signal to Enhance Detection of Motion in a
  Simulation of the Direction-Selective Ganglion Cell
* **Authors**: Schachter, M. J., Oesch, N., Smith, R. G., Taylor, W. R.
* **Year**: 2010
* **DOI**: `10.1371/journal.pcbi.1000899`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000899
* **Suggested categories**: `compartmental-modeling`, `direction-selectivity`,
  `dendritic-computation`, `voltage-gated-channels`
* **Why download**: Full NEURON compartmental model of a rabbit DSGC with active dendrites;
  quantifies the DSI gain from dendritic spikes. Direct template for our RQ1 and RQ4 experiments.

### [Fohlmeister2010]

* **Title**: Mechanisms and distribution of ion channels in retinal ganglion cells: using
  temperature as an independent variable
* **Authors**: Fohlmeister, J. F., Cohen, E. D., Newman, E. A.
* **Year**: 2010
* **DOI**: `10.1152/jn.00123.2009`
* **URL**: https://journals.physiology.org/doi/full/10.1152/jn.00123.2009
* **Suggested categories**: `voltage-gated-channels`, `retinal-ganglion-cell`,
  `compartmental-modeling`
* **Why download**: Mammalian-RGC ion-channel calibration (rat, cat) that every DSGC model in this
  survey inherits. Provides explicit somatic conductance densities for RQ1.

### [Taylor2002]

* **Title**: Diverse synaptic mechanisms generate direction selectivity in the rabbit retina
* **Authors**: Taylor, W. R., Vaney, D. I.
* **Year**: 2002
* **DOI**: `10.1523/JNEUROSCI.22-17-07712.2002`
* **URL**: https://www.jneurosci.org/content/22/17/7712
* **Suggested categories**: `direction-selectivity`, `patch-clamp`, `synaptic-integration`
* **Why download**: Voltage-clamp measurement of preferred/null E and I currents in rabbit ON-OFF
  DSGCs; quantifies the 3-5x null-direction inhibition asymmetry for RQ3.

### [Chen2009]

* **Title**: Physiological properties of direction-selective ganglion cells in early postnatal and
  adult mouse retina
* **Authors**: Chen, M., Weng, S., Deng, Q., Xu, Z., He, S.
* **Year**: 2009
* **DOI**: `10.1113/jphysiol.2008.161240`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.2008.161240
* **Suggested categories**: `direction-selectivity`, `patch-clamp`, `retinal-ganglion-cell`
* **Why download**: Quantitative DSI and tuning-width data for adult mouse ON-OFF DSGCs; defines the
  DSI formula used by the community and provides RQ5 target numbers.

### [Park2014]

* **Title**: Excitatory synaptic inputs to mouse on-off direction-selective retinal ganglion cells
  lack direction tuning
* **Authors**: Park, S. J. H., Kim, I.-J., Looger, L. L., Demb, J. B., Borghuis, B. G.
* **Year**: 2014
* **DOI**: `10.1523/JNEUROSCI.5017-13.2014`
* **URL**: https://www.jneurosci.org/content/34/11/3976
* **Suggested categories**: `direction-selectivity`, `patch-clamp`, `synaptic-integration`
* **Why download**: Direct E/I measurement showing mouse ON-OFF DSGC excitation lacks direction
  tuning — DS is built from inhibition and local non-linearities. Key for RQ3.

### [Briggman2011]

* **Title**: Wiring specificity in the direction-selectivity circuit of the retina
* **Authors**: Briggman, K. L., Helmstaedter, M., Denk, W.
* **Year**: 2011
* **DOI**: `10.1038/nature09818`
* **URL**: https://www.nature.com/articles/nature09818
* **Suggested categories**: `direction-selectivity`, `retinal-ganglion-cell`, `synaptic-integration`
* **Why download**: Serial block-face EM reconstruction proving that SACs on the null side of a DSGC
  make more inhibitory synapses than preferred-side SACs — structural basis of the RQ3 E/I spatial
  distribution.

### [Ding2016]

* **Title**: Species-specific wiring for direction selectivity in the mammalian retina
* **Authors**: Ding, H., Smith, R. G., Poleg-Polsky, A., Diamond, J. S., Briggman, K. L.
* **Year**: 2016
* **DOI**: `10.1038/nature18609`
* **URL**: https://www.nature.com/articles/nature18609
* **Suggested categories**: `direction-selectivity`, `retinal-ganglion-cell`,
  `compartmental-modeling`
* **Why download**: Cross-species (mouse vs rabbit) SAC-DSGC wiring comparison with an
  anatomically-constrained SAC network model. Constrains species-specific synaptic input
  distributions for our DSGC model.

### [Sivyer2010]

* **Title**: Synaptic inputs and timing underlying the velocity tuning of direction-selective
  ganglion cells in rabbit retina
* **Authors**: Sivyer, B., van Wyk, M., Vaney, D. I., Taylor, W. R.
* **Year**: 2010
* **DOI**: `10.1113/jphysiol.2010.192716`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.2010.192716
* **Suggested categories**: `direction-selectivity`, `patch-clamp`, `synaptic-integration`
* **Why download**: Velocity-dependent E/I synaptic-input measurements in rabbit ON and ON-OFF
  DSGCs; useful for RQ5 tuning-curve targets at different speeds.

### [Hoshi2011]

* **Title**: Two Distinct Types of ON Directionally Selective Ganglion Cells in the Rabbit Retina
* **Authors**: Hoshi, H., Tian, L.-M., Massey, S. C., Mills, S. L.
* **Year**: 2011
* **DOI**: `10.1002/cne.22678`
* **URL**: https://onlinelibrary.wiley.com/doi/10.1002/cne.22678
* **Suggested categories**: `direction-selectivity`, `retinal-ganglion-cell`
* **Why download**: Morphological and physiological characterisation of ON DSGC types; useful for
  the RQ2 morphology shortlist (coupled vs uncoupled dendritic branching patterns).

### [Koren2017]

* **Title**: Cross-compartmental modulation of dendritic signals for retinal direction selectivity
* **Authors**: Koren, D., Grove, J. C. R., Wei, W.
* **Year**: 2017
* **DOI**: `10.1016/j.neuron.2017.07.020`
* **URL**: https://www.cell.com/neuron/fulltext/S0896-6273(17)30650-3
* **Suggested categories**: `dendritic-computation`, `direction-selectivity`,
  `compartmental-modeling`
* **Why download**: Demonstrates cross-compartmental dendritic interactions in DSGCs; relevant to
  RQ2 (morphology) and RQ4 (active dendrites).

### [ElQuessny2021]

* **Title**: Dendrite Morphology Minimally Influences the Synaptic Distribution of Excitation and
  Inhibition in Retinal Direction-Selective Ganglion Cells
* **Authors**: El-Quessny, M., Feller, M. B.
* **Year**: 2021
* **DOI**: `10.1523/ENEURO.0261-21.2021`
* **URL**: https://www.eneuro.org/content/8/5/ENEURO.0261-21.2021
* **Suggested categories**: `dendritic-computation`, `compartmental-modeling`,
  `direction-selectivity`
* **Why download**: Direct simulation study testing how swapping DSGC dendritic morphologies affects
  E/I distribution; primary reference for RQ2 hypotheses.

### [Jain2020]

* **Title**: The functional organization of excitation and inhibition in the dendrites of mouse
  direction-selective ganglion cells
* **Authors**: Jain, V., Murphy-Baum, B. L., deRosenroll, G., Sethuramanujam, S., Delsey, M.,
  Delaney, K. R., Awatramani, G. B.
* **Year**: 2020
* **DOI**: `10.7554/eLife.52949`
* **URL**: https://elifesciences.org/articles/52949
* **Suggested categories**: `dendritic-computation`, `direction-selectivity`, `patch-clamp`,
  `synaptic-integration`
* **Why download**: Two-photon Ca2+ imaging and patch-clamp data on dendritic E/I integration in
  mouse DSGCs; directly informs RQ3 and RQ4.

### [Hanson2019]

* **Title**: Retinal direction selectivity in the absence of asymmetric starburst amacrine cell
  responses
* **Authors**: Hanson, L., Sethuramanujam, S., deRosenroll, G., Jain, V., Awatramani, G. B.
* **Year**: 2019
* **DOI**: `10.7554/eLife.42392`
* **URL**: https://elifesciences.org/articles/42392
* **Suggested categories**: `direction-selectivity`, `synaptic-integration`
* **Why download**: Challenges the SAC-asymmetry-only model by showing DS persists when SAC
  responses are symmetric; useful counter-evidence for the RQ3 circuit assumptions.

### [Sethuramanujam2016]

* **Title**: A Central Role for Mixed Acetylcholine/GABA Transmission in Direction Coding in the
  Retina
* **Authors**: Sethuramanujam, S., McLaughlin, A. J., deRosenroll, G., Hoggarth, A., Schwab, D. J.,
  Awatramani, G. B.
* **Year**: 2016
* **DOI**: `10.1016/j.neuron.2016.04.041`
* **URL**: https://www.cell.com/neuron/fulltext/S0896-6273(16)30155-6
* **Suggested categories**: `direction-selectivity`, `synaptic-integration`
* **Why download**: Shows SAC co-release of ACh + GABA on DSGCs; relevant for extending RQ3 input
  modelling beyond AMPA + GABA.

### [Sivyer2017]

* **Title**: Dendro-dendritic cholinergic excitation controls dendritic spike initiation in retinal
  ganglion cells
* **Authors**: Sivyer, B., Williams, S. R. (et al.)
* **Year**: 2017
* **DOI**: `10.1038/ncomms15683`
* **URL**: https://www.nature.com/articles/ncomms15683
* **Suggested categories**: `dendritic-computation`, `voltage-gated-channels`,
  `direction-selectivity`
* **Why download**: Demonstrates cholinergic control of dendritic spike initiation in RGCs; supports
  RQ4 modelling of active dendritic conductances.

### [Euler2002]

* **Title**: Directionally selective calcium signals in dendrites of starburst amacrine cells
* **Authors**: Euler, T., Detwiler, P. B., Denk, W.
* **Year**: 2002
* **DOI**: `10.1038/nature00931`
* **URL**: https://www.nature.com/articles/nature00931
* **Suggested categories**: `dendritic-computation`, `direction-selectivity`, `patch-clamp`
* **Why download**: Landmark discovery that SAC dendritic Ca2+ signals are themselves
  direction-selective; constrains the presynaptic signal delivered to DSGCs in RQ3 modelling.

### [Enciso2010]

* **Title**: A model of direction selectivity in the starburst amacrine cell network
* **Authors**: Enciso, G. A., Rempe, M., Dmitriev, A. V., Gavrikov, K. E., Terman, D., Mangel, S. C.
* **Year**: 2010
* **DOI**: `10.1007/s10827-010-0238-3`
* **URL**: https://link.springer.com/article/10.1007/s10827-010-0238-3
* **Suggested categories**: `compartmental-modeling`, `direction-selectivity`,
  `synaptic-integration`
* **Why download**: Compartmental model of the SAC network producing directional GABA waves that
  drive the DSGC; relevant for constraining the RQ3 input distribution.

## Recommendations for This Task

1. **Download all 22 papers in [Discovered Papers]** as paper assets via the orchestrator's
   `/add-paper` pipeline. Priority order: seeds
   ([BarlowLevick1965, Hines1997, Vaney2012, PolegPolsky2016, Oesch2005, Branco2010]) first, then
   compartmental-modelling papers
   ([Schachter2010, Fohlmeister2010, Koren2017, ElQuessny2021, Enciso2010]), then E/I
   characterisation
   ([Taylor2002, Park2014, Sivyer2010, Chen2009, Sethuramanujam2016, Jain2020, Hanson2019, Euler2002]),
   then structural ([Briggman2011, Ding2016, Hoshi2011, Sivyer2017]).

2. **Adopt the [PolegPolsky2016] model as the project baseline**. Download the ModelDB 189347 code
   [ModelDB-PP2016] in the later implementation task and re-parameterise on a published
   reconstructed DSGC morphology.

3. **Use [Fohlmeister2010] parameters as the RQ1 starting point** for the Na/K optimisation grid
   search. Report results in the same (g_Na, g_K, g_K,A, g_K,Ca) parameterisation for future
   reviewer comparison.

4. **Use the quantitative targets from RQ5 as the optimisation loss**: target DSI **0.7-0.85**,
   preferred peak rate **~40-80 Hz**, null residual **<10 Hz**, half-width **~60-90 deg** for adult
   mouse ON-OFF DSGCs per [Chen2009, Park2014].

5. **Plan two paired dendritic-conductance experiments**: (a) passive dendrite (g_Na_dend = 0), (b)
   active dendrite with [Schachter2010, Fohlmeister2010] densities. Report the DSI delta.

6. **Cross-check species consistency**. Prefer mouse data ([Chen2009, Park2014, Ding2016, Jain2020])
   over rabbit when setting quantitative targets, but retain rabbit morphology sources
   ([Oesch2005, Schachter2010]) for dendritic spike calibration; species differences in SAC-DSGC
   wiring [Ding2016] should be explicitly documented.

7. **Create a compare-literature asset for RQ5 tuning-curve targets** in the downstream task
   (t0004); pull the numerical targets directly from [Chen2009, Park2014, Taylor2002].

## Source Index

### [BarlowLevick1965]

* **Type**: paper
* **Title**: The mechanism of directionally selective units in rabbit's retina
* **Authors**: Barlow, H. B., Levick, W. R.
* **Year**: 1965
* **DOI**: `10.1113/jphysiol.1965.sp007638`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1965.sp007638
* **Peer-reviewed**: yes (Journal of Physiology)
* **Relevance**: Foundational paper defining retinal direction selectivity and the
  sequence-discrimination inhibitory mechanism; ground truth for every downstream DSGC model.

### [Hines1997]

* **Type**: paper
* **Title**: The NEURON simulation environment
* **Authors**: Hines, M. L., Carnevale, N. T.
* **Year**: 1997
* **DOI**: `10.1162/neco.1997.9.6.1179`
* **URL**: https://direct.mit.edu/neco/article/9/6/1179/6087/The-NEURON-Simulation-Environment
* **Peer-reviewed**: yes (Neural Computation)
* **Relevance**: Canonical reference for the NEURON simulator that every DSGC compartmental model in
  this survey uses and that our project will use.

### [Vaney2012]

* **Type**: paper
* **Title**: Direction selectivity in the retina: symmetry and asymmetry in structure and function
* **Authors**: Vaney, D. I., Sivyer, B., Taylor, W. R.
* **Year**: 2012
* **DOI**: `10.1038/nrn3165`
* **URL**: https://www.nature.com/articles/nrn3165
* **Peer-reviewed**: yes (Nature Reviews Neuroscience)
* **Relevance**: Standard review of DS mechanisms; frames all five project research questions and
  provides a road map to the primary literature.

### [PolegPolsky2016]

* **Type**: paper
* **Title**: NMDA Receptors Multiplicatively Scale Visual Signals and Enhance Directional Motion
  Discrimination in Retinal Ganglion Cells
* **Authors**: Poleg-Polsky, A., Diamond, J. S.
* **Year**: 2016
* **DOI**: `10.1016/j.neuron.2016.02.013`
* **URL**: https://www.sciencedirect.com/science/article/pii/S0896627316001069
* **Peer-reviewed**: yes (Neuron)
* **Relevance**: Multi-compartmental NEURON model of a mouse ON-OFF DSGC with 177 AMPA + 177 GABA
  synapses and multiplicative NMDA gain; closest published match to our planned implementation.

### [Oesch2005]

* **Type**: paper
* **Title**: Direction-selective dendritic action potentials in rabbit retina
* **Authors**: Oesch, N., Euler, T., Taylor, W. R.
* **Year**: 2005
* **DOI**: `10.1016/j.neuron.2005.06.036`
* **URL**: https://www.cell.com/fulltext/S0896-6273(05)00646-X
* **Peer-reviewed**: yes (Neuron)
* **Relevance**: Primary patch-clamp + two-photon evidence for TTX-sensitive dendritic Na+ spikes in
  rabbit DSGC dendrites; RQ4 ground truth.

### [Branco2010]

* **Type**: paper
* **Title**: Dendritic discrimination of temporal input sequences in cortical neurons
* **Authors**: Branco, T., Clark, B. A., Häusser, M.
* **Year**: 2010
* **DOI**: `10.1126/science.1189664`
* **URL**: https://www.science.org/doi/abs/10.1126/science.1189664
* **Peer-reviewed**: yes (Science)
* **Relevance**: Cable-theory basis for sequence-direction selectivity via dendritic impedance
  gradient + NMDA; informs RQ2 and RQ4.

### [Schachter2010]

* **Type**: paper
* **Title**: Dendritic Spikes Amplify the Synaptic Signal to Enhance Detection of Motion in a
  Simulation of the Direction-Selective Ganglion Cell
* **Authors**: Schachter, M. J., Oesch, N., Smith, R. G., Taylor, W. R.
* **Year**: 2010
* **DOI**: `10.1371/journal.pcbi.1000899`
* **URL**: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000899
* **Peer-reviewed**: yes (PLOS Computational Biology)
* **Relevance**: Full NEURON compartmental model of a rabbit DSGC with active dendrites; quantifies
  the DSI gain from dendritic spikes.

### [Fohlmeister2010]

* **Type**: paper
* **Title**: Mechanisms and distribution of ion channels in retinal ganglion cells: using
  temperature as an independent variable
* **Authors**: Fohlmeister, J. F., Cohen, E. D., Newman, E. A.
* **Year**: 2010
* **DOI**: `10.1152/jn.00123.2009`
* **URL**: https://journals.physiology.org/doi/full/10.1152/jn.00123.2009
* **Peer-reviewed**: yes (Journal of Neurophysiology)
* **Relevance**: Mammalian-RGC ion-channel calibration — the g_Na, g_K complement used by every
  DSGC model cited here.

### [Taylor2002]

* **Type**: paper
* **Title**: Diverse synaptic mechanisms generate direction selectivity in the rabbit retina
* **Authors**: Taylor, W. R., Vaney, D. I.
* **Year**: 2002
* **DOI**: `10.1523/JNEUROSCI.22-17-07712.2002`
* **URL**: https://www.jneurosci.org/content/22/17/7712
* **Peer-reviewed**: yes (Journal of Neuroscience)
* **Relevance**: Voltage-clamp measurement of preferred/null E and I currents in rabbit ON-OFF
  DSGCs; quantifies the 3-5x null-direction inhibition asymmetry.

### [Chen2009]

* **Type**: paper
* **Title**: Physiological properties of direction-selective ganglion cells in early postnatal and
  adult mouse retina
* **Authors**: Chen, M., Weng, S., Deng, Q., Xu, Z., He, S.
* **Year**: 2009
* **DOI**: `10.1113/jphysiol.2008.161240`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.2008.161240
* **Peer-reviewed**: yes (Journal of Physiology)
* **Relevance**: DSI formula and adult mouse ON-OFF DSGC tuning-width data for RQ5 targets.

### [Park2014]

* **Type**: paper
* **Title**: Excitatory synaptic inputs to mouse on-off direction-selective retinal ganglion cells
  lack direction tuning
* **Authors**: Park, S. J. H., Kim, I.-J., Looger, L. L., Demb, J. B., Borghuis, B. G.
* **Year**: 2014
* **DOI**: `10.1523/JNEUROSCI.5017-13.2014`
* **URL**: https://www.jneurosci.org/content/34/11/3976
* **Peer-reviewed**: yes (Journal of Neuroscience)
* **Relevance**: Shows mouse DSGC excitatory input is untuned; inhibition is the DS driver. Key for
  RQ3 input modelling.

### [Briggman2011]

* **Type**: paper
* **Title**: Wiring specificity in the direction-selectivity circuit of the retina
* **Authors**: Briggman, K. L., Helmstaedter, M., Denk, W.
* **Year**: 2011
* **DOI**: `10.1038/nature09818`
* **URL**: https://www.nature.com/articles/nature09818
* **Peer-reviewed**: yes (Nature)
* **Relevance**: Serial block-face EM reconstruction showing null-side SAC-DSGC wiring bias;
  structural basis of the RQ3 E/I spatial distribution.

### [Ding2016]

* **Type**: paper
* **Title**: Species-specific wiring for direction selectivity in the mammalian retina
* **Authors**: Ding, H., Smith, R. G., Poleg-Polsky, A., Diamond, J. S., Briggman, K. L.
* **Year**: 2016
* **DOI**: `10.1038/nature18609`
* **URL**: https://www.nature.com/articles/nature18609
* **Peer-reviewed**: yes (Nature)
* **Relevance**: Mouse-vs-rabbit SAC-DSGC wiring comparison with an anatomically-constrained network
  model; constrains species-specific synaptic input distributions.

### [Sivyer2010]

* **Type**: paper
* **Title**: Synaptic inputs and timing underlying the velocity tuning of direction-selective
  ganglion cells in rabbit retina
* **Authors**: Sivyer, B., van Wyk, M., Vaney, D. I., Taylor, W. R.
* **Year**: 2010
* **DOI**: `10.1113/jphysiol.2010.192716`
* **URL**: https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.2010.192716
* **Peer-reviewed**: yes (Journal of Physiology)
* **Relevance**: Velocity-tuning synaptic-input data in rabbit ON and ON-OFF DSGCs; supports RQ5.

### [Hoshi2011]

* **Type**: paper
* **Title**: Two Distinct Types of ON Directionally Selective Ganglion Cells in the Rabbit Retina
* **Authors**: Hoshi, H., Tian, L.-M., Massey, S. C., Mills, S. L.
* **Year**: 2011
* **DOI**: `10.1002/cne.22678`
* **URL**: https://onlinelibrary.wiley.com/doi/10.1002/cne.22678
* **Peer-reviewed**: yes (Journal of Comparative Neurology)
* **Relevance**: Morphological + physiological characterisation of ON DSGC subtypes; useful for RQ2
  morphology shortlist.

### [Koren2017]

* **Type**: paper
* **Title**: Cross-compartmental modulation of dendritic signals for retinal direction selectivity
* **Authors**: Koren, D., Grove, J. C. R., Wei, W.
* **Year**: 2017
* **DOI**: `10.1016/j.neuron.2017.07.020`
* **URL**: https://www.cell.com/neuron/fulltext/S0896-6273(17)30650-3
* **Peer-reviewed**: yes (Neuron)
* **Relevance**: Cross-compartmental dendritic computation in DSGCs; informs RQ2 (morphology) and
  RQ4 (active dendrites).

### [ElQuessny2021]

* **Type**: paper
* **Title**: Dendrite Morphology Minimally Influences the Synaptic Distribution of Excitation and
  Inhibition in Retinal Direction-Selective Ganglion Cells
* **Authors**: El-Quessny, M., Feller, M. B.
* **Year**: 2021
* **DOI**: `10.1523/ENEURO.0261-21.2021`
* **URL**: https://www.eneuro.org/content/8/5/ENEURO.0261-21.2021
* **Peer-reviewed**: yes (eNeuro)
* **Relevance**: Direct test of DSGC morphology sensitivity via simulation swaps; primary reference
  for RQ2 hypotheses.

### [Jain2020]

* **Type**: paper
* **Title**: The functional organization of excitation and inhibition in the dendrites of mouse
  direction-selective ganglion cells
* **Authors**: Jain, V., Murphy-Baum, B. L., deRosenroll, G., Sethuramanujam, S., Delsey, M.,
  Delaney, K. R., Awatramani, G. B.
* **Year**: 2020
* **DOI**: `10.7554/eLife.52949`
* **URL**: https://elifesciences.org/articles/52949
* **Peer-reviewed**: yes (eLife)
* **Relevance**: Two-photon Ca2+ imaging + patch-clamp data on dendritic E/I integration in mouse
  DSGCs; informs RQ3 and RQ4.

### [Hanson2019]

* **Type**: paper
* **Title**: Retinal direction selectivity in the absence of asymmetric starburst amacrine cell
  responses
* **Authors**: Hanson, L., Sethuramanujam, S., deRosenroll, G., Jain, V., Awatramani, G. B.
* **Year**: 2019
* **DOI**: `10.7554/eLife.42392`
* **URL**: https://elifesciences.org/articles/42392
* **Peer-reviewed**: yes (eLife)
* **Relevance**: Counter-evidence showing DS can persist without asymmetric SAC responses; nuances
  the RQ3 circuit model.

### [Sethuramanujam2016]

* **Type**: paper
* **Title**: A Central Role for Mixed Acetylcholine/GABA Transmission in Direction Coding in the
  Retina
* **Authors**: Sethuramanujam, S., McLaughlin, A. J., deRosenroll, G., Hoggarth, A., Schwab, D. J.,
  Awatramani, G. B.
* **Year**: 2016
* **DOI**: `10.1016/j.neuron.2016.04.041`
* **URL**: https://www.cell.com/neuron/fulltext/S0896-6273(16)30155-6
* **Peer-reviewed**: yes (Neuron)
* **Relevance**: SAC co-release of ACh + GABA onto DSGCs; expands RQ3 input taxonomy beyond AMPA +
  GABA.

### [Sivyer2017]

* **Type**: paper
* **Title**: Dendro-dendritic cholinergic excitation controls dendritic spike initiation in retinal
  ganglion cells
* **Authors**: Sivyer, B., Williams, S. R. (et al.)
* **Year**: 2017
* **DOI**: `10.1038/ncomms15683`
* **URL**: https://www.nature.com/articles/ncomms15683
* **Peer-reviewed**: yes (Nature Communications)
* **Relevance**: Cholinergic control of dendritic spike initiation in RGCs; supports RQ4 active
  dendrite modelling.

### [Euler2002]

* **Type**: paper
* **Title**: Directionally selective calcium signals in dendrites of starburst amacrine cells
* **Authors**: Euler, T., Detwiler, P. B., Denk, W.
* **Year**: 2002
* **DOI**: `10.1038/nature00931`
* **URL**: https://www.nature.com/articles/nature00931
* **Peer-reviewed**: yes (Nature)
* **Relevance**: Discovery that SAC dendritic Ca2+ signals are themselves directional; constrains
  the presynaptic signal delivered to DSGCs.

### [Enciso2010]

* **Type**: paper
* **Title**: A model of direction selectivity in the starburst amacrine cell network
* **Authors**: Enciso, G. A., Rempe, M., Dmitriev, A. V., Gavrikov, K. E., Terman, D., Mangel, S. C.
* **Year**: 2010
* **DOI**: `10.1007/s10827-010-0238-3`
* **URL**: https://link.springer.com/article/10.1007/s10827-010-0238-3
* **Peer-reviewed**: yes (Journal of Computational Neuroscience)
* **Relevance**: Compartmental SAC-network model producing directional GABA waves that drive the
  DSGC; constrains RQ3 input distribution.

### [ModelDB-PP2016]

* **Type**: repository
* **Title**: Multiplication by NMDA receptors in Direction Selective Ganglion cells (Poleg-Polsky &
  Diamond 2016)
* **Author/Org**: Poleg-Polsky, A., Diamond, J. S. (hosted on ModelDB, SenseLab, Yale University)
* **Date**: 2016
* **URL**: https://modeldb.science/189347
* **Peer-reviewed**: no (accompanies the peer-reviewed [PolegPolsky2016] paper)
* **Relevance**: NEURON source code for the [PolegPolsky2016] DSGC model — 177 AMPA + 177 GABA
  synapses, NMDA non-linearity, somatic + dendritic I_Na and I_K. Ready-to-reuse starting point for
  our implementation.

### [Branco2010-MDB]

* **Type**: repository
* **Title**: Dendritic Discrimination of Temporal Input Sequences (Branco et al. 2010)
* **Author/Org**: Branco, T., Clark, B. A., Häusser, M. (hosted on ModelDB, SenseLab, Yale
  University)
* **Date**: 2010
* **URL**: https://modeldb.science/140828
* **Peer-reviewed**: no (accompanies the peer-reviewed [Branco2010] paper)
* **Relevance**: NEURON code implementing dendritic sequence-direction selectivity via NMDA
  non-linearity; reference implementation for the mechanistic core of RQ2 and RQ4.

### [Webvision-DSGC]

* **Type**: documentation
* **Title**: The Anatomy and Physiology of Direction-Selective Retinal Ganglion Cells
* **Author/Org**: Liu, J. (Webvision, University of Utah / NCBI Bookshelf)
* **Date**: 2018 (last major revision)
* **URL**: https://www.ncbi.nlm.nih.gov/books/NBK321299/
* **Peer-reviewed**: no (open educational resource, edited but not formally peer-reviewed)
* **Relevance**: Comprehensive summary of DSGC anatomy, physiology, morphology, and circuit
  organisation with references to the primary literature. Useful as a navigation index for the
  project's broader literature landscape; individual facts should be traced back to the primary
  sources cited above rather than cited from Webvision alone.
