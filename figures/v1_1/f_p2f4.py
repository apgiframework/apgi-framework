from style import *
import mask_model as m

m.P['G'] = 0.9671630859375
crit = m.crit_isi()
fig = plt.figure(figsize=(7.2, 3.0))
ax = fig.add_axes([0.07, 0.16, 0.42, 0.72])
conds = [(30, OI['blue'], 'ISI 30 ms: collapses (unconscious)', '-'),
         (crit - 1.0, OI['orange'], f'ISI ≈ {crit:.0f} ms (critical): ±1 ms decides the outcome', '-'),
         (crit + 1.0, OI['orange'], None, '--'),
         (180, OI['green'], 'ISI 180 ms: ignites (conscious)', '-')]
ax.axvspan(0, 50, color='#BBBBBB', alpha=0.35, lw=0)
ax.text(25, 0.10, 'target', ha='center', fontsize=6.3)
seen=set()
for isi, c, lab, ls in conds:
    t, S, r = m.sim(isi)
    m0 = 50 + isi
    ax.plot(t, S, color=c, lw=1.4, ls=ls, label=lab)
    if round(m0/10) in seen: continue
    seen.add(round(m0/10))
    ax.axvspan(m0, m0 + 50, ymin=0.0, ymax=0.035, color=c, alpha=0.9, lw=0)
    ax.text(m0 + 25, 0.10, 'mask', ha='center', fontsize=6, color=c)
ax.axhline(1.0, color=INK, lw=0.7, ls='--')
ax.text(395, 1.04, r'$\theta_t$', fontsize=7.5)
ax.set_xlim(0, 400); ax.set_ylim(0, 2.2)
ax.set_xlabel('Time from target onset (ms)')
ax.set_ylabel(r'Accumulated signal $S_t$ (units of $\theta_t$)')
ax.legend(loc='upper left', bbox_to_anchor=(0.14, 1.02), frameon=False, fontsize=6.1)
panel(ax, 'A', -0.12)

bx = fig.add_axes([0.60, 0.16, 0.38, 0.72])
rho_ref = m.P['rho']
xs_rho = np.array([0.70, 0.75, 0.80, 0.83, 0.86, 0.88, 0.90, 0.91, 0.92, 0.93])
ci_rho = np.array([m.crit_isi(rho=r) for r in xs_rho])
xs = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0])
ci_pi = np.array([m.crit_isi(Pi=v) for v in xs])
xs_th = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
ci_th = np.array([m.crit_isi(theta=v) for v in xs_th])
bx.plot(xs, ci_pi, 'o-', color=OI['purple'], ms=3, lw=1.2, label=r'target precision $\Pi^{e}_{target}/\Pi_{ref}$')
bx.plot(xs_th, ci_th, 's-', color=OI['green'], ms=3, lw=1.2, label=r'threshold $\theta_t/\theta_{ref}$')
bx.plot(xs_rho / rho_ref, ci_rho, '^-', color=OI['blue'], ms=3, lw=1.2, label=r'spectral radius $\rho_{res}/\rho_{ref}$ ($\rho_{ref}=0.90$)')
bx.plot([1], [crit], 'o', mfc='white', mec=INK, ms=6, zorder=5)
bx.annotate(f'reference\n(1.0, {crit:.0f} ms)', (1, crit), (1.30, 105), fontsize=6.3, arrowprops=dict(arrowstyle='-', lw=0.5))
bx.set_xlim(0.5, 2.05); bx.set_ylim(0, 210)
bx.set_xlabel('Parameter value / reference value')
bx.set_ylabel('Critical ISI (ms)')
bx.legend(loc='upper right', frameon=False, fontsize=6.2)
panel(bx, 'B', -0.14)
save(fig, 'P2F4', 'Reduced-model simulation', 'Illustrative masking model with fixed reference gain; critical ISIs require empirical calibration.')
print('crit', crit, 'rho', dict(zip(xs_rho, np.round(ci_rho, 1))), 'pi', dict(zip(xs, np.round(ci_pi, 1))), 'th', dict(zip(xs_th, np.round(ci_th, 1))))
