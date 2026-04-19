---
spec_version: "3"
paper_id: "10.1016_j.neuron.2005.06.036"
citation_key: "Oesch2005"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Direction-Selective Dendritic Action Potentials in Rabbit Retina

## Metadata

* **File**: `files/oesch_2005_ds-dendritic-aps.pdf`
* **Published**: 2005 (Neuron, Vol. 47, 739-750)
* **Authors**: Nicholas Oesch 🇺🇸, Thomas Euler 🇩🇪, W. Rowland Taylor 🇺🇸
* **Venue**: Neuron (journal)
* **DOI**: `10.1016/j.neuron.2005.06.036`

## Abstract

Dendritic spikes that propagate toward the soma are well documented, but their physiological role
remains uncertain. Our in vitro patch-clamp recordings and two-photon calcium imaging show that
direction-selective retinal ganglion cells (DSGCs) utilize orthograde dendritic spikes during
physiological activity. DSGCs signal the direction of image motion. Excitatory subthreshold
postsynaptic potentials are observed in DSGCs for motion in all directions and provide a weakly
tuned directional signal. However, spikes are generated over only a narrow range of motion angles,
indicating that spike generation greatly enhances directional tuning. Our results indicate that
spikes are initiated at multiple sites within the dendritic arbors of DSGCs and that each dendritic
spike initiates a somatic spike. We propose that dendritic spike failure, produced by local
inhibitory inputs, might be a critical factor that enhances directional tuning of somatic spikes.

## Overview

Oesch, Euler, and Taylor present the first direct evidence that ON-OFF direction-selective ganglion
cells (DSGCs) in the rabbit retina generate dendritic action potentials during light-evoked
physiological activity, and that these orthograde dendritic spikes are the proximate cause of
somatic firing. The study addresses a long-standing puzzle: extracellular recordings show that DSGC
spike output is far more sharply tuned to motion direction than the underlying excitatory
postsynaptic potentials (EPSPs) measured at the soma. A purely somatic integration model cannot
explain this mismatch, because the subthreshold EPSP amplitudes in the preferred and null directions
are nearly identical.

Using whole-cell patch-clamp recordings combined with local tetrodotoxin (TTX) application,
intracellular QX-314, somatic hyperpolarization, and two-photon Ca2+ imaging with Oregon Green
BAPTA-1, the authors identify two distinct spike populations in DSGCs: large ~55 mV somatic spikes
and small ~7 mV dendritic spikelets. When somatic spiking is suppressed pharmacologically or by
hyperpolarization, the underlying dendritic spikes are unmasked. The dendritic spikes retain the
full directional tuning seen in somatic output, indicating that spike initiation and not somatic
integration performs the sharpening. Multi-site dendritic initiation is supported by superposition
of dendritic spikelets at intervals shorter than the somatic refractory period and by
subtype-specific preferences for ON versus OFF dendritic arbors.

The authors propose a model in which locally offset starburst amacrine cell inhibition produces
dendritic spike failure in the null direction, so that only preferred-direction-evoked dendritic
spikes successfully propagate to the soma. This recasts direction selectivity as a distributed,
compartmentalized dendritic computation rather than a single somatic threshold decision.

## Architecture, Models and Methods

Experiments used flat-mount retinas from dark-adapted, Dutch-belted rabbits (right eye), perfused
with oxygenated bicarbonate-buffered Ames medium at 34-36 C. Whole-cell current-clamp recordings
were made with patch electrodes (4-8 Mohm) filled with a K-methylsulfonate internal solution (110 mM
K-methylsulfonate, 10 mM NaCl, 5 mM Na-HEPES, 1 mM K-EGTA, 1 mM Na-ATP, 0.1 mM Na-GTP); a 10 mV
liquid junction potential was subtracted. Signals were filtered at 2 kHz with a Multiclamp 700A and
digitized at 5-10 kHz. DSGCs were pre-identified extracellularly via loose patch, then re-targeted
for whole-cell recording after their preferred direction was measured.

Light stimuli were bright or dark bars (250 um wide, 800-1200 um/s) presented in 12 evenly spaced
directions across 360 deg on a miniature LCD or CRT monitor, covering a 1 mm region centered on the
cell; stimulus contrast was 30-100%. Directional tuning was quantified with a direction selectivity
index (DSI) derived from the vector sum of responses, and tuning curves were fit with a von Mises
distribution.

Three pharmacological strategies isolated dendritic spikes: (1) focal puff application of 0.2-1 uM
TTX onto the soma (~10 um) to suppress Na+-driven somatic APs while leaving dendritic Na+ channels
active; (2) dendritic TTX application 10-20 um below the inner limiting membrane at 80-200 um from
the soma; (3) intracellular dialysis of 1-10 mM QX-314. Bath TTX served as a full-block control.
Somatic hyperpolarization (+25 to -500 pA steps) was used to unmask dendritic events
non-pharmacologically. Spikes were detected by thresholding the second derivative of the voltage
(-2.105 V/s^2), and thresholds were computed from derivative crossings prior to the peak. Somatic
PSP command waveforms, constructed from digitally blanked light-evoked PSPs scaled by the measured
input resistance, were injected to compare somatic-depolarization-evoked versus light-evoked spike
generation.

Two-photon Ca2+ imaging at 920-930 nm (Mira-900 Ti:Sapphire) was performed with DSGCs dialyzed with
100-200 uM Oregon Green BAPTA-1 and counterstained with sulforhodamine 101; line scans (64 pixel,
500 Hz) and image blocks (64x8 pixel, 62.5 Hz) recorded dendritic [Ca2+] transients in ON and OFF
arbors during preferred-direction stimuli, with and without local dendritic TTX.

## Results

* Spike-based DSI averaged **0.67 +/- 0.13 (ON)** and **0.74 +/- 0.13 (OFF)**, while PSP-based DSI
  (spike-blanked) was only **0.09 +/- 0.05 (ON)** and **0.14 +/- 0.08 (OFF)** - spike generation
  sharpens tuning roughly **6-fold**.
* Bath TTX collapsed PSP DSI to **0.04 (ON)** and **0.21 (OFF)** and abolished the ON-OFF
  preferred-direction alignment (12 +/- 9 deg for spikes vs 38 +/- 52 deg for PSPs, n = 12).
* Resting membrane potential was **-70.7 +/- 1.6 mV** (n = 13); input resistance **82.0 +/- 20.6
  MOhm** (n = 9); f-I slope **0.31 +/- 0.18 Hz/pA**.
* Light-evoked PSPs peaked at **-59.1 +/- 1.5 mV** (11.6 mV depolarization) and produced **59 +/- 21
  spikes/stimulus** at a modal rate of **148 +/- 30 Hz**. PSP-shaped somatic current injection
  reaching an even more depolarized **-56.8 +/- 1.3 mV** elicited only **11 +/- 9 spikes/stimulus**
  at **41 +/- 47 Hz** (p < 0.001) - somatic depolarization alone cannot explain light-driven firing.
* Light-evoked spike threshold distribution peaked at **-56 mV** (width ~8 mV) versus **-49 mV**
  (width ~4 mV) for current-injected spikes (2117 vs 1233 spikes pooled from 10 cells).
* Focal somatic TTX unmasked a bimodal spike amplitude distribution: small dendritic spikelets at
  **7.4 +/- 1.9 mV** and somatic spikes at **54.8 +/- 3.5 mV**.
* Somatic absolute refractory period was **3.5 +/- 0.7 ms** (n = 9); dendritic spikelets had a
  markedly shorter refractory period and superimposed, consistent with multiple independent
  initiation zones.
* Dendritic TTX application reduced light-evoked spikes by **13-73% (mean 41.5 +/- 15%)**, while
  depolarization-evoked spikes fell only **25.2 +/- 7.8%**, arguing that light-evoked spikes
  originate in the dendrites.
* Two-photon Ca2+ imaging showed direction-tuned dendritic Ca2+ transients that were abolished by
  bath TTX; local dendritic TTX suppressed transients near the puff site but spared distant
  segments, directly demonstrating active, TTX-sensitive Na+ conductances in DSGC dendrites.

## Innovations

### First demonstration of light-evoked orthograde dendritic spikes in DSGCs

Earlier work (Velte and Masland, 1999) showed dendritic spikes in alpha-type retinal ganglion cells,
but only in response to artificial current injection. This paper establishes that DSGCs - the
canonical direction-computing retinal neuron - generate dendritic action potentials during natural
visual input, and that those spikes are the primary trigger for somatic output.

### Multiple independent spike initiation zones within a single ganglion cell

The shorter, non-refractory interspike intervals of dendritic spikelets, their superposition, and
the ON/OFF asymmetries during hyperpolarization provide mutually reinforcing evidence that
individual DSGCs host several dendritic trigger zones across both the ON and OFF arbors, rather than
a single somatic or axon-initial-segment trigger.

### Dendritic spike failure as the direction-selectivity mechanism

The authors reframe direction selectivity: rather than nullward stimuli producing smaller somatic
PSPs, nullward stimuli produce dendritic spikes that fail to propagate because GABAergic starburst
amacrine inhibition lies on-the-path between the excitatory input and the soma. This is a
compartmentalized, postsynaptic, spatially-offset mechanism consistent with earlier Barlow and
Levick conjectures and with the observed nondirectional zone and preferred-side receptive field
offset.

### Combined patch-clamp and two-photon Ca2+ imaging in intact retina

The study integrates focal TTX puffing, QX-314 dialysis, PSP-waveform current injection, and
two-photon Ca2+ imaging of dye-filled dendrites during visual stimulation into a single experimental
pipeline that isolates dendritic from somatic contributions without requiring dendritic patch
recordings (impractical given ~0.5 um dendritic diameters).

## Datasets

This is an experimental neurophysiology study; no public datasets are used or released. The
experimental subjects are dark-adapted, Dutch-belted rabbits, with retinas dissected and
flat-mounted for in vitro recording. Sample sizes across the figures range from n = 4 to 13 DSGCs
per experimental condition (for example, n = 13 for resting membrane potential and ISI-based spike
rate, n = 12 for DSI comparisons, n = 10 for spike-threshold distributions, n = 9 for
refractory-period measurements, n = 8 for dendritic TTX application, n = 4 for localized dendritic
TTX plus Ca2+ imaging). Animal procedures were approved by the OHSU IACUC and followed NIH
guidelines. Supplemental data include one additional figure (on QX-314 unmasking) referenced in the
online version of the paper.

## Main Ideas

* Dendritic Na+ channels (TTX-sensitive) are required to reproduce DSGC firing: any compartmental
  model restricted to passive dendrites or somatic-only spike initiation will fail to match observed
  spike DSIs (~0.7) even when the PSP DSI (~0.1) is matched correctly - this directly constrains the
  **active vs passive dendrites** question (RQ4) and the Na+/K+ conductance placement (RQ1).
* The 6-fold gap between PSP DSI and spike DSI means that the sharp **angle-to-AP tuning curves**
  (RQ5) observed in vivo cannot be reproduced by tuning somatic thresholds alone; compartmental
  models must implement spatially distributed dendritic spike initiation and selective failure.
* The relative positions of excitatory bipolar input and inhibitory starburst amacrine input along
  the DSGC dendrite control whether a dendritic spike propagates, making **dendritic morphology**
  (RQ2) and the **AMPA/GABA spatial balance** (RQ3) jointly load-bearing parameters - the model must
  preserve on-the-path inhibition geometry rather than lumping inhibition globally.
* Somatic PSPs are nearly identical in preferred and null directions (0 to ~10 mV difference) yet
  produce dramatically different spike counts; this quantitative constraint provides a clean
  validation target for compartmental simulations.
* Each dendritic spike initiates a somatic spike with probability close to 1, and somatic spike
  threshold is set well above somatic PSP peaks - a compartmental model must set axonal/somatic Na+
  excitability such that only dendrite-initiated events (not summed somatic PSPs) cross threshold.

## Summary

Oesch, Euler, and Taylor address a central unresolved question in retinal direction selectivity: why
does a ganglion cell whose somatic subthreshold EPSPs are only weakly directional produce spike
output that is sharply tuned to the preferred direction of motion? By combining whole-cell
current-clamp recordings from ON-OFF DSGCs in flat-mounted rabbit retina with focal and dendritic
TTX application, intracellular QX-314, controlled somatic hyperpolarization, and two-photon Ca2+
imaging of dendritic arbors, they dissect the spatial origin of the spikes that drive DSGC output
during visual stimulation.

The headline finding is a bimodal spike amplitude distribution - large ~55 mV somatic action
potentials and small ~7 mV dendritic spikelets - that can be separated by any of three independent
manipulations (somatic TTX, QX-314, somatic hyperpolarization). The dendritic spikelets inherit the
full directional tuning of the somatic output (DSI ~0.6-0.7), superimpose at sub-somatic-refractory
intervals, and are selectively suppressed by puffing TTX onto the dendrites (reducing light-evoked
spikes by ~42% while barely affecting depolarization-evoked somatic spikes). Calcium imaging
confirms that the dendrites host functional TTX-sensitive Na+ channels active during light-driven
responses.

Mechanistically, the authors argue that direction selectivity is computed by dendritic spike
failure: locally offset GABAergic inhibition from starburst amacrine cells, positioned between
bipolar-cell excitation and the soma along the null-direction pathway, shunts dendritic spikes
before they can reach the soma. In the preferred direction the inhibition is distal to the
excitation, so dendritic spikes propagate successfully. This model naturally explains the
nondirectional zone on the preferred side of the receptive field and the preferred-side receptive
field offset.

For a DSGC compartmental modeling project, this paper is foundational. It supplies the quantitative
targets (somatic PSP amplitudes of ~12 mV across all directions, somatic threshold near -49 mV,
dendritic spikelet amplitude ~7 mV, spike DSI ~0.7 versus PSP DSI ~0.1) that any biophysical
simulation must reproduce, and it specifies the qualitative requirements: active dendrites with
distributed Na+ channels, multiple independent initiation zones, on-the-path starburst inhibition,
and a near-unity dendritic-to-somatic spike coupling. Any model that relies on passive dendrites and
a single somatic threshold cannot reach the observed tuning sharpness and should be rejected on
quantitative grounds.
