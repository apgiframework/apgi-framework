from style import *
from nilearn import plotting
rng = np.random.default_rng(11)

def corr_data(n, r, mx, sx, my, sy):
    z1 = rng.normal(size=n); z2 = r * z1 + np.sqrt(1 - r ** 2) * rng.normal(size=n)
    return mx + sx * z1, my + sy * z2

def regline(ax, x, y, c):
    b, a = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 50)
    n = len(x); yhat = a + b * x; s = np.sqrt(np.sum((y - yhat) ** 2) / (n - 2))
    se = s * np.sqrt(1 / n + (xs - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2))
    ax.plot(xs, a + b * xs, color=c, lw=1.3); ax.fill_between(xs, a + b * xs - 1.96 * se, a + b * xs + 1.96 * se, color=c, alpha=0.15, lw=0)

# ---------------- P0 ----------------
def prf1():
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6)); fig.subplots_adjust(wspace=0.42, left=0.07, right=0.99, bottom=0.2, top=0.82)
    ax = axs[0]
    x, y = corr_data(115, 0.40, 0.6, 0.75, 1.5, 1.0)
    ax.scatter(x, y, s=7, color=OI['verm'], alpha=0.7, lw=0); regline(ax, x, y, OI['verm'])
    ax.set_title('Pred 0.A: r ≈ 0.40, N = 115\n(retain if r > 0.35)', fontsize=6.3, color=OI['verm'])
    ax.set_xlabel("Interoceptive d′\n(heartbeat discrimination)"); ax.set_ylabel('HEP amplitude (µV; 250–400 ms post-R)')
    panel(ax, 'A', -0.3)
    ax = axs[1]
    n = 40; pl = rng.normal(1.6, 0.8, n); ph = pl * 1.22 + rng.normal(0, 0.25, n)
    for a, b in zip(pl, ph): ax.plot([0, 1], [a, b], color='#AAAAAA', lw=0.5)
    ax.scatter(np.zeros(n), pl, s=6, color='#777777', zorder=3); ax.scatter(np.ones(n), ph, s=6, color=OI['green'], zorder=3)
    for xi, v, c in ((-0.18, pl, '#555555'), (1.18, ph, OI['green'])):
        ax.errorbar([xi], [v.mean()], yerr=[v.std(ddof=1) / np.sqrt(n)], fmt='o', color=c, ms=4, capsize=3, lw=1)
    ax.set_xticks([0, 1]); ax.set_xticklabels(['Placebo', 'Physostigmine']); ax.set_xlim(-0.45, 1.45)
    ax.set_ylabel('HEP amplitude (µV)')
    ax.set_title('Pred 0.B: ≥ 15% increase, d ≥ 0.50\n(40 of 115 participants shown)', fontsize=6.3, color=OI['green'])
    panel(ax, 'B', -0.3)
    ax = axs[2]
    x, y = corr_data(150, 0.30, 0.0, 1.0, 1.5, 1.1)
    ax.scatter(x, y, s=6, color=OI['blue'], alpha=0.6, lw=0); regline(ax, x, y, OI['blue'])
    ax.set_title('Pred 0.C: within-participant r ≈ 0.30 (retain if r > 0.30)\none representative participant, 150 trials', fontsize=6.0, color=OI['blue'])
    ax.set_xlabel('Anterior-insula BOLD\n(trial-wise, z-scored)'); ax.set_ylabel('HEP amplitude (µV)')
    panel(ax, 'C', -0.3)
    save(fig, 'PRF1')

# ---------------- P1 ----------------
def prf2():
    fig = plt.figure(figsize=(7.2, 3.4))
    ax = fig.add_axes([0.13, 0.62, 0.85, 0.30])
    t = np.linspace(-1100, 1400, 4000)
    def ecg(t):
        y = np.zeros_like(t)
        for R in (-1000, 0, 1000):
            y += 1.0 * np.exp(-((t - R) / 9) ** 2) - 0.15 * np.exp(-((t - R - 25) / 12) ** 2) + 0.25 * np.exp(-((t - R - 300) / 45) ** 2) + 0.1 * np.exp(-((t - R + 160) / 30) ** 2)
        return y
    ax.plot(t, ecg(t), color=INK, lw=0.8)
    for R in (-1000, 0, 1000):
        ax.text(R, 1.12, 'R' if R == 0 else ('R$_{-1}$' if R < 0 else 'R$_{+1}$'), ha='center', fontsize=6.5)
    ax.axvspan(-750, -600, color=OI['blue'], alpha=0.22, lw=0); ax.text(-675, -0.42, 'HEP\n250–400 ms\npost-R$_{-1}$', ha='center', fontsize=5.6, color=OI['blue'], va='top')
    ax.axvspan(250, 400, color=OI['verm'], alpha=0.22, lw=0); ax.text(325, -0.42, 'systole\nR+250 ms →\nT-wave end', ha='center', fontsize=5.6, color=OI['verm'], va='top')
    ax.axvspan(500, 900, color=OI['green'], alpha=0.18, lw=0); ax.text(700, -0.42, 'diastole\nT-wave end + 100 ms →\nnext R − 100 ms', ha='center', fontsize=5.6, color=OI['green'], va='top')
    ax.set_xlim(-1100, 1400); ax.set_ylim(-1.3, 1.3); ax.axis('off')
    fig.text(0.13, 0.95, 'ECG-anchored cardiac phases (defined per participant; illustrated for RR = 1,000 ms)', fontsize=6.8, fontweight='bold')
    bx = fig.add_axes([0.13, 0.12, 0.85, 0.38])
    rowsy = {'systolic trial': 1.0, 'diastolic trial': 0.0}
    for lab, on, c in (('systolic trial', 300, OI['verm']), ('diastolic trial', 700, OI['green'])):
        y = rowsy[lab]
        bx.add_patch(Rectangle((on, y - 0.18), 50, 0.36, fc=c, ec=INK, lw=0.5))
        bx.text(on + 25, y - 0.24, 'Gabor', ha='center', va='top', fontsize=5.8)
        bx.add_patch(Rectangle((on + 250, y - 0.10), 250, 0.20, fc=OI['purple'], alpha=0.45, ec='none'))
        bx.text(on + 375, y - 0.14, 'P3b: 250–500 ms after stimulus', ha='center', va='top', fontsize=5.6, color='#7A3E6A')
        bx.add_patch(Rectangle((on + 50, y + 0.12), 750, 0.06, fc=OI['yellow'], alpha=0.8, ec='none'))
        bx.text(on + 60, y + 0.30, 'response window →', fontsize=5.6, va='center')
        bx.add_patch(Rectangle((-750, y - 0.10), 150, 0.20, fc=OI['blue'], alpha=0.35, ec='none'))
        bx.text(-1090, y, lab, va='center', fontsize=6.3, fontweight='bold', color=c)
    bx.set_xlim(-1100, 1400); bx.set_ylim(-0.5, 1.5); bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xticks([-1000, -750, -600, 0, 300, 700, 1000])
    bx.set_xticklabels(['−1000', '−750', '−600', 'R', '300', '700', '1000'], fontsize=6)
    bx.set_xlabel('Time relative to the R-peak of the stimulus heartbeat (ms)')
    fig.text(0.13, 0.555, 'Timing identical in interoceptive-focus, exteroceptive-focus and dual-task\nconditions; only the attentional instruction differs. Stimulus contrast is QUEST-titrated per phase bin.',
            ha='left', va='top', fontsize=5.8, style='italic')
    save(fig, 'PRF2')

# ---------------- P2 ----------------
def prf3():
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.0)); fig.subplots_adjust(wspace=0.32, hspace=0.55, left=0.08, right=0.98, top=0.95, bottom=0.08)
    ax = axs[0, 0]; tt = np.arange(1, 301)
    agents = [('Full APGI', 0.85, 28, OI['blue']), (r'$\beta_{SM}$ lesion', 0.75, 70, OI['verm']),
              (r'$\Pi^{i}$ lesion', 0.70, 90, OI['orange']), ('learning-rate lesion', 0.62, 120, OI['purple'])]
    ax.axvspan(50, 80, color=OI['sky'], alpha=0.25, lw=0)
    ax.text(65, 0.98, 'human IGT\nconvergence\n(50–80 trials)', ha='center', va='top', fontsize=5.6)
    for nm, asym, tau, c in agents:
        p = 1 / 3 + (asym - 1 / 3) * (1 - np.exp(-tt / tau))
        ax.plot(tt, p, color=c, lw=1.3, label=nm); ax.fill_between(tt, p - 0.025, p + 0.025, color=c, alpha=0.15, lw=0)
    ax.axhline(1 / 3, color='#888888', ls='--', lw=0.9, label='random baseline')
    ax.set_xlim(0, 300); ax.set_ylim(0.25, 1.0)
    ax.set_xlabel('Trial'); ax.set_ylabel('P(optimal choice)\n(10-trial moving average)')
    ax.legend(fontsize=5.8, frameon=False, loc='lower right'); panel(ax, 'A', -0.17)
    ax = axs[0, 1]; lags = np.arange(-5, 6); cc = [0.08, 0.28, 0.56, 0.78, 0.62, 0.30, 0.10, -0.06, -0.16, -0.20, -0.18]
    ax.axhline(0, color='#999999', lw=0.6); ax.axvline(0, color='#999999', lw=0.6, ls=':')
    ax.plot(lags, cc, 'o-', color=OI['blue'], ms=3.5, lw=1.2)
    for l, v in zip(lags, cc): ax.text(l, v + 0.06, f'{v:.2f}', ha='center', fontsize=5.4)
    ax.set_xlabel(r'Lag (trials; negative = $\hat{M}$ leads $B_t$)'); ax.set_ylabel(r'Cross-correlation $\hat{M}$ × $B_t$')
    ax.set_ylim(-0.4, 1.0); ax.text(-5, 0.92, r'peak at −2: $\hat{M}$ leads ignition by ≥ 1 trial (Pred 2.C)', fontsize=5.8)
    panel(ax, 'B', -0.17)
    ax = axs[1, 0]; n = 40
    pre = np.clip(rng.normal(0.52, 0.10, n), 0.2, 0.95); post = np.clip(pre + rng.normal(0.29, 0.08, n), 0.3, 1.0)
    for a, b in zip(pre, post): ax.plot([0, 1], [a, b], color='#BBBBBB', lw=0.5)
    ax.scatter(np.zeros(n), pre, s=6, color='#777777', zorder=3); ax.scatter(np.ones(n), post, s=6, color=OI['purple'], zorder=3)
    for xi, v, c in ((-0.18, pre, '#555555'), (1.18, post, OI['purple'])):
        ax.errorbar([xi], [v.mean()], yerr=[v.std(ddof=1) / np.sqrt(n)], fmt='o', color=c, ms=4, capsize=3)
    ax.set_xticks([0, 1]); ax.set_xticklabels([r'pre-ignition ($S_t<\theta_t$)', r'post-ignition ($B_t=1$)'], fontsize=6.3)
    ax.set_xlim(-0.45, 1.45); ax.set_ylim(0, 1.05); ax.set_ylabel('Normalised action-selection entropy\n(H / log 3; 3-armed bandit)')
    ax.text(0.5, 1.0, 'exploratory (Pred 2.F-flex)', ha='center', va='top', fontsize=5.8, transform=ax.transAxes)
    panel(ax, 'C', -0.17)
    ax = axs[1, 1]; m = ['APGI\n(full model)', 'Standard\nPP', 'GNWT-only']; bic = [512, 752, 972]
    ax.bar(range(3), bic, color=[OI['blue'], '#9A9A9A', OI['orange']], width=0.6)
    for i, b in enumerate(bic): ax.text(i, b + 15, str(b), ha='center', fontsize=6)
    for j, (k, lab) in enumerate(((1, 'ΔBIC = 240'), (2, 'ΔBIC = 460'))):
        yb = 1040 + j * 100
        ax.plot([0, 0, k, k], [yb - 30, yb, yb, bic[k] + 60], color=INK, lw=0.7); ax.text(k / 2, yb + 10, lab, ha='center', fontsize=6)
    ax.set_xticks(range(3)); ax.set_xticklabels(m, fontsize=6.4); ax.set_ylim(0, 1320)
    ax.set_ylabel('BIC on the fitting sample (lower is better)')
    ax.text(-0.4, 1290, 'criterion: ΔBIC ≥ 10 (very strong evidence; Pred 2.E)', ha='left', va='top', fontsize=5.8)
    panel(ax, 'D', -0.17)
    save(fig, 'PRF3')

# ---------------- P3 ----------------
def bracket(ax, x0, x1, y, txt):
    ax.plot([x0, x0, x1, x1], [y - 0.02 * ax.get_ylim()[1], y, y, y - 0.02 * ax.get_ylim()[1]], color=INK, lw=0.7)
    ax.text(0.5 * (x0 + x1), y + 0.01 * ax.get_ylim()[1], txt, ha='center', va='bottom', fontsize=5.8)

def prf4():
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7)); fig.subplots_adjust(wspace=0.45, left=0.08, right=0.99, bottom=0.24, top=0.80)
    ax = axs[0]; ax.set_ylim(-0.05, 0.80)
    vals = [(0, 0.48, 0.07, OI['blue'], ''), (1, 0.20, 0.06, '#BBBBBB', '////'), (2.6, 0.06, 0.05, OI['blue'], ''), (3.6, 0.19, 0.06, '#BBBBBB', '////')]
    for x, v, e, c, h in vals:
        ax.bar(x, v, 0.85, color=c, hatch=h, edgecolor='white' if h else c, yerr=e, capsize=2.5, error_kw=dict(lw=0.8))
        ax.text(x, v + e + 0.015, f'{v:.2f}', ha='center', fontsize=5.8)
    ax.axhline(0, color=INK, lw=0.6)
    bracket(ax, 0, 2.6, 0.64, 'predicted contrast')
    ax.set_xticks([0.5, 3.1]); ax.set_xticklabels(['Anticipation\n(−3000 to 0 ms)', 'Outcome\n(0 to 2000 ms)'], fontsize=6.2)
    ax.set_ylabel('PPI coupling (seed: vmPFC; a.u.)')
    ax.set_title('Pred 3.B: coupling specificity', fontsize=7)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=OI['blue'], label='vmPFC–aINS'), Patch(fc='#BBBBBB', hatch='////', ec='white', label='vmPFC–pIC')], fontsize=5.6, frameon=False, loc='center right')
    panel(ax, 'A', -0.3, 1.1)
    ax = axs[1]; ax.set_ylim(-0.1, 1.40)
    for x, v, e in ((0, 0.92, 0.12), (1, 0.12, 0.09)):
        ax.bar(x, v, 0.6, color=OI['blue'], yerr=e, capsize=2.5, error_kw=dict(lw=0.8)); ax.text(x, v + e + 0.03, f'{v:.2f}', ha='center', fontsize=5.8)
    ax.axhline(0, color=INK, lw=0.6); bracket(ax, 0, 1, 1.18, 'predicted contrast')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['Option expected\nvalue (valence)', 'Sensory\ncontrast'], fontsize=6.2)
    ax.set_ylabel('vmPFC BOLD (β, a.u.)'); ax.set_title('Pred 3.C: vmPFC tracks value', fontsize=7)
    panel(ax, 'B', -0.3, 1.1)
    ax = axs[2]; ax.set_ylim(-0.08, 0.72)
    for x, v, e in ((0, 0.46, 0.08), (1, 0.01, 0.06)):
        ax.bar(x, v, 0.6, color=OI['blue'], yerr=e, capsize=2.5, error_kw=dict(lw=0.8)); ax.text(x, v + e + 0.02, f'{v:.2f}', ha='center', fontsize=5.8)
    ax.axhline(0, color=INK, lw=0.6); bracket(ax, 0, 1, 0.61, 'predicted contrast')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['Long foreperiod\n(2000–4000 ms)', 'No foreperiod'], fontsize=6.2)
    ax.set_ylabel('vmPFC–aINS PPI (a.u.)'); ax.set_title('Pred 3.D: anticipatory retrieval', fontsize=7)
    panel(ax, 'C', -0.3, 1.1)
    fig.text(0.5, 0.015, 'Bars: predicted group means ± predicted SEM (illustrative pre-data values).', ha='center', fontsize=5.8, style='italic')
    save(fig, 'PRF4')

# ---------------- P4 ----------------
def prf5():
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6)); fig.subplots_adjust(wspace=0.45, left=0.08, right=0.99, bottom=0.2, top=0.88)
    HL, NE = OI['verm'], '#888888'
    for ax, (hl, ne, e, yl, lim) in zip(axs[:2], (((2.50, 1.90), (2.40, 2.30), 0.12, "Perceptual sensitivity d′", (1.5, 2.8)),
                                                ((8.8, 6.9), (8.1, 7.9), 0.6, 'P3b amplitude (µV)', (5.5, 10.0)))):
        ax.errorbar([0, 1], hl, yerr=e, color=HL, marker='o', ms=4, capsize=3, lw=1.3, label='high interoceptive load')
        ax.errorbar([0, 1], ne, yerr=e, color=NE, marker='o', ms=4, capsize=3, lw=1.3, label='neutral exteroceptive')
        ax.set_xticks([0, 1]); ax.set_xticklabels(['Rested', 'Depleted']); ax.set_xlim(-0.3, 1.3); ax.set_ylim(*lim)
        ax.set_ylabel(yl); ax.set_xlabel('Metabolic state')
        ax.text(0.03, 0.04, 'State × Load interaction\n' + r'confirmatory $\eta_p^2\geq0.06$', transform=ax.transAxes, fontsize=5.8)
    axs[0].legend(fontsize=5.8, frameon=False, loc='upper right')
    panel(axs[0], 'A', -0.3); panel(axs[1], 'B', -0.3)
    ax = axs[2]
    ax.bar([0, 1], [0.12, 0.09], 0.55, color=[HL, '#E59A73'], yerr=[[0.03, 0.02], [0.03, 0.02]], capsize=3, error_kw=dict(lw=0.9))
    ax.axhline(0.06, color=INK, ls='--', lw=0.8); ax.text(-0.45, 0.185, r'dashed: $\eta_p^2=0.06$, confirmatory effect-size floor', fontsize=5.6, ha='left', va='top')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['unadjusted', '+ pupil (trial)\n+ RMSSD (block)'], fontsize=6.2)
    ax.set_ylabel(r'Interaction effect size $\eta_p^2$'); ax.set_ylim(0, 0.2); ax.set_xlim(-0.5, 1.5)
    ax.set_title('Interaction survives arousal covariates', fontsize=7)
    panel(ax, 'C', -0.3)
    save(fig, 'PRF5')

# ---------------- P5 ----------------
def prf6():
    fig = plt.figure(figsize=(7.2, 5.0))
    ax = fig.add_axes([0.0, 0.62, 0.60, 0.34])
    d = plotting.plot_glass_brain(None, display_mode='lzr', axes=ax, annotate=False)
    T = [((34, 14, 0), OI['verm']), ((-44, 36, 20), OI['blue']), ((28, -60, 46), OI['purple']), ((-28, -60, 46), OI['purple']), ((0, -30, 70), '#777777')]
    for c, col in T: d.add_markers([c], marker_color=col, marker_size=30)
    fig.text(0.01, 0.985, 'A', fontsize=11, fontweight='bold', va='top')
    lx = fig.add_axes([0.61, 0.62, 0.38, 0.34]); lx.axis('off'); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
    items = [('aINS (R) [34, 14, 0] — tFUS', OI['verm']), ('dlPFC (L) [−44, 36, 20] — TMS', OI['blue']),
             ('PPC [±28, −60, 46] — TMS', OI['purple']), ('vertex sham [0, −30, 70] — TMS', '#777777')]
    for i, (t, c) in enumerate(items):
        lx.plot(0.03, 0.92 - i * 0.13, 'o', color=c, ms=5.5); lx.text(0.08, 0.92 - i * 0.13, t, fontsize=6.2, va='center')
    lx.text(0.0, 0.30, 'PCI is measured with a fixed TMS probe before\nand after each target block (OSF H12).\nEngagement gate: aINS depth 3–4 cm; > 20% gate\nfailure reclassifies the cohort as exploratory.', fontsize=5.8, va='top')
    vals = {'aINS': (0.42, OI['verm']), 'dlPFC': (0.44, OI['blue']), 'PPC': (0.43, OI['purple']), 'vertex\n(sham)': (0.52, '#999999')}
    bx = fig.add_axes([0.08, 0.38, 0.38, 0.19])
    for i, (k, (v, c)) in enumerate(vals.items()):
        bx.bar(i, v, 0.6, color=c, yerr=0.02, capsize=2.5)
        pct = '' if 'vertex' in k else '\n(' + f'{(v - 0.52) / 0.52 * 100:+.0f}'.replace('-', '−') + '%)'
        bx.text(i, v + 0.03, f'{v:.2f}{pct}', ha='center', fontsize=5.6)
    bx.axhline(0.31, color=INK, ls='--', lw=0.8); bx.text(-0.45, 0.715, 'dashed: PCI* = 0.31 (Casarotto et al., 2016)', ha='left', va='top', fontsize=5.5)
    bx.set_xticks(range(4)); bx.set_xticklabels(list(vals.keys()), fontsize=6.2); bx.set_ylim(0, 0.72); bx.set_ylabel('PCI')
    bx.set_title('Pred 5.A: PCI relative to vertex', fontsize=7); panel(bx, 'B', -0.22, 1.05)
    cx = fig.add_axes([0.58, 0.38, 0.40, 0.19])
    cv = {'aINS': (0.02, OI['verm']), 'dlPFC': (0.35, OI['blue']), 'PPC': (0.32, OI['purple']), 'vertex\n(sham)': (0.36, '#999999')}
    for i, (k, (v, c)) in enumerate(cv.items()):
        cx.bar(i, v, 0.6, color=c, yerr=0.05, capsize=2.5); cx.text(i, v + 0.065, f'{v:.2f}', ha='center', fontsize=5.6)
    cx.axhline(0, color=INK, lw=0.6)
    cx.set_xticks(range(4)); cx.set_xticklabels(list(cv.keys()), fontsize=6.2); cx.set_ylim(-0.1, 0.62); cx.set_ylabel(r'HEP–P3b coupling ($r$)')
    cx.set_title('Pred 5.B: double dissociation', fontsize=7); panel(cx, 'C', -0.2, 1.05)
    cx.text(1.5, 0.605, 'aINS abolishes coupling; dlPFC and PPC preserve it while reducing PCI', ha='center', va='top', fontsize=5.5, style='italic')
    dx = fig.add_axes([0.08, 0.06, 0.55, 0.19])
    tert = [1, 2, 3]
    for nm, ys, c, mk in (('aINS', [-0.05, -0.10, -0.15], OI['verm'], 'o'), ('dlPFC', [-0.08, -0.08, -0.08], OI['blue'], 's'), ('PPC', [-0.09, -0.09, -0.09], OI['purple'], '^')):
        dx.errorbar(tert, ys, yerr=0.012, color=c, marker=mk, ms=4, capsize=2, lw=1.2, label=nm)
    dx.axhline(0, color='#999999', lw=0.6)
    dx.set_xticks(tert); dx.set_xticklabels(['low', 'middle', 'high']); dx.set_xlim(0.7, 3.3); dx.set_ylim(-0.2, 0.02)
    dx.set_xlabel('Baseline interoceptive-accuracy tertile'); dx.set_ylabel('ΔPCI relative to vertex\n(vertex = 0)')
    dx.legend(fontsize=5.8, frameon=False, loc='lower left', ncol=3)
    dx.set_title('Pred 5.C–D: IA dependence for aINS only\n(tertile means equal the panel B reductions)', fontsize=6.6); panel(dx, 'D', -0.13, 1.05)
    fig.text(0.70, 0.12, 'All values are illustrative\npre-data predictions.', fontsize=6, style='italic')
    save(fig, 'PRF6')

# ---------------- P6 ----------------
def prf7():
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.0)); fig.subplots_adjust(wspace=0.3, hspace=0.5, left=0.08, right=0.98, top=0.95, bottom=0.08)
    bins = np.linspace(0, 20, 81)
    nd = rng.normal(3.5, 1.2, 3000); de = rng.normal(12, 1.6, 3000)
    ax = axs[0, 0]
    ax.axvspan(6.5, 8.5, color='#DDDDDD', alpha=0.7, lw=0)
    ax.hist(nd, bins, color=OI['verm'], alpha=0.45, label='non-detected trials')
    ax.hist(de, bins, color=OI['blue'], alpha=0.45, label='detected trials')
    ax.hist(np.r_[nd, de], bins, histtype='step', color=INK, lw=1.0, label='all trials (pooled)')
    ax.text(7.5, ax.get_ylim()[1] * 0.92, 'intermediate\nband\n6.5–8.5 a.u.', ha='center', va='top', fontsize=5.6)
    ax.set_xlabel('Frontoparietal high-gamma amplitude (a.u.)'); ax.set_ylabel('Trials')
    ax.legend(fontsize=5.6, frameon=False, loc='upper right'); ax.set_title('Pred 6.A: pooled distribution is bimodal', fontsize=7)
    panel(ax, 'A', -0.15)
    ax = axs[0, 1]
    fp = np.r_[rng.normal(3.8, 1.1, 2500), rng.normal(11.2, 1.3, 2500)]; oc = rng.gamma(6, 1.25, 5000)
    ax.axvspan(6.5, 8.5, color='#DDDDDD', alpha=0.7, lw=0)
    ax.hist(fp, bins, color=OI['blue'], alpha=0.5, label='frontoparietal (bimodal)')
    ax.hist(oc, bins, color='#999999', alpha=0.5, label='occipital (graded)')
    ax.set_xlabel('High-gamma amplitude (a.u.)'); ax.set_ylabel('Trials')
    ax.legend(fontsize=5.6, frameon=False, loc='upper right')
    ax.set_title('Pred 6.B: regional specificity; intermediate-band dwell < 15%', fontsize=6.6)
    panel(ax, 'B', -0.15)
    ax = axs[1, 0]; tt = np.linspace(-500, 0, 200)
    det = 0.10 + 0.40 * ((tt + 500) / 500) ** 1.3 + rng.normal(0, 0.008, tt.size)
    non = 0.10 + rng.normal(0, 0.008, tt.size)
    ax.plot(tt, det, color=OI['blue'], lw=1.4, label='detected'); ax.plot(tt, non, color=OI['verm'], lw=1.4, ls='--', label='non-detected')
    ax.set_xlabel('Time before stimulus onset (ms)'); ax.set_ylabel('AC1 of high-gamma (lag 1)')
    ax.set_ylim(0, 0.6); ax.legend(fontsize=5.8, frameon=False, loc='upper left')
    ax.set_title('Pred 6.C: pre-stimulus critical slowing', fontsize=7)
    panel(ax, 'C', -0.15)
    ax = axs[1, 1]; tt = np.linspace(-100, 1300, 400)
    def rise(a, tau, decay):
        y = np.where(tt < 0, 0.03, 0.03 + a * (1 - np.exp(-np.clip(tt, 0, None) / tau)) * np.exp(-np.clip(tt, 0, None) / decay))
        return y
    d1 = rise(0.60, 60, 1e9); d0 = rise(0.33, 70, 2500)
    for y, c, lab, ls in ((d1, OI['blue'], 'detected', '-'), (d0, OI['verm'], 'non-detected', '--')):
        ax.plot(tt, y, color=c, lw=1.4, ls=ls, label=lab); ax.fill_between(tt, y - 0.05, y + 0.05, color=c, alpha=0.15, lw=0)
    ax.axvline(0, color='#999999', lw=0.6, ls=':'); ax.axvline(200, color='#999999', lw=0.6, ls=':')
    ax.text(205, 0.05, '200 ms', fontsize=5.6)
    ax.set_xlabel('Time after stimulus onset (ms)'); ax.set_ylabel('Frontoparietal gamma-band\n(30–80 Hz) coherence')
    ax.set_ylim(0, 0.8); ax.legend(fontsize=5.8, frameon=False, loc='upper right')
    ax.set_title('Pred 6.D: coherence rises by 200 ms, then sustained', fontsize=7)
    panel(ax, 'D', -0.15)
    save(fig, 'PRF7')

for f in (prf1, prf2, prf3, prf4, prf5, prf6, prf7):
    f()
