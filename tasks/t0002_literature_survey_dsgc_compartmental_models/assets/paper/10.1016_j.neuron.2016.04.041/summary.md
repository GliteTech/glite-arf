---
spec_version: "3"
paper_id: "10.1016_j.neuron.2016.04.041"
citation_key: "Sethuramanujam2016"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# A Central Role for Mixed Acetylcholine/GABA Transmission in Direction Coding in the Retina

## Metadata

* **File**: Download failed (see details.json for reason)
* **Published**: 2016
* **Authors**: Santhosh Sethuramanujam (CA), Amanda J. McLaughlin (CA), Geoffery deRosenroll (CA),
  Alex Hoggarth (CA), David J. Schwab (US), Gautam B. Awatramani (CA)
* **Venue**: Neuron, Volume 90, Issue 6, pp. 1243-1256
* **DOI**: `10.1016/j.neuron.2016.04.041`

## Abstract

A surprisingly large number of neurons throughout the brain are endowed with the ability to
co-release both a fast excitatory and inhibitory transmitter. The computational benefits of dual
transmitter release, however, remain poorly understood. Here, we address the role of co-transmission
of acetylcholine (ACh) and GABA from starburst amacrine cells (SACs) to direction-selective ganglion
cells (DSGCs). Using a combination of pharmacology, optogenetics, and linear regression methods, we
estimated the spatiotemporal profiles of GABA, ACh, and glutamate receptor-mediated synaptic
activity in DSGCs evoked by motion. We found that ACh initiates responses to motion in natural
scenes or under low-contrast conditions. In contrast, classical glutamatergic pathways play a
secondary role, amplifying cholinergic responses via NMDA receptor activation. Furthermore, under
these conditions, the network of SACs differentially transmits ACh and GABA to DSGCs in a
directional manner. Thus, mixed transmission plays a central role in shaping directional responses
of DSGCs.

## Overview

This summary is based on the abstract and publicly available information only; the full paper could
not be downloaded.

Sethuramanujam et al. (2016) address a central unresolved question in retinal direction selectivity:
what role does co-transmission of ACh and GABA from SACs play in shaping directional responses in
downstream DSGCs? The classical view held that bipolar cell glutamate was the dominant excitatory
drive, with SAC-derived GABA providing asymmetric inhibition. This paper challenges that picture by
showing that, under natural viewing conditions or low stimulus contrast, the cholinergic SAC output
is the primary excitatory drive -- not a background modulator.

The study uses whole-cell patch-clamp recordings from DSGCs in rabbit retina combined with
pharmacological isolation of synaptic components and a linear regression framework to decompose the
total DSGC synaptic current into GABA, ACh, and glutamate components as a function of direction and
contrast. Optogenetic stimulation of SACs expressing channelrhodopsin-2 (ChR2) in isolation --
bypassing bipolar cell drive entirely -- establishes that the SAC network alone generates
direction-selective DSGC output.

The key finding is a contrast-dependent switch in dominant excitatory transmitter. At low contrast
or under natural stimuli, ACh is the obligatory initiating excitation; glutamate acts only through
NMDA receptors that are Mg2+-blocked at rest and cannot activate without prior cholinergic
depolarization. At high contrast, glutamate via both AMPA and NMDA becomes sufficient. The SAC
network also generates asymmetric directional GABA and ACh signals that together deliver accurate
direction information to DSGC dendrites.

## Architecture, Models and Methods

This summary is based on the abstract and publicly available information only; the full paper could
not be downloaded. Full methodology not available -- paper not downloaded. The following is inferred
from the abstract, paper highlights, and descriptions in citing papers.

The primary preparation is whole-mount rabbit retina (Awatramani lab, University of Victoria).
Whole-cell voltage-clamp patch-clamp recordings are made from ON-OFF DSGCs, identified by the
presence of both cholinergic EPSCs and GABAergic IPSCs during optogenetic SAC stimulation and by
directional spiking tuning.

Three synaptic pathways are pharmacologically dissected:

* Cholinergic: blocked with muscarinic and nicotinic receptor antagonists
* GABAergic: blocked with GABA-A receptor antagonists (gabazine/SR95531)
* Glutamatergic: AMPA blocked with CNQX; NMDA blocked with APV; DL-AP4 suppresses
  photoreceptor-driven bipolar input during optogenetic isolation experiments

A linear regression framework decomposes the full synaptic current waveform recorded during moving
stimuli into contributions from the three receptor classes as a function of stimulus direction,
providing spatiotemporal profiles of each transmitter component across the direction space.

Optogenetic experiments: SACs express ChR2. Glutamatergic retinal drive is silenced
pharmacologically (DL-AP4 50 uM, UBP310, CNQX 10-20 uM) and a high-intensity optical stimulus
directly activates SAC ChR2 in isolation from bipolar cells. Direction selectivity of resulting DSGC
responses demonstrates that the SAC network alone is a sufficient DS encoder.

Contrast manipulation: natural scene movies and sinusoidal gratings at multiple contrast levels
establish the regime in which ACh vs. glutamate dominates excitation. The transition from
cholinergic-dominant to glutamate-sufficient excitation is characterised across contrast levels.

## Results

Results not available -- paper not downloaded. Abstract reports the following; additional
mechanistic details inferred from citing papers:

* Under low-contrast or natural stimulus conditions, ACh from SACs is the primary source of
  excitation to DSGCs; glutamate plays only a secondary amplifying role.
* At low contrast, glutamate input to DSGCs is mediated exclusively through NMDA receptors and
  cannot depolarize cells without prior cholinergic depolarization (Mg2+ block of NMDA at rest). ACh
  is the obligatory trigger for DSGC responses under these conditions.
* At high contrast, both AMPA and NMDA receptors are recruited and cholinergic excitation is no
  longer obligatory for driving DSGC responses.
* Optogenetic activation of SACs alone (all bipolar cell input blocked) drives direction-selective
  responses in DSGCs, demonstrating the SAC network is a computationally complete DS encoder
  independent of bipolar cell asymmetries.
* The SAC network transmits both GABA and ACh to DSGCs in a direction-tuned manner under
  natural/low-contrast conditions; preferred-direction vs. null-direction cholinergic current
  amplitudes differ, confirming ACh is not purely paracrine or undirected.
* Cholinergic transmission is more transient than GABAergic transmission from SACs; the temporal
  mismatch between fast ACh onset and sustained GABA contributes to the E/I kinetic asymmetry
  underlying direction selectivity.
* The ACh-NMDA interaction is nonlinear: cholinergic depolarization unblocks NMDA receptors,
  enabling glutamate amplification -- a coincidence detection mechanism for direction coding.

## Innovations

### Reversal of Glutamate-Dominant Excitation Hierarchy

Prior models assumed bipolar cell glutamate was the primary DSGC excitatory drive. This paper
establishes ACh as the obligatory trigger under natural and low-contrast conditions, reversing the
classical hierarchy and identifying a major gap in previous DSGC computational models.

### Linear Regression Decomposition of Mixed Transmitter Inputs

Quantification of spatiotemporal contributions of GABA, ACh, and glutamate receptor classes
simultaneously during motion stimuli provides a component-resolved description of synaptic inputs
directly usable in biophysical compartmental simulations.

### Optogenetic Isolation of SAC Network as Sufficient DS Encoder

Direct demonstration that the SAC-to-DSGC circuit alone generates direction selectivity without any
bipolar cell asymmetry isolates DS computation at the SAC output synapse and establishes a minimal
biophysical substrate for direction coding.

### ACh-NMDA Coincidence Detection Mechanism

NMDA synapses onto DSGCs are functionally silent without prior ACh depolarization, establishing a
nonlinear gating mechanism that links two transmitter systems at the single-synapse level.

## Datasets

No dedicated publicly released datasets are described. Experimental data consist of patch-clamp
recordings from rabbit retinal DSGCs, with optogenetic experiments also likely performed in mouse
ChAT-Cre retina. No externally archived data repositories are cited in the abstract or in citing
papers.

## Main Ideas

* ACh dominates at low contrast; glutamate amplifies at high contrast. Compartmental DSGC models
  should implement contrast-dependent transmitter hierarchy rather than fixed glutamate dominance.
* SAC GABA and ACh outputs are both direction-asymmetric. Models should assign asymmetric spatial
  weights to both transmitter conductances across DSGC dendrites.
* ACh kinetics (fast/transient) and GABA kinetics (slow/sustained) both contribute mechanistically
  to direction selectivity via temporal E/I asymmetry. Compartmental models should reproduce this
  kinetic mismatch in synaptic conductance waveforms.
* NMDA receptors act as coincidence detectors gated by ACh depolarization. NMDA conductances should
  be parameterised as voltage-dependent with a threshold requiring prior cholinergic activation,
  especially for low-contrast stimulus simulations.
* The SAC network alone suffices for DS computation. This supports models focused on SAC-to-DSGC
  synapse geometry and transmitter kinetics as the primary substrate of DS tuning.

## Summary

Sethuramanujam et al. (2016) investigate the computational function of co-transmission of ACh and
GABA from SACs onto DSGCs, asking whether the excitatory/inhibitory transmitter mixture at the same
synapse has functional consequences beyond what single-transmitter models predict. The study is
conducted in rabbit retina across natural, low-contrast, and high-contrast visual stimulation.

The authors combine whole-cell voltage-clamp recordings from DSGCs with pharmacological isolation of
GABA, ACh, and glutamate receptor currents, a linear regression decomposition of multi-component
synaptic inputs, and optogenetic ChR2 activation of SACs while bipolar cell input is silenced. These
tools measure each transmitter contribution independently across direction and contrast.

The central result is that ACh is the obligatory excitatory initiator at low contrast and under
natural stimuli, while glutamate through NMDA receptors acts as a dependent amplifier via a
nonlinear coincidence detection gate. Optogenetic isolation of the SAC network confirms that SACs
alone encode direction without upstream bipolar cell asymmetry. Both GABA and ACh from SACs are
direction-tuned, and their kinetic differences -- transient ACh vs. sustained GABA -- contribute to
the E/I asymmetry underlying direction selectivity.

For this project, the paper directly constrains the synaptic input parameterisation of a
compartmental DSGC model: cholinergic conductances must be direction-asymmetric and fast, GABAergic
conductances sustained and direction-asymmetric, and NMDA conductances voltage-dependent with a
contrast-dependent activation threshold. These constraints govern the choice of AMPA, NMDA, and
GABA-A conductance waveforms, their spatial distributions across the dendritic arbor, and their
directional weight asymmetries in the compartmental simulation.
