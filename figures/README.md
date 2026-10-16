# APGI figures

Two figure series live here. **Version 1.1 (`v1_1/`) is the current series**; version 1.0
(`v1_0/`) is frozen and kept so every published figure can still be traced and regenerated.

```text
figures/
├── README.md        # this file
├── common/          # helpers shared by the 1.0 scripts (utils.py: palette, save_figure, …)
├── v1_0/            # frozen 1.0 series — bug fixes only
│   ├── protocols/   # protocol figures, one script per protocol: pK_<protocol>.py
│   ├── output/      # their exports, published numbering: figureN.pdf / figureN.png
│   └── paper1/ … paper4/   # per-paper figures: generate_fig*.py + output/
└── v1_1/            # current 1.1 review series
    ├── generate.py, validate.py and helper modules
    ├── captions.json, CAPTIONS.md, MANIFEST.json, PROVENANCE.json, VALIDATION.json
    ├── index.html   # side-by-side 1.0 / 1.1 comparison
    ├── output/      # 32 figure sets × PNG, PDF, SVG
    └── archive/     # supplied October 4 code, preserved unchanged for audit (not run)
```

## Building

```bash
python3 figures/v1_1/validate.py   # check the committed 1.1 series (and the 1.0 baseline images)
python3 figures/v1_1/generate.py   # rebuild the 1.1 series, then validate again

for s in figures/v1_0/protocols/p[0-7]_*.py; do python3 "$s" --no-show; done   # 1.0 protocol figures
python3 figures/v1_0/paper1/generate_fig1.py --no-show                          # one 1.0 paper figure
```

Run `validate.py` **before** regenerating 1.0 figures. It checks that the committed 1.0 images are
unchanged, and the 1.0 scripts overwrite them; rebuilt images can differ in bytes across platforms.
`bash reproduce_all.sh` and CI follow this order.

`validate.py` needs Pillow and pypdf (`pip install -e ".[dev]"`).

## Version 1.0 protocol figures

Scripts are named by protocol; outputs keep the published numbering, **Figure N ↔ Protocol N−1**,
which matches the captions in the OSF preregistration.

| Script (`v1_0/`) | Protocol | Output (`v1_0/`) | Figure |
| :--- | :---: | :--- | :--- |
| `protocols/p0_hep_proxy.py` | 0 | `output/figure1.{pdf,png}` | Figure 1 — HEP proxy validation |
| `protocols/p1_cardiac_eeg.py` | 1 | `output/figure2.{pdf,png}` | Figure 2 — Cardiac-EEG trial timeline |
| `protocols/p2_somatic_agent_sim.py` | 2 | `output/figure3.{pdf,png}` | Figure 3 — Somatic-marker agent advantage |
| `protocols/p3_anticipation_fmri.py` | 3 | `output/figure4.{pdf,png}` | Figure 4 — vmPFC–insula anticipatory coupling |
| `protocols/p4_metabolic_crossover.py` | 4 | `output/figure5.{pdf,png}` | Figure 5 — Allostatic threshold modulation |
| `protocols/p5_causal_tms.py` | 5 | `output/figure6.{pdf,png}` | Figure 6 — Causal PCI/HEP dissociation |
| `protocols/p6_ignition_ieeg.py` | 6 | `output/figure7.{pdf,png}` | Figure 7 — iEEG bimodality + AC1 slowing |
| `protocols/p7_doc_biomarker.py` | 7 | `output/figure8.{pdf,png}` | Figure 8 — Joint PCI–HEP DoC model |

## Mapping: 1.0 → 1.1

All 31 version 1.0 figures map to a 1.1 counterpart, plus a new graphical abstract (`GA`).
Generated from `v1_1/MANIFEST.json`; paths are relative to `v1_0/`. Some supplements
intentionally share protocol artwork. For the reason behind each change, see `v1_1/README.md`;
for the comparison, open `v1_1/index.html`.

| 1.1 ID | 1.0 figure | 1.1 status |
| :--- | :--- | :--- |
| `GA` | — (new) | Model schematic |
| `P1F1` | `paper1/output/fig1_architecture_pipeline` | Model schematic |
| `P1F2` | `paper1/output/fig2_somatic_marker_circuit` | Proposed mechanism |
| `P1F3` | `paper1/output/fig3_thermodynamic_bridge` | Derivation schematic |
| `P1F4` | `paper1/output/fig4_onset_ignition_timeline` | Hypothesized timing schematic |
| `P1F5` | `paper1/output/fig5_epistemic_tier_falsification_mapping` | Specification schematic |
| `P1S1` | `paper1/output/figS1_parameter_recovery` | Analysis-design replacement |
| `P1S2` | `paper1/output/figS2_sensitivity_tornado` | Analysis-design replacement |
| `P1S3` | `paper1/output/figS3_protocol1_trial_timeline` | Prospective protocol schematic |
| `P1S4` | `paper1/output/figS4_protocol3_fmri_trial` | Prospective protocol schematic |
| `P2F1` | `paper2/output/fig1_biological_constraints_lsm` | Analytical architecture comparison |
| `P2F2` | `paper2/output/fig2_cortical_microcircuit` | Proposed mechanism |
| `P2F3` | `paper2/output/fig3_bifurcation_analysis` | Reduced-model illustration |
| `P2F4` | `paper2/output/fig4_visual_masking_trajectories` | Reduced-model simulation |
| `P2S1` | `paper2/output/figS1_ep2_ep6_protocol_schematics` | Prospective design schematic |
| `P3F1` | `paper3/output/fig1_russian_doll_hierarchy` | Hierarchical model schematic |
| `P3F2` | `paper3/output/fig2_1f_power_spectrum` | Analytical OU spectrum |
| `P3F3` | `paper3/output/fig3_neuromodulatory_coupling` | Proposed mechanism |
| `P3F4` | `paper3/output/fig4_psychiatric_disorder_profiles` | Specification schematic |
| `P3F5` | `paper3/output/figS1_protocol7_clinical_design` | Prospective protocol schematic |
| `P3F6` | `paper3/output/fig5_developmental_maturation_spectral` | Illustrative developmental prediction |
| `P4F1` | `paper4/output/fig1_three_tier_epistemic_architecture` | Specification schematic |
| `P4F2` | `paper4/output/fig2_comparative_audit_bar_chart` | Single-author provisional audit |
| `P4F3` | `paper4/output/figS1_twelve_prediction_matrix` | Prospective prediction matrix |
| `PRF1` | `output/figure1` | Prospective protocol schematic |
| `PRF2` | `output/figure2` | Prospective protocol schematic |
| `PRF3` | `output/figure3` | Prospective protocol schematic |
| `PRF4` | `output/figure4` | Prospective protocol schematic |
| `PRF5` | `output/figure5` | Prospective protocol schematic |
| `PRF6` | `output/figure6` | Prospective protocol schematic |
| `PRF7` | `output/figure7` | Prospective protocol schematic |
| `PRF8` | `output/figure8` | Prospective protocol schematic |

## Notes

- `common/` holds only the 1.0 helpers. The 1.1 series keeps its own `v1_1/style.py`; merging the
  two would change the 1.1 exports and their recorded checksums.
- `v1_1/archive/` is checked by `validate.py` against `v1_1/PROVENANCE.json`; do not edit it.
- 1.1 IDs: `P<n>F<k>` = Paper n main figure k, `P<n>S<k>` = supplement, `PRF<k>` = protocol figure k
  (Protocol k−1), `GA` = graphical abstract.
