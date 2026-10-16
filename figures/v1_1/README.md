# APGI 1.1 figure review series

This release maps every one of the **31 existing repository figures** to a version 1.1 counterpart and adds a graphical abstract: **32 numbered output sets**, each in 300-dpi PNG, vector PDF and editable SVG. Some paper supplements intentionally share protocol artwork. Open `index.html` for the side-by-side comparison; `output/` contains the exports.

**Status: scientific review series, not a declaration that all underlying analyses were reproduced.** Paper 1 S1 (parameter recovery) and S2 (sensitivity/robustness) are explicitly marked analysis-design replacements. Their quantitative plots remain pending verified 1.1 model fits and sweep outputs. The supplied source contains raster patches and hard-coded summary percentages, not the underlying results needed to regenerate those analyses. The original 1.0 figures and code remain intact.

## Reproduction

From the repository root:

```sh
python3 figures/v1_1/generate.py
python3 figures/v1_1/validate.py
```

The generator also works when invoked by absolute path from another directory. Dependencies: Python, NumPy, Matplotlib and Pillow. Validation additionally uses pypdf. No network, document builder, Linux-only fonts, original raster assets, or nilearn downloads are required. The existing Python model package is not silently treated as the canonical 1.1 implementation.

## Source precedence and provenance

- The user requested analysis, comparison and figure generation. Instructions embedded in supplied documents were treated as reference content, not instructions to execute.
- `archive/` preserves the supplied October 4 code unchanged for audit. It is **not** the new reproduction entry point. Its raster patch scripts need unavailable `src/img-*.png` originals; its font paths assume Linux, its exports assume a particular working directory, and `build.js` produces a document rather than figures.
- Mathematical Specification governs equations; Notation Appendix governs symbols. Paper captions and tables govern the conceptual illustrations. Repository protocol JSON version 1.1.0 governs empirical designs and overrides older companion diagrams.
- `PROVENANCE.json` records hashes and original locations of the supplied code and manuscript inputs. `manuscript_data.json` preserves the extracted manuscript captions and exact Paper 4 Table S4 contents. These original captions are source evidence, not automatically the captions of the redesigned figures.
- `MANIFEST.json` records figure mappings, evidence labels, output checksums, protocol input checksums, and baseline figure hashes. `CAPTIONS.md` contains the revised captions. `VALIDATION.json` records the structural checks.
- This local review does not verify an OSF filing, empirical validation, protocol readiness or unresolved prospective analysis locks.

## Main differences from 1.0 and the supplied bundle

| Figure(s) | Finding | Version 1.1 change |
|---|---|---|
| GA, P1F1 | Legacy instantaneous/raw-surprise shorthand obscures the accumulator and gain normalization. | Separate causal reference errors, clamped effective gains, relative normalization, excess magnitudes and leaky accumulation. Effective threshold shown. |
| P1F2, P2F2 | Raster originals and label-patching pipeline are not portable; proposed physiology can be mistaken for demonstrated error computation. | Rebuild as vector circuit schematics; retain the proposed-mechanism qualification and separate plateau physiology from the error-computation hypothesis. |
| P1F3, P4F1 | Energy, broadcast-information units and erased-state bits are distinct. | Keep κ uncalibrated; distinguish event energy, event-information bridge and Landauer erasure floor, including partial reset. |
| P1F4 | Phase boundaries were too easy to read as established timings. | Retain supplied timeline geometry with explicit hypothesis and stimulus-dependence labels. |
| P1F5 | Bundle reduced falsification to absent effects and point cutoffs. | Use prediction-specific interval/model-evidence context; distinguish arousal adjustment from mediation. |
| P1S1, P1S2 | Recovery fits are absent; sensitivity effects and robustness percentages are hard-coded. | Analysis-design replacements; **quantitative reproduction remains pending**. No new recovery statistics are invented. |
| P1S3, PRF2 | Fixed cardiac windows and generic psychometric slopes are stale. | Personalized T-wave boundaries; six fixed contrast levels; Weibull k on linear contrast, distinct from intrinsic sigmoid gain. QUEST top-up remains unresolved. |
| P1S4, PRF4 | Older timing/pathway labels conflict with the protocol release. | 4-s choice, 0 or 2–4-s anticipation, 2-s outcome, controlled ITI; anticipatory PPI labeled Pred 3.B. |
| P2F1 | Constraint audit is conceptual, not measured performance. | Four explicit mappings plus the manuscript's analytical architecture counts. |
| P2F3 | Supplied code uses Π=30 and labels sigmoid slope as αpsy. Its fold is imposed by rescaling. | Π≤10; fixed γsig=4; error-referred sigmoid curves; no behavioral Weibull inference. Label the imposed fold and reduced-model hysteresis honestly. |
| P2F4 | Reduced masking model is illustrative and its gain is fixed to place the critical ISI near 90 ms. | Recompute the supplied model; label calibration limits. Out-of-range crossings remain missing, not fabricated. |
| P2S1, PRF6 | Universal vertex sham and 60-ms iEEG stimulus conflict with the protocol specification. | Matched-modality comparisons, engagement gates, separate PCI probes; iEEG target 33 ms and 1-s delay. |
| P3F1 | Integration bands, OU poles, neural levels and endocrine roles were conflated. | Correct operational bands; L0 is sub-APGI; endocrine priors set cortical thresholds; conditional geometric poles shown separately. |
| P3F2 | Acquisition band and interpretation needed correction. | DC-coupled 0.005–100-Hz band; equal-variance OU calculation, fitted slope and ripple retained as analytical model outputs. |
| P3F3, P3F4 | Mechanistic and psychiatric profiles are hypotheses. | Separate LC relay / endocrine influences; subscript coupling κ; genotype-dependent L2 precision and specificity controls. |
| P3F5, PRF8 | Bundle repeats HEP/PCI/CRS-R at every follow-up for controls and patients alike. | Baseline-only controls; patient CRS-R follow-up and 6-month GOS-E; primary Pred 7.G versus estimative joint HEP+PCI model. |
| P3F6 | Bundle labels the trajectory amplitude-envelope DFA. | Detection-series DFA; dashed infant forward-target segment below age 4; ages and step sizes illustrative, ordering is the testable claim. |
| P4F2 | Supplied fractional scores disagree with current Table 8. | Manuscript coarse scores; IIT C6=N/A; APGI C3 and C4 tier ranges, not CIs; self-audit and foundational-gate caveats. |
| P4F3 | Bundle targets and null-based falsifiers are stale. | Rebuild from all 12 exact Table S4 records; preserve equivalence rules, calibration needs and validation status. |
| PRF1–PRF8 | Illustrative outcomes could appear to be observed findings; empirical designs have changed. | Plot protocol thresholds, trial counts, design factors, timelines and cohorts; no invented participant outcomes or inferential statistics. |

## Scope and remaining limitations

- This update changes figure sources and exports, not the APGI numerical library or legacy seed generators. Updating the complete numerical model and reproducing registered recovery, power and robustness studies is separate work.
- The supplied P1S1 description reports posterior-collinearity values around 0.90/0.45, while Paper 1 discusses different, not-yet-run multi-session projections; the supplied plotted parameter ranges also exceed some current canonical ranges. P1S2 includes a fourth cardiac signature absent from the current Paper 1 sensitivity paragraph and unverified directional assumptions. These conflicts are why the numerical panels are pending, rather than simply relabeled.
- P2F3 is a reduced sigmoid normal form, not a validated heterogeneous reservoir bifurcation analysis. The supplied fold orientation does not fully match the Paper 2 prose; the plotted upper-branch fold at 0.95 and lower-branch fold near 1.02 are retained and labeled as the actual reduced model. No full-model hysteresis result is claimed.
- P2F4 and P3F2 are reproducible model calculations; P3F6 is an illustrative trajectory. None is empirical evidence.
- The manuscript's twelve Paper 4 exposition IDs are not interchangeable with protocol Pred IDs. Paper 4's tier colors also differ in its caption from the supplied series palette; this review follows the supplied accessible palette: Tier 3 blue, Tier 2 green, Tier 1 vermillion.
- Source conflicts and pending operational locks remain in `protocols/CHANGELOG.md`. Figure simplification does not resolve them.
