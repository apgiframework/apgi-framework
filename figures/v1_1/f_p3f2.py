from style import *

tau0 = 0.05; k = 133.0
taus = tau0 * k ** np.arange(5)              # 0.05 s ... ~1.56e7 s
names = ['Level 0', 'Level 1', 'Level 2', 'Level 3', 'Level 4']
fc = 1 / (2 * np.pi * taus)
f = np.logspace(-9, 2, 4000)
def lor(tau):   # equal-variance OU (sigma^2 = 1)
    return 4 * tau / (1 + (2 * np.pi * f * tau) ** 2)
comps = [lor(t) for t in taus]
tot = np.sum(comps, axis=0)
part = np.sum(comps[:3], axis=0)
# fitted slopes
def slope(F, S, lo, hi):
    mm = (F >= lo) & (F <= hi)
    return np.polyfit(np.log10(F[mm]), np.log10(S[mm]), 1)
b_tot, a_tot = slope(f, tot, 1e-7, 1.0)
b_part, a_part = slope(f, part, 1e-3, 1.0)
res = np.log10(tot) - (a_tot + b_tot * np.log10(f))
mm = (f >= 1e-7) & (f <= 1.0)
ripple_db = 10 * (res[mm].max() - res[mm].min())

fig = plt.figure(figsize=(7.2, 3.6))
ax = fig.add_axes([0.08, 0.30, 0.90, 0.62])
cols = [OI['verm'], OI['blue'], OI['green'], OI['purple'], OI['orange']]
ax.axvspan(0.005, 100, color='#DDDDDD', alpha=0.5, lw=0)
ax.text(0.9, 3e-6, 'DC-coupled acquisition\n0.005–100 Hz', fontsize=6.3, ha='center', color='#555555')
for c, n, t, comp in zip(cols, names, taus, comps):
    ax.loglog(f, comp, '--', color=c, lw=1.0, label=f'{n}')
ax.loglog(f, tot, color=INK, lw=2.0, label=r'$S_{total}$ (Levels 0–4)')
ax.loglog(f, part, color='#888888', lw=1.6, label='partial hierarchy (Levels 0–2)')
labs = ['3.2 Hz\n(L0/L1)', '0.024 Hz\n(L1/L2)', r'1.8×10$^{-4}$ Hz' + '\n(L2/L3)', r'1.3×10$^{-6}$ Hz' + '\n(L3/L4)']
for i, (x, lab) in enumerate(zip(fc[:4], labs)):
    ax.axvline(x, color=INK, lw=0.8 if i < 2 else 0.5, ls='-' if i < 2 else ':', alpha=0.8)
    ax.text(x, 3e8, lab, fontsize=6.2, ha='center', va='bottom')
ax.set_xlim(1e-9, 1e2); ax.set_ylim(1e-6, 3e8)
ax.set_xlabel('Frequency f (Hz)')
ax.set_ylabel('Power P(f) (arbitrary units)')
ax.legend(loc='lower left', fontsize=6.2, frameon=True, framealpha=0.9, ncol=2)

ax.annotate(f'mean slope {b_tot:.2f} over $10^{{-7}}$–1 Hz\n(≈{ripple_db:.0f} dB peak-to-peak ripple)', (1e-5, 10 ** (a_tot + b_tot * -5) ),
            (3e-4, 3e5), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=0.5))
ax.annotate(f'partial hierarchy: slope {b_part:.2f}\nover $10^{{-3}}$–1 Hz', (0.03, 10 ** (a_part + b_part * np.log10(0.03))),
            (0.3, 1e3), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=0.5))
# table
tx = fig.add_axes([0.08, 0.0, 0.90, 0.16]); tx.axis('off'); tx.set_xlim(0,1); tx.set_ylim(0,1)
rows = [['Level', '0', '1', '2', '3', '4'],
        [r'Time constant $\tau_\ell$', '50 ms', '6.6 s', '15 min', '1.4 d', '6 mo'],
        [r'Corner $f_{c,\ell}=1/(2\pi\tau_\ell)$', '3.2 Hz', '0.024 Hz', r'1.8×10$^{-4}$ Hz', r'1.3×10$^{-6}$ Hz', r'1.0×10$^{-8}$ Hz']]
xs = [0.0, 0.30, 0.44, 0.58, 0.72, 0.86]
for r_i, row in enumerate(rows):
    for c_i, (x, v) in enumerate(zip(xs, row)):
        tx.text(x, 0.85 - r_i * 0.36, v, fontsize=6.6, fontweight='bold' if r_i == 0 or c_i == 0 else 'normal',
                color=cols[c_i - 1] if (r_i == 0 and c_i > 0) else INK)
tx.plot([0, 1], [0.70, 0.70], color='#999999', lw=0.5, transform=tx.transAxes)
save(fig, 'P3F2', 'Analytical OU spectrum', 'Equal stationary variance; geometric poles are conditional model assumptions, not measured neural timescales.')
print('b_tot', b_tot, 'b_part', b_part, 'ripple_db', ripple_db, 'fc', fc)
