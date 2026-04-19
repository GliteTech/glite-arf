---
spec_version: "2"
answer_id: "how-does-dsgc-literature-structure-the-five-research-questions"
answered_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_answered: "2026-04-18"
confidence: "medium"
---
# DSGC literature structure of the five RQs

## Question

How does the existing peer-reviewed literature on compartmental models of
direction-selective retinal ganglion cells structure the five project research questions
(Na/K conductances, morphology sensitivity, AMPA/GABA balance, active vs passive
dendrites, and angle-to-AP-frequency tuning curves), and what quantitative targets does
it provide?

## Short Answer

The literature structures the five questions around a small set of quantitative targets
that the project must hit. For Na/K conductances the Fohlmeister-Miller parameter set
(peak somatic g_Na around 0.04-0.10 S/cm^2, delayed-rectifier g_K around 0.012 S/cm^2)
is the standard starting point, and no published paper reports a factorial (g_Na, g_K)
grid for DSGCs. For morphology the asymmetric ON-OFF DSGC dendrite is sharply wired in
the null direction through SAC-mediated inhibition, yet global dendrite shape only
minimally changes the synaptic map while local electrotonic compartments still matter.
For AMPA/GABA balance the canonical counts on a reconstructed mouse DSGC are 177 AMPA
and 177 GABA synapses, with null-direction inhibition running three to five times larger
than preferred inhibition. Active dendrites with Fohlmeister-like channel densities
roughly double the direction-selectivity index versus passive trees, and the target
mouse ON-OFF DSGC tuning curve should hit DSI 0.7-0.85, preferred peak 40-80 Hz, null
residual under 10 Hz, and a half-width of 60-90 degrees.

## Research Process

The research proceeded in three phases. Phase 1 collected the six seed references listed
in `project/description.md` (Barlow & Levick 1965, Hines & Carnevale 1997, Vaney et al.
2012, Poleg-Polsky & Diamond 2016, Oesch et al. 2005, Branco et al. 2010) and confirmed
their coverage of the five research questions using `research/research_internet.md`.
Phase 2 ran a structured internet search covering 14 additional peer-reviewed papers
spread across the five RQs, catalogued them in `research/research_internet.md` under
`## Discovered Papers`, and mapped each candidate to one or more RQs and to a
Schachter-style selection criterion (compartmental model, published morphology, or
quantitative angle-to-rate data). Phase 3 downloaded all 20 selected papers via the
`/add-paper` skill (one subagent per paper) and produced a per-paper canonical summary
document conforming to the paper-asset specification v3. Conflicting evidence between
papers was resolved by preferring mouse ON-OFF DSGC recordings over rabbit or turtle
data when the project target is mouse, and by citing both sources in the synthesis when
the numbers genuinely diverged. Internet sources supplemented the peer-reviewed papers
for bibliographic metadata only (DOIs, journal URLs, author affiliations); no
non-peer-reviewed claim enters the synthesis.

## Evidence from Papers

All 20 downloaded paper assets contribute evidence to this synthesis. The evidence is
organised by the five research questions.

**RQ1 (Na/K conductances).** [Fohlmeister2010][fohlmeister2010] reports the canonical
ganglion-cell parameter set with peak somatic g_Na in the 0.04-0.10 S/cm^2 band,
delayed-rectifier g_K around 0.012 S/cm^2, transient g_K,A around 0.036 S/cm^2, and
calcium-dependent g_K,Ca around 0.001 S/cm^2, calibrated across 7-37 degrees C.
[Schachter2010][schachter2010] and [PolegPolsky2016][polegpolsky2016] adopt
Fohlmeister-like kinetics for their DSGC compartmental models, and
[Vaney2012][vaney2012] reviews the broader RGC conductance literature without
identifying a factorial (g_Na, g_K) grid search specific to DSGCs.

**RQ2 (morphology sensitivity).** [Branco2010][branco2010] establishes cable-theory
sensitivity of spike output to input timing and location, giving the theoretical
scaffold. [Hoshi2011][hoshi2011] characterises ON DSGC morphology in mouse;
[Koren2017][koren2017] demonstrates cross-compartmental modelling under varied dendrite
shapes; [ElQuessny2021][elquessny2021] runs an explicit morphology-swap simulation
between symmetric and asymmetric DSGCs and concludes that global dendrite morphology
only minimally influences the synaptic distribution of excitation and inhibition, while
local dendritic electrotonic compartments still matter for computation.
[Briggman2011][briggman2011] and [Ding2016][ding2016] supply SBEM reconstructions that
make the morphology concrete.

**RQ3 (AMPA/GABA balance).** [PolegPolsky2016][polegpolsky2016] supplies the canonical
synaptic budget on a reconstructed mouse DSGC: 177 AMPA and 177 GABA synapses.
[Taylor2002][taylor2002] and [Park2014][park2014] report voltage-clamp E/I measurements
with null-direction inhibition three to five times larger than preferred inhibition.
[BarlowLevick1965][barlowlevick1965] provides the original rabbit DSGC DS measurements
that set the terminology. [Jain2020][jain2020] adds dendritic-Ca and E/I imaging;
[Hanson2019][hanson2019] shows circuit-level DS without pure SAC-asymmetry reliance;
[Sethuramanujam2016][sethuramanujam2016] adds the mixed ACh/GABA SAC co-transmission
constraint.

**RQ4 (active vs passive dendrites).** [Oesch2005][oesch2005] provides the patch-clamp
evidence for TTX-sensitive dendritic Na+ spikes in DSGC dendrites.
[Schachter2010][schachter2010] demonstrates in silico that active dendrites with
Fohlmeister-like densities roughly double the DSI compared to purely passive dendrites
(DSI around 0.3 passive to around 0.7 active). [Branco2010][branco2010] supports the
active-dendrite computation thesis at the cable-theory level. [Koren2017][koren2017]
shows cross-compartmental effects of active conductances; [Jain2020][jain2020] adds
calcium-imaging evidence that dendritic compartments fire local Ca events that are
direction-dependent.

**RQ5 (angle-to-AP-frequency tuning curves).** [Chen2009][chen2009] and
[Park2014][park2014] report adult mouse ON-OFF DSGC tuning-curve parameters: preferred
peak 40-80 Hz, null 3-10 Hz, DSI 0.6-0.9, half-width 60-90 degrees.
[BarlowLevick1965][barlowlevick1965] contributes rabbit baselines that anchor the
tuning-curve shape (cosine-like preferred response, sharp null).
[Taylor2002][taylor2002] and [Oesch2005][oesch2005] add E/I current traces that
constrain the drive-to-spike mapping. [Sivyer2010][sivyer2010] adds velocity-dependent
tuning-curve sharpening that is relevant to the angle-to-rate mapping.

**Methods and infrastructure papers.** [Hines1997][hines1997] provides the NEURON
simulator mathematical framework that underlies every compartmental DSGC model in the
corpus. [Vaney2012][vaney2012] is the cross-cutting review that motivates the five-RQ
decomposition in this project's scope.

## Evidence from Internet Sources

The internet-sources method was used only for bibliographic metadata retrieval (DOIs,
journal landing pages, PDF URLs, abstracts for paywalled items). All substantive claims
in this synthesis come from the 20 peer-reviewed paper assets. No quantitative number in
the Synthesis section was sourced only from an unreviewed web page. The internet search
is documented in `research/research_internet.md`.

## Evidence from Code or Experiments

The code-experiment method was not used for this task. This is a pure literature survey
task with `expected_assets` `paper: 20, answer: 1` and no compartmental model code or
simulation run. Any numeric target stated below comes from a reviewed paper, not from a
simulation executed inside this task.

## Synthesis

The 20-paper corpus converges on a concrete, quantitatively-specified target for every
one of the project's five research questions. The following subsections state each RQ's
answer together with the load-bearing numerical targets a downstream compartmental DSGC
model must match.

### RQ1 Na/K conductances

The Fohlmeister-Miller parameter set is the standard starting point for ganglion-cell
compartmental models and is adopted by the two published DSGC compartmental models in
this corpus. Specific numerical targets a new model should hit: peak somatic g_Na in the
0.04-0.10 S/cm^2 band, delayed-rectifier g_K around 0.012 S/cm^2, transient g_K,A around
0.036 S/cm^2, and calcium-dependent g_K,Ca around 0.001 S/cm^2, calibrated across 7-37
degrees C. No paper in the corpus reports a factorial (g_Na, g_K) grid search specific
to a DSGC — this is a genuine gap that downstream tasks t0006+ should fill. Supported by
[Fohlmeister2010][fohlmeister2010], [Schachter2010][schachter2010],
[PolegPolsky2016][polegpolsky2016], [Vaney2012][vaney2012].

### RQ2 morphology sensitivity

Global dendritic morphology has a smaller effect on DSGC computation than the prior
intuition suggested. The [ElQuessny2021][elquessny2021] morphology-swap simulation is
the most direct evidence: symmetric and asymmetric DSGCs produce similar synaptic
distributions when the underlying connectivity motif is held fixed. However, local
dendritic electrotonic compartments (typical lambda of 100-200 um in rabbit ON-OFF DSGCs
per [Oesch2005][oesch2005] and [Koren2017][koren2017]) still matter for the generation
of dendritic spikes and the isolation of dendritic subunits. A compartmental model
should therefore preserve realistic segment lengths and diameters while being relatively
insensitive to exact branching topology beyond the primary dendrite. SBEM
reconstructions in [Briggman2011][briggman2011] and [Ding2016][ding2016] supply the
canonical morphologies. Supported by [Branco2010][branco2010], [Hoshi2011][hoshi2011],
[Koren2017][koren2017], [ElQuessny2021][elquessny2021], [Briggman2011][briggman2011],
[Ding2016][ding2016].

### RQ3 AMPA/GABA balance

A reconstructed mouse ON-OFF DSGC carries 177 AMPA and 177 GABA synapses (1:1 nominal
ratio) per [PolegPolsky2016][polegpolsky2016]. Direction selectivity arises from spatial
and directional asymmetry of GABA drive, not from counts: null-direction IPSC amplitude
is three to five times the preferred-direction IPSC amplitude in voltage-clamp
recordings per [Park2014][park2014] and [Taylor2002][taylor2002]. Excitation is weakly
directionally tuned by comparison. SAC co-release of ACh and GABA per
[Sethuramanujam2016][sethuramanujam2016] adds a modulatory layer that a minimal
compartmental model can ignore at first pass. For a model to reproduce the full E/I
balance, it must implement the 177/177 count and the 3-5x null/preferred inhibitory
asymmetry simultaneously. Supported by [PolegPolsky2016][polegpolsky2016],
[Taylor2002][taylor2002], [Park2014][park2014], [Jain2020][jain2020],
[Hanson2019][hanson2019], [Sethuramanujam2016][sethuramanujam2016],
[BarlowLevick1965][barlowlevick1965].

### RQ4 active vs passive dendrites

Active dendrites roughly double the DSI relative to a purely passive tree, per
[Schachter2010][schachter2010] who reports DSI rising from ~0.3 (passive) to ~0.7
(active with Fohlmeister-like densities) under the same synaptic input.
[Oesch2005][oesch2005] provides the empirical basis via patch-clamp recordings of
TTX-sensitive dendritic Na+ spikes in rabbit ON-OFF DSGC dendrites. [Jain2020][jain2020]
supplies calcium-imaging evidence that individual dendritic compartments fire
direction-selective Ca events. The implication for a compartmental model is that
dendrites must carry at least Na, K, and K,A densities of the Fohlmeister-Miller family;
omitting active dendritic conductances produces a DSI ceiling near 0.3-0.4 that falls
below the project target. Supported by [Oesch2005][oesch2005],
[Schachter2010][schachter2010], [Branco2010][branco2010], [Koren2017][koren2017],
[Jain2020][jain2020].

### RQ5 angle-to-AP-frequency tuning curves

Adult mouse ON-OFF DSGC tuning curves hit the following quantitative targets.
Preferred-direction peak spike rate: 40-80 Hz. Null-direction residual spike rate: below
10 Hz (typically 3-10 Hz). Direction selectivity index (DSI): 0.7-0.85 typical, 0.6-0.9
across cells. Tuning-curve half-width at half-maximum (HWHM): 60-90 degrees. These
targets derive from whole-cell and extracellular recordings in [Chen2009][chen2009] and
[Park2014][park2014], with [BarlowLevick1965][barlowlevick1965] anchoring the classical
rabbit-DSGC preferred-null terminology and [Sivyer2010][sivyer2010] adding the
velocity-dependence component. A compartmental DSGC model should reproduce all four
numerical targets simultaneously on a moving bar stimulus. Supported by
[BarlowLevick1965][barlowlevick1965], [Chen2009][chen2009], [Park2014][park2014],
[Taylor2002][taylor2002], [Oesch2005][oesch2005], [Sivyer2010][sivyer2010].

## Limitations

Four limitations shape the confidence level of this synthesis at `medium`. First, the
corpus does not contain a factorial (g_Na, g_K) grid search for a DSGC — the
Fohlmeister-Miller parameter set is a single point in a high-dimensional space and
downstream tasks will have to vary channel densities experimentally. Second, the
morphology-sensitivity evidence rests mainly on one paper
([ElQuessny2021][elquessny2021]) that is relatively recent; independent replication with
other DSGC subtypes (e.g., ON DSGC, JAM-B DSGC) would strengthen the conclusion. Third,
the 177/177 AMPA/GABA count from [PolegPolsky2016][polegpolsky2016] is a single
reconstruction of a single mouse ON-OFF DSGC and has not been independently reproduced
at the level of explicit counted synapses. Fourth, the angle-to-AP tuning-curve targets
vary across mouse strains, ages, and recording conditions; the 40-80 Hz / DSI 0.7-0.85
targets should be interpreted as an operating range rather than a single ground-truth
value. A downstream task that simulates compartmental DSGC responses to drifting bars
and compares against [Chen2009][chen2009] and [Park2014][park2014] data directly would
improve the confidence to `high`.

## Sources

* Paper: `10.1113_jphysiol.1965.sp007638` — Barlow & Levick 1965, rabbit DSGC classical
  measurements
* Paper: `10.1162_neco.1997.9.6.1179` — Hines & Carnevale 1997, NEURON simulator
* Paper: `10.1038_nrn3165` — Vaney, Sivyer & Taylor 2012, DSGC review
* Paper: `10.1016_j.neuron.2016.02.013` — Poleg-Polsky & Diamond 2016, 177/177 synaptic
  budget
* Paper: `10.1016_j.neuron.2005.06.036` — Oesch, Euler & Taylor 2005, dendritic Na+
  spikes
* Paper: `10.1126_science.1189664` — Branco, Clark & Häusser 2010, cable-theory model
* Paper: `10.1371_journal.pcbi.1000899` — Schachter 2010, active-dendrite DSI gain
* Paper: `10.1152_jn.00123.2009` — Fohlmeister 2010, Na/K parameter set
* Paper: `10.1523_JNEUROSCI.22-17-07712.2002` — Taylor & Vaney 2002, E/I conductances
* Paper: `10.1113_jphysiol.2008.161240` — Chen & Chiao 2009, mouse DSGC tuning curves
* Paper: `10.1523_JNEUROSCI.5017-13.2014` — Park 2014, mouse ON-OFF DSGC tuning targets
* Paper: `10.1038_nature09818` — Briggman, Helmstaedter & Denk 2011, SBEM reconstruction
* Paper: `10.1038_nature18609` — Ding 2016, cross-species morphology + network model
* Paper: `10.1113_jphysiol.2010.192716` — Sivyer 2010, velocity-dependent tuning
* Paper: `10.1002_cne.22678` — Hoshi 2011, ON DSGC morphology
* Paper: `10.1016_j.neuron.2017.07.020` — Koren 2017, cross-compartmental DSGC model
* Paper: `10.1523_ENEURO.0261-21.2021` — El-Quessny & Feller 2021, morphology-swap
  simulation
* Paper: `10.7554_eLife.52949` — Jain 2020, dendritic Ca and E/I imaging
* Paper: `10.7554_eLife.42392` — Hanson 2019, circuit-level DS without SAC asymmetry
* Paper: `10.1016_j.neuron.2016.04.041` — Sethuramanujam 2016, mixed ACh/GABA SAC
  co-transmission
* Task: `t0002_literature_survey_dsgc_compartmental_models`

[barlowlevick1965]: ../../paper/10.1113_jphysiol.1965.sp007638/summary.md
[hines1997]: ../../paper/10.1162_neco.1997.9.6.1179/summary.md
[vaney2012]: ../../paper/10.1038_nrn3165/summary.md
[polegpolsky2016]: ../../paper/10.1016_j.neuron.2016.02.013/summary.md
[oesch2005]: ../../paper/10.1016_j.neuron.2005.06.036/summary.md
[branco2010]: ../../paper/10.1126_science.1189664/summary.md
[schachter2010]: ../../paper/10.1371_journal.pcbi.1000899/summary.md
[fohlmeister2010]: ../../paper/10.1152_jn.00123.2009/summary.md
[taylor2002]: ../../paper/10.1523_JNEUROSCI.22-17-07712.2002/summary.md
[chen2009]: ../../paper/10.1113_jphysiol.2008.161240/summary.md
[park2014]: ../../paper/10.1523_JNEUROSCI.5017-13.2014/summary.md
[briggman2011]: ../../paper/10.1038_nature09818/summary.md
[ding2016]: ../../paper/10.1038_nature18609/summary.md
[sivyer2010]: ../../paper/10.1113_jphysiol.2010.192716/summary.md
[hoshi2011]: ../../paper/10.1002_cne.22678/summary.md
[koren2017]: ../../paper/10.1016_j.neuron.2017.07.020/summary.md
[elquessny2021]: ../../paper/10.1523_ENEURO.0261-21.2021/summary.md
[jain2020]: ../../paper/10.7554_eLife.52949/summary.md
[hanson2019]: ../../paper/10.7554_eLife.42392/summary.md
[sethuramanujam2016]: ../../paper/10.1016_j.neuron.2016.04.041/summary.md
