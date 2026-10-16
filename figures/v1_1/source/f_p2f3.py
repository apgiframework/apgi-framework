from style import *

k, x0 = 4.0, 0.575
a = np.linspace(1e-4, 1 - 1e-4, 40000)
w = (x0 + np.log(a / (1 - a)) / k) / a
dw = np.gradient(w, a)
idx = np.where(np.diff(np.sign(dw)) != 0)[0]
i_lo, i_hi = sorted(idx, key=lambda i: a[i])          # lower fold (a small), upper fold (a large)
w_SN = w[i_hi]                                         # upper branch appears here
scale = 0.95 / w_SN
rho = w * scale
rho_on = rho[i_lo]
y_SN = a[i_hi]

fig = plt.figure(figsize=(7.2, 3.0))
ax = fig.add_axes([0.07, 0.15, 0.40, 0.75])
lower = a <= a[i_lo]; middle = (a > a[i_lo]) & (a < a[i_hi]); upper = a >= a[i_hi]
xmin, xmax = 0.6, 1.2
# shading: sub-threshold basin below separatrix (and everywhere before fold), ignition above
xs = np.linspace(xmin, xmax, 600)
sep = np.interp(xs, rho[middle][::-1], a[middle][::-1], left=np.nan, right=np.nan)
sep_full = np.where(xs < 0.95, 1.05, np.where(xs > rho_on, -0.01, sep))
ax.fill_between(xs, 0, sep_full, color=OI['sky'], alpha=0.22, lw=0)
ax.fill_between(xs, sep_full, 1.05, color=OI['verm'], alpha=0.14, lw=0)
m = rho <= xmax
ax.plot(rho[lower & m], a[lower & m], color=OI['blue'], lw=1.8, label='stable quiescent branch')
ax.plot(rho[upper & m], a[upper & m], color=OI['verm'], lw=1.8, label='stable ignited branch')
ax.plot(rho[middle], a[middle], color=INK, lw=1.0, ls='--', label='unstable branch (separatrix)')
# folds
ax.plot([0.95], [y_SN], 'o', color=INK, ms=4.5, zorder=5)
ax.plot([rho_on], [a[i_lo]], 'o', mfc='white', mec=INK, ms=4.5, zorder=5)
ax.annotate(r'$\rho_{SN}\approx 0.95$' + '\n(ignited state appears)', (0.95, y_SN), (0.70, 0.70), fontsize=6.6,
            arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
ax.annotate(r'$\rho_{on}\approx$' + f'{rho_on:.2f}' + '\n(quiescent state lost)', (rho_on, a[i_lo]), (1.065, 0.14), fontsize=6.6,
            arrowprops=dict(arrowstyle='-', lw=0.6, color=INK))
# hysteresis paths
arr(ax, (rho_on + 0.004, a[i_lo] + 0.03), (rho_on + 0.004, np.interp(rho_on, rho[upper], a[upper]) - 0.03), color=OI['verm'], lw=0.9, ms=7)
arr(ax, (0.95 - 0.004, y_SN - 0.03), (0.95 - 0.004, np.interp(0.95, rho[lower][::-1], a[lower][::-1]) + 0.03), color=OI['blue'], lw=0.9, ms=7)
ax.text(rho_on + 0.012, 0.42, 'onset\njump', fontsize=6.3, color=OI['verm'])
ax.text(0.905, 0.42, 'return\njump', fontsize=6.3, color=OI['blue'], ha='right')
ax.axvspan(0.7, 0.95, ymin=0, ymax=0.035, color=INK, alpha=0.5, lw=0)
ax.text(0.825, 0.045, r'baseline band $\rho_{res}\in[0.7, 0.95]$', fontsize=6.2, ha='center')
ax.text(1.19, 1.02, 'IGNITION BASIN', color=OI['verm'], fontsize=7, fontweight='bold', va='top', ha='right')
ax.text(0.62, 0.20, 'SUB-THRESHOLD BASIN', color=OI['blue'], fontsize=7, fontweight='bold')
ax.text(0.612, 0.50, r'$|y^{*}-y_{SN}|\propto\sqrt{\rho_{res}-\rho_{SN}}$' + '\nfinite jump at the fold', fontsize=6.3,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#999999', lw=0.5), transform=ax.transData, va='bottom')
ax.set_xlim(xmin, xmax); ax.set_ylim(0, 1.05)
ax.set_xlabel(r'Reservoir spectral radius $\rho_{res}$')
ax.set_ylabel(r'Steady-state activity $|y^{*}|$ (normalised)')
ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=6.2, handlelength=1.6)
panel(ax, 'A', -0.13)

# Panel B
bx = fig.add_axes([0.58, 0.15, 0.40, 0.75])
x = np.linspace(0, 2.5, 500)
cols = ['#9A9A9A', OI['sky'], OI['green'], OI['purple'], OI['verm']]
Pis = [0.3, 1, 3, 10, 30]; alphas = [2, 4, 7, 12, 20]
for P, al, c in zip(Pis, alphas, cols):
    y = 1 / (1 + np.exp(-al * (x - 1)))
    lw = 1.8 if al >= 10 else 1.1
    bx.plot(x, y, color=c, lw=lw, label=rf'$\Pi={P}$:  $\alpha_{{psy}}={al}$' )
bx.axvline(1, color=INK, lw=0.6, ls=':')
bx.text(1.03, 0.04, r'$S_t=\theta_t$', fontsize=6.8)
bx.set_xlim(0, 2.5); bx.set_ylim(-0.02, 1.02)
bx.set_xlabel(r'Normalised drive $S_t/\theta_t$')
bx.set_ylabel('Ignition probability')
bx.legend(loc='lower right', frameon=False, fontsize=6.3, title='Precision (illustrative)', title_fontsize=6.5)
bx.text(2.47, 0.55, r'$\alpha_{psy}\geq 10$: predicted' + '\n' + r'5–10: inconclusive' + '\n' + r'$<5$: falsifies (OSF H3)',
        fontsize=6.2, ha='right', va='center', bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#999999', lw=0.5))
panel(bx, 'B', -0.13)
save(fig, 'P2F3')
print('rho_on', rho_on, 'y_SN', y_SN)
