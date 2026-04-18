# Electrophysiological Basis of Retinal Direction Selectivity

## Goal

Investigate how the internal electrophysiological properties of a single neuron shape its
direction-selective function. Using a compartmental model of a direction-selective retinal ganglion
cell, vary morphology, synaptic input density (AMPA and GABA), EPSP and IPSP amplitude and kinetics,
combinations of somatic voltage-gated sodium and potassium conductances, and the presence or absence
of voltage-gated conductances in the dendrites, then optimise these parameters against a target
relationship between the angle of a spreading excitatory/inhibitory wave and the cell's action
potential (AP) frequency.

## Scope

### In Scope

* Single-cell compartmental simulation (NEURON or equivalent) of a direction-selective retinal
  ganglion cell
* Parametric variation of morphology, input density, EPSP and IPSP amplitude and kinetics, and
  combinations of voltage-gated sodium and potassium conductances
* Comparison of active vs passive dendrites (presence or absence of voltage-gated conductances in
  the dendritic tree)
* Wave stimulus protocols that sweep excitatory and inhibitory activation across the dendritic arbor
  at controlled angles
* Optimisation of the Na/K conductance combination to match a target angle-to-AP-frequency tuning
  curve
* In vitro patch-clamp data as validation ground truth

### Out of Scope

* Synaptic plasticity, learning, and developmental changes
* In vivo electrophysiological recordings (only patch-clamp data are acceptable)
* Network-level simulations beyond the single target cell
* Non-retinal direction-selective systems (visual cortex, vestibular, etc.)

## Research Questions

1. Which combinations of somatic voltage-gated sodium and potassium conductances maximise AP
   frequency for a preferred-direction wave while suppressing firing in the null direction?
2. How sensitive is directional AP tuning to morphological parameters such as dendritic branching
   pattern and compartment length and diameter?
3. What effect do the ratio and spatial distribution of AMPA vs GABA input density have on the
   sharpness of directional tuning?
4. Do active dendritic voltage-gated conductances improve, degrade, or have no effect on the match
   to the target angle-frequency curve compared with passive dendrites?
5. How closely can the optimised single-cell model reproduce the target tuning curve, and what
   residual error remains?

## Success Criteria

* A modifiable compartmental model in which morphology, input density, EPSP and IPSP amplitude and
  dynamics, somatic Na/K conductances, and dendritic active conductances can each be varied
  independently
* Identification of a Na/K conductance combination that reproduces the target angle-to-AP-frequency
  relationship within a defined error tolerance
* Systematic comparison of active vs passive dendritic configurations on directional tuning
  sharpness
* Reproducible simulation pipeline (seedable, scripted) that runs end-to-end on the researcher's
  local machine

## Key References

* Barlow & Levick (1965) — "The mechanism of directionally selective units in rabbit's retina", *J
  Physiol* (foundational paper defining retinal direction selectivity)
* Hines & Carnevale (1997) — "The NEURON Simulation Environment", *Neural Computation* (canonical
  reference for the simulator used in this project)
* Vaney, Sivyer & Taylor (2012) — "Direction selectivity in the retina: symmetry and asymmetry in
  structure and function", *Nature Reviews Neuroscience* (standard review of DS mechanisms)
* Poleg-Polsky & Diamond (2016) — multi-compartmental NEURON model of an ON-OFF DSGC with
  distributed excitatory and inhibitory inputs (directly matches this project's modelling approach)
* Oesch, Euler & Taylor (2005) — "Direction-selective dendritic action potentials in rabbit
  retina", *Neuron* (evidence for the functional role of active dendritic conductances in DSGCs)
* Branco, Clark & Häusser (2010) — "Dendritic Discrimination of Temporal Input Sequences in
  Cortical Neurons", *Science* (cable-theory account of sequence-direction selectivity via dendritic
  impedance gradients and NMDA-receptor nonlinearities)

## Current Phase

The project is just starting. The next step is a literature survey of compartmental models of
direction-selective retinal ganglion cells, together with selection of a published morphology and a
target angle-to-AP-frequency tuning curve to use as the optimisation reference.
