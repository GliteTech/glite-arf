---
spec_version: "3"
paper_id: "10.1523_JNEUROSCI.5017-13.2014"
citation_key: "Park2014"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Excitatory Synaptic Inputs to Mouse On-Off Direction-Selective Retinal Ganglion Cells Lack Direction Tuning

## Metadata

* **File**: `files/park_2014_dsgc-ei.pdf`
* **Published**: 2014
* **Authors**: Silvia J.H. Park 🇺🇸, In-Jung Kim 🇺🇸, Loren L. Looger 🇺🇸, Jonathan
  B. Demb 🇺🇸, Bart G. Borghuis 🇺🇸
* **Venue**: The Journal of Neuroscience, Vol. 34(11), pp. 3976-3981
* **DOI**: `10.1523/JNEUROSCI.5017-13.2014`

## Abstract

Direction selectivity represents a fundamental visual computation. In mammalian retina, On-Off
direction-selective ganglion cells (DSGCs) respond strongly to motion in a preferred direction and
weakly to motion in the opposite, null direction. Electrical recordings suggested three
direction-selective (DS) synaptic mechanisms: DS GABA release during null-direction motion from
starburst amacrine cells (SACs) and DS acetylcholine and glutamate release during preferred
direction motion from SACs and bipolar cells. However, evidence for DS acetylcholine and glutamate
release has been inconsistent and at least one bipolar cell type that contacts another DSGC
(On-type) lacks DS release. Here, whole-cell recordings in mouse retina showed that cholinergic
input to On-Off DSGCs lacked DS, whereas the remaining (glutamatergic) input showed apparent DS.
Fluorescence measurements with the glutamate biosensor intensity-based glutamate-sensing fluorescent
reporter (iGluSnFR) conditionally expressed in On-Off DSGCs showed that glutamate release in both
On- and Off-layer dendrites lacked DS, whereas simultaneously recorded excitatory currents showed
apparent DS. With GABA-A receptors blocked, both iGluSnFR signals and excitatory currents lacked DS.
Our measurements rule out DS release from bipolar cells onto On-Off DSGCs and support a theoretical
model suggesting that apparent DS excitation in voltage-clamp recordings results from inadequate
voltage control of DSGC dendrites during null-direction inhibition. SAC GABA release is the apparent
sole source of DS input onto On-Off DSGCs.

## Overview

This brief communication resolves a longstanding controversy about the synaptic origins of direction
selectivity in mouse On-Off DSGCs. The classical account proposed three DS synaptic sources:
null-direction GABA from starburst amacrine cells (SACs), and separately, preferred- direction
acetylcholine and glutamate from SACs and bipolar cells. Park et al. (2014) directly test whether
acetylcholine and glutamate release onto On-Off DSGC dendrites are actually directionally tuned,
combining whole-cell patch-clamp in voltage-clamp mode with simultaneous two-photon fluorescence
imaging using the genetically encoded glutamate sensor iGluSnFR.

The key methodological advance is conditional expression of iGluSnFR on the DSGC dendrites via the
CART-Cre transgenic mouse line. This optical sensor reports glutamate release locally at the
dendritic membrane, independent of voltage-clamp artefacts that distort current measurements. When
cholinergic transmission was blocked with hexamethonium (100 uM), apparent DS of the excitatory
current persisted, suggesting the remaining glutamatergic input was DS. But iGluSnFR signals on the
same dendrites showed no directional bias simultaneously.

The resolution came from a third manipulation: blocking GABA-A receptors with gabazine (50 uM).
After removing null-direction inhibition, both excitatory conductance and iGluSnFR signals lost
directional selectivity. This confirms that the apparent tuning of the excitatory conductance was an
artefact of imperfect space clamp: strong inhibition during the null direction drives dendritic
membrane away from the command potential, producing an artifactual difference in the measured
excitatory current. The sole genuinely tuned synaptic input is SAC GABA release in the null
direction.

These findings constrain models of On-Off DSGC circuitry. The excitatory drive (glutamate and
acetylcholine) is omnidirectional, and full DS of the cell emerges from asymmetric null-direction
inhibition combined with intrinsic cellular mechanisms such as active dendritic conductances and
dendritic morphology.

## Architecture, Models and Methods

**Preparation.** Retinas were acutely isolated from adult C57/B6 mice (2-6 months, either sex) and
perfused at 6 ml/min with oxygenated (95% O2-5% CO2) Ames medium at 32-34 degrees C. All recording
was in vitro on a custom-built two-photon fluorescence microscope (ScanImage software).

**Cell identification.** On-Off DSGCs were targeted by soma size (approx. 15 um diameter) in
wild-type retinas, or by GFP expression in TRHR-GFP transgenic animals. Identity confirmed by
light-response tuning and dendritic morphology.

**Whole-cell recordings.** Pipettes (6-10 MOhm) contained Cs-methanesulfonate internal solution (120
mM CsMs, 5 mM TEA-Cl, 10 mM HEPES, 10 mM BAPTA, 3 mM NaCl, 2 mM QX-314-Cl, 4 mM ATP-Mg, 0.4 mM
GTP-Na2, 10 mM phosphocreatine-Tris2, pH 7.3, 280 mOsm) plus red fluorophores (Alexa Fluor 594
biocytin or Alexa Fluor 568, 10 uM). Excitatory and inhibitory currents were recorded at holding
potentials near E_Cl (-67 mV) and E_cation (-10 mV), corrected for the liquid junction potential (9
mV). Series resistance (20-40 MOhm) compensated at 50-60%. Conductances obtained by dividing current
by the 70 mV driving force.

**Stimulus.** Drifting grating (1 Hz temporal frequency; 0.85 or 1 mm period; 100% contrast; 31 or
36 deg/s) windowed in an aperture (0.43-0.55 mm), presented through the microscope condenser at
0.5-1.0 x 10^4 R* per cone per second. DS tuning assessed across eight directions of motion.

**iGluSnFR imaging.** AAV2/1.syn.FLEX.iGluSnFR (Cre-dependent, 0.8-2.0 x 10^13 IU/ml) was injected
intravitreally (approx. 1 ul) into CART-Cre mice; retinas harvested 14-28 days later. Sparse
conditional expression allowed ROIs on the recorded DSGC dendrites (3-20 um length) to be drawn
without contamination from nearby processes. Fluorescence responses quantified as peak-to- peak
amplitude of the F1:4 Fourier harmonic fit.

**Pharmacology.** Nicotinic block: hexamethonium 100 uM. GABA-A block: SR95531 (gabazine) 50 uM.

**Statistics.** One-tailed Student's t tests for tuning in preferred direction (excitation,
glutamate) or null direction (inhibition). For imaging data, n = number of cells, not ROIs. DS index
= (ResponsePref - ResponseNull) / (ResponsePref + ResponseNull).

**Sample sizes.** Hexamethonium pharmacology: n = 16 cells. Simultaneous iGluSnFR and voltage-
clamp: 25 ROIs across n = 14 cells. iGluSnFR + hexamethonium + gabazine series: 7-9 ROIs across n =
4 cells. TRHR-GFP and wild-type DS index reference: n = 38 cells.

## Results

* **DS index** of On-Off DSGCs in CART-Cre mice: **0.65 +/- 0.05** (n = 14); similar to TRHR-GFP and
  wild-type cells (**0.73 +/- 0.03**, n = 38).
* **Null-direction inhibitory conductance** (preferred minus null): **-2.43 +/- 0.31 nS** (t = 7.97,
  p < 0.00001), confirming robust direction-tuned inhibition.
* **Apparent preferred-direction excitatory conductance** (P - N): **+0.31 +/- 0.05 nS** (t = 6.33,
  p < 0.000001) under control conditions.
* **Hexamethonium (100 uM)** did not significantly alter excitatory P - N (control: +0.31 +/- 0.05
  nS vs. hexamethonium: **+0.26 +/- 0.04 nS**; t = 1.32, p = 0.103), ruling out DS cholinergic input
  to On-Off DSGCs.
* **iGluSnFR signal tuning** (On + Off dendrites, simultaneous with voltage-clamp): P - N = **+0.073
  +/- 0.04** (t = 1.76, p = 0.95); not significantly tuned, while simultaneously recorded excitatory
  conductance was tuned (**+0.35 +/- 0.07 nS**, t = 4.87, p = 0.00015).
* **With gabazine (50 uM)**: excitatory conductance P - N = **+0.0065 +/- 0.039 nS** (p = 0.56);
  iGluSnFR P - N = **-0.07 +/- 0.05** (p = 0.86); both untuned after GABA-A block.
* **iGluSnFR under hexamethonium alone** remained untuned (P - N = **+0.11 +/- 0.14**, p = 0.76),
  even as excitatory conductance showed apparent DS (**+0.42 +/- 0.064 nS**, p = 0.004).
* **Inhibition exceeds excitation by approximately 8-fold** (2.43 nS vs. 0.31 nS P - N),
  establishing the relative E/I scale that a compartmental model of these cells must reproduce.

## Innovations

### Optical Dissection of Presynaptic Release Directionality

Conditional expression of iGluSnFR on DSGC dendrites via CART-Cre mice provided the first direct
optical measurement of glutamate release directionality at On-Off DSGC synapses, recorded
simultaneously with voltage-clamp conductances in the same cell. This dual readout proved the DS of
the electrical excitatory signal was a voltage-clamp artefact, not tuned presynaptic release.

### Experimental Confirmation of the Space-Clamp Artefact in DSGCs

The theoretical prediction of Poleg-Polsky and Diamond (2011) that imperfect voltage control of DSGC
dendrites during strong null-direction inhibition creates artifactual DS of the excitatory
conductance is confirmed experimentally for the first time. Gabazine abolished apparent excitatory
DS in both the electrical and optical readouts simultaneously, providing the definitive test.

### Minimal Sufficient Circuit Model

The study reduces the DS circuit to a single tuned input: null-direction GABA from SACs. Excitatory
drive (glutamate and acetylcholine) is omnidirectional. This minimal model, combined with the known
selective SAC-to-DSGC wiring, is sufficient to account for On-Off DSGC direction selectivity in
mouse retina without invoking DS excitatory release.

## Datasets

No publicly archived numerical datasets were deposited. The study used:

* C57/B6 wild-type mice (2-6 months, either sex), in vitro acute retinal preparations
* TRHR-GFP transgenic mice (Rivlin-Etzion et al., 2011) for GFP-labelled On-Off DSGCs
* CART-Cre transgenic mice (Kay et al., 2011, Jackson Laboratory) for conditional iGluSnFR
  expression in On-Off DSGCs and a subset of other retinal cell types

The iGluSnFR AAV construct was provided by Loren Looger's lab (HHMI Janelia) and is described in
Marvin et al. (2013, Nature Methods). No pre-existing external datasets were used; all data were
generated in this study.

## Main Ideas

* **Sole DS synaptic input to mouse On-Off DSGCs is null-direction GABA from SACs.** Excitation
  (glutamate + acetylcholine) is omnidirectional. Compartmental models should implement untuned
  excitatory conductances and null-direction-tuned inhibitory conductances.
* **The target DS index for model optimisation is 0.65-0.73.** In vitro CART-Cre recordings: 0.65
  +/- 0.05; wild-type TRHR-GFP cells: 0.73 +/- 0.03.
* **Null-direction inhibitory conductance is approximately 8x the apparent excitatory P - N** (2.43
  nS vs. 0.31 nS). GABA conductances must be calibrated roughly an order of magnitude above AMPA
  conductances for null-direction suppression.
* **Apparent DS in voltage-clamp excitatory currents is an artefact of imperfect space clamp.** Do
  not use apparent excitatory tuning in experimental voltage-clamp traces to calibrate any model
  excitatory tuning parameter.
* **Series resistance (20-40 MOhm) compensated at only 50-60% limits conductance accuracy.** Treat
  voltage-clamp conductance values as approximate bounds, not precise targets, when fitting
  compartmental model parameters.

## Summary

Park et al. (2014) investigate the synaptic basis of direction selectivity in mouse On-Off DSGCs,
asking whether acetylcholine and glutamate inputs are genuinely directionally tuned alongside the
well-established null-direction GABA from starburst amacrine cells. The study is motivated by a
decade of contradictory voltage-clamp data that appeared to show preferred-direction-tuned
excitatory conductances, implying DS presynaptic release from bipolar cells and SAC cholinergic
terminals.

The authors combine whole-cell patch-clamp with simultaneous two-photon imaging of iGluSnFR
conditionally expressed on DSGC dendrites via CART-Cre mice, applying pharmacological manipulations
(hexamethonium for nicotinic block, gabazine for GABA-A block). Recording the optical glutamate
signal and electrical conductance in the same cell at the same time allows direct dissociation of
presynaptic release directionality from voltage-clamp measurement artefacts.

The central result is unambiguous: glutamate release lacks directional tuning (iGluSnFR P - N =
+0.073 +/- 0.04, p = 0.95) even while simultaneously recorded excitatory current appears tuned
(+0.35 +/- 0.07 nS, p = 0.00015). Blocking GABA-A receptors with gabazine abolishes apparent
excitatory DS in both modalities, confirming the artefact arises from imperfect space clamp during
strong null-direction inhibition (2.43 +/- 0.31 nS). The DS index of recorded cells is 0.65 +/-
0.05, establishing a quantitative target for model optimisation.

For this project's compartmental simulation, these results provide three hard constraints: (1)
excitatory inputs (glutamate and acetylcholine) must be modelled as omnidirectional; (2) null-
direction GABA inhibition is the primary DS-generating mechanism with a P - N magnitude of
approximately 2.4 nS; and (3) the target DS index for optimisation is 0.65-0.73 under in vitro
patch-clamp conditions. The space-clamp artefact warns against using apparent excitatory tuning in
experimental voltage-clamp traces to calibrate any model excitatory tuning parameter.
