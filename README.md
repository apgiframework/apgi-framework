# APGI Framework

**Allostatic Precision-Gated Ignition** — a computational framework for consciousness research.

[![CI](https://github.com/apgiframework/apgi-framework/actions/workflows/test.yml/badge.svg)](https://github.com/apgiframework/apgi-framework/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21632264.svg)](https://doi.org/10.5281/zenodo.21632264)
[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)
[![OSF](https://img.shields.io/badge/OSF-t5hcq-1284c5.svg)](https://osf.io/t5hcq)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--0328--2896-a6ce39.svg)](https://orcid.org/0009-0005-0328-2896)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/apgiframework/apgi-framework/HEAD?labpath=notebooks%2Fquick_start.ipynb)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/apgiframework/apgi-framework/blob/main/notebooks/quick_start.ipynb)

## Manuscript

> **Pesochin, D.** ([0009-0005-0328-2896](https://orcid.org/0009-0005-0328-2896)) **(2026).** Allostatic Precision-Gated Ignition: A Computational Framework for Consciousness. *Manuscript under review.*  
> Preprint: [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)

This repository is the companion code release for the paper series above.
Figure scripts are in `figures/` (current 1.1 series in `figures/v1_1/`, frozen 1.0 figures in `figures/v1_0/`) and `scripts/`.
Version 1.1 protocol specifications are in `protocols/`. The OSF project is [osf.io/t5hcq](https://osf.io/t5hcq); the stated 2026-10-16 amendment has not been independently verified.

### Project links

| Resource | Location |
| :--- | :--- |
| Code repository | <https://github.com/apgiframework/apgi-framework> |
| Zenodo archive (manuscripts + protocol battery, v1.0) | [10.5281/zenodo.21632264](https://doi.org/10.5281/zenodo.21632264) |
| OSF project (pre-registrations) | <https://osf.io/t5hcq> |
| Author ORCID | <https://orcid.org/0009-0005-0328-2896> |
| OSF Registry DOI | [10.17605/OSF.IO/YK29G](https://doi.org/10.17605/OSF.IO/YK29G) |

To reproduce all figures from archived data in one command:

```bash
bash reproduce_all.sh
```

## Overview

The APGI framework implements the core equations from the APGI paper series:

| Symbol | Formula | Meaning |
| :--- | :--- | :--- |
| Πⁱ_eff | Πⁱ · exp(−C/κ) | Metabolically gated inhibitory precision |
| Sₜ | Πᵉ·\|zᵉ\| + Πⁱ_eff·\|zⁱ\| | Global integration signal |
| θₜ | α·C + β·V | Adaptive ignition threshold |

**Paper 1** — core APGI equations; EEG interoceptive gating, TMS-insular gating, active inference simulations, DoC biomarkers, fMRI anticipation, and iEEG ignition-dynamics protocols  
**Paper 2** — Liquid Neural Network extension (`apgi.extensions.liquid_network`)  
**Paper 3** — Five-level hierarchical architecture (`apgi.extensions.hierarchical`)

## Repository structure

```text
apgi-framework/
├── src/apgi/              # pip-installable library
│   ├── core.py            # Sₜ, θₜ, Πⁱ_eff equations
│   ├── normalizer.py      # APGINormalizer
│   ├── integration.py     # APGICoreIntegration (stateful session)
│   ├── clinical.py        # EnhancedClinicalInterpreter
│   ├── parameter_recovery.py
│   └── extensions/        # optional
│       ├── liquid_network.py
│       └── hierarchical.py
├── protocols/             # pre-registered experimental protocols
│   ├── schemas/           # JSON Schema validation
│   └── *.json
├── tests/                 # pytest suite
├── notebooks/             # worked examples
├── figures/               # see figures/README.md
│   ├── common/            # shared helpers (utils.py)
│   ├── v1_0/              # frozen 1.0 figures: protocols/, paper1–4/, output/
│   └── v1_1/              # current 1.1 review series (generate.py, validate.py, output/)
├── scripts/               # standalone CLI helpers
├── data/                  # local data cache + seed datasets
│   ├── seeds/             # .npz + .csv + .h5 (sim3) seed files (generated, not committed)
│   │   └── seed_manifest.json  # tracked v1.1.0 release record of the seed files
│   ├── generate_seeds.py  # deterministic seed generator (MASTER_SEED = 2025)
│   └── checksums.sha256
├── DATA_DICTIONARY.md     # full variable codebook for all seed datasets
└── POWER_ANALYSIS.md      # sample-size and power justifications
```

## Installation

```bash
git clone https://github.com/apgiframework/apgi-framework.git
cd apgi-framework
pip install -e ".[dev]"
```

### Conda (HPC / clean-machine replication)

```bash
conda env create -f environment.yml
conda activate apgi
pip install -e ".[dev]"
```

### Optional: Paper 2 LNN extension (requires PyTorch)

```bash
pip install -e ".[lnn]"
```

## Quick start

```python
import apgi

# Core equations — available directly from the package
pi_i_eff = apgi.compute_pi_i_eff(pi_i=1.0, C_metabolic=50.0, kappa=100.0)
S_t      = apgi.compute_S_t(pi_e=1.2, z_e=0.8, pi_i_eff=pi_i_eff, z_i=0.5)
theta_t  = apgi.compute_theta_t(C_metabolic=1.0, V_information=0.5, alpha=0.3, beta=0.7)
print(f"Sₜ={S_t:.4f}  θₜ={theta_t:.4f}  ignition={apgi.ignition_criterion(S_t, theta_t)}")
```

### Stateful session integration

```python
from apgi.integration import APGICoreIntegration
import apgi

# Built-in sample data — no Zenodo download required
session = apgi.datasets.make_sample_session(n_trials=200, seed=0)

integ = APGICoreIntegration(alpha=0.3, beta=0.7, gamma=0.9)
integ.run_sequence(**{k: session[k] for k in
    ("pi_e", "z_e", "pi_i", "z_i", "C_metabolic", "V_information")})
print(f"Ignition rate: {integ.ignition_rate():.3f}")
```

### Paper 2 / 3 extensions (not pulled in by default)

```python
from apgi.extensions.liquid_network import LiquidNeuralNetwork
from apgi.extensions.hierarchical  import APGIHierarchy
```

## Notebooks

Interactive walkthroughs are in `notebooks/`. The protocol notebooks follow protocol specification **v1.1.0**: they read
design counts and decision thresholds directly from `protocols/*.json`, and they classify each prediction as CONFIRMED,
FALSIFIED or INDETERMINATE (failing to confirm is not falsification). All data are synthetic.

| Notebook | Content |
| :--- | :--- |
| `quick_start.ipynb` | Core equations, v1.1 parameter registry check, `APGICoreIntegration`, signal normalisation |
| `protocol0_hep_proxy_validation.ipynb` | Protocol 0 — HEP proxy validation and downstream proxy gate (Pred 0.A–0.C) |
| `protocol1_cardiac_eeg.ipynb` | Protocol 1 — Cardiac-EEG: attention × cardiac phase, IA moderation, Weibull steepness (Pred 1.A–1.F) |
| `protocol2_somatic_agent_sim.ipynb` | Protocol 2 — Somatic-AgentSim: seven IGT architectures under the volatility schedule (Pred 2.A–2.E) |
| `protocol3_anticipation_fmri.ipynb` | Protocol 3 — Anticipation-fMRI: vmPFC→aINS vs vmPFC→pIC dissociation (Pred 3.A–3.D) |
| `protocol4_metabolic_crossover.ipynb` | Protocol 4 — Metabolic-state crossover: four sessions, signed 15 % d′ margin (Pred 4.A–4.C) |
| `protocol5_insula_tms.ipynb` | Protocol 5 — Causal neuromodulation: aINS tFUS/dTMS vs matched sham, ROPE equivalence (Pred 5.A–5.E) |
| `protocol6_ignition_ieeg.ipynb` | Protocol 6 — Ignition-iEEG: fixed-contrast bimodality, dwell, AC1 estimator check (Pred 6.A–6.E) |
| `protocol7_doc_biomarker.ipynb` | Protocol 7 — DoC biomarkers: primary Pred 7.G HEP→CRS-R LRT, joint HEP+PCI (Pred 7.A–7.G) |

```bash
jupyter lab notebooks/
```

## Reproducing figures

The **APGI 1.1 figure review series** is in [`figures/v1_1/`](figures/v1_1/README.md), with a [side-by-side comparison](figures/v1_1/index.html), revised captions, provenance and a complete mapping of all 31 legacy figures. Generate its 32 PNG/PDF/SVG sets with:

```bash
python3 figures/v1_1/generate.py
python3 figures/v1_1/validate.py
```

Two quantitative panels (parameter recovery and sensitivity/robustness) are explicitly pending verified 1.1 analysis outputs; their current replacements describe the required analyses. The following commands reproduce the frozen **1.0** protocol figures in `figures/v1_0/`, not the 1.1 review series. Run `validate.py` first: it checks the committed 1.0 images that these scripts overwrite.

```bash
python figures/v1_0/protocols/p0_hep_proxy.py            # Figure 1 — Protocol 0: HEP proxy validation (Pred 0.A–0.C)
python figures/v1_0/protocols/p1_cardiac_eeg.py          # Figure 2 — Protocol 1: Cardiac-EEG trial timeline
python figures/v1_0/protocols/p2_somatic_agent_sim.py    # Figure 3 — Protocol 2: somatic-marker agent advantage
python figures/v1_0/protocols/p3_anticipation_fmri.py    # Figure 4 — Protocol 3: vmPFC–insula anticipatory coupling
python figures/v1_0/protocols/p4_metabolic_crossover.py  # Figure 5 — Protocol 4: allostatic threshold modulation
python figures/v1_0/protocols/p5_causal_tms.py           # Figure 6 — Protocol 5: causal PCI/HEP dissociation
python figures/v1_0/protocols/p6_ignition_ieeg.py        # Figure 7 — Protocol 6: iEEG bimodality + AC1 slowing
python figures/v1_0/protocols/p7_doc_biomarker.py        # Figure 8 — Protocol 7: joint PCI–HEP model (N=110)
```

Scripts are named by protocol (`pK_…`); their outputs keep the published numbering, Figure N ↔ Protocol (N−1),
matching the captions in `OUP-Protocols.txt` / the OSF preregistration, and land in `figures/v1_0/output/figureN.{pdf,png}`.
The per-paper 1.0 figures are in `figures/v1_0/paper1/`–`paper4/`. See [`figures/README.md`](figures/README.md) for the layout and the 1.0 → 1.1 mapping.

## Running tests

```bash
pytest tests/ -v
```

The full suite (379 tests, 99% line coverage of `src/apgi`, `scripts/` and `figures/`) covers core
equations, normaliser, integration, clinical interpreter, parameter recovery, LNN, bifurcation analysis,
five-level hierarchy, protocol validation, and the seed-manifest release record.

## Data

The nine synthetic seed datasets (`sim0`–`sim8`) are not yet deposited on Zenodo; the v1.0 record
([10.5281/zenodo.21632264](https://doi.org/10.5281/zenodo.21632264)) holds the manuscripts and protocol battery.
Regenerate them locally and check them against the release checksums:

```bash
python data/generate_seeds.py                    # all nine datasets → data/seeds/ (sim2 takes ~2 h)
python data/generate_seeds.py --dataset sim0,sim5
python data/generate_seeds.py --verify           # compare with data/checksums.sha256
bash reproduce_all.sh --local                    # figures from the local seeds
```

Once the datasets are deposited, `apgi-fetch` (`--list`, `--dataset NAME`, `--verify`) downloads them instead.
Binder builds `data/seeds/` automatically (`binder/postBuild`, all datasets except `sim2`).

Checksums are recorded in [`data/checksums.sha256`](data/checksums.sha256); the release record
[`data/seeds/seed_manifest.json`](data/seeds/seed_manifest.json) adds each dataset's seed, consumers,
generating environment and alignment with protocol specification v1.1.0.
Full variable codebook: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).
Sample-size justifications: [`POWER_ANALYSIS.md`](POWER_ANALYSIS.md).

The LNN trajectory dataset (`sim3_liquid_network`) is also written as
`sim3_liquid_network.h5` (HDF5, gzip-compressed) for direct use in
MNE-Python, NWB tools, MATLAB (`h5read`), and Julia (`HDF5.jl`):

```matlab
states = h5read('sim3_liquid_network.h5', '/data/states');  % (20, 500, 100)
```

```julia
using HDF5
fid = h5open("sim3_liquid_network.h5", "r")
states = read(fid["data/states"])
close(fid)
```

## Experimental protocols

The eight protocol specifications use version `1.1.0` (protocol release version). They contain 40 prediction records. Source conflicts and pending analysis locks are documented in `protocols/CHANGELOG.md`; JSON validation does not establish empirical validation or study readiness.

| File | Paradigm | Predictions |
| :--- | :--- | :--- |
| `protocol_0_hep_proxy_validation.json` | HEP proxy validation | 0.A–C |
| `protocol_1_cardiac_eeg.json` | Cardiac EEG | 1.A–F |
| `protocol_2_somatic_agent_sim.json` | Somatic agent simulation | 2.A–G |
| `protocol_3_anticipation_fmri.json` | Anticipation fMRI | 3.A–D |
| `protocol_4_metabolic_crossover.json` | Metabolic crossover | 4.A–C |
| `protocol_5_causal_tms.json` | Causal stimulation | 5.A–E |
| `protocol_6_ignition_ieeg.json` | Ignition iEEG | 6.A–E |
| `protocol_7_doc_biomarker.json` | DoC biomarkers | 7.A–G |

CI validates the schema, date/URI formats, release membership, cross-field consistency, report and SHA256 manifest:

```bash
python3 scripts/validate_protocols.py
python3 -m pytest tests/test_validate_protocols.py
```

An external release folder can be supplied as the first argument. Add `--source-dir /path/to/FINAL` to verify the source-document hashes. After intentional edits, `--refresh-metadata` regenerates `VALIDATION.json` and `MANIFEST.json` only after the protocol checks pass. Normal validation never rewrites files.

## Citation

```bibtex
@software{apgi_framework_2026,
  author  = {Pesochin, Dimitry},
  title   = {APGI Framework},
  year    = {2026},
  version = {1.1.0},
  doi     = {10.5281/zenodo.21632264},
  url     = {https://github.com/apgiframework/apgi-framework},
  note    = {ORCID: 0009-0005-0328-2896. Pre-registrations: https://osf.io/t5hcq}
}
```

## License

MIT — see [LICENSE](LICENSE).
