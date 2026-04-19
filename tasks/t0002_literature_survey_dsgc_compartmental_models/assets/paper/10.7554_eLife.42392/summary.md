---
spec_version: "3"
paper_id: "10.7554_eLife.42392"
citation_key: "Hanson2019"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Retinal direction selectivity in the absence of asymmetric starburst amacrine cell responses

## Metadata

* **File**: `files/hanson_2019_circuit-ds.pdf`
* **Published**: 2019-02-04
* **Authors**: Laura Hanson (CA), Santhosh Sethuramanujam (CA), Geoff deRosenroll (CA), Varsha Jain
  (CA), Gautam B Awatramani (CA)
* **Venue**: eLife 2019;8:e42392
* **DOI**: `10.7554/eLife.42392`

## Abstract

In the mammalian retina, direction-selectivity is thought to originate in the dendrites of
GABAergic/cholinergic starburst amacrine cells, where it is first observed. However, here we
demonstrate that direction selectivity in downstream ganglion cells remains remarkably unaffected
when starburst dendrites are rendered non-directional, using a novel strategy combining a
conditional GABAA a2 receptor knockout mouse with optogenetics. We show that temporal asymmetries
between excitation/inhibition, arising from the differential connectivity patterns of starburst
cholinergic and GABAergic synapses to ganglion cells, form the basis for a parallel mechanism
generating direction selectivity. We further demonstrate that these distinct mechanisms work in a
coordinated way to refine direction selectivity as the stimulus crosses the ganglion cells receptive
field. Thus, precise spatiotemporal patterns of inhibition and excitation that determine directional
responses in ganglion cells are shaped by two core mechanisms, both arising from distinct
specializations of the starburst network.

## Overview

Hanson and colleagues challenge the prevailing view that direction selectivity (DS) in retinal
ganglion cells is inherited almost exclusively from the directionally tuned GABA release of
starburst amacrine cell (SAC) dendrites. By combining a conditional Gabra2 knockout (to abolish
SAC-SAC mutual inhibition) with channelrhodopsin-2 (ChR2) activation of SACs while pharmacologically
blocking photoreceptor and bipolar-cell drive, the authors create the first experimental condition
in which SAC output is rendered non-directional (IPSC direction-selectivity index DSI falls from
about 0.33 in wild type to **0.07** in the double manipulation). They then show that DSGCs in this
preparation nonetheless produce robustly direction-tuned spiking, revealing a second, parallel core
mechanism.

The parallel mechanism arises from temporal asymmetries between cholinergic excitation and GABAergic
inhibition, which originate in the differential wiring of SAC synapses to DSGCs: cholinergic inputs
come symmetrically from all surrounding starbursts, whereas GABAergic inputs come predominantly from
null-side starbursts. This spatial asymmetry imposes a velocity-dependent E/I onset-time offset of
up to 50 ms in the preferred direction, shrinking toward zero in the null direction, that
corresponds to a near-fixed **25-30 microm** spatial offset. A multicompartmental NEURON model of a
real DSGC reproduces the experimental spiking responses under both full wiring and non-directional
inhibition, and demonstrates that amplitude-based DS and temporal-offset DS drive distinct phases of
the response: offsets sharpen the early phase, amplitude asymmetry broadens but stabilises the peak
phase.

The paper combines optogenetics, pharmacology, mouse genetics, paired patch-clamp recordings, and
compartmental modelling. The model used is a modified version of the Poleg-Polsky and Diamond (2016)
NEURON DSGC reconstruction, whose public code repository
(`geoffder/Spatial-Offset-DSGC-NEURON-Model`) is one of the closest matches to this projects
modelling goals.

## Architecture, Models and Methods

**Experimental preparation.** Adult mice of either sex from Trhr-EGFP or ChAT-IRES-Cre x Ai32
(ChR2-expressing SACs) lines, optionally crossed with the Gabra2 conditional KO. Retina isolated,
perfused with warm Ringers solution (35-37 degC) containing 110 mM NaCl, 2.5 mM KCl, 1 mM CaCl2, 1.6
mM MgCl2, 10 mM dextrose, 22 mM NaHCO3, bubbled with 95% O2 / 5% CO2.

**Recordings.** Loose cell-attached spike recordings (5-10 MOhm electrodes filled with Ringers) and
whole-cell voltage-clamp (4-7 MOhm electrodes; internal: 112.5 mM CH3CsO3S, 7.75 mM CsCl, 1 mM
MgSO4, 10 mM EGTA, 10 mM HEPES, 5 mM QX-314, 100 microM spermine; pH 7.4; chloride reversal -56 mV).
MultiClamp 700B amplifier, 10 kHz digitisation. Stimuli: 200 microm spots moving in 8 directions at
1-1.6 mm/s (velocity also varied up to about 2.4 mm/s for tuning curves). Background about 10 R*/s;
ND filters raise stimulus intensity 10^5-fold to activate ChR2 in isolation.

**Pharmacology.** Bipolar/photoreceptor block: 50 microM DL-AP4, 10 microM UBP310, 20 microM CNQX.
Nicotinic block: 100 microM hexamethonium (HEX). GABA-A block: 5 microM SR-95531. NMDA block: D-AP5
(controls for voltage-clamp artefacts per Poleg-Polsky and Diamond, 2011).

**Compartmental model.** Modified Poleg-Polsky and Diamond (2016) NEURON model built on a
reconstructed DSGC morphology. Passive properties: Cm = **1 microF/cm^2**, Ra = **100 Ohm cm**, leak
reversal = **-60 mV**. Active conductances (stochastic Hodgkin-Huxley MOD files) at soma, primary,
and terminal dendrites: Na **150/150/30 mS/cm^2**, K rectifier **70/70/35 mS/cm^2**, delayed
rectifier **3/0.8/0.4 mS/cm^2**. Na and K were blocked for voltage-clamp simulations.

**Synaptic inputs.** AMPA, nicotinic-ACh, and GABA-A receptor synapses on terminal dendrites, with
kinetics fit to experimentally measured miniature events. A simulated bar moves over the arbor at
**1 mm/s** in 8 directions. Cholinergic release probability Pr = **0.5** (symmetric). GABA Pr scales
sigmoidally from **about 0.5 (null) to about 0.012 (preferred)**; spatial offset of inhibitory sites
ranges from **about 50 microm (null) to about 0 microm (preferred)**; cholinergic inputs are offset
**about 50 microm** from AMPA inputs (yielding a 50 ms temporal offset at 1 mm/s). Exact sigmoidal
fits are given in the Methods section. Offsets/velocities are used to convert spatial to temporal
offsets.

**Analysis.** DSI computed as the normalised vector sum of 8-direction spike counts. E/I temporal
offset = onset-latency difference of EPSC and IPSC, measured by extrapolating a straight-line fit to
the 20-80% rise of each synaptic current to the time axis. Early vs peak spike phases aligned to the
glutamatergic receptive-field edge (SR-95531 and HEX); early = about 50 ms before edge entry; peak =
about 50 ms around the peak firing rate. Statistics: Students t-test, significance p < 0.05; values
reported as mean +/- SEM.

## Results

* Wild-type DSGC IPSCs show a **DSI about 0.33 +/- 0.019** (n = 6) that drops only to **0.28 +/-
  0.022** (n = 6) in the Gabra2 KO alone (n.s.).
* Combined Gabra2 KO + ChR2 stimulation of SACs in the presence of bipolar blockade reduces
  starburst IPSC DSI to **0.07 +/- 0.02** (n = 7), the first reported non-directional starburst
  output condition.
* Despite non-directional SAC output, DSGC spiking remains robustly directional: preferred direction
  and DSI under ChR2 stimulation match those measured in the same cell under intact photoreceptor
  drive (n = 7), consistent across stimulus velocities of 1000-4000 microm/s.
* Under physiological (photoreceptor-driven) recording, E/I temporal offsets peak at **about 50-60
  ms** in the preferred direction and collapse to near zero in the null direction (n = 11); DSI of
  offsets is significantly higher than DSI of spiking (p < 0.001).
* Nicotinic-ACh block (100 microM HEX) delays EPSC onset uniformly by **26 +/- 2 ms** (n = 8) across
  all directions, abolishing E/I offsets in the preferred direction; corresponding spatial offset
  **about 25 microm** at 1 mm/s.
* Over a 500-2400 microm/s velocity range, temporal E/I offsets correspond to a relatively fixed
  **about 30 microm** spatial offset between excitatory and inhibitory receptive fields.
* A NEURON model driven only by direction-dependent E/I offsets (fixed E:I amplitude ratio 1:2)
  reproduces robust DS across velocity, failing only at the lowest velocity tested.
* Early (first 50 ms) DSGC spikes are sharply tuned (higher DSI) but noisier in preferred-direction
  estimate (SD **16 +/- 20 deg**); peak spikes are broader in DSI but more reliable in preferred
  direction (SD **8 +/- 20 deg**, n = 8).
* The two mechanisms are complementary: offset-only models reproduce the sharp early tuning;
  amplitude-only models reproduce the broader, stable peak tuning; both together reproduce the full
  temporal profile of directional spiking.

## Innovations

### First genetic/optogenetic abolition of starburst direction selectivity

By combining the Gabra2 conditional KO with ChR2 activation of SACs while blocking bipolar input,
the authors produce the first preparation in which starburst IPSC output to DSGCs is measurably
non-directional (DSI about 0.07). This creates a clean experimental substrate for isolating parallel
DS mechanisms that previous pharmacology could not reach.

### Identification of E/I temporal offset as an independent core DS mechanism

The paper converts a long-noted but dismissed phenomenon (E/I timing differences) into a
quantitatively measured, direction-tuned mechanism that is sufficient to generate DS spiking in the
total absence of amplitude asymmetry. E/I offsets are shown to be tuned more sharply for direction
than the spiking output itself.

### Cholinergic origin of the E/I offset

Hexamethonium delays preferred-direction EPSC onsets by a direction-independent **about 25 ms**,
proving that the offset is produced by a cholinergic lead over GABA. This reassigns ACh from a
modulatory role (as in classical rabbit-retina models) to a core contributor to DS in mouse retina.

### Phase-specific functional separation of the two DS mechanisms

Fine temporal analysis and a compartmental model demonstrate that offset-based DS dominates the
sharp early phase of the DSGC response, whereas amplitude-based DS dominates the broader, more
reliable peak phase. This two-mechanism, two-phase picture unifies previously conflicting
literature.

### Open-source multicompartmental DSGC model

The extended NEURON model used in Figures 6 and 7 is published at
`github.com/geoffder/Spatial-Offset-DSGC-NEURON-Model` and is one of the closest existing matches to
this projects target modelling substrate: reconstructed DSGC morphology, distributed AMPA/ACh/GABA
synapses with explicitly tunable spatial offsets and release probabilities, and somatic
Na/K/delayed-rectifier conductance combinations.

## Datasets

This is primarily an experimental neuroscience paper; the main datasets are laboratory recordings
and a compartmental model.

* **In vitro patch-clamp recordings**: loose cell-attached spike trains and whole-cell voltage-clamp
  EPSC/IPSC traces from mouse ON-OFF DSGCs. Sample sizes: n = 6 for wild type, Gabra2 KO, and ChR2
  alone; n = 7 for Gabra2 KO/ChR2 (Figure 2); n = 7 and n = 11 for optogenetic and physiological E/I
  offset analyses (Figure 4); n = 8 for HEX experiments (Figures 5, 7); n = 6 and n = 8 for velocity
  tuning (Figure 6). Raw source data are provided as Excel files in the eLife supplement (DOIs
  10.7554/eLife.42392.004, .006, .008, .009, .016, .018, .013).
* **Mouse lines**: Trhr-EGFP (RRID: MMRRC_030036-UCD), ChAT-IRES-Cre (RRID: MGI_5475195) x Ai32
  (RRID: MGI_5013789), Gabra2tm2.2Uru (RRID: MGI_5140553).
* **Compartmental model**: modified Poleg-Polsky and Diamond (2016) NEURON DSGC model, published at
  `https://github.com/geoffder/Spatial-Offset-DSGC-NEURON-Model` (check repository for license).

## Main Ideas

* Retinal DSGC spiking is produced by at least two parallel mechanisms: classical null-side
  amplitude-asymmetric GABA inhibition **and** a spatially-driven E/I temporal offset sourced from
  differential ACh-vs-GABA wiring of SACs. Any compartmental model aimed at reproducing DSGC tuning
  must support both mechanisms independently and in combination.
* Cholinergic excitation is *not* a non-directional modulator; in mouse retina it drives a
  direction-tuned 25-30 microm spatial offset between excitatory and inhibitory receptive fields,
  equivalent to about 25 ms of temporal lead. AMPA, ACh, and GABA must be modelled as three distinct
  synaptic populations with different spatial distributions and kinetics.
* The papers NEURON model (Poleg-Polsky and Diamond 2016 morphology, extended by deRosenroll) uses
  exactly the conductance combinations this project plans to explore: somatic Na = **150 mS/cm^2**,
  K rectifier = **70 mS/cm^2**, delayed rectifier = **3 mS/cm^2**, with reduced dendritic densities.
  These can serve as a baseline for the Na/K optimisation grid.
* Two response phases (early vs peak) show different direction tuning. A target
  angle-to-AP-frequency curve for this project should therefore ideally specify temporal structure
  (early versus sustained) rather than a single trial-averaged firing rate, otherwise amplitude and
  offset mechanisms cannot be distinguished.
* The mouse Ca/Na/K conductance recipe, passive properties (Cm = 1 microF/cm^2, Ra = 100 Ohm cm,
  leak reversal -60 mV), and release-probability tuning curves (sigmoidal Pr vs direction; fixed
  spatial offsets) are directly usable as initial parameter values and parameterisations for this
  projects simulation pipeline.

## Summary

Hanson et al. revisit one of the most entrenched assumptions in retinal neuroscience: that direction
selectivity in direction-selective retinal ganglion cells (DSGCs) is inherited from the
directionally tuned GABA release of starburst amacrine cells. They ask whether DSGCs can still
compute direction when starburst output itself is no longer directional, a question made answerable
for the first time by combining the Gabra2 conditional KO (which removes mutual SAC inhibition) with
optogenetic stimulation of SACs while bipolar-cell drive is pharmacologically silenced.

Methodologically, the study integrates four approaches: cell-specific genetics to control SAC
inhibition, ChR2 optogenetics to control excitation of SACs in isolation, whole-cell and loose
cell-attached patch-clamp recordings to read out EPSCs, IPSCs, and spiking in the same DSGCs, and a
multicompartmental NEURON model (built on the Poleg-Polsky and Diamond 2016 DSGC morphology) to test
the computational sufficiency of the proposed mechanisms. Pharmacology (hexamethonium, SR-95531,
DL-AP4, UBP310, CNQX, D-AP5) isolates cholinergic, GABAergic, and glutamatergic components.
Modelling synapses and somatic Na/K/delayed-rectifier conductances are set to densities matched to
prior literature, and release probabilities are parameterised sigmoidally with direction.

The central findings are that (i) starburst IPSC direction selectivity can be essentially abolished
(DSI about 0.07) while DSGC spiking remains robustly directional; (ii) the residual DS is explained
by a directionally tuned excitation-inhibition temporal offset of up to 50 ms in the preferred
direction, which corresponds to a relatively fixed 25-30 microm spatial offset across velocities;
(iii) this offset is cholinergic in origin, since hexamethonium delays preferred-direction EPSCs by
about 25 ms and collapses the offset; and (iv) the two DS mechanisms (amplitude and timing) dominate
different phases of the response: offsets sharpen the early phase, amplitude differences broaden and
stabilise the peak phase. The NEURON model reproduces all of these features under both full and
reduced wiring.

For this project, Hanson et al. 2019 is directly relevant on three fronts. First, it constrains the
target tuning curve: a single trial-averaged angle-to-AP-frequency curve is unlikely to capture the
dual-mechanism structure, so the target should ideally include early-versus-peak temporal structure.
Second, it provides a specific, reconstructed, publicly available NEURON model
(`geoffder/Spatial-Offset-DSGC-NEURON-Model`) with the exact conductance recipe, passive properties,
and distributed AMPA/ACh/GABA synapses needed as a baseline for the morphology/conductance/input
parametric variation planned here. Third, it establishes that any realistic DSGC model in this
project must treat excitation as two distinct populations (bipolar AMPA and starburst ACh) with
different spatial offsets, because their differential timing is itself a DS mechanism that must be
represented if the optimiser is to fit mouse DSGC behaviour rather than a generic ON-OFF ganglion
cell.
