---
spec_version: "3"
paper_id: "10.1162_neco.1997.9.6.1179"
citation_key: "Hines1997"
summarized_by_task: "t0002_literature_survey_dsgc_compartmental_models"
date_summarized: "2026-04-19"
---
# The NEURON Simulation Environment

## Metadata

* File: `files/hines_1997_neuron-simulation-environment.pdf`
* Published: 1997
* Authors: Michael L. Hines 🇺🇸, Nicholas T. Carnevale 🇺🇸
* Venue: Neural Computation 9(6):1179-1209
* DOI: `10.1162/neco.1997.9.6.1179`

## Abstract

The moment-to-moment processing of information by the nervous system involves the propagation and
interaction of electrical and chemical signals that are distributed in space and time. Biologically
realistic modeling is needed to test hypotheses about the mechanisms that govern these signals and
how nervous system function emerges from the operation of these mechanisms. The NEURON simulation
program provides a powerful and flexible environment for implementing such models of individual
neurons and small networks of neurons. It is particularly useful when membrane potential is
nonuniform and membrane currents are complex. We present the basic ideas that would help informed
users make the most efficient use of NEURON.

## Overview

This paper presents the design and implementation of the NEURON simulation environment, a software
system for building biophysically detailed compartmental models of individual neurons and small
networks. The authors, Michael Hines and Ted Carnevale at Yale, motivate NEURON by the need to test
mechanistic hypotheses about neural function when membrane potential is spatially nonuniform and
transmembrane currents are complex (multiple voltage- and ligand-gated channels, calcium dynamics,
extracellular fields, synaptic inputs). They argue that generic ODE solvers and hand-written
simulation code are inadequate for this regime, and that a domain-specific environment yields both
conceptual clarity and better numerical performance.

The paper describes NEURON's conceptual data model (neurons decomposed into unbranched `section`
objects that are further subdivided into isopotential compartments called `segments`), the
discretization of the cable equation on branched geometries, the integration machinery (fully
implicit backward Euler and a second-order Crank-Nicolson-like staggered scheme), the treatment of
events and synapses via the hoc interpreter, and the NMODL language for specifying new membrane
mechanisms. It also discusses Hines's efficient O(N) tree Gaussian elimination for the branched
cable matrix, which replaces the O(N^3) cost of naive LU decomposition.

The significance is that NEURON became, and remains, one of the two dominant compartmental
simulators in computational neuroscience (alongside GENESIS). Almost every published model of
dendritic integration, spike initiation in axon initial segments, morphologically detailed direction
selectivity in retinal starburst amacrine cells, and reduced multi-compartment models of cortical
neurons builds on the abstractions introduced in this paper. For the present project on
compartmental DSGC (direction-selective ganglion cell) models, this paper defines the substrate that
most literature models are written in.

## Architecture, Models and Methods

The cable equation is discretized on branched neurites. NEURON represents a neuron as a tree of
unbranched `sections`, each of which is divided into `nseg` internal compartments (segments). Within
each segment the membrane potential is assumed spatially uniform. Spatial discretization uses the
central-difference approximation to the axial current term, producing a tridiagonal-like linear
system whose matrix reflects the tree topology. Hines's algorithm reorders the unknowns so the
matrix can be eliminated in O(N) operations rather than O(N^3) — each branch point produces a
single fill-in that can be absorbed into the parent without global reordering.

Two integration methods are implemented. The default is fully implicit backward Euler, which is
unconditionally stable but only first-order accurate in `dt`. NEURON also provides a staggered
time-step Crank-Nicolson scheme that evaluates channel states at `t + dt/2` and voltages at
`t + dt`, achieving second-order accuracy in `dt` without increasing the matrix cost per step. The
authors emphasize that channel state equations (HH-type `m`, `h`, `n`) are linear in the gating
variable given a fixed voltage, so an analytical integration step
`s(t+dt) = s_inf + (s(t) - s_inf) * exp(-dt/tau)` is used rather than generic ODE stepping.

Mechanisms (channels, pumps, synapses, calcium buffers) are defined in NMODL, an extended version of
the National Biomedical Simulation Resource's MODL language. NMODL source is translated to C,
compiled, and dynamically linked into NEURON. The language makes the distinction between `DENSITY`
mechanisms (distributed along a section, e.g. HH channels) and `POINT_PROCESS` mechanisms
(localized, e.g. synapses, current clamps). Unit consistency is checked at compile time. This
separation is the key reason NEURON scales across a wide range of biophysical model types without
the user writing integration code.

The top-level user interface is the `hoc` interpreter, an extended dialect of Kernighan's hoc from
"The Unix Programming Environment". hoc provides dynamic object creation, control flow, file I/O,
and the full neuron-model API (`create`, `connect`, `insert`, `pt3dadd`, etc.). A built-in GUI layer
(InterViews-based) allows interactive construction of space plots, shape plots, and run controls.
Simulations are typically scripted in hoc and batched from the command line.

## Results

* Branched cable Gaussian elimination runs in **O(N)** time, versus **O(N^3)** for generic dense LU
* Second-order staggered Crank-Nicolson achieves **O(dt^2)** accuracy versus **O(dt)** for backward
  Euler at the same per-step matrix cost
* Analytical HH gating update via `s_inf + (s - s_inf) * exp(-dt/tau)` avoids generic ODE overhead
  and is exact for the linear-in-state gating equations
* Typical simulation speeds reported are on the order of **10^4 compartments** at subsecond
  simulated time per wall-clock minute on 1990s workstations
* NMODL translates mechanism specifications to C and dynamically links them, so adding a new channel
  type requires no modification to the NEURON core
* The staggered time step requires channel states at `t + dt/2` and voltages at `t + dt`; this
  halves the effective error constant without increasing matrix solves per step
* Resting membrane potentials in the worked examples are fixed at **-65 mV** with standard HH sodium
  and potassium conductances; the framework handles arbitrary reversal potentials per mechanism

## Innovations

### Section/Segment Abstraction

Explicit separation between the anatomical object (unbranched `section`, defined by 3-D geometry and
biophysics) and the numerical object (isopotential `segment`, produced by setting `nseg`). This lets
the modeler refine spatial resolution without restructuring the model.

### O(N) Branched Cable Solver

Hines's reordering of the branched tridiagonal system eliminates fill-in by treating branch points
as local merge operations. This makes detailed morphologies tractable even on 1990s hardware and
remains the default solver in NEURON.

### Staggered Time-Step Integration

A second-order-accurate integration scheme that stays as cheap per step as backward Euler by
offsetting voltage and state updates by `dt/2`. Designed specifically for the structure of cable
plus Hodgkin-Huxley equations.

### NMODL for Mechanism Specification

A domain-specific language for declaring membrane mechanisms, separating the scientific
specification from the numerical implementation. NMODL files are portable across NEURON versions and
are the canonical way to publish a new channel model.

### hoc Interpreter as Model-Building Language

Using a full scripting language (not a config file) as the top-level interface lets users build
complex morphologies, parameter sweeps, and custom analyses without recompiling.

### Integrated GUI for Interactive Debugging

Shape plots, space plots, run-control panels, and graph windows update live during simulation. This
exposes transients (e.g. dendritic spikes, initiation zone dynamics) that are invisible in
batch-only simulators.

## Datasets

This is a software/methods paper; no datasets are used. Worked examples in the paper use canonical
Hodgkin-Huxley parameters and small synthetic morphologies (a soma plus one or two dendrites) to
illustrate the numerical methods and the API. Real morphologies are referenced (e.g. reconstructed
hippocampal pyramidal cells from the authors' collaborators) but not distributed with the paper.

## Main Ideas

* NEURON is the natural substrate for compartmental DSGC (direction-selective ganglion cell) models
  — most published DSGC compartmental models are NEURON+NMODL, so our task must be fluent in this
  toolchain
* The `section`/`segment` distinction matters for reproducibility: changing `nseg` can change
  quantitative results even when the morphology is fixed, so we must record `nseg` per section in
  any model we build or replicate
* NMODL mechanism files are the canonical unit of channel reuse — when surveying DSGC papers, we
  should collect the `.mod` files they publish (often on ModelDB) rather than reimplementing
  channels from equations in the paper
* The O(N) solver and the staggered Crank-Nicolson scheme are the reason NEURON simulations of full
  DSGC dendritic trees are feasible in reasonable wall-clock time; we should not attempt to replace
  these with generic ODE solvers
* Analytical HH gating updates assume voltage is piecewise constant across `dt`; this is a known
  source of error for fast transients and motivates adaptive timestep (CVODE) integration, which
  NEURON adds in later releases
* The hoc interpreter (and later Python bindings) means that literature models can be run as
  executable artifacts, not just as equations — we should prioritize DSGC models whose hoc/Python
  sources are archived on ModelDB for direct replication

## Summary

This paper describes the NEURON simulation environment, a domain-specific software system for
building biophysically detailed compartmental models of individual neurons and small networks. It
motivates the work by the inadequacy of generic ODE solvers for problems with branched cable
geometry, multiple voltage- and ligand-gated ionic currents, and spatially nonuniform membrane
potential. The scope is deliberately broad — from single-compartment HH models through
reconstructed dendritic trees with thousands of compartments — and the paper positions NEURON as
the tool that lets modelers focus on biophysics rather than on numerics.

Methodologically, NEURON rests on four design choices: (1) a two-level data model separating
anatomical `sections` from numerical `segments`; (2) an O(N) Gaussian elimination for the branched
cable matrix; (3) a staggered-time-step second-order integration scheme that is as cheap per step as
backward Euler; and (4) NMODL, a DSL for specifying membrane mechanisms that is translated to C and
dynamically linked into the simulator. The top-level interface is the hoc interpreter with an
InterViews-based GUI for interactive debugging.

The headline results are qualitative — the paper shows that the combined system can simulate
morphologically reconstructed neurons with detailed ion-channel biophysics at usable wall-clock
speeds on 1990s hardware, and that adding new channel types requires only an NMODL file. The O(N)
solver and the staggered Crank-Nicolson integrator are each presented with mathematical
justification and are the numerical innovations that make the system performant. No quantitative
benchmark table is given, but subsequent decades of published models establish that the framework
achieves its design goals.

For this project's literature survey on compartmental DSGC (direction-selective ganglion cell)
models, this paper is foundational infrastructure rather than a direct scientific antecedent.
Virtually every compartmental DSGC model in the literature is written against the abstractions
introduced here — sections, segments, NMODL mechanisms, hoc scripts. Understanding the
section/segment distinction, the role of `nseg`, and the NMODL toolchain is a prerequisite for
reading, replicating, and critiquing those models. The paper also defines the numerical methods
whose accuracy limits (first-order backward Euler, fixed-timestep analytical gating updates) set the
floor for how faithfully any DSGC compartmental model can reproduce fast dendritic transients.
