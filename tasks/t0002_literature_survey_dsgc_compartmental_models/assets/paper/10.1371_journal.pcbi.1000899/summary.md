---
spec_version: "3"
paper_id: "10.1371_journal.pcbi.1000899"
citation_key: "Schachter2010"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Dendritic Spikes Amplify the Synaptic Signal to Enhance Detection of Motion in a Simulation of the Direction-Selective Ganglion Cell

## Metadata

* **File**: `files/schachter_2010_dendritic-spikes-dsgc.pdf`
* **Published**: 2010
* **Authors**: Michael J. Schachter 🇺🇸, Nicholas Oesch 🇺🇸, Robert G. Smith 🇺🇸, W.
  Rowland Taylor 🇺🇸
* **Venue**: PLoS Computational Biology
* **DOI**: `10.1371/journal.pcbi.1000899`

## Abstract

The On-Off direction-selective ganglion cell (DSGC) in mammalian retinas responds most strongly to a
stimulus moving in a specific direction. The DSGC initiates spikes in its dendritic tree, which are
thought to propagate to the soma with high probability. Both dendritic and somatic spikes in the
DSGC display strong directional tuning, whereas somatic PSPs (postsynaptic potentials) are only
weakly directional, indicating that spike generation includes marked enhancement of the directional
signal. We used a realistic computational model based on anatomical and physiological measurements
to determine the source of the enhancement. Our results indicate that the DSGC dendritic tree is
partitioned into separate electrotonic regions, each summing its local excitatory and inhibitory
synaptic inputs to initiate spikes. Within each local region the local spike threshold nonlinearly
amplifies the preferred response over the null response on the basis of PSP amplitude. Using
inhibitory conductances previously measured in DSGCs, the simulation results showed that inhibition
is only sufficient to prevent spike initiation and cannot affect spike propagation. Therefore,
inhibition will only act locally within the dendritic arbor. We identified the role of three
mechanisms that generate directional selectivity (DS) in the local dendritic regions. First, a
mechanism for DS intrinsic to the dendritic structure of the DSGC enhances DS on the null side of
the cell's dendritic tree and weakens it on the preferred side. Second, spatially offset
postsynaptic inhibition generates robust DS in the isolated dendritic tips but weak DS near the
soma. Third, presynaptic DS is apparently necessary because it is more robust across the dendritic
tree. The pre- and postsynaptic mechanisms together can overcome the local intrinsic DS. These local
dendritic mechanisms can perform independent nonlinear computations to make a decision, and there
could be analogous mechanisms within cortical circuitry.
## Overview

Schachter et al. build a biophysically detailed compartmental model of a rabbit On-Off DSGC to
explain how weak directional selectivity (DS) in postsynaptic potentials (PSP DSI ~0.2) is
transformed into strongly tuned somatic spike output (spike DSI ~0.8). Rather than proposing a new
mechanism, the paper tests whether known retinal mechanisms, presynaptic DS from starburst amacrine
cells (SACs), postsynaptic spatially offset inhibition, and intrinsic dendritic electrotonic
structure, can jointly account for the measured tuning when embedded in an anatomically
reconstructed neuron with voltage-gated channels.

The central finding is that the DSGC dendritic tree fragments into quasi-independent electrotonic
subunits. Each subunit integrates its own local excitation and inhibition and reaches a local spike
threshold that acts as a nonlinear amplifier: small preferred/null PSP differences (a few nS of
conductance) become large firing rate differences. Dendritic spikes generated in these subunits
propagate reliably to the soma under physiological conditions and drive each somatic spike 1:1,
matching the in vitro observations of Oesch, Euler & Taylor (2005).

A second major conclusion is that inhibition acts locally. With experimentally measured inhibitory
conductances (peak ~6 nS on the null side), inhibition can block spike initiation in a local subunit
but cannot prevent a dendritic spike that has already initiated from propagating to the soma;
blocking propagation would require ~85 nS of shunting inhibition, an order of magnitude larger than
what is measured. This dissociation, initiation blockable, propagation not, explains why presynaptic
DS remains necessary: postsynaptic inhibition alone produces strong DS only at isolated distal tips
and weak DS near the soma, so input-side (SAC-generated) DS must carry the signal over the rest of
the arbor.

The third contribution is the identification of an intrinsic dendritic DS effect that actually
opposes the desired tuning on the preferred side of the cell. Because dendrites on the side toward
which the stimulus is moving receive spatially leading excitation from distal to proximal, their
larger distal-to-proximal summation produces stronger responses to null-direction motion locally.
The network-level DS (presynaptic + spatially offset inhibition) has to be strong enough to overcome
this intrinsic bias.
## Architecture, Models and Methods

The model uses a complete anatomical reconstruction of a whole-mounted rabbit On-Off DSGC
(NeuronC/NeuronJ), with soma (~15 um), primary dendrites, and sublaminar On and Off dendritic arbors
in the ON and OFF sublaminae of the inner plexiform layer. The arbor radius is ~150 um and contains
thousands of compartments; each dendritic segment is <0.1 lambda so propagation is spatially well
resolved. Axial resistivity Ri = 110 Ohm cm and specific membrane capacitance Cm = 1 uF/cm^2 are
used throughout.

Passive properties: specific membrane resistance Rm_dend = 10-22 kOhm cm^2 on dendrites and Rm_soma
= 10 kOhm cm^2, producing dendritic input resistances that vary from ~150-200 MOhm near the soma to
>1 GOhm at the distal tips. The membrane time constant is ~20 ms. The dendritic tree is
electrotonically compact near the soma but electrically isolated at the tips, which is the necessary
substrate for local subunit integration.

Active channels include a fast Nav1.6-like sodium channel with Hodgkin-Huxley-style kinetics,
delayed rectifier Kv and A-type Kv4 potassium currents, a Ca channel, and a Ca-activated K current.
Baseline dendritic sodium density is 40 mS/cm^2 uniformly, with alternative gradient configurations
of 45 mS/cm^2 proximal decaying to 20 mS/cm^2 distal tested for robustness. Somatic gNa is typically
150 mS/cm^2 to ensure reliable somatic spike generation. Potassium channel densities are tuned so
that somatic spikes repolarize in ~1 ms and dendritic spikes are brief and slightly graded.

Synapses are point conductance changes with AMPA-like excitation (Erev = 0 mV, tau_rise = 0.1 ms,
tau_decay = 2 ms) and GABA-A-like inhibition (Erev = -65 mV, tau_rise = 0.5 ms, tau_decay = 10 ms).
Individual excitatory synapses are in the 0.2-1.0 nS range; inhibition is placed within ~20 um of
each excitatory input to implement spatially offset (pre-null-side) inhibition. Peak compound
conductances driving a moving-bar response are approximately g_exc = 6.5 nS / g_inh = 3.5 nS in the
preferred direction and g_exc = 2.5 nS / g_inh = 6.0 nS in the null direction, matching
voltage-clamp data from Oesch, Euler & Taylor (2005) and related studies.

Stimulation protocols include: (1) single-synapse activation at various dendritic locations to map
local spike thresholds, (2) paired excitation+inhibition with varied inhibitory amplitude and timing
to quantify how much inhibition is needed to block initiation vs propagation, (3) full drifting bar
simulations across 12 directions at 1 mm/s with SAC-derived presynaptic DS templates, and (4)
removal experiments that independently zero out presynaptic DS, postsynaptic inhibition, or
dendritic voltage-gated channels. Outputs are quantified as peak somatic voltage, dendritic spike
count, somatic spike count, and the direction-selectivity index DSI = (pref - null) / (pref + null)
applied to both subthreshold PSPs and spike counts.

The authors also use the model to estimate how much voltage-clamp at the soma underestimates true
synaptic conductance in distal dendrites due to space-clamp error; compensation factors of 40-100%
are reported depending on dendritic location.
## Results

* Dendritic spike initiation threshold drops steeply with distance: a single excitatory synapse with
  peak conductance **~1 nS** is sufficient to trigger a local dendritic spike at the distal tips,
  but **3-4 nS** is required near the soma.
* Local input resistance scales from **~150-200 MOhm** on proximal dendrites to **>1 GOhm** at
  distal tips, producing the spatial gradient of spike threshold.
* With physiological synaptic drive, PSP directional tuning is weak (**DSI ~0.2**) but somatic spike
  tuning is strong (**DSI ~0.8**), a **~4x amplification** via the dendritic spike threshold
  nonlinearity.
* Measured inhibitory conductances (**~4-10 nS** leading) are sufficient to prevent dendritic spike
  initiation but **cannot** block propagation once a spike has started.
* Blocking propagation of an existing dendritic spike requires shunting inhibition on the order of
  **~85 nS**, roughly **10x** larger than what is physiologically available.
* Every dendritic spike that initiates propagates to the soma and drives a **1:1** somatic spike,
  consistent with the in vitro recordings of Oesch et al. (2005).
* Removing presynaptic DS (uniform SAC input) drops spike DSI from **~0.8** to **~0.3-0.4** despite
  retaining postsynaptic spatially offset inhibition; postsynaptic inhibition alone gives robust DS
  only at the most isolated distal tips.
* Removing postsynaptic inhibition while keeping presynaptic DS preserves most of the somatic spike
  DS, indicating presynaptic DS is the more robust mechanism across the arbor.
* Intrinsic dendritic DS (from distal-to-proximal summation asymmetry) biases **null-direction**
  responses upward on the preferred side of the cell by roughly **DSI -0.1 to -0.2**, meaning the
  network DS mechanisms have to be strong enough to overcome an opposing intrinsic signal.
* Somatic voltage-clamp underestimates distal synaptic conductances by **40-100%** because of
  space-clamp error along high-Ri dendrites.
* Dendritic spikes are brief (**~1-2 ms** half-width), partially active (peak **~-10 to 0 mV** in
  distal dendrites vs **+20 mV** at soma), and sodium-dependent (blocked by removing dendritic gNa).
## Innovations

### Dendritic Subunit Partitioning as the Source of Spike DS Amplification

The paper is the first to quantitatively show, in an anatomically realistic DSGC model, that the
dendritic tree decomposes into independent electrotonic subunits whose local spike thresholds act as
nonlinear amplifiers transforming weak PSP-level DS into strong spike-level DS. Prior work had
hypothesized subunits; this paper puts specific numbers (threshold, gain, spatial extent) on them.

### Dissociation of Initiation vs Propagation Threshold for Inhibition

A key conceptual contribution is showing that the inhibitory conductance needed to block a dendritic
spike initiation (**a few nS**) is an order of magnitude smaller than the conductance needed to
block its propagation (**~85 nS**). This reframes the role of starburst-driven inhibition as a
spike-initiation veto rather than a shunt on outgoing signals, and explains why presynaptic DS
remains necessary.

### Identification of Intrinsic Dendritic DS Opposing Network DS

The authors isolate a purely structural DS effect arising from the asymmetric geometry of each
dendritic branch: excitation that arrives distal-to-proximal (null-direction on the preferred side)
summates more effectively than proximal-to-distal activation. This intrinsic effect opposes the
desired tuning on the preferred side and sets a lower bound on how strong the network DS must be.

### Quantification of Space-Clamp Error for DSGC Voltage-Clamp Studies

The model provides a principled estimate that somatic voltage-clamp underestimates true distal
dendritic synaptic conductances by 40-100%, giving a correction factor for interpreting published
conductance measurements in rabbit DSGCs.
## Datasets

This is a computational modeling paper; no experimental datasets are released. The model uses:

* A single anatomically reconstructed rabbit On-Off DSGC morphology (whole-mount light microscopy)
  imported into NeuronC.
* Previously published voltage-clamp measurements of excitatory and inhibitory conductances in
  rabbit DSGCs (notably Oesch, Euler & Taylor 2005 and related work from the Taylor lab) as
  constraints on synaptic conductance amplitudes.
* Starburst amacrine cell (SAC) output properties from the literature as the presynaptic DS template
  driving the GABA-A inhibitory inputs.

The NeuronC simulator (Smith lab, University of Pennsylvania) is the public software platform used.
Model code and parameter files are not included as a supplementary release in this paper.
## Main Ideas

* A biophysically detailed DSGC compartmental model with active dendrites is sufficient, without any
  new biophysics, to reproduce the in vitro observation that weak PSP DS (**DSI ~0.2**) maps onto
  strong somatic spike DS (**DSI ~0.8**), provided dendrites host voltage-gated Na channels and the
  tree is long enough to be electrotonically compartmentalized.
* Realistic dendritic Na density (**~40 mS/cm^2** uniform, or **45 to 20 mS/cm^2** gradient) and Rm
  giving distal input resistance **>1 GOhm** are the key parameters that set local spike threshold
  gradients; the model of this project should target these values and test both uniform and gradient
  Na distributions.
* Inhibition in DSGCs is best modeled as a veto on spike initiation, not a propagation shunt; peak
  inhibitory conductances of **~4-10 nS** placed spatially close to excitation inputs (within ~20
  um) reproduce measured null-direction suppression. Do not simulate inhibition at conductances
  large enough (>>10 nS) to shunt a propagating dendritic spike, this is unphysiological.
* Presynaptic DS (from SACs) and postsynaptic spatially offset inhibition are complementary:
  presynaptic DS dominates over most of the arbor while postsynaptic inhibition dominates at
  isolated distal tips. A DSGC model for this project should include both.
* Intrinsic dendritic DS is a real, measurable effect that opposes the desired tuning on the
  preferred side; models must use strong enough network DS (presynaptic + inhibition) to overcome
  this intrinsic bias, and verifying the sign and magnitude of the intrinsic effect is a useful
  sanity check on any new compartmental DSGC model.
* Somatic voltage-clamp measurements of distal synaptic conductances should be corrected upward by
  **40-100%** when used as model constraints; otherwise simulations will systematically
  underestimate true dendritic excitation.
## Summary

Schachter, Oesch, Smith & Taylor (2010) ask how the rabbit On-Off direction-selective ganglion cell
converts weakly directionally tuned synaptic input (PSP DSI ~0.2) into strongly tuned spike output
(spike DSI ~0.8). The scope is a single-cell biophysical explanation: given the known circuitry
(starburst amacrine cells providing presynaptic DS, spatially offset postsynaptic inhibition) and
the known cell (anatomical DSGC morphology with active dendrites), can the measured transformation
be reproduced, and what is each mechanism contribution? This is motivated by prior in vitro evidence
from Oesch et al. (2005) that each somatic spike is triggered by a dendritic spike, and by the
unresolved question of whether postsynaptic inhibition alone can account for DS.

The methodology is a NeuronC compartmental simulation of a reconstructed DSGC with Hodgkin-Huxley
Na, Kv, Kv4, and Ca channels in the dendrites and soma, driven by AMPA-like excitatory and
GABA-A-like inhibitory synapses whose conductances and timings match published voltage-clamp data.
Stimulation protocols include single-synapse threshold mapping, paired excitation+inhibition
titration, and full 12-direction drifting-bar experiments. Key design decisions include electrically
compartmentalizing the dendrites via high Rm and thin distal branches (Rin >1 GOhm), using uniform
or graded dendritic gNa (**40 mS/cm^2** or **45 to 20 mS/cm^2**), and systematically removing each
DS mechanism to isolate its contribution.

The headline results are that local dendritic spike thresholds act as ~4x nonlinear amplifiers of
PSP-level DS; that physiological inhibition (**~4-10 nS**) can prevent spike initiation but cannot
block propagation (which would require ~85 nS); that presynaptic DS from SACs is the more robust
mechanism across the arbor while postsynaptic inhibition dominates only at distal tips; and that an
intrinsic dendritic geometric effect actually opposes the desired DS on the preferred side,
requiring network DS to be strong enough to overcome it. Somatic voltage-clamp additionally
underestimates distal conductances by 40-100%.

For the present project compartmental modeling of DSGCs, this paper provides a concrete reference
design (channel densities, synapse conductances, inhibition placement, morphology source) and three
load-bearing predictions to reproduce: (i) the 4x amplification of DSI from PSPs to spikes via
dendritic Na, (ii) the initiation-vs-propagation asymmetry for inhibition, and (iii) the
compartmentalized-subunit structure of the tree. It also establishes that presynaptic DS cannot be
omitted from a DSGC model intended to match physiological spike tuning and gives quantitative
guidance on how to calibrate voltage-clamp-derived conductances for use in simulation.
