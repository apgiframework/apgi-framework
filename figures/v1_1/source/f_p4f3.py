from style import *

rows = [
 (3, 'P1', 'Nicotinic agonist lowers\neffective threshold', 'Nicotine or α4β2 agonist vs placebo;\npsychophysics (d′) and P3b amplitude', 'd′ increase ≥ 0.3;\nP3b increase ≥ 20%', 'No change in detection\nor P3b', 'now', True),
 (3, 'P2', 'Near-threshold bistability\nwith critical slowing', 'Staircase near threshold; trial-to-trial\nRT/EEG; lag-1 autocorrelation (AC1)', 'AC1 increase ≥ 0.2 within\n10% of threshold', 'A continuous graded\nrelationship', 'now', True),
 (3, 'P3', '200–300 ms frontoparietal TMS\nabolishes report, spares priming', 'TMS at 200–300 ms over frontoparietal\ncortex; report (d′) and priming', 'Report d′ drop ≥ 0.8; priming\npreserved (≤ 20% reduction)', 'Both disrupted equally,\nor access persists', 'now', True),
 (3, 'P4', r'$S_t>\theta_t$ predicts access' + '\n(single trial)', r'Single-trial decoding of $S_t$ and $\theta_t$' + '\n(EEG/iEEG); held-out trials', 'AUC ≥ 0.80; accuracy\ngain ≥ 10% over chance', 'AUC < 0.64 (d′ < 0.5; ≥ 2,000\ntrials); 0.64–0.80 inconclusive', 'now', True),
 (2, 'P5', 'Attentional cueing raises\nstimulus–brain mutual information', 'Cue vs no cue; stimulus–brain\nmutual information (MI)', 'ΔMI ≥ 0.1 bit (binary set,\nH(S) = 1 bit)', 'No increase', '2–5 y', False),
 (2, 'P6', 'Conscious bandwidth saturates\nat tens of bits per second', 'RSVP across modalities; information\nrate vs presentation rate', 'Asymptote 10–50 bits/s;\nsaturating curve', 'Modality variation, or\nsustained > 100 bits/s', '2–5 y', False),
 (2, 'P7', r'$\theta_t$ approximates the' + '\nNeyman–Pearson optimum', 'Model-based ROC; compare ' + r'$\theta_t$' + '\nwith NP-optimal criterion', 'Criterion within 2 SD\nof NP optimum', 'Deviation > 2 SD', '2–5 y', False),
 (2, 'P8', 'Interoceptive transfer entropy\nexceeds exteroceptive', 'iEEG/EEG transfer entropy (TE) to\nfrontoparietal cortex, by source', 'ΔTE ≥ 0.05 bits/trial', r'$TE_{intero}\leq TE_{extero}$', '2–5 y', False),
 (1, 'P9', 'Ignition trials cost more\nfrontoparietal energy', 'fMRI/PET (CMRO$_2$ or glucose); ignition\nvs matched sub-threshold trials', 'ΔCMRO$_2$ or Δglucose\n≥ 10% after controls', 'No difference\nafter controls', '5–10 y', False),
 (1, 'P10', 'Threshold-gated processing is\nmore energy-efficient', 'Threshold-gated vs continuous task;\nenergy per bit or per correct report', '≥ 20% lower\nenergy cost', 'Continuous matches\nor beats it', '5–10 y', False),
 (1, 'P11', 'Metabolic depletion\nelevates ' + r'$\theta_t$', 'Fasted vs fed crossover (Protocol 4);\nestimate ' + r'$\theta_t$' + " from d′ and P3b", r'$\theta_t$' + ' increase ≥ 0.3 SD', 'No effect, or\nlowered threshold', '5–10 y', False),
 (1, 'P12', 'Matched calibration places κ\nin the consistent band', 'Same-network, same-window event\nenergy (ATP) and information (bits)', 'κ ∈ [10, 10$^3$] ATP/bit', 'Replicated κ outside [10, 10$^4$]\nretires per-bit bridge', '5–10 y', False),
]
fig = plt.figure(figsize=(7.2, 6.2))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
cols = [0, 10.5, 15.5, 34.5, 57.5, 75, 93, 100]
heads = ['Tier', '#', 'Prediction', 'Measurement protocol', 'Target effect size', 'Falsification criterion', 'Horizon']
top = 97; hh = 4.2; rh = 6.25
for i, h in enumerate(heads):
    ax.text(0.5 * (cols[i] + cols[i + 1]), top - hh / 2, h, ha='center', va='center', fontsize=6.4, fontweight='bold')
ax.text(0.5 * (cols[6] + cols[7]), top - hh / 2, '', fontsize=6)
ax.plot([0, 100], [top - hh, top - hh], color=INK, lw=0.8)
tier_names = {3: 'Tier 3\nComputa-\ntional', 2: 'Tier 2\nInformation-\ntheoretic', 1: 'Tier 1\nThermo-\ndynamic'}
for j, (tier, pid, pred, prot, eff, fals, hor, spec) in enumerate(rows):
    y1 = top - hh - j * rh; y0 = y1 - rh
    ax.add_patch(Rectangle((cols[1], y0), 100 - cols[1], rh, fc=TIER_LIGHT[tier], ec='white', lw=0.8))
    ax.text(0.5 * (cols[1] + cols[2]), y0 + rh / 2, pid, ha='center', va='center', fontsize=6.6, fontweight='bold', color=TIER[tier])
    for i, txt in ((2, pred), (3, prot), (4, eff), (5, fals)):
        ax.text(cols[i] + 0.6, y0 + rh / 2, txt, ha='left', va='center', fontsize=5.4)
    ax.text(cols[6] + 0.4, y0 + rh / 2, hor, ha='left', va='center', fontsize=5.6)
    ax.add_patch(Circle((cols[7] - 1.4, y0 + rh / 2), 0.65, fc=INK if spec else 'white', ec=INK, lw=0.7))
# tier bands
for tier, (a, b) in {3: (0, 4), 2: (4, 8), 1: (8, 12)}.items():
    y1 = top - hh - a * rh; y0 = top - hh - b * rh
    ax.add_patch(Rectangle((0.3, y0 + 0.3), cols[1] - 0.6, y1 - y0 - 0.6, fc=TIER[tier], ec='none'))
    ax.text(0.5 * cols[1], 0.5 * (y0 + y1), tier_names[tier], ha='center', va='center', fontsize=5.8, color='white', fontweight='bold')
yb = top - hh - 12 * rh - 1.0
ax.add_patch(Circle((22, yb - 1.6), 0.65, fc=INK, ec=INK, lw=0.7))
ax.text(23.4, yb - 1.6, 'theoretically specified', va='center', fontsize=5.8)
ax.add_patch(Circle((42, yb - 1.6), 0.65, fc='white', ec=INK, lw=0.7))
ax.text(43.4, yb - 1.6, 'pending', va='center', fontsize=5.8)
ax.text(0.5, yb - 1.6, 'Status (right-hand marker):', va='center', fontsize=5.8, fontweight='bold', ha='left')
ax.text(0.5, yb - 4.4, 'Horizon: now = feasible now; 2–5 y = near-term; 5–10 y = medium-term.', va='center', fontsize=5.8)
ax.text(0.5, yb - 7.4, 'All predictions are anchored to the access criterion ' + r'$S_t=\Pi^{e}\cdot|z^{e}|+\Pi^{i}_{eff}\cdot|z^{i}|>\theta_t$' +
        '; Tier-1 predictions additionally require the κ bridge and allostatic ' + r'$\theta_t$' + ' dynamics.', fontsize=5.8, va='center')
ax.text(0.5, yb - 10.6, r'$S_t$' + ': accumulated precision-weighted surprise;  ' + r'$\theta_t$' + ': allostatically regulated access threshold;  ' +
        r'$\Pi^{e}$, $\Pi^{i}_{eff}$' + ': exteroceptive and effective interoceptive precision;  ' + r'$z^{e}$, $z^{i}$' + ': standardised prediction errors;',
        fontsize=5.4, va='center')
ax.text(0.5, yb - 13.4, "d′: sensitivity index; AC1: lag-1 autocorrelation; MI: mutual information; TE: transfer entropy; CMRO$_2$: cerebral metabolic rate of oxygen; κ: ATP per bit of ignition-event information.",
        fontsize=5.4, va='center')
ax.set_ylim(yb - 15.0, 100)
save(fig, 'P4F3')
