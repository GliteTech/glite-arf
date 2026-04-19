---
spec_version: "3"
paper_id: "10.1126_science.1189664"
citation_key: "Branco2010"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Dendritic Discrimination of Temporal Input Sequences in Cortical Neurons

## Metadata

* **File**: `files/branco_2010_dendritic-sequence-discrimination.pdf`
* **Published**: 2010
* **Authors**: Tiago Branco 🇬🇧, Beverley A. Clark 🇬🇧, Michael Häusser 🇬🇧
* **Venue**: Science, vol. 329, issue 5999, pp. 1671–1675
* **DOI**: `10.1126/science.1189664`

## Abstract

The detection and discrimination of temporal sequences is fundamental to brain function and
underlies perception, cognition, and motor output. By applying patterned, two-photon glutamate
uncaging, we found that single dendrites of cortical pyramidal neurons exhibit sensitivity to the
sequence of synaptic activation. This sensitivity is encoded by both local dendritic calcium signals
and somatic depolarization, leading to sequence-selective spike output. The mechanism involves
dendritic impedance gradients and nonlinear synaptic N-methyl-D-aspartate receptor activation and is
generalizable to dendrites in different neuronal types. This enables discrimination of patterns
delivered to a single dendrite, as well as patterns distributed randomly across the dendritic tree.
Pyramidal cell dendrites can thus act as processing compartments for the detection of synaptic
sequences, thereby implementing a fundamental cortical computation.

## Overview

Branco, Clark, and Häusser address a long-standing question in computational neuroscience: can
individual dendrites detect the temporal order of their synaptic inputs? The paper shows, for the
first time in cortical neurons, that single basal and apical oblique dendrites of layer 2/3
pyramidal cells are strongly direction- and velocity-sensitive to the spatial sequence in which a
fixed set of synapses is activated. This builds experimentally on a 1964 prediction by Wilfrid Rall
that dendrites acting as delay lines should yield direction-sensitive responses, and extends it by
demonstrating a mechanistically distinct, NMDA-receptor-dependent mechanism that operates
effectively even in short dendrites where the classical passive cable mechanism would be too weak.

The experiments rely on multi-site two-photon glutamate uncaging at identified dendritic spines of
layer 2/3 somatosensory and visual cortex pyramidal neurons. By activating 8–10 spines in ordered
sequences from branch tip to soma ("IN") or from soma to tip ("OUT"), or in random orders, the
authors show that somatic EPSP amplitude, spike probability, and local dendritic Ca2+ signals all
depend sensitively on both the direction and the velocity of the activation sequence.

The biophysical mechanism is identified through pharmacology (D-AP5 NMDAR block) and a detailed
compartmental model. Direction sensitivity depends on the interplay between the dendritic impedance
gradient (input impedance is higher at the distal tip than at the soma) and the voltage-dependent
Mg2+ block of NMDA receptors. Sequences initiated distally accumulate more local depolarisation,
progressively unblocking NMDAR conductance and generating supralinear summation. This mechanism is
active and regenerative, unlike the purely passive mechanism Rall described, and therefore operates
in short dendrites across a wide range of morphologies.

The paper also shows that the mechanism extends to discrimination of arbitrary random input patterns
on a single dendrite and, remarkably, to patterns distributed across multiple dendrites, broadening
its computational relevance far beyond simple binary directional tuning.

## Architecture, Models and Methods

**Experimental preparation.** Layer 2/3 pyramidal neurons in acute slices of rat somatosensory and
visual cortex were whole-cell patch-clamped and filled with Alexa 594 for two-photon visualisation.
Dendritic spines were selected on basal and apical oblique branches.

**Two-photon glutamate uncaging.** MNI-glutamate was photolysed at 8–10 identified spines using a
720 nm pulsed Ti:sapphire laser. Sites were activated sequentially with inter-stimulus intervals
tuned to produce a range of input velocities (reported as µm/ms along the dendrite). The IN
direction activated spines from branch tip toward the soma; OUT activated from soma toward the tip.
Optimal velocity for direction sensitivity was **2.6 ± 0.5 µm/ms** (somatic EPSP) and **2.0 ± 0.4
µm/ms** (dendritic Ca2+ signal).

**Pharmacology.** The NMDAR antagonist D-AP5 (50 µM) was bath-applied to isolate the contribution
of NMDA receptors. Recordings before and after D-AP5 established that supralinearity, direction
sensitivity, and velocity sensitivity are all NMDA-receptor-dependent.

**Calcium imaging.** OGB-1 (Oregon Green BAPTA-1) was loaded via the patch pipette. Linescan imaging
along the selected dendrite during uncaging sequences captured the spatiotemporal profile of local
Ca2+ transients, confirming that direction and velocity sensitivity of the Ca2+ signal mirrors the
somatic electrical signal.

**Compartmental modelling.** A detailed multi-compartment model of a layer 2/3 pyramidal cell was
implemented, with passive dendrites and synapses containing both AMPA and NMDA conductances (NEURON
framework; ModelDB accession 140828). The model reproduced direction sensitivity without active
dendritic conductances, confirming that impedance gradient plus NMDA non-linearity is sufficient.
The model was also used to predict the distribution of somatic EPSP amplitudes across all possible
random input sequences, and to test the effect of removing NMDAR conductances or hyperpolarising the
membrane. Morphological generality was assessed by simulating impedance gradients across a library
of reconstructed pyramidal cell dendrites (supplementary fig. S7).

**Multi-dendrite experiments.** Random input patterns were delivered across 8 dendrites of a single
cell (n = 5 cells). Somatic EPSP amplitudes for forward vs. reverse sequences were compared at
resting potential, with hyperpolarisation, and with D-AP5.

**Neuronal diversity.** The mechanism was confirmed in layer 5 pyramidal neurons and hippocampal
dentate gyrus granule cells (supplementary fig. S8), demonstrating generalisation across cell types
and morphologies.

## Results

* IN-direction sequences produced a somatic EPSP **31 ± 4% larger** than OUT-direction sequences (P
  < 0.0001, n = 20), corresponding to a mean peak voltage difference of **2.8 ± 0.4 mV**.
* Axonal spike probability was **38 ± 9% higher** for the IN vs. OUT direction (P = 0.0013, n = 7).
* Local dendritic Ca2+ signals were **48 ± 13% larger** for IN vs. OUT sequences (P = 0.0047, n =
  6), with an optimal velocity of **2.0 ± 0.4 µm/ms**.
* Somatic voltage responses to sequential inputs were supralinear at **223 ± 9% of the arithmetic
  sum** of individual responses (P < 0.0001), indicating a regenerative mechanism.
* D-AP5 abolished supralinearity (**103 ± 3%** of linear sum, P = 0.336, n = 8) and reduced the IN
  vs. OUT difference to a non-significant **0.4 ± 0.4 mV** (P = 0.0011 vs. control).
* For random single-dendrite patterns, mean peak EPSP difference between tested patterns was **2.3
  ± 0.22 mV**; **39 ± 8%** of all pair-wise sequence comparisons were significant (P < 0.05,
  Bonferroni-corrected t-test, n = 7); the probability of discriminating any two sequences (> 1 mV
  difference) was **40%**.
* D-AP5 reduced the mean pattern-discrimination difference to **0.69 ± 0.13 mV** (P < 0.0001).
* For multi-dendrite distributed patterns, mean somatic EPSP peak difference between forward and
  reverse sequences was **4.0 ± 1.3 mV** (P = 0.0036, n = 5); hyperpolarisation reduced this to
  **0.5 ± 0.4 mV** (P = 0.0075).

## Innovations

### NMDA-Dependent Active Direction Selectivity in Cortical Dendrites

This is the first experimental demonstration that cortical pyramidal cell dendrites are
directionally selective for the temporal sequence of synaptic input. The mechanism is fundamentally
different from Rall's passive cable model: it is active, driven by regenerative NMDAR recruitment,
and operates in short dendrites with any impedance gradient. It contrasts with and extends prior
work on direction selectivity in retinal neurons (Barlow & Levick 1965; Euler et al. 2002).

### Two-Photon Uncaging for Controlled Sequence Delivery

Multi-site two-photon glutamate uncaging at identified spines with sub-millisecond and sub-micron
precision enables controlled manipulation of spatiotemporal input sequences that was previously
impossible with electrical stimulation. This methodology is now standard for probing dendritic
nonlinearities.

### Mechanistic Framework: Impedance Gradient Times NMDAR Nonlinearity

The paper provides a clean mechanistic account through cable theory: the impedance gradient along a
dendrite (high distally, low proximally) causes distal synapses to depolarise more locally,
preferentially unblocking NMDAR conductance, generating a supralinear cascade. This is a reusable
biophysical framework applicable to any dendritic arbor with an impedance gradient and
NMDAR-containing synapses.

### Generalisation to Distributed and Random Patterns

By extending the finding from ordered sequences on one dendrite to discrimination of arbitrary
random patterns across multiple dendrites, the paper demonstrates that dendrites function as
general-purpose sequence detectors, substantially broadening the computational scope.

## Datasets

No publicly deposited dataset. Experimental data consist of:

* Whole-cell patch-clamp with two-photon glutamate uncaging from acute rat cortical slices (layer
  2/3 pyramidal neurons, somatosensory and visual cortex; n ranges: 5–20 per condition).
* Calcium imaging (OGB-1) during uncaging sequences (n = 6).
* Multi-dendrite experiments (n = 5).
* Supplementary recordings in layer 5 pyramidal neurons and hippocampal dentate gyrus granule cells
  (exact n not reported in the main text).

Compartmental model code is freely available on ModelDB (accession 140828) at
https://modeldb.science/140828. The model uses passive dendrites with AMPA and NMDA synaptic
conductances on a layer 2/3 pyramidal cell morphology.

This is an experimental and computational paper; no external datasets were used or deposited.

## Main Ideas

* **Dendritic impedance gradients combined with NMDA nonlinearity generate direction selectivity.**
  Distal synapses experience higher local input impedance, depolarise more, and progressively
  unblock NMDAR conductance in tip-to-soma sequences. This applies to any dendrite with an impedance
  gradient and NMDAR-containing synapses, including DSGC dendrites receiving AMPA+NMDA excitatory
  inputs.
* **Direction selectivity does not require active intrinsic conductances in the dendrite.** The
  compartmental model achieves robust direction sensitivity with entirely passive dendrites,
  provided NMDA conductances are present at synapses. This establishes a clear baseline for
  comparing passive vs. active (voltage-gated channel-bearing) dendritic configurations, directly
  relevant to RQ4 in this project.
* **Optimal input velocity for direction sensitivity is approximately 2–3 µm/ms.** This provides
  a concrete parameter target for the excitatory/inhibitory wave-sweep speed in the DSGC model
  stimulation protocol.
* **NMDA receptors are the key non-linearity.** D-AP5 reduces the IN-OUT voltage difference from
  **2.8 mV** to **0.4 mV**. Omitting NMDAR conductances from the DSGC model synapses would strongly
  attenuate directional tuning; their inclusion is essential.
* **ModelDB 140828 provides a reusable NEURON implementation.** The model (passive dendrites,
  AMPA+NMDA synapses, layer 2/3 pyramidal morphology) is a directly adaptable starting point for
  implementing analogous biophysics in a DSGC morphology.

## Summary

Branco, Clark, and Häusser ask whether individual cortical dendrites can detect the temporal order
of their synaptic inputs — a computation previously assumed to require networks of neurons. Using
multi-site two-photon glutamate uncaging in layer 2/3 pyramidal neurons of rat somatosensory and
visual cortex, they show that single dendrites produce systematically larger somatic EPSPs and
higher spike probabilities when synapses are activated from the branch tip toward the soma ("IN")
than from soma to tip ("OUT"), and that local dendritic Ca2+ signals carry the same directionality.
The finding scales up: neurons can also discriminate arbitrary random temporal sequences delivered
to a single dendrite or distributed across multiple dendrites.

The mechanism is revealed by pharmacology and a compartmental model. Blocking NMDA receptors with
D-AP5 abolishes supralinear summation (response drops from **223 ± 9%** to **103 ± 3%** of linear
sum) and the directional asymmetry (IN-OUT difference shrinks from **2.8 mV** to **0.4 mV**). The
compartmental model with passive dendrites and AMPA+NMDA synapses fully reproduces direction
sensitivity, identifying the mechanism as the interaction between the dendritic impedance gradient
(high distally, low proximally) and the voltage-dependent Mg2+ block of NMDA receptors. Sequences
initiated distally depolarise more locally, progressively relieving Mg2+ block and generating a
regenerative NMDAR cascade that is absent in the distal-to-proximal direction.

The paper's headline results are: IN responses **31 ± 4%** larger than OUT (n = 20); spike
probability **38 ± 9%** higher; Ca2+ signals **48 ± 13%** larger; random pattern discrimination
probability **40%** (> 1 mV, n = 7); multi-dendrite sequence discrimination **4.0 ± 1.3 mV** (n =
5). All effects are abolished by D-AP5 or hyperpolarisation. The mechanism is confirmed in layer 5
pyramidal neurons and hippocampal dentate gyrus granule cells.

For this project, Branco et al. (2010) provides the mechanistic logic for dendritic direction
selectivity in the compartmental model: the impedance gradient combined with NMDA receptor
non-linearity converts a spatiotemporal sweep of synaptic activation into a directionally tuned
output. Although the paper uses cortical pyramidal neurons, the mechanism explicitly generalises to
any neuron with an impedance gradient and NMDAR-containing synapses, including DSGCs. The ModelDB
140828 NEURON implementation offers directly reusable AMPA+NMDA synapse code, the ~2–3 µm/ms
optimal velocity sets a wave-sweep parameter target, and the D-AP5 results provide a clear internal
control for validating the synaptic component of the DSGC model.
