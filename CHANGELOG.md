# Changelog

All notable changes to `apgi` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-10-16

- `figures/` reorganized into symmetric version folders (all moves via `git mv`, history kept):
  `common/utils.py` (shared 1.0 helpers); `v1_0/` (frozen 1.0 series) with `protocols/` — the eight
  protocol scripts renamed by protocol, `generate_figureN.py` → `pK_<protocol>.py` (K = N − 1),
  outputs still `v1_0/output/figureN.*` — plus `paper1/`–`paper4/`; `v1_1/source/` → `v1_1/archive/`.
  New `figures/README.md` gives the layout, build order and the full 1.0 → 1.1 mapping.
  `v1_1/MANIFEST.json`, `index.html`, `generate.py` and `validate.py` point at the new 1.0 paths
  (31 baseline checksums unchanged; `validate.py` passes). CI and `reproduce_all.sh` run
  `figures/v1_1/validate.py` before the 1.0 smoke tests; `pypdf` joins the `[dev]` extras. README,
  CONTRIBUTING, coverage omits, `tests/test_figures_utils.py` and the seed-manifest consumers
  follow the new paths.
- `notebooks/` — all eight protocol notebooks rebuilt for protocol specification v1.1.0. Design counts and
  decision thresholds are now loaded from `protocols/*.json` (each notebook asserts `version == "1.1.0"`).
  Every prediction is classified CONFIRMED / FALSIFIED / INDETERMINATE under the v1.1 rule that a failure to
  confirm is not falsification. Each notebook carries a v1.0 → v1.1 change table. Legacy `KAPPA = 100`,
  `ALPHA = 0.3` and `BETA = 0.7` defaults are removed (κ is `null`, uncalibrated).
  Cohort sizes now follow v1.1: P0 N = 115 + independent N ≥ 30; P1 62/59/48; P3 40/36; P4 64/55/48 across
  two sites; P5 52/44/36; P6 20/12; P7 80 patients + 30 controls.
  New analyses: P0 proxy-gate reclassification; P1 Weibull Pred 1.E and sequential BF monitoring;
  P2 seven-architecture IGT agents with deterministic seeds; P5 Pred 5.E ROPE equivalence; P6 AC1
  five-sample estimator recovery; P7 primary Pred 7.G random-intercept LRT with whole-site bootstrap and a
  noncentral-F cross-check of the registered power table.
- `notebooks/quick_start.ipynb` — adds a v1.1 parameter-registry cell that checks the library defaults
  (θ₀, γ_sig, β_SM) against the registered ranges.
- `README.md` — notebook table updated to the actual file names and v1.1 prediction ranges.
- `data/seeds/seed_manifest.json` (new, tracked) — release 1.1.0 record of the nine seed datasets:
  SHA-256 and size of each `.npz`/`.csv`, the derived sub-seed, the protocol it illustrates, the
  figure scripts that read it, and its alignment with the v1.1.0 participants block. Five datasets
  keep their v1.0 simulated designs (`sim0`, `sim2`, `sim6`, `sim7`, `sim8`); `sim5` matches v1.1;
  `sim1`, `sim3` and `sim4` simulate no cohort. The manifest also records the generating
  environment. Written by `data/generate_seeds.py` on a full run, or rebuilt with `--manifest`.
- `data/generate_seeds.py` — `_save()` no longer passes `allow_pickle=True` to
  `np.savez_compressed`: NumPy < 2.1 stored it as a stray `allow_pickle` array in every archive,
  so the file bytes depended on the NumPy version. `--verify` now compares against
  `data/checksums.sha256` and exits 1 on mismatch (it previously only printed digests).
  `--dataset` accepts comma-separated prefixes and also limits `--verify`. `--verify` falls back to
  a per-array content fingerprint stored in the manifest (exact hashes for integer, boolean and text
  arrays; sum, sum of squares, min, max and non-finite count for floats, compared at a relative
  tolerance of 1e-9), so a dataset regenerated on another platform verifies even though its
  compressed bytes differ. `--manifest` also rewrites `data/checksums.sha256` and the `apgi-fetch`
  registry from the local files.
- `data/checksums.sha256`, `src/apgi/scripts/fetch_data.py` — file digests now come from the
  Binder reference stack (Python 3.11, NumPy 1.26.4, SciPy 1.13.0, linux-x86_64). The previous
  digests were produced on macOS arm64 and still reproduce there: `.npz` archives are
  zlib-compressed, and macOS and Linux link different zlib builds, so identical arrays give
  different file bytes. Array contents are the same on both platforms apart from last-bit
  floating-point differences (≤ 4e-15). Before depositing to Zenodo, run
  `python data/generate_seeds.py --manifest` on the machine whose files are uploaded so the
  checksums and `apgi-fetch` registry match those exact files. The Zenodo v1.0 record holds no seed
  files, so `apgi-fetch` downloads cannot succeed until the datasets are deposited.
- `binder/postBuild` (new) — regenerates `data/seeds/` at image build time (all datasets except
  `sim2`, whose ~2 h MLE sweep exceeds a Binder build and has no consumer) and checks it against
  `data/checksums.sha256`. `binder/environment.yml` adds `h5py`.
- `.gitignore` — ignores `data/seeds/*` but tracks `data/seeds/seed_manifest.json`.
- `tests/test_seed_manifest.py` (new) — checks that the manifest, `data/checksums.sha256` and the
  `apgi-fetch` registry agree, that sub-seeds follow `MASTER_SEED`, and that the recorded generator
  hash matches `data/generate_seeds.py`.
- `pyproject.toml`, `zenodo.json`, `CITATION.cff` — version 1.1.0. The project name is unified as
  *Allostatic Precision-Gated Ignition* (previously also "Adaptive Predictive Global Integration" and
  "Allostatic Predictive Gating Ignition"). `zenodo.json` now lists all nine seed datasets (sim0–sim8),
  and `CITATION.cff` describes the Zenodo v1.0 record as manuscripts plus protocol battery.
- `README.md` — fixes the "Precission" typo; the Data section now explains local seed regeneration and
  the manifest, since the seed files are not yet on Zenodo; BibTeX gains `version = {1.1.0}`.

---

- Project identifiers finalised across all documentation and metadata: Zenodo archive DOI
  `10.5281/zenodo.21632264`, OSF project `https://osf.io/t5hcq`, code repository
  `https://github.com/apgiframework/apgi-framework`, author ORCID `0009-0005-0328-2896`.
  Replaces the `XXXXXXX` placeholders in `README.md`, `CITATION.cff`, `zenodo.json`,
  `pyproject.toml`, `CONTRIBUTING.md`, `DATA_DICTIONARY.md`, `data/generate_seeds.py`,
  `src/apgi/scripts/fetch_data.py`, all eight `protocols/protocol_*.json` (`osf_url` and
  `preregistration.url`), and the `$id` in `protocols/schemas/protocol.schema.json`.
  The arXiv ID and the per-site IRB protocol numbers remain placeholders pending assignment.
- `CITATION.cff` — adds top-level `url` (OSF project) and an `identifiers` block listing the
  Zenodo DOI and OSF project; removes the obsolete "replace after Zenodo deposition" comments.
- `README.md` — adds a Project links table, OSF and ORCID badges, ORCID in the manuscript
  byline, and an ORCID/OSF `note` field in the BibTeX entry.

- `src/apgi/scripts/fetch_data.py` — corrects the stale SHA-256 for `sim5_doc_biomarker` in
  the DATASETS registry (`bd8bfca7…` → `1788cc8b…`) so it agrees with `data/checksums.sha256`
  and with the digest `data/generate_seeds.py` reproduces; `apgi-fetch --verify` previously
  reported a false mismatch for that one dataset.

- `src/apgi/datasets.py` — `make_sample_session()` and `make_sample_doc_groups()` inline toy
  datasets; no Zenodo download required; exposed as `apgi.datasets` in `__all__`.
- `data/DATA_DICTIONARY.md` — full variable codebook for all six `.npz` archives (shape,
  dtype, units, equation symbol); includes R/MATLAB/Julia loading examples.
- CSV summaries alongside every `.npz` — six `.csv` files emitted by `data/generate_seeds.py`
  for R/MATLAB/Julia readers who cannot load `.npz` natively.
- `environment.lock.yml` — exact-version conda lock file for bit-for-bit reproducibility on
  macOS arm64; regenerate with `conda-lock` for other platforms.
- `binder/environment.yml` — Binder configuration enabling in-browser notebook execution.
- Binder and Google Colab launch badges in `README.md`.
- `protocol_0_hep_proxy_validation.json` listed in README protocol table.

- `src/apgi/scripts/fetch_data.py` — adds `--verify` flag (SHA-256 check of cached files
  without re-downloading; exits non-zero on mismatch); adds `sim5` and `sim6` to DATASETS
  registry with real checksums; size hints shown in `--list` output.
- `src/apgi/parameter_recovery.py` — `recover_parameters()` now returns `converged` (bool)
  from `scipy` optimizer `success` flag; `run_recovery_simulation()` propagates it.
- `data/generate_seeds.py` — sim2 convergence criterion now uses actual optimizer success
  flags instead of hardcoded `noise_sd = 0.05`; size annotations added to dataset catalogue
  docstring; all six generators emit companion CSV summaries.
- `.github/workflows/test.yml` — validates all 7 notebooks (was 3); adds ruff lint step and
  mypy type-check step.
- `pyproject.toml` — adds `ruff>=0.4.0` and `mypy>=1.10.0` to `[dev]` extras; adds
  `[tool.ruff]` and `[tool.ruff.lint]` configuration.
- `CONTRIBUTING.md` — documents locked environment, `conda-lock` regeneration, and
  `apgi-fetch --verify` usage.
- `reproduce_all.sh` — runs `apgi-fetch --verify` after Zenodo download; mentions
  `environment.lock.yml`.
- `CHANGELOG.md` — removed duplicate `[0.1.0]` section.

---

- `data/generate_seeds.py` — canonical synthetic seed generator for all six `.npz` datasets
  (sim1–sim6). Derives every sub-RNG from `MASTER_SEED = 2025`; self-describing metadata
  is stored inside each archive. Outputs SHA-256 digests for Zenodo deposition.
- `CITATION.cff` — machine-readable citation (CFF 1.2.0); GitHub renders "Cite this
  repository" button; required by eLife, PLOS, and Semantic Scholar indexing.
- `reproduce_all.sh` — single-command reproducibility entry point: fetch data → unit tests →
  protocol validation → all 8 figures → analysis scripts.
- `CONTRIBUTING.md` — contributor guidelines covering environment setup, testing, branch
  naming, protocol additions, and figure conventions.
- `zenodo.json` — Zenodo deposit metadata (title, creators, keywords, license, related
  identifiers) ready for upload to `https://zenodo.org/deposit/new`.
- `sim5_doc_biomarker.npz`, `sim6_bifurcation.npz` seed datasets (two new datasets beyond
  the original four).
- Notebook CI validation via `pytest --nbval-lax` in `.github/workflows/test.yml`.

- `pyproject.toml` version `0.1.0` → `0.2.0`; Development Status `3 - Alpha` → `4 - Beta`.
- `environment.yml` adds `nbformat`, `ipykernel`, and `nbval` so notebooks execute in the
  conda environment without additional installs.
- `CITATION.cff` version updated to `0.2.0`; ORCID placeholder annotated with registration
  link for indexing in OpenAlex, Semantic Scholar, and Europe PMC.
- `data/checksums.sha256` updated with real SHA-256 digests for sim1, sim3–sim6; sim2
  digest to be added after the 1 000-run MLE job completes.
- `.gitignore` updated: `data/seeds/` excluded (upload to Zenodo instead); old blanket
  `data/*.npz` rule removed.

- `sim6_bifurcation` LNN parameters retuned to reliably satisfy the pre-registered
  falsification criterion (AC1 increase n ≥ 20/25, CSD ratio ≥ 1.2).

- `src/apgi/core.py` — renamed from `apgi_core.py` for cleaner import paths.
- `src/apgi/normalizer.py` — `APGINormalizer` for z-score / min-max normalisation across sessions.
- `src/apgi/integration.py` — `APGICoreIntegration` stateful session integrator.
- `src/apgi/clinical.py` — `EnhancedClinicalInterpreter` with four-level consciousness scale.
- `src/apgi/extensions/` namespace — Paper 2 (`LiquidNeuralNetwork`) and Paper 3 (`APGIHierarchy`) moved here to avoid polluting the core install.
- `protocols/schemas/protocol.schema.json` — JSON Schema for experimental protocol files; CI validates all `protocols/*.json` against it.
- `figures/utils.py` — shared APGI Neural Glow palette, `despine`, `save_figure`, `annotate_pearson_r`, and other helpers used by all figure scripts.
- `notebooks/quick_start.ipynb` — end-to-end demo of core equations, `APGICoreIntegration`, and signal normalisation.
- `scripts/fetch_data.py` — root-level shim for `apgi-fetch` CLI entry point.
- `tests/conftest.py` — shared fixtures (`rng`, `sample_S_t`, `fitted_normalizer`).
- `tests/test_normalizer.py` — full coverage of `APGINormalizer`.
- `tests/test_integration.py` — `APGICoreIntegration` tests including somatic modulation validation.
- `data/checksums.sha256` — integrity manifest for Zenodo downloads.
- `.github/workflows/release.yml` — automated PyPI and Zenodo publish on version tags.
- `CHANGELOG.md` — this file.
- Initial release: core APGI equations (`compute_S_t`, `compute_theta_t`, `compute_pi_i_eff`, `ignition_criterion`, `run_trial`, `update_theta`).
- `LiquidNeuralNetwork` continuous-time reservoir (Paper 2).
- `APGIHierarchy` five-level hierarchical architecture (Paper 3).
- `parameter_recovery` module with MLE-based recovery simulation (Appendix A.4).
- Experimental protocols: `protocol_1_cardiac_phase.json`, `protocol_2_tms_insula.json`.
- GitHub Actions CI (`test.yml`) covering Python 3.11 and 3.12.
- `src/apgi/__init__.py` now exposes an explicit `__all__` listing only the stable public API; extension classes are excluded from the top-level namespace.
- `figures/generate_figure1.py` and `generate_figure2.py` updated to import from `figures.utils` and `apgi.core`.
- `data/fetch_data.py` promoted to `src/apgi/scripts/fetch_data.py` (registered as `apgi-fetch` CLI entry point in `pyproject.toml`).
- `pyproject.toml` adds `jsonschema>=4.0` to core dependencies.
