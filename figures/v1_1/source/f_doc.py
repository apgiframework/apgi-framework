"""Master figure for Protocol 7 (used as Paper 3 Fig 5 and Protocols Fig P7)."""
from style import *
rng = np.random.default_rng(7)
groups = [  # name, N, PCI mean, sd, HEP mean, sd, colour
    ('VS/UWS', 30, 0.13, 0.045, 0.6, 0.35, OI['verm']),
    ('MCS', 30, 0.36, 0.050, 1.4, 0.45, OI['orange']),
    ('EMCS', 20, 0.46, 0.055, 2.2, 0.55, OI['sky']),
    ('Healthy controls', 30, 0.56, 0.055, 3.0, 0.60, OI['blue']),
]

LAB = {'VS/UWS': (0.13, 1.05, 'center', 'bottom'), 'MCS': (0.36, 0.90, 'center', 'top'),
       'EMCS': (0.47, 1.60, 'center', 'top'), 'Healthy controls': (0.625, 3.0, 'left', 'center')}

def draw(name):
    rng = np.random.default_rng(7)
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.07, 0.15, 0.44, 0.75])
    for g, n, pm, ps, hm, hs, c in groups:
        x = rng.normal(pm, ps, n); y = rng.normal(hm, hs, n)
        ax.scatter(x, y, s=7, color=c, alpha=0.55, lw=0)
        ax.add_patch(Ellipse((pm, hm), 2 * ps, 2 * hs, fc='none', ec=c, lw=1.2))
        ax.plot(pm, hm, '+', color=c, ms=7, mew=1.5)
        lx, ly, ha, va = LAB[g]
        ax.text(lx, ly, f'{g}\nN = {n}', color=c, ha=ha, va=va, fontsize=6.2, fontweight='bold')
    ax.axvline(0.31, color=INK, lw=0.9, ls='--')
    ax.text(0.302, 4.5, 'PCI* = 0.31\n(empirical cut-off;\nCasarotto et al., 2016)', fontsize=5.8, va='top', ha='right')
    # ordinal cut-points of a joint linear predictor eta = PCI/0.1 + HEP/0.6 (illustrative)
    wx, wy = 1 / 0.1, 1 / 0.6
    etas = [wx * g[2] + wy * g[4] for g in groups]
    xs = np.linspace(0, 0.8, 50)
    for k in range(3):
        cut = 0.5 * (etas[k] + etas[k + 1])
        ax.plot(xs, (cut - wx * xs) / wy, color='#777777', lw=0.8, ls=':')
    ax.text(0.79, 0.12, 'dotted: ordinal joint-model\ncut-points (illustrative)', fontsize=5.6, ha='right', color='#555555')
    ax.set_xlim(0, 0.8); ax.set_ylim(-0.6, 4.6)
    ax.set_xlabel('Perturbational complexity index (PCI)')
    ax.set_ylabel('Heartbeat-evoked potential amplitude (µV)')
    ax.text(0.01, -0.5, 'Ellipses: group mean ± 1 SD; points: simulated illustrative participants', fontsize=5.4, color='#555555')
    panel(ax, 'A', -0.13)
    bx = fig.add_axes([0.57, 0.15, 0.42, 0.75]); bx.set_xlim(0, 100); bx.set_ylim(0, 100); bx.axis('off')
    tps = [(37, 'Baseline\n(week 0)'), (62, '3 months\n(± 2 weeks)'), (87, '6 months\n(± 2 weeks)')]
    arr(bx, (24, 86), (100, 86), INK, lw=1.0, ms=8)
    for x, lab in tps:
        bx.plot(x, 86, 'o', mfc='white', mec=INK, ms=6)
        bx.text(x, 90, lab, ha='center', va='bottom', fontsize=6.0, fontweight='bold')
    for j, (g, n, *_, c) in enumerate(groups):
        y = 72 - j * 14
        bx.text(0, y, g.replace('Healthy controls', 'Healthy\ncontrols') + f'\n(N = {n})', fontsize=5.9, color=c, fontweight='bold', va='center')
        for x, _ in tps:
            for k, (lab, fc) in enumerate((('HEP', '#DCE9F5'), ('PCI', '#E0F0EA'), ('CRS-R', '#F6E5D8'))):
                x0 = x - 11.4 + k * 7.7
                bx.add_patch(FancyBboxPatch((x0, y - 3.4), 7.1, 6.8, boxstyle='round,pad=0,rounding_size=1', fc=fc, ec='#888888', lw=0.4))
                bx.text(x0 + 3.55, y, lab, ha='center', va='center', fontsize=5.0)
    bx.text(50, 6, 'HEP: EEG with heartbeat-evoked potentials · PCI: TMS-EEG perturbational\ncomplexity · CRS-R: Coma Recovery Scale–Revised. All participants, all time points (N = 110).',
            ha='center', fontsize=5.5)
    panel(bx, 'B', -0.02, 1.0)
    save(fig, name)

draw('P3F5')
draw('PRF8')
