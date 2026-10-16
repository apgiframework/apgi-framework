from style import *

ages = np.linspace(0, 27, 1000)
inflect = [(2, 'L1', '3.2 Hz (L0/L1)'), (7, 'L2', '0.024 Hz (L1/L2)'), (13, 'L3', r'1.8×10$^{-4}$ Hz (L2/L3)'), (25, 'L4', r'1.3×10$^{-6}$ Hz (L3/L4)')]
H0, H1 = 0.55, 0.90
steps = [0.07, 0.10, 0.10, 0.08]          # increments summing to 0.35
y = np.full_like(ages, H0)
for (a, _, _), s in zip(inflect, steps):
    y += s / (1 + np.exp(-(ages - a) / (0.35 + 0.05 * a)))
y = H0 + (y - y[0]) * (H1 - H0) / (y[-1] - y[0])

fig, ax = plt.subplots(figsize=(7.0, 3.3))
ax.plot(ages, y, color=OI['blue'], lw=2.0, label='Predicted trajectory (APGI developmental extension)')
for a, L, fcl in inflect:
    ya = np.interp(a, ages, y)
    ax.plot([a], [ya], 'o', color=OI['blue'], ms=5, zorder=4)
    ax.axvline(a, color=OI['blue'], lw=0.6, ls=':', ymax=(ya - 0.45) / (1.0 - 0.45))
    ax.annotate(f'{L} matures\n~{a} years\n{fcl}', (a, ya), (a, ya + 0.075), ha='center', fontsize=6.2,
                bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=OI['blue'], lw=0.6),
                arrowprops=dict(arrowstyle='-', lw=0.5, color=OI['blue']))
ax.axhline(0.5, color='#888888', lw=0.7, ls='--')
ax.text(26.8, 0.505, 'uncorrelated (α = 0.5)', fontsize=6.3, ha='right', va='bottom', color='#666666')
ax.text(0.3, 0.535, 'neonatal ≈ 0.55\n(Level 0 mature at birth)', fontsize=6.3, va='top')
ax.text(26.9, 0.82, 'adult ≈ 0.90', fontsize=6.3, ha='right')
ax.set_xlim(0, 27); ax.set_ylim(0.45, 1.05)
ax.set_xticks([0, 2, 5, 7, 10, 13, 16, 20, 25])
ax.set_xticklabels(['birth', '2', '5', '7', '10', '13', '16', '20', '25'])
ax.set_xlabel('Age (years; linear axis)')
ax.set_ylabel(r'Amplitude-envelope DFA exponent $\alpha_{DFA}$')
ax.legend(loc='upper left', frameon=False, fontsize=6.6)
ax.text(0.99, 0.02, 'Prediction only: no empirical data are plotted.', transform=ax.transAxes, ha='right', va='bottom', fontsize=6.0, color='#666666', style='italic')
save(fig, 'P3F6')
