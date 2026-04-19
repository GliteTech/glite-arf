---
spec_version: "3"
paper_id: "10.1016_j.neuron.2017.07.020"
citation_key: "Koren2017"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Cross-compartmental Modulation of Dendritic Signals for Retinal Direction Selectivity

## Metadata

* **File**: `files/koren_2017_cross-compartmental-ds.md` (and BioC JSON sibling)
* **Published**: 2017-08-16
* **Authors**: David Koren 🇺🇸, James C. R. Grove 🇺🇸, Wei Wei 🇺🇸
* **Venue**: Neuron, 95(4), 914-927.e4
* **DOI**: `10.1016/j.neuron.2017.07.020`

## Abstract

Compartmentalized signaling in dendritic subdomains is critical for the function of many central
neurons. In the retina, individual dendritic sectors of a starburst amacrine cell (SAC) are
preferentially activated by different directions of linear motion, indicating limited signal
propagation between the sectors. However, the mechanism that regulates this propagation is poorly
understood. Here, we find that metabotropic glutamate receptor 2 (mGluR2) signaling, which acts on
voltage-gated calcium channels in SACs, selectively restricts cross-sector signal propagation in
SACs, but does not affect local dendritic computation within individual sectors. mGluR2 signaling
ensures sufficient electrotonic isolation of dendritic sectors to prevent their depolarization
during non-preferred motion, yet enables controlled multicompartmental signal integration that
enhances responses to preferred motion. Furthermore, mGluR2-mediated dendritic compartmentalization
in SACs is important for the functional output of direction-selective ganglion cells (DSGCs).
Therefore, our results directly link modulation of dendritic compartmentalization to circuit-level
encoding of motion direction in the retina.

## Overview

This paper investigates how dendritic signals are integrated across compartments in starburst
amacrine cells (SACs), the inhibitory interneurons that supply null-direction inhibition to ON-OFF
direction-selective retinal ganglion cells (DSGCs). While earlier work treated each SAC dendritic
sector as an independent computational unit with a centrifugal (soma-to-tip) preference, the authors
show experimentally that the centrifugal response during full-field motion is substantially enhanced
by signal propagation from other dendritic sectors across the soma — a "trans-somatic"
multicompartmental integration.

The second half of the paper identifies metabotropic glutamate receptor 2 (mGluR2) — expressed
almost exclusively in SACs in the rodent retina — as the molecular regulator of the balance
between compartmental isolation and cross-compartmental propagation. The authors combine two-photon
GCaMP6 imaging of distal SAC varicosities, whole-cell patch-clamp of SACs and DSGCs, pharmacology
(the mGluR2 antagonist LY341495 and agonist LY354740), and mGluR2 knockout mice to show that mGluR2
selectively inhibits N- and P/Q-type voltage-gated calcium channels on SACs. This inhibition
prevents depolarization from a centrifugally stimulated SAC sector from back-propagating into the
opposite, centripetally-stimulated sector.

The functional consequence at the circuit level is that blocking mGluR2 selectively enhances
preferred-direction inhibition onto DSGCs (with a speed-dependent delay), which reduces DSGC firing
at higher motion speeds without affecting firing at lower speeds. The paper therefore directly links
a biophysical mechanism (mGluR2-gated Ca channels controlling trans-somatic signal propagation in
SAC dendrites) to a systems-level computation (broad speed tuning of direction selectivity).

## Architecture, Models and Methods

**Preparations**: Whole-mount retinas from P21-P40 mice. Strains used: mGluR2 knockout
(B6;129S-Grm2tm1Nak/NakRbrc), Chat-IRES-Cre x floxed tdTomato to label SACs, Drd4-GFP to label
posterior-preferring ON-OFF DSGCs. AAV intravitreal injection delivered Cre-dependent GCaMP6m to
SACs for calcium imaging.

**Two-photon calcium imaging**: Ti:sapphire laser at 920 nm, PMT detection with band-pass filters to
separate GCaMP6 emission from OLED visual stimulus. Imaging frame rate 30-50 Hz. ROIs drawn around
distal SAC varicosities (rectangular fields 70-180 x 50-120 um).

**Visual stimulation**: White OLED display (800x600, 60 Hz, 1.1 um/pixel). Full-field bars 220 um x
660 um. Subregion bars 132 um x 660 um over a 132 um circular patch. Default bar speed **440 um/s**;
for speed-dependence experiments bars ranged from 440 to 1760 um/s. Eight pseudorandomized
directions for full-field; two directions (centrifugal and centripetal) for subregion.
Positive-contrast bars on ~600 R*/rod/s background, stimulus ~6.5x10^4 R*/rod/s.

**Direction selectivity index (DSI)**: DSI = (dF_cf - dF_cp) / (dF_cf + dF_cp) for calcium; DSI = (P
\- N) / (P + N) for DSGC IPSCs where P and N are preferred and null peak amplitude or charge
transfer.

**Whole-cell electrophysiology**: Multiclamp 700B, 10 kHz digitization, 4 kHz low-pass filter, 2.5-4
MOhm pipettes. For SAC voltage-clamp of Ca currents: Cs-based internal (110 mM CsMeSO4, 2.8 mM NaCl,
4 mM EGTA, 5 mM TEA-Cl, 4 mM ATP, 0.3 mM GTP, 20 mM HEPES, 10 mM phosphocreatine, 5 mM QX314, pH
7.25). For K-current recordings, CsMeSO4 replaced by 110 mM KMeSO4 and TEA-Cl omitted. Synaptic
blockers during SAC recordings: 8 uM DHbE, 50 uM D-AP5, 50 uM DNQX, 5 uM L-AP4. DSGC IPSCs isolated
by holding at 0 mV. Bath temperature 32-33 C for light-evoked recordings. Series resistance
monitored; cells discarded if Rs changed by >20% or exceeded 40 MOhm.

**Pharmacology**: 50-100 nM LY341495 (mGluR2 antagonist) for light responses; 3 uM LY341495 for
direct SAC recordings; 500 nM-1 uM LY354740 (mGluR2 agonist); 300 uM CdCl2 (non-selective Ca
blocker); 1 uM omega-conotoxin GVIA (CTX, N-type); 250 nM omega-agatoxin IVA (AgTX, P/Q-type).

**Statistics**: Wilcoxon signed-rank for paired samples; ANOVA with Tukey or paired t-test post-hoc;
repeated-measures ANOVA for current-voltage relationships. Significance at p < 0.05. Sample size
reported per figure; ns given as number of cells (averaged across varicosities within a cell).

## Results

* Restricting motion to the imaged dendritic sector preserves centrifugal preference but reduces the
  centrifugal calcium peak significantly versus full-field stimulation (ANOVA **p < 0.0001**;
  full-field vs subregion 2 Tukey **p = 0.0037**).
* Onset of the centrifugal calcium response occurs when the bar reaches the **proximal** dendrites
  during full-field motion but only when it reaches the **distal tips** during local sector
  stimulation (ANOVA **p < 0.0001**; full field vs subregion 2 **p = 0.001**).
* Stimulating the perisomatic proximal 60% of all sectors or the opposite distal sector produces
  centrifugal responses as large as full-field stimulation, demonstrating trans-somatic signal
  integration.
* Stimulus restricted to the distal 60% of the opposite sector evokes suprathreshold transients in
  the imaged sector in only **55% of trials in the centrifugal direction** and **17% of trials in
  the centripetal direction**, showing electrotonic isolation attenuates but does not fully abolish
  trans-somatic propagation.
* mGluR2 antagonist LY341495 selectively **increases** the full-field centripetal-direction calcium
  response in distal SAC varicosities while leaving the centrifugal response unchanged; this reduces
  SAC dendritic DSI.
* LY341495 has **no effect** on direction-selective calcium responses during local (within-sector)
  stimulation, indicating mGluR2 does not alter local dendritic processing.
* mGluR2 agonist LY354740 reversibly inhibits the Ca-channel-mediated inward transient evoked by
  depolarization to 0 mV. Co-application of CTX + AgTX or CdCl2 abolishes the transient and the
  LY354740 effect, identifying N- and P/Q-type voltage-gated Ca channels as the targets.
* LY354740 further reduces the CTX-insensitive and AgTX-insensitive residual transients, confirming
  mGluR2 inhibits **both** N-type and P/Q-type channels. LY354740 does **not** affect K-current in
  SACs (Kv3-mediated outward currents are unchanged).
* In DSGCs, LY341495 produces an enhanced, delayed preferred-direction IPSC. Delay is **289 +/- 39
  ms** at a bar speed of **440 um/s** and **147 +/- 20 ms** at **1100 um/s** (corresponding to ~1
  and ~1.3 SAC dendritic radii respectively, consistent with trans-somatic propagation).
* Null-direction IPSCs are unchanged by LY341495 (centrifugal responses saturated), so DSGC
  inhibition DSI decreases.
* DSGC firing rate is **reduced** by LY341495 at a bar speed of **1100 um/s** but not at **440
  um/s**, and the reduction grows monotonically for speeds between **440 and 1760 um/s**, a
  speed-dependent effect driven by the temporal overlap between enhanced IPSCs and excitatory drive.
* At 440 um/s, the LY341495-induced IPSC increase begins after **~70% of EPSC charge transfer** and
  **~77% of DSGC spiking** have already occurred; at 1100 um/s, after only **~49% of EPSC** and
  **~59% of spiking**.
* LY341495 has no effect on DSGC firing in mGluR2 KO mice, nor on alpha RGC IPSCs; controls confirm
  that the pharmacology is specific to SAC-mediated signaling.

## Innovations

### Experimental Demonstration of Trans-Somatic Integration in SAC Dendrites

First direct experimental evidence that the centrifugal direction selectivity of SAC distal
dendrites during full-field motion depends not only on local within-sector processing but also on
signal propagation from dendrites extending across the soma. This refines the prevailing
"single-sector-as-independent-unit" model of SAC computation.

### Identification of mGluR2-Gated VGCC as the Isolation Mechanism

First identification of a specific molecular mechanism (mGluR2 modulating N- and P/Q-type
voltage-gated Ca channels) that dynamically tunes the electrotonic balance between isolation and
propagation in SAC dendrites. Prior candidates (Kv3 channels, Cl transporters) are shown to not be
the primary mechanism.

### Speed-Dependent Circuit-Level Consequence

Links the SAC-level biophysical mechanism to a DSGC-level computational outcome: mGluR2-mediated
compartmentalization contributes specifically to DSGC direction selectivity at **high motion
speeds**, which broadens the tunable speed range of the direction-selective circuit. Previously this
speed-tuning dimension was not mechanistically connected to SAC dendritic biophysics.

### Knockout + Pharmacology + Imaging + Patch-Clamp Cross-Validation

Methodologically, the paper combines SAC-targeted GCaMP6 imaging, DSGC voltage-clamp IPSC and EPSC
recording, DSGC cell-attached spiking recording, SAC voltage-clamp of VGCCs, and mGluR2 KO controls
to rule out off-target effects of LY341495. This multi-level validation is rare in the retinal-DS
literature.

## Datasets

This is a primary experimental paper. No external datasets are released. The custom MATLAB scripts
used for visual stimulation and data analysis are available from the lead contact (Wei Wei,
University of Chicago) on request. The animal strains used (mGluR2 KO, Chat-IRES-Cre, floxed
tdTomato, Drd4-GFP) are all available from Jackson Laboratory or collaborators named in the paper.
No publicly accessible raw data repository is cited.

## Main Ideas

* For a compartmental model of an ON-OFF DSGC, the SAC presynaptic machinery should not be treated
  as a collection of independent sectors: **trans-somatic propagation** between SAC dendritic
  sectors materially shapes the timing and amplitude of GABAergic inhibition onto DSGCs and
  therefore the target angle-to-AP-frequency tuning curve.
* **Voltage-gated N- and P/Q-type Ca channels** in SAC dendrites (regulated by mGluR2) are a
  biophysical substrate for tunable electrotonic isolation. If the project ever extends from the
  DSGC to the upstream SAC, these channels must be included in the compartmental model; within-DSGC
  SAC effects appear at the synaptic-input level as speed-dependent IPSC delay and amplitude.
* The reported preferred-direction IPSC onto DSGCs has a **speed-dependent latency** of ~290 ms at
  440 um/s falling to ~150 ms at 1100 um/s, with a spatial offset of ~1 SAC dendritic radius (~127
  um); this offers a quantitative constraint for the IPSC waveform and timing parameters used in the
  project's synaptic input model.
* The paper reinforces that DSGC spiking is highly sensitive to the **temporal overlap** of
  excitation and inhibition, supporting RQ3 (AMPA/GABA ratio and spatial distribution) and the need
  to parameterise IPSC kinetics and latency explicitly rather than collapsing inhibition into a
  single amplitude.
* Confirms that **saturation of null-direction inhibition** is a robust feature of the DS circuit;
  compartmental model optimisation should expect that degradation of directional tuning at high
  speeds will be easier to produce than at low speeds.

## Summary

Koren, Grove, and Wei address a gap in the mechanistic understanding of retinal direction
selectivity: how the starburst amacrine cell (SAC) maintains the required balance between
electrotonic isolation and cross-compartmental signal integration in its dendrites, and how that
balance is regulated and coupled to direction-selective ganglion cell (DSGC) output. Earlier work
established that SAC dendritic sectors are semi-independent computational units with centrifugal
preference, but the mechanisms controlling the "semi" part of that isolation were unknown.

Methodologically the paper combines two-photon GCaMP6 imaging of distal SAC varicosities, whole-cell
patch-clamp of SACs and DSGCs, subregion visual stimulation to dissociate local from global
dendritic activation, a selective pharmacology (LY341495 antagonist and LY354740 agonist) for
mGluR2, and mGluR2 knockout mice as an off-target control. Voltage-gated calcium channel subtypes
are identified with omega-conotoxin GVIA (N-type) and omega-agatoxin IVA (P/Q-type).

The central findings are that (i) the strong centrifugal response of distal SAC varicosities during
full-field motion is partly produced by trans-somatic signal integration from the opposite side of
the dendritic tree; (ii) mGluR2 signaling inhibits N- and P/Q-type VGCCs on SACs to enforce
sufficient electrotonic isolation during centripetal motion; (iii) blocking mGluR2 selectively
enhances preferred-direction IPSCs onto DSGCs (delay **289 ms at 440 um/s**, **147 ms at 1100
um/s**); and (iv) this aberrant inhibition reduces DSGC spiking specifically at high motion speeds,
contributing to the broad speed tuning of the direction-selective circuit.

For this project's goal of a compartmental DSGC model that matches a target angle-to-AP-frequency
curve, the paper has two concrete implications. First, the IPSC input model on the DSGC must reflect
speed-dependent latency and amplitude arising from SAC trans-somatic propagation rather than a
speed-invariant null-direction inhibition. Second, the saturation of centrifugal SAC calcium signals
and null-direction DSGC IPSCs, even under strong pharmacological perturbation, suggests that the
target tuning curve can be reproduced with a degenerate set of Na/K conductance combinations (RQ1
"ridge" hypothesis), because upstream inhibition is the first-order constraint on firing at
preferred direction and any well-chosen conductance combination that preserves somatic excitability
will suffice. Active dendritic conductances in the DSGC (RQ4) can be evaluated against this
framework, but the primary directional signal arrives pre-shaped by SAC compartmental computation,
not generated locally in the DSGC dendrites.
