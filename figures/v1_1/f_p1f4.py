from style import *

fig = plt.figure(figsize=(7.2, 3.3))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(-3, 46); ax.axis('off')
phases = [  # (t0, t1, title, color)
    (0, 50, 'Phase 1\nError generation', OI['orange']),
    (50, 120, 'Phase 2\nPrecision weighting', OI['verm']),
    (120, 250, 'Phase 3\nAccumulation', OI['blue']),
    (250, 320, 'Phase 4\nIgnition decision', OI['green']),
    (320, 500, 'Phase 5\nGlobal broadcast', OI['purple']),
]
X0, X1 = 16, 99.5
cols_x = np.linspace(X0, X1, 6)       # equal-width columns (timing on axis below)
def cx(i): return 0.5 * (cols_x[i] + cols_x[i + 1])
rows = [
    ('Neural\nsubstrate', [
        'Feedforward sensory\ninput; prediction error\nin early cortex',
        'Neuromodulatory gating\nof precision\n(interoceptive and\nexteroceptive)',
        'Recurrent loops in\nassociation cortex',
        'Frontoparietal–thalamic\nloop compares\n' + r'$S_t$' + ' with ' + r'$\theta_t$',
        'Cortico–thalamo–cortical\nbroadcast\n(global workspace)']),
    ('APGI\nvariable', [
        'Prediction errors\n' + r'$\varepsilon^{e}$, $\varepsilon^{i}$',
        'Precision\n' + r'$\Pi^{e}$, $\Pi^{i}_{eff}$' + '\n(gain control)',
        'Accumulated surprise\n' + r'$S_t$' + ' (rises over time)',
        'Ignition if\n' + r'$S_t>\theta_t$',
        'Ignition state\n' + r'$B_t=1$' + '\n(workspace stabilization)']),
    ('EEG/MEG\nmarker', [
        'C1/P1 and early\ngamma ~50–100 ms',
        'Pre-stimulus alpha\npower (attentional gain)',
        'N2 / sustained gamma\n~150–250 ms',
        'P3b onset\n~250 ms',
        'P3b (250–500 ms;\nto ~600 ms when ' + r'$\theta_t$' + '\nis high)']),
]
# header chevrons
for i, (t0, t1, title, c) in enumerate(phases):
    x0, x1 = cols_x[i] + 0.3, cols_x[i + 1] - 0.3
    pts = [(x0, 39), (x1 - 1.6, 39), (x1, 42.2), (x1 - 1.6, 45.4), (x0, 45.4), (x0 + (1.6 if i else 0), 42.2)]
    ax.add_patch(Polygon(pts, closed=True, fc=c, ec='none', alpha=0.9))
    ax.text(0.5 * (x0 + x1), 42.2, title, ha='center', va='center', fontsize=5.9, color='white', fontweight='bold')
    ax.text(cx(i), 36.6, f'{t0}–{t1} ms', ha='center', va='center', fontsize=6.4, color=c, fontweight='bold')
ax.text(X0 - 1.2, 36.6, 'Approx. time\nafter onset', ha='right', va='center', fontsize=6.0)
# rows
ytop = 34.5; rh = 11.2
for r, (name, cells) in enumerate(rows):
    y0 = ytop - (r + 1) * rh
    ax.add_patch(Rectangle((0.5, y0), X1 - 0.5, rh, fc='#F6F6F6' if r % 2 == 0 else 'white', ec='#BBBBBB', lw=0.5))
    ax.text(8.0, y0 + rh / 2, name, ha='center', va='center', fontsize=6.8, fontweight='bold')
    for i, txt in enumerate(cells):
        ax.text(cx(i), y0 + rh / 2, txt, ha='center', va='center', fontsize=5.8,
                color=INK)
    for xv in cols_x:
        ax.plot([xv, xv], [y0, y0 + rh], color='#BBBBBB', lw=0.5)
ax.text(X1, -2.6, 'Latencies are approximate and stimulus-dependent; phases are temporal, not the pipeline stages of Figure 1.',
        ha='right', va='bottom', fontsize=5.6, style='italic', color='#555555')
save(fig, 'P1F4', 'Hypothesized timing schematic', 'Phase boundaries and substrate assignments are hypotheses; latencies depend on stimulus and state.')
