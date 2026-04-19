---
spec_version: "3"
paper_id: "10.7554_eLife.52949"
citation_key: "Jain2020"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# The functional organization of excitation and inhibition in the dendrites of mouse direction-selective ganglion cells

## Metadata

* **File**: `files/jain_2020_dsgc-ca.pdf`
* **Published**: 2020-02-25
* **Authors**: Varsha Jain 🇨🇦, Benjamin L Murphy-Baum 🇨🇦, Geoff deRosenroll 🇨🇦, Santhosh
  Sethuramanujam 🇨🇦, Mike Delsey 🇨🇦, Kerry R Delaney 🇨🇦, Gautam Bhagwan Awatramani 🇨🇦
* **Venue**: eLife (2020; 9:e52949)
* **DOI**: `10.7554/eLife.52949`

## Abstract

Recent studies indicate that the precise timing and location of excitation and inhibition (E/I)
within active dendritic trees can significantly impact neuronal function. How synaptic inputs are
functionally organized at the subcellular level in intact circuits remains unclear. To address this
issue, we took advantage of the retinal direction-selective ganglion cell circuit, where
directionally tuned inhibition is known to shape non-directional excitatory signals. We combined
two-photon calcium imaging with genetic, pharmacological, and single-cell ablation methods to
examine the extent to which inhibition 'vetoes' excitation at the level of individual dendrites of
direction-selective ganglion cells. We demonstrate that inhibition shapes direction selectivity
independently within small dendritic segments (<10um) with remarkable accuracy. The data suggest
that the parallel processing schemes proposed for direction encoding could be more fine-grained than
previously envisioned.

## Overview

Jain et al. combine two-photon dendritic Ca²⁺ imaging with genetics, pharmacology, single-cell
ablation, and a multi-compartmental NEURON model to dissect how excitation and inhibition are
organized along the dendrites of mouse ON-OFF direction-selective ganglion cells (DSGCs). The
central empirical claim is that direction selectivity (DS) is computed independently inside very
small dendritic segments (~5–10 µm) — substantially smaller than previously assumed subunit sizes of
50–100 µm from earlier cable-theory estimates (Koch et al. 1982).

To isolate local synaptic activity from back-propagating somatic spikes, the authors block
voltage-gated Na⁺ channels either intracellularly (2 mM QX-314 in the pipette) or extracellularly (1
µM TTX). With Na⁺ channels silenced, the residual dendritic Ca²⁺ signal reflects influx through
voltage-gated Ca²⁺ channels (CaV) and NMDA receptors — the two nonlinearities the paper then uses to
argue that dendritic compartmentalization is enhanced beyond what passive cable properties predict.

Key findings: (1) Ca²⁺ signals rise sequentially along the arbor as a spot traverses the receptive
field, recovering the stimulus speed (524 ± 28 µm/s) from the linear fit of ROI delay versus
position; (2) noise correlations between ROI pairs decay exponentially with cable distance with a
space constant λ = 5.3 µm; (3) directional tuning width of the dendritic Ca²⁺ signal matches that of
somatic spikes and is narrower than subthreshold somatic voltage; (4) individual 3–4 µm ROIs
reliably encode the cell's overall preferred direction (angular SD = 31.6° across 353 ROIs in 7
cells after averaging); (5) ablating 3–7 null-side starburst amacrine cells (SACs) selectively
disrupts DS at interspersed dendritic hot-spots while neighbouring segments remain tuned.

A NEURON model of a reconstructed ON-OFF DSGC with 177 directionally-tuned inhibitory and untuned
excitatory synapses shows that applying a soft voltage threshold (−55 to −48 mV) — comparable to CaV
activation — converts weakly-tuned dendritic voltage into strongly-tuned and locally independent
Ca²⁺-like responses, reproducing the imaging data and providing a mechanistic explanation for
fine-grained parallel processing.

## Architecture, Models and Methods

**Preparation and electrophysiology.** Adult (P30+) C57BL/6J, ChAT-Cre × nGFP, and ChAT-Cre ×
Slc32a1^fl/fl (vGAT-KO) mice; retinas superfused at 35 °C with bicarbonate Ringer (110 mM NaCl, 2.5
mM KCl, 1 mM CaCl₂, 1.6 mM MgCl₂, 10 mM glucose, 22 mM NaHCO₃). DSGCs were identified by
extracellular spiking to positive-contrast spots (200 µm diameter, 500 µm/s) in eight directions.
Borosilicate pipettes (3–6 MΩ). Current-clamp pipette solution (mM): 115 K-gluconate, 7.7 KCl, 10
HEPES, 1 MgCl₂, 2 ATP-Na₂, 1 GTP-Na, 5 phosphocreatine, 2 QX-314, 0.2 Oregon Green BAPTA-1 (OGB-1),
0.05 sulforhodamine-101. Signals sampled at 10 kHz, filtered at 2 kHz, MultiClamp 700B.
Pharmacology: DL-AP4 50 µM, D-AP5 50 µM, CNQX 20 µM, UBP-310 10 µM, TTX 0.5–1 µM.

**Two-photon Ca²⁺ imaging.** Insight DeepSee+ laser at 920 nm; X/Y galvo scanning; custom Pockels
cell gating that blanks laser during projector LED phases. PMT signals digitized at 40 MHz,
time-integrated over 1 µs, then sampled at 1 MHz (PCI-6110). ROIs were 3–4 µm; traces smoothed with
a 2nd-order Savitzky-Golay filter.

**Analysis.** Preferred direction (PD) and direction-selectivity index (DSI) from vector-sum of
eight-direction responses (Equations 1–6); angular SD via the circular statistic σ_θ = √(−2·log V)
(Equations 7–8). Statistics: Watson-Williams, Angular Distance, Kolmogorov-Smirnov, two-tailed
Student t; α = 0.05.

**SAC ablation.** 3–7 ON SACs within 50–150 µm of the DSGC soma on the null side were mechanically
disrupted by injecting 20 nA for 10–15 s through a sharp electrode; Ca²⁺ responses measured in 0.5
µM TTX before and after ablation.

**Multi-compartmental model (NEURON).** Reconstructed ON-OFF DSGC morphology from Poleg-Polsky &
Diamond 2016. Parameters: C_m = 1 µF/cm², R_a = 100 Ω·cm, passive leak reversal −60 mV; stochastic
Hodgkin-Huxley channels. Active conductances in mS/cm² (soma / primary dendrites / terminal
dendrites): Na 150 / 200 / 30; K rectifier 35 / 35 / 25; K delayed rectifier 0.8 / 0.8 / 0.8. 177
paired excitatory + inhibitory synapses distributed across the arbor; inhibition directionally
tuned, excitation untuned. Simulated edge swept at 1 µm/s; voltage recorded at 700 compartments;
release success sampled from Gaussian distributions that narrow for preferred motion and widen for
null motion.

## Results

* Sequential onset of dendritic Ca²⁺ signals during preferred motion recovers a stimulus speed of
  **524 ± 28 µm/s** (n = 6 cells) versus the nominal **500 µm/s**.
* Noise correlations between ROI pairs decay exponentially with cable distance with a space constant
  **λ = 5.3 µm** (n = 7 cells); shuffled-trial controls show no correlation structure.
* Isolated null-direction "hot spots" have Gaussian FWHM = **3.0 ± 1.2 µm** (n = 61 sites, 7 cells).
* Dendritic Ca²⁺ tuning width (Von Mises 1/κ) is indistinguishable from somatic spiking tuning and
  **significantly narrower** than subthreshold somatic voltage (p < 0.05, n = 7 cells).
* Across 353 ROIs from 7 cells, angular SD of PD per single 8-direction set is **σ_θ = 52.8°**,
  falling to **σ_θ = 31.6°** after averaging 3–5 sets; only **9/353 = 2.5 %** of ROIs encode the
  wrong directional hemisphere.
* Mean DSI across dendritic ROIs = **0.19 ± 0.08** (m ± s.d.). Low-DSI (<0.1) sites show weaker
  preferred responses (ΔF/F = **0.60 ± 0.09** vs. **1.02 ± 0.12** for high-DSI, p < 0.01) and
  stronger null responses (**0.49 ± 0.08** vs. **0.31 ± 0.05**, p < 0.01).
* NMDA-receptor blockade (50 µM D-AP5) reduces Ca²⁺ amplitude but leaves PD (Watson-Williams T =
  0.55 < T_C = 1.96; p = 0.49) and DSI (KS p = 0.15) distributions unchanged — NMDA scales
  multiplicatively.
* Mechanical ablation of **3–7 null-side SACs** shifts the DSI distribution strongly relative to
  control (KS p ≈ 10⁻¹⁶); strongly and weakly tuned segments become interspersed on the same
  dendritic branch.
* NEURON model: thresholding local dendritic voltage at **−55, −50, −48 mV** yields angular SD =
  **25.4°, 40.4°, 45.0°** and mean DSI = **0.42, 0.70, 0.80**, demonstrating that dendritic
  threshold nonlinearities sharpen tuning and promote compartmentalization of otherwise
  identically-tuned inputs.
* Response variability during orthogonal motion is significantly reduced in vGAT-KO mice, showing
  that most trial-to-trial variability is synaptic rather than technical.

## Innovations

### Fine-grained (5–10 µm) dendritic DS subunits in an intact circuit

First experimental demonstration that DS information is independently computed on a scale an order
of magnitude smaller than classic cable-theory subunit estimates (~50–100 µm; Koch et al. 1982).
This reshapes how DSGC dendritic processing should be modelled and suggests that the effective
number of parallel directional computations per cell is much larger than previously assumed.

### Direct single-cell SAC ablation test of local veto

Ablating only 3–7 null-side starburst amacrine cells selectively abolishes DS at a subset of
dendritic segments while leaving neighbours tuned. This is the most direct evidence to date that
inhibition from individual SACs vetoes excitation within a tightly localized spatial window.

### CaV/NMDA thresholding as a compartmentalization mechanism

The authors combine pharmacology (D-AP5) with a NEURON model to show that voltage-dependent Ca²⁺
channels and NMDA receptors — not passive cable attenuation alone — are what make neighbouring
dendritic segments functionally independent. A soft voltage threshold in the −55 to −48 mV range
converts weakly tuned voltage into strongly tuned and independent Ca²⁺ signals.

### Parallel-processing interpretation of DSGC dendrites

The Ca²⁺ tuning width matches somatic spike tuning while being narrower than the subthreshold
membrane voltage. This argues that the soma reads out an already-thresholded, already-sharpened
dendritic representation, consistent with a "many-dendrite-parallel-detector" scheme rather than
global integration.

## Datasets

This paper does not release a tabular dataset in the sense used in ML benchmarks. It provides:

* Source data files for every figure, included with the eLife publication (`Source data 1` tables
  per figure, covering spiking, currents, Ca²⁺ responses, rise times, cross-correlations, DSI
  distributions, and model outputs).
* Analysis code at `https://github.com/benmurphybaum/eLife_2020_Analysis` (MATLAB / Igor Pro).
* Visual stimulation software StimGen at `https://github.com/benmurphybaum/StimGen` (MATLAB +
  Psychtoolbox / Python + PsychoPy).

**Experimental sample**: adult (≥P30) mice of both sexes, strains C57BL/6J, ChAT-Cre × nGFP,
ChAT-Cre × Slc32a1^fl/fl (vGAT-KO), Trhr-EGFP, Hb9-EGFP. Population totals cited in the paper
include 7 ON-OFF DSGCs for the core dendritic tuning analysis (353 ROIs total), 6 cells for the
noise-correlation / λ measurement, 4 cells for the SAC-ablation DSI distribution, and 1
reconstructed DSGC morphology simulated in NEURON with 177 synaptic pairs and 700 recorded
compartments.

## Main Ideas

* The target ON-OFF DSGC for our compartmental model can be implemented with **177 paired E/I
  inputs**, a stochastic HH mechanism, and the Poleg-Polsky & Diamond 2016 morphology; exact
  published conductance densities are reproduced here (soma/primary/terminal dendrite Na = 150 / 200
  / 30 mS/cm², K-rect = 35 / 35 / 25, K-delayed = 0.8 / 0.8 / 0.8 mS/cm²; C_m = 1 µF/cm², R_a = 100
  Ω·cm). These are directly usable initial values for our own NEURON build.
* Our "angle versus AP frequency" target should be benchmarked against **σ_θ ≈ 32°** angular SD of
  dendritic PDs and a DSGC-level DSI that produces angular tuning as sharp as somatic spikes (1/κ
  from Von Mises fits), not merely against somatic subthreshold PSP tuning.
* Wave-stimulus design should emulate the paper's sweep of excitatory/inhibitory activation across
  the arbor at calibrated speeds (e.g. 500 µm/s); with tuned inhibition and untuned excitation the
  model already produces realistic PD/DSI behavior — a useful sanity check for our parametric sweeps
  over AMPA/GABA density and kinetics.
* Inhibition must be delivered co-local with excitation (≤5–10 µm and within ~10 ms) for
  null-direction spike suppression; our model's wave-stimulus protocol should therefore include an
  E–I timing offset parameter, not only amplitude/density parameters.
* Dendritic **active** Na⁺ / K⁺ conductances (or equivalently a CaV-like soft threshold near −55 to
  −48 mV) are predicted to sharpen directional tuning substantially relative to passive dendrites;
  this is a direct empirical reference point for the project's active-vs-passive dendrite
  comparison.
* NMDA-receptor nonlinearities multiplicatively amplify responses without changing PD/DSI
  distributions — useful when deciding whether to include NMDA as a separate mechanism or fold it
  into an effective supralinear current.

## Summary

This eLife paper asks a specific question about retinal direction selectivity: at what spatial scale
is the direction-selective computation actually performed inside the dendrites of an ON-OFF DSGC?
The question is motivated by decades of theoretical work (Koch, Poggio & Torre 1982; Schachter et
al. 2010) proposing dendritic subunits on a 50–100 µm scale, by anatomical evidence that starburst
amacrine cells wrap varicosities around DSGC dendrites with direction-dependent orientation
(Briggman et al. 2011), and by earlier patch-clamp results (Sivyer & Williams 2013) suggesting
subthreshold local tuning. The authors set out to measure that spatial scale directly in an intact
mouse retina.

Their methodology combines two-photon Ca²⁺ imaging of small (3–4 µm) dendritic ROIs in OGB-1-loaded
DSGCs with voltage-gated Na⁺ channel blockade (intracellular QX-314 or bath TTX), pharmacological
dissection of NMDA receptors (D-AP5), genetic disruption of GABA release from starburst amacrine
cells (vGAT-KO), mechanical ablation of individual SACs via sharp-electrode lesions, and a
multi-compartmental NEURON model of a reconstructed DSGC with 177 E/I synaptic pairs and stochastic
release. The combination of imaging, targeted circuit perturbation, and biophysical simulation is
the paper's methodological core.

The headline findings are that DS information exists and is independently generated inside 5–10 µm
dendritic segments — an order of magnitude smaller than classic cable-theory estimates; that noise
correlations between dendritic ROIs fall off with a 5.3 µm space constant; that dendritic Ca²⁺
tuning matches somatic spiking tuning and is sharper than subthreshold somatic voltage; that NMDA
receptors scale responses multiplicatively without altering PD or DSI; that ablating just 3–7
null-side SACs selectively disrupts DS at interspersed dendritic hot spots leaving other segments
intact; and that a soft dendritic voltage threshold in the CaV activation range (−55 to −48 mV) is
sufficient in the model to convert homogeneously-tuned inputs into strongly-tuned,
locally-independent compartments.

For this project the paper is central. It pins down the empirical target that an ON-OFF DSGC
compartmental model must reproduce: sharp somatic directional tuning that emerges from many small,
locally-tuned dendritic segments whose independence is enforced by dendritic threshold
nonlinearities and by spatially-precise GABAergic inhibition. It also supplies an explicit set of
channel conductances, a morphology reference (Poleg-Polsky & Diamond 2016), a ratio of 1:1
excitatory-to-inhibitory synapse count (177 each), and a concrete prediction — active dendritic
Na⁺/K⁺ channels are expected to sharpen tuning — that we will test directly as part of our
active-vs-passive dendrite experiment. The measured DSI distribution, angular SD of ~32°, and 5–10
µm compartment scale give us quantitative benchmarks to score candidate model configurations
against.
