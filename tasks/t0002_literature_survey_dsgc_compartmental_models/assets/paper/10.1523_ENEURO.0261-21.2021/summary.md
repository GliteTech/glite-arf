---
spec_version: "3"
paper_id: "10.1523_ENEURO.0261-21.2021"
citation_key: "ElQuessny2021"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Dendrite Morphology Minimally Influences the Synaptic Distribution of Excitation and Inhibition in Retinal Direction-Selective Ganglion Cells

## Metadata

* **File**: `files/el-quessny_2021_dsgc-morph.pdf`
* **Published**: 2021
* **Authors**: Malak El-Quessny 🇺🇸, Marla B. Feller 🇺🇸
* **Venue**: eNeuro (Society for Neuroscience), 8(5)
* **DOI**: `10.1523/ENEURO.0261-21.2021`

## Abstract

Throughout the nervous system, the organization of excitatory and inhibitory synaptic inputs within
a neuron’s receptive field shapes its output computation. In some cases, multiple motifs of
synaptic organization can contribute to a single computation. Here, we compare two of these
mechanisms performed by two morphologically distinct retinal direction-selective ganglion cells
(DSGCs): directionally tuned inhibition and spatially offset inhibition. Using drifting stimuli, we
found that DSGCs that have asymmetric dendrites exhibited stronger directionally tuned inhibition
than symmetric DSGCs. Using stationary stimuli to map receptive fields, we found that DSGCs with
both symmetric and asymmetric dendrites exhibited similar spatially offset inhibition.
Interestingly, we observed that excitatory and inhibitory synapses for both cell types were locally
correlated in strength. This result indicates that in the mouse retina, dendritic morphology
influences the amount of tuned inhibition attained through asymmetric wiring but does not dictate
the synaptic organization of excitation relative to inhibition.

## Overview

The paper asks whether dendrite morphology (global geometry of the dendritic arbor) instructs the
spatial and directional organization of excitatory and inhibitory synaptic inputs onto mouse
direction-selective retinal ganglion cells (DSGCs). The authors compare two genetically labeled DSGC
subtypes that have markedly different dendritic shapes but similar direction-selective spike output:
Hb9::GFP-labeled ventral-preferring DSGCs (vDSGCs), which have asymmetric dendrites biased toward
the preferred direction, and Trhr::GFP-labeled nasal-preferring DSGCs (nDSGCs), whose dendrites are
symmetric with no consistent bias toward the preferred direction.

Using two-photon targeted whole-cell voltage clamp in wholemount mouse retina, they record
excitatory (EPSC) and inhibitory (IPSC) currents evoked by both drifting bars (eight directions) and
a 10 x 10 grid of small stationary flashes over a 500 x 500 um soma-centered field. For every
recorded cell they also obtain a two-photon morphological reconstruction, allowing per-cell
comparison of dendritic geometry to synaptic receptive fields. They then quantify (i) dendritic
asymmetry (soma-to-COM vector of skeletonized dendrites), (ii) the direction selectivity index (DSI)
of IPSCs, (iii) the magnitude and angle of spatial offset between excitatory and inhibitory
receptive-field centers of mass, (iv) pixel-by-pixel correlation between E and I amplitudes, and (v)
dendritic vs synaptic field size.

The headline result is a dissociation: dendritic morphology determines how strongly inhibition is
directionally tuned (asymmetric vDSGCs have significantly higher IPSC DSI than symmetric nDSGCs),
but it does not determine the spatial offset between excitatory and inhibitory receptive fields.
Both cell types show small (<50 um) E-to-I offsets aligned with the preferred direction, a strong
per-pixel local correlation between E and I amplitudes, and E and I receptive fields that are
roughly 1.6-3.3x larger than the dendritic field. Pharmacological block of nAChRs (100 uM
hexamethonium) shrinks the excitatory receptive field back toward the dendritic field, attributing
the excess area to cholinergic input from starburst amacrine cells (SACs).

## Architecture, Models and Methods

The study uses female and male C57BL/6 mice of age p30-p60. vDSGCs are targeted via Hb9::GFP mice
(Arber et al., 1999) and nDSGCs via Trhr::GFP mice (Rivlin-Etzion et al., 2011). Isolated whole
retinas are dissected in oxygenated (95% O2 / 5% CO2) Ames’ medium, cut into dorsal and ventral
halves, and mounted photoreceptor-side down over a 1-2 mm^2 hole in nitrocellulose filter paper.
Recordings are done at 32-34 C on a custom two-photon microscope (Fluoview 300) tuned to 920 nm for
GFP/cell identification and 800 nm for Alexa Fluor 594 morphology imaging.

Whole-cell voltage-clamp electrodes (4-5 MOhm) are filled with a cesium-based internal containing
110 mM CsMeSO4, 2.8 mM NaCl, 20 mM HEPES, 4 mM EGTA, 5 mM TEA-Cl, 4 mM Mg-ATP, 0.3 mM Na3GTP, 10 mM
Na2-phosphocreatine, and 5 mM QX-Cl (pH 7.2, osmolarity 290, E_Cl = -60 mV). After a 10 mV liquid
junction correction, EPSCs are isolated at -70 mV and IPSCs at 0 mV. Signals are acquired with a
Multiclamp 700A, sampled at 10 kHz and low-pass filtered at 6 kHz via Clampex 10.4.

Visual stimuli are generated in MATLAB / Psychophysics Toolbox and projected through a DLI Cel5500
DMD with a 420-520 nm LED source, focused on the photoreceptor layer. Drifting bars: 250 um/s, 600
um long x 350 um wide, 96% Michelson contrast, eight block-shuffled directions, three repeats, 6 s
presentation + 3 s ISI, illumination radius 1.4 mm to limit wide-field amacrine engagement.
Stationary receptive-field mapping: a 10 x 10 grid of 30 x 30 um squares over a 500 x 500 um field,
100 block-shuffled positions, three repeats, 0.5 s flash + 1.2 s ISI, 96% Michelson, 3.1 x 10^5
R*/s/rod. Cholinergic block uses 100 uM hexamethonium perfused 5-10 min at 1 ml/min.

Dendrites are imaged at 480 x 480 um x 1 um z-steps, oversampled 15x per stack, then segmented into
ON (IPL depth 10-30 um) and OFF (35-55 um) strata in FIJI and skeletonized with Simple Neurite
Tracer. Quantification includes: center-of-mass (COM) vectors from soma to skeleton, EPSC/IPSC peak
amplitudes per pixel, dendritic 10 x 10 bin maps matched to the stimulus grid, DSI = (ND - PD) / (ND
\+ PD), vector-sum tuning (Mazurek et al., 2014), and receptive-field area thresholded at 50 pA.
Statistics use one-way ANOVA with Dunn-Sidak post hoc, Wilcoxon rank-sum, paired t-tests, and
Pearson correlations (p < 0.05 significant). Sample sizes per experiment range from n = 5 to n = 23
cells with at least two mice per condition.

## Results

* ON dendrite asymmetry: vDSGCs **66.67 +/- 25.50 um** (n = 23) vs nDSGCs **43.08 +/- 20.51 um** (n
  = 17); OFF: **65.83 +/- 25.40 um** vs **39.98 +/- 17.32 um** (one-way ANOVA p = **4e-4**, post hoc
  **p < 0.01**).
* IPSC direction selectivity index is **significantly higher in asymmetric vDSGCs** (ON DSI **0.48
  +/- 0.19**, OFF **0.56 +/- 0.11**) than symmetric nDSGCs (ON **0.34 +/- 0.14**, OFF **0.31 +/-
  0.17**; Wilcoxon rank-sum **p < 0.01** ON, **p < 0.001** OFF).
* Preferred-direction IPSC amplitude is **lower in vDSGCs** (ON **290.7 +/- 136.8 pA**, OFF **173.6
  +/- 88.6 pA**) than nDSGCs (ON **325.8 +/- 102.0 pA**, OFF **213.0 +/- 63.2 pA**), so the tuning
  difference is driven mainly by reduced preferred-side inhibition in vDSGCs.
* Receptive-field E-to-I spatial offset magnitude is **small and similar across morphologies**:
  vDSGCs ON **20.80 +/- 15.54 um**, OFF **19.83 +/- 14.49 um**; nDSGCs ON **38.14 +/- 23.39 um**,
  OFF **33.72 +/- 27.01 um** (Wilcoxon rank-sum ON p < 0.05, OFF n.s.). Both are below the 50-um
  mapping resolution and both cluster around the preferred direction.
* EPSC vs IPSC receptive-field angle is **strongly correlated** per cell: vDSGCs Pearson R =
  **0.83** (ON, p = 2.7e-5) and **0.92** (OFF, p = 1.6e-9); nDSGCs **0.67** (ON, p = 5.0e-3) and
  **0.67** (OFF, p = 6.3e-3).
* Local per-pixel E vs I amplitude correlation is strong, with excitation explaining on average
  **65%** of inhibition variance in vDSGCs and **51%** in nDSGCs.
* Receptive fields are **much larger than dendritic fields**: EPSC/dendrite area ratio **1.9-2.87**,
  IPSC/dendrite area ratio **1.64-3.31** across subtypes and layers (one-sided t-test vs ratio 1,
  all **p < 0.001**).
* Under 100 uM hexamethonium, glutamatergic EPSC receptive field shrinks to **~1.6-1.98x** dendritic
  area (vs ~1.9-2.87x for mixed EPSC), and its orientation flips in nDSGCs: the glutamatergic EPSC
  angle points toward the **null direction** (mean 200.5 deg ON, 220.9 deg OFF) whereas in vDSGCs it
  remains **preferred (ventrally) oriented** (266.9 deg ON, 272.9 deg OFF).
* Temporal E-I peak-time differences during preferred-direction motion predict larger spatial
  offsets (ON **36-64 um**, OFF **74-110 um**) than the stationary-stimulus maps actually measure
  (one-sided t-test measured vs predicted **p < 0.001**), implying stationary and moving stimuli
  recruit partly different lateral inhibitory circuits.

## Innovations

### Morphology-Matched Two-Subtype Comparison in the Same Retina

First study to record E and I receptive fields and reconstruct dendritic morphology from the same
mouse DSGC population using two genetically defined subtypes (Hb9::GFP vDSGCs and Trhr::GFP nDSGCs)
that share direction-selective output but differ maximally in dendritic asymmetry. This turns
morphology into a natural experimental variable rather than requiring morphological manipulation.

### High-Resolution 2D Mapping of E and I Receptive Fields

Uses 30 x 30 um stationary flashes on a 10 x 10 grid spanning 500 x 500 um to separately map EPSC
and IPSC receptive fields of every recorded cell and to compute per-pixel E-vs-I correlations. This
goes beyond one-dimensional drifting-bar measurements and reveals the dissociation between
directional tuning of inhibition (morphology-dependent) and E/I spatial organization
(morphology-independent).

### Dissociation of Dendrite-Dependent and Dendrite-Independent DS Mechanisms

Demonstrates that the two canonical DS mechanisms (directionally tuned inhibition vs. spatially
offset inhibition) have different dependence on dendritic morphology. This reframes DSGC function as
two parallel mechanisms that can be tuned semi-independently and establishes that symmetric DSGCs
lean more on spatially offset inhibition to reach similar spike tuning.

### Cholinergic vs Glutamatergic Receptive-Field Dissection

By combining receptive-field mapping with 100 uM hexamethonium block, the paper attributes the
excess of synaptic-field area over dendritic-field area to cholinergic input from SACs and reveals
that glutamatergic receptive fields in nDSGCs are skewed toward the null direction, while vDSGC
glutamatergic fields remain preferred-side biased.

## Datasets

No external datasets. The data are primary electrophysiology and morphology recordings:

* Whole-cell voltage-clamp recordings of EPSCs and IPSCs from Hb9::GFP vDSGCs and Trhr::GFP nDSGCs
  (n per experiment ranges 5-23 cells, at least two animals per condition, both sexes, age p30-p60).
* Two-photon morphological reconstructions of the same cells (Alexa Fluor 594 fills, segmented ON
  and OFF dendrites).
* Stimulus protocols and scoring are implemented in MATLAB / Psychophysics Toolbox; FIJI + Simple
  Neurite Tracer for skeletonization. No public dataset URL is provided in the paper.

## Main Ideas

* For this project, "morphology" must be treated as a two-level factor: it materially controls the
  directional tuning of inhibition (asymmetric DSGCs get stronger tuned inhibition, primarily by
  losing preferred-side IPSC amplitude), but it does not control the spatial E-I offset or the local
  E/I amplitude correlation.
* Any compartmental model of a mouse DSGC must place synapses over a region roughly **1.6-3.3x the
  dendritic field area** (driven by off-dendrite cholinergic input from SACs); restricting synapses
  to the dendritic footprint will underestimate the excitatory and inhibitory drive.
* Excitation and inhibition are **locally correlated in strength per pixel** (R^2 ~ 0.51-0.65), so a
  plausible modeling assumption is that AMPA and GABA input density are co-varied (e.g., share a
  spatial profile) rather than assigned independently.
* E and I centers of mass are offset by **<50 um along the preferred direction** in both cell types,
  and drifting-bar temporal offsets (~100-300 ms) predict a larger effective spatial offset than
  stationary maps reveal; both should be reproducible from a single compartmental model if it
  includes stimulus-dependent lateral-inhibition engagement.
* Cholinergic nAChR input is the component that makes EPSC receptive fields exceed the dendritic
  footprint; a glutamate-only model will reproduce dendrite-matched EPSC area (ratio ~1.6-2.0)
  whereas a mixed ACh+glutamate model reproduces the measured ~1.9-2.9 ratio.
* Symmetric nDSGCs reach similar spike tuning to asymmetric vDSGCs despite weaker IPSC DSI, because
  once inhibition exceeds a shunting threshold the spike tuning saturates (Koch et al., 1983; Taylor
  et al., 2000). This constrains how strongly a model needs to tune inhibition to reproduce
  experimental AP direction curves.

## Summary

El-Quessny and Feller test whether the global shape of a DSGC’s dendritic arbor determines how its
excitatory and inhibitory synaptic inputs are spatially organized. They exploit a natural biological
contrast: Hb9::GFP vDSGCs have strongly asymmetric dendrites oriented toward the preferred
direction, while Trhr::GFP nDSGCs have symmetric dendrites but similar direction-selective spike
output. The motivation is to dissociate two classical mechanisms of retinal direction selectivity,
tuned inhibition and spatially offset inhibition, and to ask which of them tracks dendritic
morphology.

Methodologically, the authors combine two-photon targeted whole-cell voltage clamp of EPSCs (V_hold
= -70 mV) and IPSCs (V_hold = 0 mV) with per-cell morphological reconstruction in flat-mount mouse
retina. Cells are probed with both drifting bars (eight directions, 250 um/s) and a 10 x 10
stationary flash grid over a 500 x 500 um soma-centered field (30 x 30 um squares), which allows
independent measurement of directional tuning and 2D receptive-field geometry. Additional
experiments block nAChRs with 100 uM hexamethonium to separate cholinergic from glutamatergic
excitation, and a set of vector-based COM analyses quantifies dendritic asymmetry, E-to-I spatial
offset, per-pixel E vs I correlation, and the ratio of synaptic-field to dendritic-field area.

The headline findings are a clean dissociation. Asymmetric vDSGCs show significantly sharper
directional tuning of inhibition than symmetric nDSGCs (IPSC DSI **0.48** vs **0.34** ON; **0.56**
vs **0.31** OFF), driven by weaker preferred-side inhibition. However, E-to-I spatial offsets are
small (**<50 um**) and comparable between subtypes, E and I amplitudes are locally correlated (R^2 ~
0.51-0.65 per pixel), and both receptive fields exceed the dendritic field by a factor of
**~1.6-3.3** because of cholinergic (SAC) input. Pharmacological block of nAChRs shrinks the
excitatory receptive field toward the dendritic field and reveals that nDSGC glutamatergic fields
point toward the null direction, whereas vDSGC glutamatergic fields remain biased toward the
preferred direction.

For this project, which aims to match single-DSGC angle-to-AP-frequency curves in a compartmental
model, the paper is foundational. It tells us (i) dendritic asymmetry matters for tuned inhibition
but not for spatial E/I organization, so a compartmental model that ignores global morphology can
still reproduce E/I spatial structure if it gets SAC-mediated wiring right; (ii) synapse
distributions should cover **1.6-3.3x** the dendritic footprint with a co-varying local E/I
amplitude ratio; (iii) the E-to-I spatial offset along the preferred axis is **<50 um** and
inhibition is locally correlated with excitation in strength; and (iv) reproducing the gap between
stationary-map and drifting-bar offsets requires stimulus-dependent recruitment of lateral
inhibition. These quantitative constraints directly feed into the AMPA/GABA placement, synaptic
density maps, and stimulus protocols used to tune the project’s DSGC compartmental model.
