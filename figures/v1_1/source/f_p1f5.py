from style import *

fig = plt.figure(figsize=(7.2, 3.25))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(3.2, 50); ax.axis('off')
colx = [0.5, 19, 43, 66, 99.5]
heads = ['Epistemic tier', 'Protocol(s)', 'Primary measure', 'Falsification threshold (registered)']
for i, h in enumerate(heads):
    ax.text(0.5 * (colx[i] + colx[i + 1]), 47.8, h, ha='center', va='center', fontsize=7, fontweight='bold')
# Protocol 0 gate
box(ax, 0.5, 41.2, 99, 4.6, fc='#EFEFEF', ec='#777777', lw=0.7, r=0.6)
ax.text(50, 43.5, 'Gate · Protocol 0 (HEP proxy validation) — HEP-dependent tests at every tier stay confirmatory only if Pred 0.A–0.C pass (OSF H2)',
        ha='center', va='center', fontsize=6.2)
rows = [
    (3, 'Computational', 'Protocols 2 & 3\nmodel comparison;\nvmPFC–aINS PPI',
     'Model evidence (ΔBIC) on human\nIGT choices; anticipatory\nvmPFC–aINS coupling',
     'ΔBIC < 10 against Standard PP and\nGNWT-only (Pred 2.E); no incremental\nvariance over ' + r'$\varepsilon^{i}$' + ' (OSF H5)'),
    (2, 'Information-\ntheoretic', 'Protocol 1\ncardiac-phase EEG\n(HEP, P3b)',
     'Phase × condition effects on\ndetection; psychometric\nsteepness ' + r'$\alpha_{psy}$',
     'No phase × condition interaction;\n' + r'$\alpha_{psy}<5$' + '; interoceptive ' + r'$R^{2}<0.02$' + '\n(OSF H1, H3, H4)'),
    (1, 'Thermodynamic', 'Protocol 4\nmetabolic-state\ncrossover',
     r"$d'$" + ' and P3b:\nState × Load interaction',
     'No covariate-adjusted State × Load\ninteraction (OSF H6). ' + r'$\kappa$' + ' is a calibration\ntarget, not a falsifier'),
]
rh = 11.2; y = 40.0
for tier, name, prot, meas, fals in rows:
    y0 = y - rh
    box(ax, 0.5, y0 + 0.4, 99, rh - 0.8, fc=TIER_LIGHT[tier], ec=TIER[tier], lw=0.9, r=0.8)
    box(ax, 0.9, y0 + 0.8, 17.6, rh - 1.6, fc=TIER[tier], ec=TIER[tier], lw=0, r=0.6)
    ax.text(9.7, y0 + rh / 2 + 1.6, f'Tier {tier}', ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    ax.text(9.7, y0 + rh / 2 - 1.9, name, ha='center', va='center', fontsize=6.4, color='white')
    for x0, x1, txt in ((colx[1], colx[2], prot), (colx[2], colx[3], meas), (colx[3], colx[4], fals)):
        ax.text(0.5 * (x0 + x1), y0 + rh / 2, txt, ha='center', va='center', fontsize=6.0)
    y = y0
    if tier > 1:
        arr(ax, (30.5, y + 0.9), (30.5, y - 0.6), INK, lw=1.0, ms=7)
        ax.text(31.6, y + 0.2, 'bridge principle', fontsize=5.6, va='center', style='italic')
ax.text(99.5, 4.2, 'Protocols 5–7 (causal neuromodulation, iEEG ignition, disorders of consciousness) are mapped in the Protocols figures.',
        ha='right', fontsize=5.6, style='italic', color='#555555')
save(fig, 'P1F5')
