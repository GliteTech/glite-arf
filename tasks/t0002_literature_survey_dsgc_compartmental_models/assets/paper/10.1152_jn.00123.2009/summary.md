---
spec_version: "3"
paper_id: "10.1152_jn.00123.2009"
citation_key: "Fohlmeister2010"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Mechanisms and Distribution of Ion Channels in Retinal Ganglion Cells: Using Temperature as an Independent Variable

## Metadata

* File: `files/fohlmeister_2010_rgc-ion-channels-temperature.pdf`
* Published: 2010
* Authors: Jurgen F. Fohlmeister (US), Ethan D. Cohen (US), Eric A. Newman (US)
* Venue: Journal of Neurophysiology (J Neurophysiol 103:1357-1374, 2010)
* DOI: `10.1152/jn.00123.2009`

## Abstract

Trains of action potentials of rat and cat retinal ganglion cells (RGCs) were recorded
intracellularly across a temperature range of 7-37 C. Phase plots of the experimental impulse trains
were precision fit using multicompartment simulations of anatomically reconstructed rat and cat
RGCs. Action potential excitation was simulated with a "Five-channel model"
[Na, K(delayed rectifier), Ca, K(A), and K(Ca-activated) channels] and the nonspace-clamped
condition of the whole cell recording was exploited to determine the channels distribution on the
dendrites, soma, and proximal axon. At each temperature, optimal phase-plot fits for RGCs occurred
with the same unique channel distribution. The "waveform" of the electrotonic current was found to
be temperature dependent, which reflected the shape changes in the experimental action potentials
and confirmed the channel distributions. The distributions are cell-type specific and adequate for
soma and dendritic excitation with a safety margin. The highest Na-channel density was found on an
axonal segment some 50-130 um distal to the soma, as determined from the temperature-dependent
"initial segment-somadendritic (IS-SD) break." The voltage dependence of the gating rate constants
remains invariant between 7 and 23 C and between 30 and 37 C, but undergoes a transition between 23
and 30 C. Both gating-kinetic and ion-permeability Q10s remain virtually constant between 23 and 37
C (kinetic Q10s ~ 1.9-1.95; permeability Q10s ~ 1.49-1.64). The Q10s systematically increase for T <
23 C (kinetic Q10 ~ 8 at T ~ 8 C). The Na channels were consistently "sleepy" (non-Arrhenius) for T
< 8 C, with a loss of spiking for T < 7 C.

## Overview

Fohlmeister, Cohen, and Newman extend the classical Fohlmeister-Miller Five-channel model of RGC
excitability by making temperature an independent experimental variable across the wide range 7-37
C. Whole-cell current-clamp recordings from anatomically reconstructed rat (Type I and Type II) and
cat (alpha and beta) RGCs are paired with NEURON multicompartment simulations that reproduce the
measured spike trains via phase-plot fitting. By operating in the non-space-clamped regime,
electrotonic currents feeding the soma from dendrites and axon become diagnostic of where channels
sit, letting the authors infer Na, K(DR), Ca, K(A), and K(Ca) densities on dendrites, soma, initial
segment, thin segment, and distal axon.

The key methodological move is using temperature not as a nuisance but as a lever: as T varies, the
relative speed of channel gating versus electrotonic spread changes, and the shape of the phase plot
changes in ways that depend on channel placement. Fits that are internally consistent across all
temperatures with a single channel distribution are strong evidence for that distribution. The paper
reports cell-type-specific conductance maps with the highest Na density (up to 448 mS/cm^2 in cat
alpha) on a thin axonal segment 50-130 um distal to the soma, and the "IS-SD break" in the somatic
phase plot is shown to depend on temperature because the initial-segment spike crosses the low-Na
axon hillock before invading the soma-dendritic region.

Quantitatively, gating-kinetic Q10s stay near 1.9-1.95 between 23 and 37 C, while ion-permeability
Q10s stay near 1.49-1.64; both scaling factors climb sharply below 23 C (kinetic Q10 reaches ~8 at
~8 C), and Na channels become "sleepy" (non-Arrhenius) below 8 C with loss of spiking below 7 C. The
voltage dependence of the rate constants is temperature-invariant in two plateaus (7-23 C and 30-37
C) separated by a transition band at 23-30 C that is consistent with a lipid-phase rearrangement in
the membrane. Together, this gives a calibrated, physically grounded parameter set for compartmental
RGC models at any physiological temperature.

## Architecture, Models and Methods

The simulation framework is the Fohlmeister-Miller Five-channel model: Hodgkin-Huxley-style Na
(m^3h) and delayed-rectifier K (n^4), plus Ca (c^3), a transient A-type K (a^3 b^1), and a
Ca-activated K (k = [Ca]^2/(K_d^2 + [Ca]^2)) channel, implemented in NEURON on anatomically
reconstructed morphologies. Rat Type I (9 cells) and Type II (9 cells) and cat alpha (3) and beta
(3) RGC reconstructions are used. Each cell has dendrites, soma, initial segment (IS, ~20-30 um
long), a thin segment (TS, the high-Na axonal hotspot ~50-130 um from soma), and the remaining axon.
Passive parameters: R_m = 40 kohm-cm^2, C_m = 1 uF/cm^2, R_i = 100 ohm-cm.

Compartmental peak conductance densities (G-bar) at 35 C in mS/cm^2 across (dendrites / soma / IS /
TS / axon) are:
* Rat Type I: Na 79.5 / 72.0 / 141.1 / 231.1 / 124; K 23.4 / 50.4 / 67.8 / 74.6 / 50; Ca 1.2 / 1.2 /
  0.753 / 0 / 0; K(A) ~36 on soma/dendrites; K(Ca) small.
* Rat Type II: Na 56.7 / 88.4 / 176.6 / 378.6 / 124; K 43.1 / 94.8 / 134.6 / 134.6 / 50.
* Cat beta: Na 63.9 / 69.4 / 100.0 / 244.5 / 124; K 13.4 / 32.0 / 50.1 / 50.1 / 50.
* Cat alpha: Na 60.8 / 158.0 / 277.0 / 448.5 / 124; K 41.2 / 36.1 / 50.1 / 46.7 / 50.

Temperature scaling uses two Q10 families: one for gating rate constants (alpha, beta of m, h, n, a,
b, c) and one for ionic permeability (P_Na, P_K, P_Ca, P_A) via a GHK-style current equation.
Between 23 and 37 C both Q10s are constant: kinetic Q10 ~ 1.9-1.95, permeability Q10 ~ 1.49-1.64.
Below 23 C, rates slow super-exponentially and Q10s climb (kinetic Q10 ~ 8 at 9.8 C). Fitting is
performed by matching simulated phase-plot loops (dV/dt vs V) of repetitive spiking to intracellular
recordings using a downhill-simplex (SUBPLX-family) minimization on the G-bar values; the voltage
midpoints and slopes of rate constants are held fixed within each 7-23 C or 30-37 C plateau and
interpolated through the 23-30 C transition. Intracellular Ca dynamics use a thin submembrane shell
with first-order removal; K(Ca) activates via the resulting [Ca]_i rise.

## Results

* At 35 C, Na peak conductance on the thin axonal segment reaches **448.5 mS/cm^2** in cat alpha
  RGCs, versus **~70-160 mS/cm^2** on the soma, confirming the "high-Na hotspot" 50-130 um distal to
  the soma.
* Gating-kinetic Q10s are **~1.95 for Na** and **~1.90 for K** over 23.5-37.1 C and rise to **~8.0
  at 9.8 C**; permeability Q10s are **1.64 (Na)** and **1.61 (K)** at 37.1 C.
* The voltage dependence of the rate constants is **invariant within 7-23 C and within 30-37 C**,
  with a distinct transition between 23 and 30 C consistent with a membrane-phase rearrangement.
* Na channels are **non-Arrhenius ("sleepy") below 8 C**, and repetitive spiking **fails below 7 C**
  in both rat and cat RGCs.
* The **IS-SD break** (the characteristic inflection in the somatic phase plot marking the
  initial-segment-to-soma-dendritic transition) **shifts systematically with temperature**, and its
  position is reproduced only when the TS carries the highest Na density.
* Single unique G-bar distributions per cell type fit phase plots at every temperature with RMS
  errors below ~5% of peak dV/dt, so the channel map is temperature-independent even though the
  waveforms are temperature-dependent.
* Peak somatic **g_Na is ~0.07-0.16 S/cm^2**, **g_K(DR) is ~0.013-0.095 S/cm^2**, and **g_K(A) on
  soma/dendrites is ~0.036 S/cm^2**, bracketing prior literature values.
* Dendritic Na (50-80 mS/cm^2) plus K(A) gives a **~2x safety factor for antidromic/back-propagating
  spikes**, so somatic spikes invade dendrites rather than failing at branch points.
* Adjusting only Q10s (not G-bars or rate constants) reproduces the slowing, broadening, and
  amplitude loss of action potentials from 37 C down to 10 C in both rat and cat.

## Innovations

### Temperature as an Identifiability Lever

Using temperature as an independent variable across 7-37 C makes channel-distribution parameters
uniquely identifiable: the same G-bar map must fit all temperatures simultaneously, so the huge
parameter degeneracy that usually plagues multicompartment fitting collapses to a single
cell-type-specific solution.

### Two Temperature-Invariant Gating Plateaus with a Phase Transition

The finding that voltage-dependences of rate constants are constant within 7-23 C and within 30-37
C, with an abrupt transition in between, is a concrete physical constraint (plausibly lipid-phase
driven) rather than an empirical curve, and it simplifies temperature scaling to two Q10 families.

### Localized Axonal Na Hotspot

The thin axonal segment 50-130 um distal to the soma is identified as the Na hotspot (up to 448
mS/cm^2), which naturally explains the IS-SD break in phase plots and pinpoints where spikes
initiate - a distribution that must be carried into any realistic RGC compartmental model.

### Non-Arrhenius "Sleepy" Na Below 8 C

The authors document a qualitative change in Na channel behavior below 8 C (loss of Arrhenius
scaling, spike failure below 7 C) that sets a hard lower bound on the applicability of standard
Q10-scaled Hodgkin-Huxley descriptions.

## Datasets

This is an experimental and modeling paper; the primary data are intracellular current-clamp
recordings from 9 rat Type I RGCs, 9 rat Type II RGCs, 3 cat alpha RGCs, and 3 cat beta RGCs,
recorded across 7-37 C. Morphologies are anatomically reconstructed individual RGCs used directly in
NEURON. No public machine-readable dataset is released with the paper, but the G-bar tables (Table
1. and rate-constant tables (Table 2) fully specify the model.

## Main Ideas

* Adopt the Five-channel model (Na, K(DR), Ca, K(A), K(Ca)) with the Table 1 G-bar maps as the
  baseline somatic-axonal-dendritic channel set for any DSGC compartmental simulation; DSGCs are
  RGCs and share the same channel repertoire.
* Place the Na hotspot on a thin axonal segment 50-130 um from the soma (peak ~250-450 mS/cm^2)
  rather than on the soma itself; the somatic g_Na should be only ~70-160 mS/cm^2.
* Use the two-plateau temperature model: keep rate-constant voltage dependences fixed within 30-37 C
  (physiological), scale by kinetic Q10 ~1.95 (Na) / 1.90 (K) and permeability Q10 ~1.6 (Na) / 1.6
  (K) between the reference temperature and the simulation temperature.
* Phase-plot fitting (dV/dt vs V) is the right identifiability tool for calibrating compartmental
  RGC/DSGC models against intracellular recordings - prefer it over waveform-RMS fits.
* Dendritic Na (50-80 mS/cm^2) with co-localized K(A) (~36 mS/cm^2) gives a ~2x safety factor for
  back-propagating spikes, which matters for DSGC direction-selective dendritic computations where
  back-propagation is implicated in nonlinear dendritic integration.

## Summary

Fohlmeister, Cohen, and Newman ask how ion channels are distributed across the dendrites, soma,
initial segment, and axon of rat and cat retinal ganglion cells, and how that distribution must be
scaled with temperature to reproduce whole-cell action-potential trains across 7-37 C. The question
matters because single-compartment or under-constrained multicompartment models of RGCs have
historically suffered from parameter degeneracy: many G-bar maps can fit a recording at one
temperature, and the community lacked a principled, temperature-transferable channel set.

Methodologically, the authors record repetitive spiking in anatomically reconstructed rat Type I and
Type II and cat alpha and beta RGCs at multiple temperatures, then fit phase plots (dV/dt versus V)
of each cell with NEURON multicompartment simulations of the Fohlmeister-Miller Five-channel model
(Na, K(DR), Ca, K(A), K(Ca)). The crucial design choice is to demand that a single G-bar map fit
every temperature simultaneously, so temperature becomes an identifiability lever, and to separate
gating-kinetic Q10s from ion-permeability Q10s in a GHK-style current equation.

They find that the voltage dependence of rate constants is constant within 7-23 C and within 30-37 C
with a sharp transition at 23-30 C; that gating Q10s are ~1.9-1.95 and permeability Q10s are
~1.5-1.65 above 23 C but climb toward ~8 below 10 C; and that Na channels become non-Arrhenius below
8 C, with spike failure below 7 C. Peak Na conductance is concentrated on a thin axonal segment
50-130 um distal to the soma (up to 448 mS/cm^2 in cat alpha), and the temperature dependence of the
IS-SD phase-plot break confirms this localization. A single cell-type-specific channel map fits all
temperatures.

For this project, which is building DSGC compartmental models, this paper is foundational: it
provides a fully calibrated, temperature-scaled Five-channel parameter set for retinal ganglion
cells in rat and cat, including the Na hotspot location, the dendritic Na+K(A) safety factor, and
the two-plateau temperature-scaling scheme. The G-bar tables and Q10 values should be adopted as the
default channel-density prior for DSGC models, modified only where DSGC-specific evidence demands
it, and the phase-plot fitting methodology should be used to calibrate DSGC compartmental models
against future whole-cell recordings.
