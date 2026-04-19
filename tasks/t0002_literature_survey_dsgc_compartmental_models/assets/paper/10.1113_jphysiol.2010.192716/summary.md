---
spec_version: "3"
paper_id: "10.1113_jphysiol.2010.192716"
citation_key: "Sivyer2010"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Synaptic inputs and timing underlying the velocity tuning of direction-selective ganglion cells in rabbit retina

## Metadata

* File: Download failed (see `details.json` `download_failure_reason`)
* Published: 2010
* Authors: Benjamin Sivyer 🇦🇺, Michiel Van Wyk 🇦🇺, David I. Vaney 🇦🇺, W. Rowland
  Taylor 🇺🇸
* Venue: The Journal of Physiology
* DOI: `10.1113/jphysiol.2010.192716`

## Abstract

There are two types of direction-selective ganglion cells (DSGCs) identified in the rabbit retina,
which can be readily distinguished both morphologically and physiologically. The well characterized
ON-OFF DSGCs respond to a broad range of image velocities whereas the less common ON DSGCs are tuned
to slower image velocities. This study examined how the synaptic inputs shape the velocity tuning of
DSGCs in an isolated preparation of the rabbit retina. The receptive-field properties were mapped by
extracellular spike recordings and compared with the light-evoked excitatory and inhibitory synaptic
conductances that were measured under voltage-clamp. The synaptic mechanisms underlying the
generation of direction selectivity appear to be similar in both cell types in that
preferred-direction image motion elicits a greater excitatory input and null-direction image motion
elicits a greater inhibitory input. To examine the temporal tuning of the DSGCs, the cells were
stimulated with either a grating drifted over the receptive-field centre at a range of velocities or
with a light spot flickered at different temporal frequencies. Whereas the excitatory and inhibitory
inputs to the ON-OFF DSGCs are relatively constant over a wide range of temporal frequencies, the ON
DSGCs receive less excitation and more inhibition at higher temporal frequencies. Moreover,
transient inhibition precedes sustained excitation in the ON DSGCs, leading to slowly activating,
sustained spike responses. Consequently, at higher temporal frequencies, weaker excitation combines
with fast-rising inhibition resulting in lower spike output.

## Overview

The full PDF could not be downloaded (PMC served a proof-of-work JavaScript challenge and the Wiley
pdfdirect endpoint returned a Cloudflare anti-bot interstitial). However, the full HTML rendering of
the paper on PMC was accessible and was used as the source for this summary alongside the abstract
from the CrossRef metadata.

The paper compares two morphologically and physiologically distinct direction-selective retinal
ganglion cell populations in the rabbit retina, the bistratified ON-OFF DSGC and the monostratified
ON DSGC, and asks why the ON DSGC is tuned to slow image velocities while the ON-OFF DSGC responds
to a broad range of velocities. The authors record extracellular spiking to map direction-velocity
preferences, then switch to whole-cell voltage clamp at the reversal potentials for excitation
(around the chloride reversal) and inhibition (near 0 mV) to isolate the light-evoked excitatory and
inhibitory conductances during grating drift and local flicker stimuli.

The central finding is that both cell types share a common directional mechanism (greater excitation
in the preferred direction, greater inhibition in the null direction) but differ fundamentally in
temporal tuning. In ON-OFF cells the excitatory and inhibitory conductances are relatively flat
across temporal frequency, so spike output follows the stimulus over a wide velocity range. In ON
cells, excitation falls and inhibition rises with increasing temporal frequency, and a transient
inhibitory conductance precedes a slow, sustained excitatory conductance. The mismatched kinetics
reduce net depolarization at high velocities, producing a band-pass velocity filter with a low-pass
shape relative to the ON-OFF cell. This demonstrates that the velocity tuning of a DSGC is set by
the balance and kinetics of bipolar-cell drive and amacrine-cell inhibition onto the ganglion cell,
not solely by the starburst-amacrine-cell directional circuit.

The paper is directly relevant to this project because it provides both qualitative and quantitative
constraints on the excitatory/inhibitory input to DSGC compartmental models: the ratio of null- to
preferred-direction inhibition, the ratio of preferred- to null-direction excitation, the temporal
kinetics of each conductance, and the resulting angle- and velocity-dependent spike output.

## Architecture, Models and Methods

Full methodology not available from the PDF; the following is reconstructed from the PMC HTML
rendering of the paper.

Experiments were performed on isolated, intact retinae of adult Dutch-belted rabbits (approximately
1.5-2 kg) under a red safe light in oxygenated Ames medium at 33-35 degrees Celsius. DSGCs were
identified by soma size and by their characteristic spiking responses to a moving spot; cell-type
assignment (ON-OFF vs ON DSGC) was later confirmed by dendritic morphology after filling the cell
with Neurobiotin or Lucifer yellow and imaging bistratified (ON-OFF) or monostratified (ON) arbors.

Extracellular spiking was recorded in loose-patch mode and used to build direction tuning curves at
multiple image velocities, using a drifting square-wave grating (typically 400 um period) on the
receptive-field centre across velocities spanning 50-1200 um/s.

Light-evoked synaptic conductances were then recorded in whole-cell voltage clamp using a
caesium-based internal solution with QX-314 to block sodium channels and voltage-gated potassium
currents. The excitatory conductance (gE) was isolated by holding near the reversal potential for
inhibition (approximately -60 mV) and the inhibitory conductance (gI) by holding near the reversal
potential for excitation (approximately 0 mV); leak and capacitance were subtracted. gE and gI were
computed from the light-evoked current using the two-conductance equation
`I_m = g_E (V - E_E) + g_I (V - E_I)`, assuming reversal potentials of 0 mV and approximately -60 mV
respectively. Directional selectivity was quantified by a direction selectivity index (DSI) defined
as (R_pref - R_null) / (R_pref + R_null), and direction tuning was fitted with a von Mises
distribution characterized by a concentration parameter kappa. Temporal-frequency tuning was mapped
by flickering a 200 um spot on the receptive-field centre at frequencies between approximately 0.5
and 10 Hz.

Velocity tuning curves were summarized across cells and reported as means plus or minus standard
deviation; n values reported in the paper were typically 5-11 cells per condition.

## Results

* The ON DSGC has a low-pass velocity tuning that peaks between approximately **50 and 200 um/s**
  and falls off sharply at higher velocities, whereas the ON-OFF DSGC shows a relatively flat
  velocity response across the tested range of approximately **50-1200 um/s**.
* Directional tuning was strong in both cell types: DSI values were approximately **0.45** for
  ON-OFF DSGC ON responses, **0.50** for ON-OFF DSGC OFF responses, and **0.57** for ON DSGCs.
* Von Mises concentration parameter kappa was approximately **0.91 plus or minus 0.07** for ON-OFF
  DSGCs and **1.06 plus or minus 0.05** for ON DSGCs, indicating slightly sharper tuning in the ON
  DSGC population.
* The null-to-preferred ratio of inhibitory conductance (GI,N/GI,P) was approximately **3.4 plus or
  minus 2.0**, confirming that inhibition is stronger on the null side in both cell types.
* The preferred-to-null ratio of excitatory conductance (GE,P/GE,N) was approximately **1.6 plus or
  minus 0.7**, confirming that excitation is stronger on the preferred side.
* In ON DSGCs, inhibition peaks earlier than excitation: the peak inhibitory conductance occurred at
  approximately **125 plus or minus 26 ms** while the excitatory conductance rose more slowly and
  was sustained, producing an inhibition-first-excitation-second temporal motif.
* In ON DSGCs, the peak excitatory conductance decreased and the peak inhibitory conductance
  increased with rising temporal frequency; the crossover of these two trends defines the
  high-velocity cutoff of the cell.
* In ON-OFF DSGCs, both the excitatory and inhibitory conductances remained approximately constant
  across temporal frequencies from about **0.5 to 8 Hz**, accounting for their broad velocity
  bandwidth.
* The direction-selectivity mechanism itself (preferred-side excitation, null-side inhibition) is
  preserved across all tested velocities for both cell types, indicating that it is the
  frequency-dependent amplitude and relative timing of inputs, not their directional asymmetry, that
  differ between ON and ON-OFF DSGCs.
* Local flicker on the receptive-field centre reproduces the temporal-frequency-dependent
  differences seen during grating drift, demonstrating that the velocity tuning arises from temporal
  filtering of synaptic inputs rather than from spatial-offset circuitry between excitation and
  inhibition.

## Innovations

### Direct dissection of velocity tuning into excitatory and inhibitory conductances

Earlier work on DSGC direction selectivity focused almost entirely on the spatial asymmetry between
preferred and null directions. This paper is among the first to decompose the velocity
(temporal-frequency) dimension of tuning into its excitatory and inhibitory components using
voltage-clamp recordings at the two reversal potentials, showing that velocity preference is set by
the temporal-frequency response of the two conductances rather than by the directional asymmetry
itself.

### Temporal mismatch between transient inhibition and sustained excitation in ON DSGCs

The paper identifies a specific cellular mechanism for low-pass velocity tuning: in ON DSGCs
inhibition rises and decays faster than excitation, so at high temporal frequencies inhibition
preempts and truncates each excitatory event. This is a concrete, testable kinetic scheme that
distinguishes ON from ON-OFF DSGCs at the synaptic level.

### A two-cell-type comparison framework for DSGC modelling

By recording identical protocols in morphologically confirmed ON and ON-OFF DSGCs, the paper
provides matched datasets that let modellers test whether a single compartmental model with
different input kinetics can reproduce both velocity-tuning phenotypes, or whether morphological
differences (monostratified vs bistratified arbor) are required.

## Datasets

No public datasets were released with this paper. The empirical data consists of voltage-clamp and
loose-patch recordings from identified ON and ON-OFF DSGCs in isolated adult Dutch-belted rabbit
retinae, collected at the University of Queensland under animal-ethics approval. Per-condition group
sizes are typically n = 5-11 cells, with individual recording traces, direction tuning curves,
velocity tuning curves, and peak-conductance values reported in the paper figures rather than as a
downloadable supplement. Full source data can in principle be requested from the corresponding
authors (Sivyer or Taylor).

## Main Ideas

* Excitatory and inhibitory conductance waveforms, measured at the two synaptic reversal potentials,
  are the natural input to a DSGC compartmental model and should replace phenomenological rate-based
  inputs when tuning the model against real cells.
* For the project compartmental model, the preferred/null conductance ratios reported here
  (GI,N/GI,P of about 3.4, GE,P/GE,N of about 1.6) provide a first-pass target for the spatial
  asymmetry of AMPA and GABA inputs on the dendritic arbor.
* Velocity tuning should be modelled not by changing directional asymmetry but by changing the
  kinetics (rise time, decay time) of excitatory and inhibitory conductances; the project EPSP/IPSP
  amplitude-and-kinetics parameter sweep is therefore directly motivated by this paper findings.
* The temporal offset between inhibition and excitation (inhibition leading by roughly 100 ms in ON
  DSGCs) is a load-bearing parameter that should be explicitly included in the model wave-stimulus
  protocol.

## Summary

The paper asks why two morphologically distinct direction-selective ganglion cells in the rabbit
retina, the bistratified ON-OFF DSGC and the monostratified ON DSGC, have different velocity tuning
despite sharing the same directional computation. Using a combined extracellular-spiking and
whole-cell voltage-clamp protocol in the isolated rabbit retina, the authors record spiking
direction-velocity tuning and then isolate the light-evoked excitatory and inhibitory synaptic
conductances under voltage clamp at the chloride and cation reversal potentials respectively.

Methodologically, the work is an application of the now-standard two-conductance decomposition to a
velocity-tuning question: the same drifting-grating and local-flicker stimuli are presented under
current- and voltage-clamp, and conductances are computed from holding-potential-dependent currents
while sodium channels are blocked with intracellular QX-314. Direction tuning is quantified with a
DSI and von Mises kappa; temporal tuning is quantified by measuring the peak excitatory and
inhibitory conductances as a function of temporal frequency. Cell types are confirmed post hoc by
dye-fill morphology to ensure that reported differences are not confounded by misclassification.

The central finding is that the direction-selective mechanism itself is identical in the two cell
types (preferred-side excitation, null-side inhibition, with GI,N/GI,P around 3.4 and GE,P/GE,N
around 1.6) but that the velocity bandwidth differs because the ON DSGC receives a transient
inhibitory conductance that precedes a slower sustained excitatory conductance, and the ratio of
inhibition to excitation grows with temporal frequency. In ON-OFF DSGCs, by contrast, both
conductances are approximately flat from 0.5 to 8 Hz, producing the broad velocity response for
which these cells are known.

For this project, the paper is load-bearing because it converts the qualitative statement that ON
DSGCs prefer slow motion into a quantitative recipe for the inputs of a compartmental model:
spatially asymmetric preferred/null conductance ratios, temporally mismatched rise and decay
kinetics, and a specific lead-lag offset between inhibition and excitation. These constraints
directly inform both the EPSP/IPSP amplitude-and-kinetics sweep and the wave-stimulus protocol
described in the project scope, and supply a matched ON vs ON-OFF comparison framework against which
the model velocity-tuning output can be validated.
