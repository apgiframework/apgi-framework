from style import *

crit = ['C1\nTier\ntransparency', 'C2\nBridge\nprinciples', 'C3\nQuantitative\nbenchmarks', 'C4\nFalsification\nconditions',
        'C5\nAlternative\ncomparison', 'C6\nEvolutionary\nplausibility', 'C7\nCausal\nroadmap']
S = {'GNWT': [1.64, 1.50, 1.40, 1.23, 1.64, 1.61, 1.23],
     'IIT (3.0 scoring)': [1.21, 0.0, 0.68, 0.58, 1.00, 1.00, 0.0],
     'PP/FEP': [1.61, 1.20, 1.08, 1.12, 1.51, 1.29, 1.05],
     'APGI (self-audit)': [1.84, 1.61, 1.20, 1.51, 1.74, 1.61, 1.15]}
cols = {'GNWT': OI['sky'], 'IIT (3.0 scoring)': OI['orange'], 'PP/FEP': '#9A9A9A', 'APGI (self-audit)': OI['purple']}
fig = plt.figure(figsize=(7.2, 4.4))
ax = fig.add_axes([0.07, 0.43, 0.91, 0.52])
w = 0.2; x = np.arange(7)
for j, (k, v) in enumerate(S.items()):
    xs = x + (j - 1.5) * w
    bars = ax.bar(xs, v, w * 0.92, color=cols[k], hatch='////' if 'APGI' in k else '', edgecolor='white' if 'APGI' in k else cols[k], lw=0.3, label=k)
    for xi, vi in zip(xs, v):
        if vi == 0:
            ax.text(xi, 0.04, '0', ha='center', va='bottom', fontsize=6.5, color=cols[k], fontweight='bold')
# C3 tier-resolved range attached to the APGI bar
xa = 2 + 1.5 * w
ax.errorbar([xa], [1.5], yerr=[[0.5], [0.5]], fmt='none', ecolor=INK, elinewidth=0.9, capsize=3)
ax.text(xa + 0.12, 1.95, 'APGI tier range\n(Tier 1 min – Tier 3 max;\nnot a CI)', fontsize=5.5, va='top')
ax.axhline(1.1, color=INK, lw=0.8, ls='--', label='acceptance threshold 1.1 (= 55/100)')
ax.set_xticks(x); ax.set_xticklabels(crit, fontsize=6.3)
ax.set_ylim(0, 2.05); ax.set_ylabel('Mean criterion score (0–2)')
ax.legend(ncol=5, loc='upper center', bbox_to_anchor=(0.5, 1.13), frameon=False, fontsize=6.0)
panel(ax, 'A', -0.065, 1.05)
# Panel B cards
bx = fig.add_axes([0.0, 0.0, 1.0, 0.27]); bx.set_xlim(0, 100); bx.set_ylim(0, 30); bx.axis('off')
cards = [('GNWT', 'Tier 3 (computational)', 'Ignition threshold not derived\nfrom precision or metabolic cost'),
         ('IIT (3.0 scoring)', 'Tier 2 (information-theoretic)', 'Φ uncomputable at\nbiological scale'),
         ('PP/FEP', 'Tier 3 (computational)', 'No conscious-access\ngating criterion'),
         ('APGI (self-audit)', 'Tier 1 (thermodynamic)', 'Bridge parameter κ\n(ATP per bit) uncalibrated')]
for i, (k, tier, gap) in enumerate(cards):
    x0 = 1 + i * 24.8
    box(ax=bx, x=x0, y=2, w=23.4, h=25, fc='white', ec=cols[k], lw=1.2, r=1.0)
    bx.text(x0 + 11.7, 23, k, ha='center', fontsize=7.2, fontweight='bold', color=cols[k] if k != 'PP/FEP' else '#555555')
    bx.text(x0 + 11.7, 18.6, 'Primary falsification gap', ha='center', fontsize=5.8, color='#555555')
    bx.text(x0 + 11.7, 12.0, gap, ha='center', va='center', fontsize=6.2)
    bx.text(x0 + 11.7, 4.6, tier, ha='center', fontsize=6.0, fontweight='bold')
bx.text(0.5, 29.5, 'B', fontsize=11, fontweight='bold', va='top')
save(fig, 'P4F2')
