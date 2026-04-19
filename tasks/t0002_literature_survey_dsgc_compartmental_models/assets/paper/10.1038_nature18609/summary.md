---
spec_version: "3"
paper_id: "10.1038_nature18609"
citation_key: "Ding2016"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# Species-specific wiring for direction selectivity in the mammalian retina

## Metadata

* **File**: `files/ding_2016_ds-network.xml`
* **Published**: 2016
* **Authors**: Huayu Ding (US), Robert G. Smith (US), Alon Poleg-Polsky (US), Jeffrey S. Diamond
  (US), Kevin L. Briggman (DE)
* **Venue**: Nature, vol. 535, pp. 105-110
* **DOI**: `10.1038/nature18609`

## Abstract

Directionally tuned signaling in starburst amacrine cell (SAC) dendrites lies at the heart of the
direction selective (DS) circuit in the mammalian retina. The relative contributions of intrinsic
cellular properties and network connectivity to SAC DS remain unclear. We present a detailed
connectomic reconstruction of SAC circuitry in mouse retina and describe previously unknown features
of synapse distributions along SAC dendrites: 1) input and output synapses are segregated, with
inputs restricted to proximal dendrites; 2) the distribution of inhibitory inputs is fundamentally
different from that observed in rabbit retina. An anatomically constrained SAC network model
suggests that SAC-SAC wiring differences between mouse and rabbit retina underlie distinct
contributions of synaptic inhibition to velocity and contrast tuning and receptive field structure.
In particular, the model indicates that mouse connectivity enables SACs to encode lower linear
velocities that account for smaller eye diameter, thereby conserving angular velocity tuning.

## Overview

Ding et al. (2016) address a fundamental gap in understanding the direction-selective (DS) circuit
of the mammalian retina: the precise synaptic wiring of starburst amacrine cells (SACs) and how this
wiring differs across species. Using serial block-face scanning electron microscopy (SBEM) on an
adult mouse retina, they produced a dense connectomic reconstruction of four SACs (two ON, two OFF)
along with their presynaptic partners. The key anatomical finding is that inhibitory (SAC-SAC)
inputs are confined to the proximal third of SAC dendrites in mouse, whereas in rabbit retina they
arrive along the distal dendrites. Ribbon-type excitatory (bipolar cell) inputs are distributed
across the proximal two-thirds, leaving the distal third as the exclusive output zone.

To interpret these anatomical differences functionally, the authors built an anatomically
constrained network model of seven interacting SACs using the Neuron-C simulation language. The
model incorporates realistic dendritic morphology, measured dendritic diameters, and active membrane
conductances. By comparing mouse-like (proximal inhibition, 145 um inter-soma spacing) and
rabbit-like (distal inhibition, 200 um inter-soma spacing) configurations, the paper shows that the
locus of inhibitory input governs velocity tuning: mouse SACs remain DS down to ~100 um/s linear
velocity, whereas the rabbit model degrades at low velocities. This difference is explained by the
five-fold difference in eye diameter: the same angular velocity corresponds to a five-fold lower
linear velocity on the mouse retina, and the proximal-inhibition wiring compensates.

Calcium imaging of ChAT-tdTomato mouse SAC dendrites loaded with OGB1 confirmed the model velocity
tuning predictions. Experiments with the GABA-A antagonist SR95531 confirmed that SAC-SAC inhibition
is required for DS at high contrast and for DS in response to centrally restricted (bulls-eye)
stimuli. The study establishes that subtle shifts in synapse location along a dendrite can adapt an
entire DS circuit to species-specific visual demands.

## Architecture, Models and Methods

**Connectomics.** A 50 x 210 x 260 um^3 SBEM volume was acquired from an adult C57BL/6 mouse (P30)
retina at 13.2 x 13.2 x 26 nm voxel resolution (10,112 consecutive sections, ~110 pA beam current at
2 keV). Skeletons and synapses were annotated manually in KNOSSOS. One ON-OFF DSGC and four SACs
(two ON, two OFF) were fully reconstructed. Input synapse types (ribbon = excitatory, conventional =
inhibitory) and output synapse locations were recorded as fractional radial distance from soma.

**Bipolar cell classification.** OFF BC types (BC1, BC2, BC3a, BC3b, BC4) and ON BC types (BC7,
BC5o, BC5t, BC5i) were classified by IPL stratification depth and axonal arborisation area. Synapse
counts per BC type per SAC were tabulated (mean +/- SD).

**SAC anti-parallel wiring analysis.** Relative angles between pre- and postsynaptic SAC dendrites
at each inhibitory synapse were measured. Skew toward anti-parallel (180 deg) wiring was confirmed
with the Kolmogorov-Smirnov test (p = 2 x 10^-53 for OFF SACs).

**Neuron-C network model.** A 7-SAC network model was built in Neuron-C (Smith lab, University of
Pennsylvania). A digitized SAC morphology with multiplicative diameter factors from EM measurements
was used. Membrane conductances: NaV1.8 (3e-3 S/cm^2 in medial and distal thirds), Kdr (3e-3 S/cm^2
soma, 2e-3 in all thirds), L-type Ca^2+ (1e-3 S/cm^2 medial and distal thirds). Passive parameters:
Rm = 10,000 Ohm-cm^2, Ri = 75 Ohm-cm. Each central SAC received ~120-250 inhibitory synapses.
Excitatory synaptic conductances: ~230 pS; inhibitory: 80-160 pS. BC inputs modeled as
voltage-clamped presynaptic compartments. Models ran on 220 AMD Opteron 3.2 GHz CPU cores; each
7-SAC simulation took 4-48 h. DSI = (PD - ND)/PD using distal dendritic calcium concentration.

**Mouse vs. rabbit comparison.** Inter-soma distance: 145 um (mouse, proximal contacts) vs. 200 um
(rabbit, distal contacts). Velocity tuning tested over 30-2000 um/s linear velocities.

**Two-photon calcium imaging.** ChAT-tdTomato mice (P30-P60), both sexes; OGB1 loaded by
sharp-electrode iontophoresis. Imaging: 80 x 80 um field, 256 x 100 px, 10 Hz frame rate, 920 nm
Ti:sapphire excitation. Bar stimuli (400 x 400 um) swept in 8 directions at 30-2000 um/s. Bulls-eye
stimuli matched to SAC arbor size. Responses averaged over 3-5 repeats. SR95531 (25 uM) used to
block GABA-A receptors. Calcium DSI = (PD - ND)/ND. Paired t-tests for pharmacology comparisons.

## Results

* In mouse SAC dendrites, inhibitory (SAC-SAC) inputs are **restricted to the proximal third** of
  the dendritic tree, whereas in rabbit they arrive along the distal dendrites -- a fundamental
  species difference in DS circuit wiring.
* Anti-parallel SAC-SAC wiring is strongly preferred: relative-angle distribution was significantly
  skewed toward 180 deg (KS test p = **2 x 10^-53** for OFF SACs).
* The 7-SAC model remained DS at linear velocities down to **~100 um/s** with mouse-like proximal
  inhibition, versus degraded DS at low velocities in the rabbit-like (200 um inter-soma, distal)
  model.
* A 10 deg/s angular velocity corresponds to **1500 um/s** on rabbit retina vs. **300 um/s** on
  mouse retina; proximal mouse wiring compensates for the five-fold smaller eye diameter.
* Redistributing BC inputs uniformly along SAC dendrites (overlapping with output zone) **reversed
  direction preference** from CF to CP in the model.
* Blocking SAC-SAC inhibition with SR95531 (25 uM) significantly reduced DSI at **300% contrast**,
  confirming that inhibition expands contrast tuning range.
* SR95531 also significantly reduced DS to centrally restricted bulls-eye stimuli, confirming that
  proximal inhibition underlies **central receptive field DS** in mouse.
* Full model biophysical parameters: NaV1.8 density **3e-3 S/cm^2** in medial/distal thirds; Kdr
  **3e-3 S/cm^2** at soma; L-type Ca^2+ **1e-3 S/cm^2** in medial/distal thirds.

## Innovations

### Cross-Species Connectomic Comparison

First dense SBEM reconstruction of mouse SAC circuitry revealing that inhibitory SAC-SAC inputs
arrive exclusively on proximal dendrites -- opposite to the distal-input organisation in rabbit.
This species comparison directly links a specific wiring location to a functional velocity-tuning
consequence and serves as a template for anatomically constrained DS circuit modeling.

### Anatomically Constrained 7-SAC Network Model in Neuron-C

An anatomically grounded network model (7 SACs, ~120-250 inhibitory synapses per cell, measured
dendritic diameters, active conductances) predicts velocity tuning, contrast range, and receptive
field DS from first principles. One of the first studies to use dense EM-derived connectivity to
parameterise a biophysically detailed multi-compartmental SAC model with all parameters fully
tabulated.

### Velocity Tuning as an Adaptive Property of Wiring Geometry

Demonstrates that the locus of inhibitory input (proximal vs. distal) determines the minimum linear
velocity at which a SAC can be DS, linking eye diameter to a specific synaptic design rule and
providing a general framework for cross-species DS circuit adaptation.

### Proximal-Inhibition Mechanism for Central Receptive Field DS

Shows that in mouse, unlike rabbit, DS for centrally restricted stimuli depends on network
inhibition rather than intrinsic dendritic conductances alone, because SAC-SAC synapses are proximal
enough to be activated by local stimuli.

## Datasets

* **SBEM retinal volume (k0725)**: one adult C57BL/6 mouse (P30); 50 x 210 x 260 um^3; 13.2 nm x
  13.2 nm x 26 nm voxels; 10,112 sections. Model code available at
  `ftp://retina.anatomy.upenn.edu/pub/rob/nc.tgz`.
* **SAC morphology for modeling**: digitized confocal stack of a labeled mouse SAC; distributed with
  the Neuron-C model code.
* **Calcium imaging data**: two-photon OGB1 recordings from ChAT-tdTomato adult mice (P30-P60), both
  sexes; not deposited in a public repository.
* **Rabbit SAC anatomy**: digitised from Famiglietti (1991) figure 15; not a new dataset.

## Main Ideas

* Segregation of excitatory inputs (proximal two-thirds) from inhibitory outputs (distal third)
  along SAC dendrites is critical for CF direction preference; placing excitation near the output
  zone abolishes DS. In any compartmental DSGC model incorporating SAC-derived inhibition, AMPA vs.
  GABA spatial placement must respect this segregation.
* A shift in where inhibitory synapses land (proximal vs. distal) fundamentally changes velocity
  tuning bandwidth. Spatial placement of GABA inputs in a compartmental DSGC model matters as much
  as total conductance magnitude.
* Species differences (mouse vs. rabbit) yield quantitatively distinct optimal wiring; models
  calibrated to rabbit physiology cannot be directly applied to mouse DSGC models.
* Active conductances in SAC dendrites (NaV1.8, Kdr, L-type Ca^2+) are necessary for intrinsic DS;
  the tabulated parameter values can seed a starting point for a compartmental DSGC model.
* SAC-SAC inhibition expands contrast tuning range; removing it causes saturation at high contrast,
  relevant for parameterising inhibitory conductance strength in DSGC models.

## Summary

Ding et al. use serial block-face EM to reconstruct the complete synaptic wiring of four starburst
amacrine cells in mouse retina and compare it with the previously characterised rabbit circuit. The
central finding is that mouse SACs receive inhibitory SAC-SAC inputs exclusively on their proximal
dendrites, whereas rabbit SACs receive them distally. The study is motivated by the need to
understand which circuit features -- intrinsic or network-based -- account for direction selectivity
of SAC dendrites, and whether that organisation varies across species.

To interpret the anatomy, the authors construct a 7-SAC network model in Neuron-C with anatomically
measured dendritic diameters, biophysically grounded active conductances (NaV1.8, Kdr, L-type
Ca^2+), and synapse placements derived from the EM data. Mouse-like (proximal inhibition, 145 um
inter-soma spacing) and rabbit-like (distal inhibition, 200 um spacing) configurations are compared
over stimulus velocities 30-2000 um/s. Two-photon calcium imaging and SR95531 pharmacology confirm
the model predictions in vitro.

Key quantitative results: the mouse model remains DS down to ~100 um/s linear velocity, matching the
smaller mouse eye (3 mm axial diameter, ~30 um/deg) to conserve angular velocity tuning.
Distributing BC inputs uniformly reverses direction preference in the model. SAC-SAC inhibition is
necessary for DS at high contrast (300%) and for DS to centrally restricted stimuli in mouse. Full
biophysical parameters (Rm = 10,000 Ohm-cm^2, Ri = 75 Ohm-cm, NaV1.8/Kdr/Ca^2+ densities per
dendritic zone) are tabulated and distributed with the model code.

For this project, Ding et al. (2016) provides three concrete resources: (1) a fully described
multi-compartmental DS circuit model with biophysical parameters and DSI protocol that can directly
inform DSGC model parameterisation; (2) a design principle -- restrict excitatory inputs to proximal
zones away from the output zone -- guiding AMPA vs. GABA placement in the DSGC dendritic model; and
(3) mouse-specific synaptic geometry (inhibitory inputs at proximal third, excitatory at proximal
two-thirds) to validate against when choosing GABA input distributions in the project compartmental
DSGC model.
