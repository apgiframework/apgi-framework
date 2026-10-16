from style import *

params = [(r'$\theta_0$', 34, -1), (r'$\Pi^{i}_{baseline}$', 22, +1), (r'$\beta_{SM}$', 15, +1),
          (r'$\gamma_{sig}$', 9, +1), (r'$\tau_S$', 5, +1), (r'$\lambda_\Pi$', 2, +1)]
fig = plt.figure(figsize=(7.2, 3.0))
ax = fig.add_axes([0.08, 0.20, 0.38, 0.68])
inc, dec = OI['green'], OI['verm']
for i, (lab, mag, sign) in enumerate(params):
    y = len(params) - 1 - i
    # effect of +50% and -50% parameter change
    eff_plus = sign * mag; eff_minus = -sign * mag
    for eff, hatch, nm in ((eff_plus, '', '+50%'), (eff_minus, '////', '−50%')):
        ax.barh(y, eff, height=0.62, color=inc if eff > 0 else dec, hatch=hatch, edgecolor='white', lw=0.4)
    ax.text(-41, y, f'{lab}  (±{mag}%)', va='center', ha='right', fontsize=7.2)
ax.axvline(0, color=INK, lw=0.8)
ax.set_yticks([]); ax.spines['left'].set_visible(False)
ax.set_xlim(-40, 40)
ax.set_xlabel('Change in P(ignition) (%)')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc='#BBBBBB', ec='white', label='+50% parameter change'),
                   Patch(fc='#BBBBBB', ec='white', hatch='////', label='−50% parameter change'),
                   Patch(fc=inc, label='raises P(ignition)'), Patch(fc=dec, label='lowers P(ignition)')],
          loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, fontsize=6.2)
ax.set_title('One-at-a-time ±50% sweep', fontsize=8)
panel(ax, 'A', -0.42)

bx = fig.add_axes([0.60, 0.20, 0.38, 0.68])
labels = ['Bistability', 'Cardiac-phase\ndifference > 8%', 'HEP–P3b\n$r$ > 0.30', 'Post-block\nthreshold elevation']
vals = [94.2, 87.6, 91.8, 96.4]
cols = [OI['blue'], OI['orange'], OI['green'], OI['purple']]
bx.bar(range(4), vals, color=cols, width=0.62)
for i, v in enumerate(vals):
    bx.text(i, v + 1.2, f'{v:.1f}%', ha='center', fontsize=7)
bx.axhline(80, color=INK, lw=0.8, ls='--')
bx.text(3.45, 74.5, '80% pass threshold', ha='right', fontsize=6.4, bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))
bx.set_xticks(range(4)); bx.set_xticklabels(labels, fontsize=6.5)
bx.set_ylim(0, 105); bx.set_ylabel('Monte-Carlo runs passing (%)')
bx.set_title('Robustness of qualitative signatures (N = 10,000 runs)', fontsize=8)
panel(bx, 'B', -0.16)
save(fig, 'P1S2')
