# Answers (2)

2 answer(s).

**Browse by view**: By category:
[`compartmental-modeling`](by-category/compartmental-modeling.md),
[`dendritic-computation`](by-category/dendritic-computation.md),
[`direction-selectivity`](by-category/direction-selectivity.md),
[`retinal-ganglion-cell`](by-category/retinal-ganglion-cell.md),
[`synaptic-integration`](by-category/synaptic-integration.md),
[`voltage-gated-channels`](by-category/voltage-gated-channels.md); [By date
added](by-date-added/README.md)

---

<details>
<summary><strong>How does the existing peer-reviewed literature on compartmental
models of direction-selective retinal ganglion cells structure the five
project research questions (Na/K conductances, morphology sensitivity,
AMPA/GABA balance, active vs passive dendrites, and angle-to-AP-frequency
tuning curves), and what quantitative targets does it provide?</strong></summary>

**Confidence**: medium

The literature structures the five questions around a small set of quantitative targets that
the project must hit. For Na/K conductances the Fohlmeister-Miller parameter set (peak somatic
g_Na around 0.04-0.10 S/cm^2, delayed-rectifier g_K around 0.012 S/cm^2) is the standard
starting point, and no published paper reports a factorial (g_Na, g_K) grid for DSGCs. For
morphology the asymmetric ON-OFF DSGC dendrite is sharply wired in the null direction through
SAC-mediated inhibition, yet global dendrite shape only minimally changes the synaptic map
while local electrotonic compartments still matter. For AMPA/GABA balance the canonical counts
on a reconstructed mouse DSGC are 177 AMPA and 177 GABA synapses, with null-direction
inhibition running three to five times larger than preferred inhibition. Active dendrites with
Fohlmeister-like channel densities roughly double the direction-selectivity index versus
passive trees, and the target mouse ON-OFF DSGC tuning curve should hit DSI 0.7-0.85,
preferred peak 40-80 Hz, null residual under 10 Hz, and a half-width of 60-90 degrees.

| Field | Value |
|---|---|
| **Full answer** | [`full_answer.md`](../../tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/full_answer.md) |
| **ID** | [`how-does-dsgc-literature-structure-the-five-research-questions`](../../tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/how-does-dsgc-literature-structure-the-five-research-questions/) |
| **Question** | How does the existing peer-reviewed literature on compartmental models of direction-selective retinal ganglion cells structure the five project research questions (Na/K conductances, morphology sensitivity, AMPA/GABA balance, active vs passive dendrites, and angle-to-AP-frequency tuning curves), and what quantitative targets does it provide? |
| **Methods** | `papers`, `internet` |
| **Confidence** | medium |
| **Date created** | 2026-04-18 |
| **Categories** | [`direction-selectivity`](../../meta/categories/direction-selectivity/), [`compartmental-modeling`](../../meta/categories/compartmental-modeling/), [`retinal-ganglion-cell`](../../meta/categories/retinal-ganglion-cell/), [`dendritic-computation`](../../meta/categories/dendritic-computation/), [`synaptic-integration`](../../meta/categories/synaptic-integration/), [`voltage-gated-channels`](../../meta/categories/voltage-gated-channels/) |
| **Paper sources** | `10.1113_jphysiol.1965.sp007638`, `10.1162_neco.1997.9.6.1179`, `10.1038_nrn3165`, `10.1016_j.neuron.2016.02.013`, `10.1016_j.neuron.2005.06.036`, `10.1126_science.1189664`, `10.1371_journal.pcbi.1000899`, `10.1152_jn.00123.2009`, `10.1523_JNEUROSCI.22-17-07712.2002`, `10.1113_jphysiol.2008.161240`, `10.1523_JNEUROSCI.5017-13.2014`, `10.1038_nature09818`, `10.1038_nature18609`, `10.1113_jphysiol.2010.192716`, `10.1002_cne.22678`, `10.1016_j.neuron.2017.07.020`, `10.1523_ENEURO.0261-21.2021`, `10.7554_eLife.52949`, `10.7554_eLife.42392`, `10.1016_j.neuron.2016.04.041` |
| **Task sources** | — |
| **URL sources** | — |
| **Created by** | [`t0002_literature_survey_dsgc_compartmental_models`](../../overview/tasks/task_pages/t0002_literature_survey_dsgc_compartmental_models.md) |

</details>

<details>
<summary><strong>Which compartmental simulator should the direction-selective
ganglion cell (DSGC) project use as its primary simulator, and which should
it keep as a backup?</strong></summary>

**Confidence**: high

Use NEURON 8.2.7 as the primary simulator, wrapped with NetPyNE 1.1.1 for parameter sweeps and
optimisation. Keep Arbor 0.12.0 as the backup simulator to exploit its 7-12x single-cell
speedup whenever the parameter sweep outgrows the NEURON workstation budget. Brian2 and MOOSE
are rejected because Brian2's own authors describe its multicompartment support as immature
and MOOSE shows the weakest maintenance signal of the five candidates.

| Field | Value |
|---|---|
| **Full answer** | [`full_answer.md`](../../tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md) |
| **ID** | [`dsgc-compartmental-simulator-choice`](../../tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/) |
| **Question** | Which compartmental simulator should the direction-selective ganglion cell (DSGC) project use as its primary simulator, and which should it keep as a backup? |
| **Methods** | `internet` |
| **Confidence** | high |
| **Date created** | 2026-04-19 |
| **Categories** | [`compartmental-modeling`](../../meta/categories/compartmental-modeling/), [`retinal-ganglion-cell`](../../meta/categories/retinal-ganglion-cell/) |
| **Paper sources** | — |
| **Task sources** | — |
| **URL sources** | [url 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC9272742/), [url 2](https://elifesciences.org/articles/47314), [url 3](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013926), [url 4](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000899), [url 5](https://modeldb.science/189347), [url 6](https://github.com/neuronsimulator/nrn/blob/master/docs/changelog.md), [url 7](https://github.com/neuronsimulator/nrn/issues/3595), [url 8](https://github.com/arbor-sim/arbor/releases), [url 9](https://docs.arbor-sim.org/en/latest/install/python.html), [url 10](https://docs.arbor-sim.org/en/latest/index.html), [url 11](https://docs.arbor-sim.org/en/latest/fileformat/nmodl.html), [url 12](http://doc.netpyne.org/), [url 13](https://github.com/suny-downstate-medical-center/netpyne), [url 14](https://brian2.readthedocs.io/en/stable/user/multicompartmental.html), [url 15](https://github.com/brian-team/brian2), [url 16](https://github.com/BhallaLab/moose), [url 17](https://github.com/BhallaLab/moose/releases), [url 18](https://moose.ncbs.res.in/readthedocs/user/py/rdesigneur/rdes.html), [url 19](https://github.com/jzlab/dsg), [url 20](https://github.com/berenslab/rgc_dendrites) |
| **Created by** | [`t0003_simulator_library_survey`](../../overview/tasks/task_pages/t0003_simulator_library_survey.md) |

</details>
