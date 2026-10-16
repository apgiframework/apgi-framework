from style import *

fig = plt.figure(figsize=(7.2, 2.65))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(-1, 36); ax.axis('off')
EXT, INT = OI['blue'], OI['verm']
W, H, Y0 = 13.2, 25, 9
xs = [11.0, 27.6, 44.2, 60.8]
stages = [('Error\ngeneration', 'standardised\nprediction errors', '#E8EEF8'),
          ('Precision\nweighting', 'weight by\nestimated precision', '#E3F1EC'),
          ('Somatic-marker\namplification', 'interoceptive\nprecision only', '#FBEBDD'),
          ('Surprise\naccumulation', 'leaky accumulator\n(over time)', '#EDE6F3')]
for i, (x, (title, sub, fc)) in enumerate(zip(xs, stages)):
    box(ax, x, Y0, W, H, fc=fc, ec=INK, lw=0.8, r=1.2)
    ax.add_patch(Circle((x + W / 2, Y0 + H - 2.6), 1.4, fc=INK, ec=INK))
    ax.text(x + W / 2, Y0 + H - 2.6, str(i + 1), color='white', ha='center', va='center', fontsize=6.6, fontweight='bold')
    ax.text(x + W / 2, Y0 + H - 7.0, title, ha='center', va='center', fontsize=6.6, fontweight='bold')
    ax.text(x + W / 2, Y0 + H - 11.8, sub, ha='center', va='center', fontsize=5.7, color='#444444')
ax.text(0.3, 33.6, 'Exteroceptive\nprediction error', color=EXT, fontsize=5.8, fontweight='bold', va='center')
ax.text(0.3, 7.6, 'Interoceptive\nprediction error', color=INT, fontsize=5.8, fontweight='bold', va='center')
ye, yi = 18.0, 12.6
c = [x + W / 2 for x in xs]
ax.text(c[0], ye, r'$z^{e}$', color=EXT, ha='center', fontsize=9)
ax.text(c[0], yi, r'$z^{i}$', color=INT, ha='center', fontsize=9)
ax.text(c[1], ye, r'$\Pi^{e}\cdot|z^{e}|$', color=EXT, ha='center', fontsize=8)
ax.text(c[1], yi, r'$\Pi^{i}_{baseline}\cdot|z^{i}|$', color=INT, ha='center', fontsize=7.2)
ax.text(c[2], ye + 0.6, r'$\Pi^{e}\cdot|z^{e}|$', color=EXT, ha='center', fontsize=8)
ax.text(c[2], ye - 2.2, '(unchanged)', color=EXT, ha='center', fontsize=5.6)
ax.text(c[2], yi, r'$\Pi^{i}_{eff}\cdot|z^{i}|$', color=INT, ha='center', fontsize=8)
ax.text(c[3], 16.4, r'$S_t$', ha='center', fontsize=12)
ax.text(c[3], 11.4, 'integrates\n' + r'$\Pi^{e}|z^{e}|+\Pi^{i}_{eff}|z^{i}|$', ha='center', fontsize=5.4, va='center')
for k in range(3):
    x0 = xs[k] + W; x1 = xs[k + 1]
    arr(ax, (x0 + 0.2, 30.5), (x1 - 0.1, 30.5), EXT, lw=1.0, ms=7)
    if k == 1:
        arr(ax, (x0 + 0.2, 11.0), (x1 - 2.9, 11.0), INT, lw=1.0, ms=6)
        arr(ax, (x1 - 1.6, 11.0), (x1 - 0.1, 11.0), INT, lw=1.0, ms=6)
    else:
        arr(ax, (x0 + 0.2, 11.0), (x1 - 0.1, 11.0), INT, lw=1.0, ms=7)
arr(ax, (0.5, 30.5), (xs[0] - 0.1, 30.5), EXT, lw=1.0, ms=7)
arr(ax, (0.5, 11.0), (xs[0] - 0.1, 11.0), INT, lw=1.0, ms=7)
# multiplication node between stages 2 and 3 on interoceptive stream only
mx = xs[2] - 2.25
ax.add_patch(Circle((mx, 11.0), 1.25, fc='white', ec=INK, lw=0.8, zorder=4))
ax.text(mx, 11.0, '×', ha='center', va='center', fontsize=8, zorder=5)
box(ax, 28.5, -0.4, 34.0, 6.6, fc='#EEEEEE', ec=INK, lw=0.7, r=0.8)
ax.text(45.5, 4.0, r'Somatic marker $\hat{M}(c,a)$:  vmPFC → VIP$^{+}$ ⊣ SST$^{+}$', ha='center', fontsize=5.6, fontweight='bold')
ax.text(45.5, 1.2, r'$\Pi^{i}_{eff}=\Pi^{i}_{baseline}\cdot\exp(\beta_{SM}\cdot\hat{M}(c,a))$', ha='center', fontsize=6.0)
arr(ax, (mx, 6.2), (mx, 9.7), INK, lw=0.8, ms=6, ls='--')
# merge arrows into accumulator handled inside stage 4 (streams end at its edge)
dx, dy = 81.6, 21.5
ax.add_patch(Polygon([(dx - 5, dy), (dx, dy + 5.4), (dx + 5, dy), (dx, dy - 5.4)], closed=True, fc='white', ec=INK, lw=0.9))
ax.text(dx, dy, r'$S_t>\theta_t$?', ha='center', va='center', fontsize=7.0)
arr(ax, (xs[3] + W + 0.2, dy), (dx - 5.1, dy), INK, lw=1.0, ms=7)
ax.text(dx, dy + 10.4, 'allostatic threshold ' + r'$\theta_t$' + '\n(rises with metabolic cost)', ha='center', fontsize=5.6, va='center')
arr(ax, (dx, dy + 8.2), (dx, dy + 5.5), INK, lw=0.8, ms=6)
arr(ax, (dx, dy - 5.4), (dx, dy - 10.6), INK, lw=0.9, ms=6, ls='--')
ax.text(dx + 0.8, dy - 9.6, 'No: no ignition', fontsize=5.8, va='center')
ax.text(dx + 4.6, dy + 1.8, 'Yes', fontsize=6.0)
arr(ax, (dx + 5, dy), (88.4, dy), INK, lw=1.0, ms=7)
box(ax, 88.4, 12.5, 11.2, 18, fc='#EDE6F3', ec=INK, lw=0.8, r=1.2)
ax.add_patch(Circle((94.0, 28.0), 1.4, fc=INK))
ax.text(94.0, 28.0, '5', color='white', ha='center', va='center', fontsize=6.6, fontweight='bold')
ax.text(94.0, 23.6, 'Ignition /\nglobal\nbroadcast', ha='center', va='center', fontsize=6.4, fontweight='bold')
ax.text(94.0, 16.2, r'$B_t=1$' + '\nfrontoparietal–\nthalamic workspace', ha='center', va='center', fontsize=5.3)
save(fig, 'P1F1')
