---
spec_version: "3"
paper_id: "10.1016_j.neuron.2016.02.013"
citation_key: "PolegPolsky2016"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# NMDA Receptors Multiplicatively Scale Visual Signals and Enhance Directional

# Motion Discrimination in Retinal Ganglion Cells

## Metadata

* **File**: `files/poleg-polsky_2016_nmda-dsgc-multiplicative.xml`
* **Published**: 2016
* **Authors**: Alon Poleg-Polsky 🇺🇸, Jeffrey S. Diamond 🇺🇸
* **Venue**: Neuron, Vol. 89, Issue 6, pp. 1277-1290
* **DOI**: `10.1016/j.neuron.2016.02.013`

## Abstract

Postsynaptic responses in many CNS neurons are typically small and variable, often making it
difficult to distinguish physiologically relevant signals from background noise. To extract salient
information, neurons are thought to integrate multiple synaptic inputs and/or selectively amplify
specific synaptic activation patterns. Here, we present evidence for a third strategy: directionally
selective ganglion cells (DSGCs) in the mouse retina multiplicatively scale visual signals via a
mechanism that requires both nonlinear NMDA receptor (NMDAR) conductances in DSGC dendrites and
directionally tuned inhibition provided by the upstream retinal circuitry. Postsynaptic
multiplication enables DSGCs to discriminate visual motion more accurately in noisy visual
conditions without compromising directional tuning. These findings demonstrate a novel role for
NMDARs in synaptic processing and provide new insights into how synaptic and network features
interact to accomplish physiologically relevant neural computations.

## Overview

Poleg-Polsky and Diamond ask how directionally selective ganglion cells (DSGCs) in the mouse retina
maintain reliable direction-selective (DS) responses in the presence of visual noise. Their starting
observation is that NMDAR blockade with AP5 reduces postsynaptic potential (PSP) amplitudes in both
the preferred direction (PD) and null direction (ND) by the same fraction -- a multiplicative
operation -- rather than subtracting a fixed amount (additive scaling). This multiplicative property
preserves the PD:ND response ratio and therefore the direction-selectivity index (DSI) under
noiseless conditions, but its functional value only becomes apparent when visual signals are
contaminated with luminance noise.

The paper combines patch-clamp electrophysiology from mouse DRD4-GFP DSGCs (an ON-OFF DSGC subtype)
with multicompartmental NEURON simulations to dissect the cellular mechanism. Two key
pharmacological manipulations identify the requirements for multiplication: (1) reversing GABAergic
inhibition from inhibitory to excitatory by dialysing with high-chloride internal solution, and (2)
removing extracellular Mg2+ to eliminate voltage-dependent block of NMDAR channels. Both
manipulations convert NMDAR scaling from multiplicative to additive, confirming that tuned GABAergic
inhibition and voltage-dependent NMDAR conductance are jointly necessary.

The functional significance of multiplication is demonstrated with receiver-operating-characteristic
(ROC) analysis applied to PSP distributions during noisy visual stimulation. In normal Mg2+ with
intact NMDARs, DSGCs discriminate PD motion from background noise and from ND motion significantly
more accurately than in AP5 or Mg2+-free conditions, across noise levels up to approximately 50%
luminance variance. Suprathreshold AP responses show the same pattern: NMDAR blockade increases AP
failures during PD stimulation and reduces DS in noisy conditions. The computational model
reproduces all key experimental features without requiring dendritic spikes, indicating that passive
dendritic propagation combined with the NMDAR nonlinearity is sufficient.

## Architecture, Models and Methods

**Animal model**: eGFP-DRD4 / Chat-Cre / TdTomato triple-transgenic mice (postnatal days 14-70,
RRID:MMRRC_000231-UNC). Retinas were isolated and superfused with Ames medium or aCSF at
approximately 35 degrees C.

**Electrophysiology**: Somatic patch-clamp in cell-attached (suprathreshold AP recording) or
whole-cell configuration (subthreshold PSP and voltage-clamp). Na+ channels blocked with TTX or
intracellular QX-314 for subthreshold PSP experiments. Intracellular MK801 (iMK801, 2 mM)
selectively blocked NMDARs in the recorded cell. AP5 (50 uM) applied extracellularly. High-chloride
internal (65 mM Cl-) shifted E_Cl to -20 mV to convert GABAergic drive to excitatory. Extracellular
Mg2+ removed (0 mM) to make NMDAR conductance voltage-independent. Sample sizes: n = 19 cells
(subthreshold AP5), n = 15 cells (iMK801), n = 8 cells (0 Mg2+ subthreshold), n = 12 cells
(high-Cl-), n = 34 cells (0 Mg2+ suprathreshold), n = 25 cells (control suprathreshold), n = 21
cells (AP5 suprathreshold noisy).

**Visual stimulation**: Bright bars (405-nm LED, 1 mm/sec) in 8 directions. Noise stimuli varied
background and bar luminance independently every 50 ms at SD = 0%, 10%, 30%, or 50% of mean.

**Direction-selectivity index (DSI)**: DSI = (R_PD - R_ND) / (R_PD + R_ND), from AP counts or PSP
amplitudes.

**Multiplicativity test**: Slope angle theta of ND vs. PD PSP amplitude line before/after NMDAR
blockade. Additive: theta = 45 degrees; multiplicative: theta = arctan(PD_AP5 / ND_AP5). Mean
observed 62.5 +/- 14.2 degrees; expected multiplicative 59.4 +/- 10.7 degrees (p = 0.4).

**Compartmental NEURON model**: Morphologically realistic reconstruction of one DRD4 DSGC. **177
AMPAR + 177 NMDAR synapses** from bipolar cells and **177 GABA_A synapses** from starburst amacrine
cells, distributed homogeneously on ON dendrites only, plus nicotinic AChR inputs. Presynaptic
network of 282 cells with vesicle-release kinetics. DS tuning via stronger inhibitory conductance in
ND. NMDAR gated by Mg2+ block (Jahr-Stevens-type kinetics). Also tested with voltage-independent
Ohmic NMDAR substitutes and directionally tuned excitation.

**Signal discrimination**: ROC analysis on PSP and AP-count distributions; AUC and accuracy-curve
area computed across noise levels.

## Results

* NMDAR blockade (AP5) reduced PD PSPs by approximately **35%** and ND PSPs by approximately **34%**
  (n = 19), proportional multiplicative reduction; DSI unchanged (p > 0.5).
* PD NMDAR-mediated PSP component: **5.8 +/- 3.1 mV**; ND: **3.3 +/- 2.8 mV** (p = 0.001, paired
  t-test), confirming NMDAR contribution scales with the underlying synaptic drive.
* Mean slope of NMDAR scaling: **62.5 +/- 14.2 degrees**; expected multiplicative: **59.4 +/- 10.7
  degrees** (p = 0.4), confirming multiplication.
* iMK801 confirmed postsynaptic locus: subsequent bath AP5 reduced PD PSPs by only **16 +/- 17%**
  after iMK801 dialysis vs. full reduction with bath AP5 alone.
* 0 Mg2+ extracellular: slope **45.5 +/- 5.3 degrees** (additive, p < 0.001 vs. multiplicative); DSI
  significantly reduced.
* High-Cl- internal: slope **45.5 +/- 3.7 degrees** (additive, p = 0.01 vs. multiplicative); DSI
  reduced (p = 0.03).
* ROC AUC for PD vs. background, noise-free: **0.99** (control) vs. **0.83** in 0 Mg2+ (p = 0.008);
  **0.98** in AP5 -- difference vs. AP5 only visible under noise.
* Under noisy conditions: control ROC accuracy significantly exceeded AP5 and 0 Mg2+ at noise levels
  up to 50% luminance variance; accuracy-curve area significantly larger in control.
* Suprathreshold: DSI in 0 Mg2+ significantly reduced vs. control and AP5 (p < 0.001, ANOVA +
  Tukey); AP5 preserved DSI but increased PD AP failure rate.
* NEURON model replicated all results; predicted additive NMDAR scaling with tuned excitation or
  Ohmic (voltage-independent) NMDAR conductance.
* Multiplication robust across developmental ages (postnatal days 14-70) and contrast levels.

## Innovations

### NMDAR Multiplication as a Signal-Fidelity Mechanism

Prior work established NMDAR contributions to DS but not that their operation is multiplicative.
This paper is the first to show via slope-angle analysis that NMDAR scaling is proportional, and to
explain why: the voltage-dependent NMDAR conductance compensates for reduced driving force at
depolarised potentials, making total excitatory drive behave like an ideal current source enabling
shunting inhibition to act in a precisely divisive manner.

### Circuit-Dependent Multiplicativity

The same NMDAR mechanism produces multiplicative or additive scaling depending on whether DS is
implemented via tuned inhibition or tuned excitation. Reversing GABAergic sign converts
multiplication to addition, providing a framework for when NMDARs contribute to gain control vs.
additive amplification.

### Multicompartmental NEURON Model of a Mouse ON-OFF DSGC

The first detailed compartmental model of a mouse DRD4 DSGC with separate AMPAR, NMDAR, GABA_A, and
nAChR synaptic types (177 each for AMPA, NMDA, GABA) on a morphologically reconstructed dendritic
tree. Freely available on ModelDB (accession 189347). Reproduces experimental DS without dendritic
spikes.

### ROC-Based Quantification of DS Fidelity Under Noise

ROC analysis on membrane-potential and spike-count distributions during noisy stimulation provides a
threshold-independent metric for DS fidelity, revealing NMDAR multiplication benefits invisible
under noiseless mean-response comparisons.

## Datasets

No external datasets were used. All data are from the authors' own patch-clamp recordings in
isolated retinas of eGFP-DRD4 mice. The morphological reconstruction is embedded in the NEURON model
files on ModelDB (https://modeldb.science/189347). Supplementary Figures S1-S8 report additional
electrophysiology sub-experiments.

## Main Ideas

* The Poleg-Polsky & Diamond NEURON model (ModelDB 189347) is the most directly relevant starting
  point for this project: 177 AMPA + 177 GABA synapses on ON dendrites of a morphologically
  reconstructed mouse DRD4 DSGC, matching our planned synaptic architecture. Model is freely
  reusable.
* Tuned GABAergic inhibition is the circuit prerequisite for multiplicative NMDAR operation. Since
  this project implements tuned inhibition, NMDAR conductances added to the model will operate
  multiplicatively. Setting Mg2+ block to zero provides a built-in additive control.
* Passive dendritic propagation is sufficient for DS computation in DRD4 DSGCs (project RQ4
  baseline). Dendritic spikes were absent and are not required to match experimental DSI values.
* The Mg2+-block driving-force compensation mechanism constrains NMDAR conductance parameters:
  voltage-dependent conductance must increase across -70 to -20 mV to offset reduced reversal-
  potential driving force during PD depolarisation.
* ROC accuracy-curve area is the recommended metric for comparing DS fidelity across model variants
  under noisy input conditions, providing a threshold-independent discrimination score.

## Summary

Poleg-Polsky and Diamond investigate how direction-selective ganglion cells (DSGCs) in the mouse
retina amplify visual signals while preserving reliable directional tuning. The central question is
why NMDA receptors are present on DSGC dendrites when direction selectivity can be computed without
them. The answer proposed is that NMDARs provide multiplicative gain -- scaling responses in both
the preferred and null directions by the same factor -- which maintains the direction-selectivity
index, increases absolute signal amplitude, and improves resistance to visual noise.

The experiments combine whole-cell patch-clamp from GFP-labeled DRD4 mouse DSGCs with a
morphologically realistic multicompartmental NEURON model containing 177 AMPAR + 177 NMDAR + 177
GABA_A synapses on reconstructed ON dendrites. Slope-angle analysis distinguishes multiplicative
from additive NMDAR scaling. Two pharmacological manipulations convert multiplication to addition:
removing voltage-dependent Mg2+ block and reversing GABAergic inhibition to excitation with high-Cl-
internal solution. The NEURON model replicates all experimental PSP and AP responses and predicts
additive NMDAR scaling under both pharmacological conditions.

The key finding is that NMDAR multiplication requires the conjunction of voltage-dependent NMDAR
conductance and directionally tuned GABAergic inhibition. Under noiseless conditions, NMDAR blockade
preserves DSI but reduces AP firing amplitude. Under noisy conditions, ROC analysis demonstrates
significantly better signal discrimination with intact NMDARs than with AP5 or 0 Mg2+. Dendritic
spikes were absent in DRD4 DSGCs; passive propagation proved sufficient for DS computation.

For this project, the Poleg-Polsky & Diamond NEURON model is the essential template. Its geometry
(single reconstructed DRD4 DSGC), synaptic counts (177 AMPA + 177 GABA on ON dendrites), and circuit
architecture (tuned GABAergic inhibition as stronger ND conductance) directly match the planned
implementation. Available on ModelDB (accession 189347). The paper validates passive- dendrite
sufficiency for project RQ4, constrains NMDAR conductance Mg2+-block parameters, and establishes ROC
accuracy-curve area as the appropriate metric for comparing DS tuning fidelity across model
variants.
