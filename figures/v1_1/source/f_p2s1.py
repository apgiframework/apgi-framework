from style import *
from nilearn import plotting

T = [('aINS (R) [34, 14, 0] — tFUS', (34, 14, 0), OI['verm']),
     ('dlPFC (L) [−44, 36, 20] — TMS', (-44, 36, 20), OI['blue']),
     ('PPC [±28, −60, 46] — TMS', (28, -60, 46), OI['purple']),
     (None, (-28, -60, 46), OI['purple']),
     ('vertex sham [0, −30, 70] — TMS', (0, -30, 70), '#777777')]

fig = plt.figure(figsize=(7.2, 4.6))
ax = fig.add_axes([0.0, 0.52, 0.62, 0.42])
d = plotting.plot_glass_brain(None, display_mode='lzr', axes=ax, annotate=False)
for nm, c, col in T:
    d.add_markers([c], marker_color=col, marker_size=34)
fig.text(0.01, 0.965, 'A', fontsize=11, fontweight='bold', va='top')
fig.text(0.05, 0.955, 'Protocol 5 neuromodulation targets (MNI; left, top and right glass-brain views)', fontsize=7.2, fontweight='bold', va='top')
lx = fig.add_axes([0.63, 0.55, 0.36, 0.38]); lx.axis('off'); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
y = 0.95
for nm, c, col in T:
    if nm is None: continue
    lx.plot(0.03, y, 'o', color=col, ms=6)
    lx.text(0.08, y, nm, va='center', fontsize=6.3)
    y -= 0.11
lx.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 0.38, boxstyle='round,pad=0,rounding_size=0.03', fc='#F6F6F6', ec='#999999', lw=0.6))
lx.text(0.04, 0.33, 'Predicted dissociation', fontsize=6.6, fontweight='bold', va='top')
lx.text(0.04, 0.24, 'aINS stimulation → HEP–P3b coupling abolished', fontsize=6.0, color=OI['verm'], va='top')
lx.text(0.04, 0.15, 'dlPFC, PPC stimulation → global ignition reduced', fontsize=6.0, color=OI['blue'], va='top')
lx.text(0.04, 0.07, '(less high-gamma spread; coupling preserved)', fontsize=5.6, color=OI['blue'], va='top')

# Panel B
bx = fig.add_axes([0.06, 0.08, 0.40, 0.30])
bx.add_patch(Rectangle((0, 0), 500, 1, fc='#E6DDF1', ec='none')); bx.text(250, 0.5, 'pre-stimulus window\n(AC1 → ' + r'$\rho_{res}$' + ' estimate)', ha='center', va='center', fontsize=6.2)
bx.add_patch(Rectangle((500, 0), 60, 1, fc='#F6D9A8', ec='none')); bx.text(530, 1.12, 'near-threshold\nstimulus', ha='center', va='bottom', fontsize=5.8)
bx.add_patch(Rectangle((560, 0), 250, 1, fc='#D7E7F5', ec='none')); bx.text(685, 0.5, 'response window', ha='center', va='center', fontsize=6.2)
bx.set_xlim(0, 810); bx.set_ylim(0, 1.6); bx.set_yticks([]); bx.spines['left'].set_visible(False)
bx.set_xticks([0, 100, 200, 300, 400, 500, 560, 700, 810]); bx.set_xlabel('Time (ms)')
fig.text(0.01, 0.43, 'B', fontsize=11, fontweight='bold', va='top')
fig.text(0.05, 0.42, 'Protocol 6 intracranial-EEG trial timeline', fontsize=7.2, fontweight='bold', va='top')
# schematic network: supra vs sub
sx = fig.add_axes([0.52, 0.03, 0.47, 0.40]); sx.set_xlim(0, 100); sx.set_ylim(0, 100); sx.axis('off')
def net(x0, y0, ignite):
    nodes = [(x0, y0), (x0 + 12, y0 + 10), (x0 + 24, y0 + 4), (x0 + 30, y0 + 18), (x0 + 18, y0 + 24)]
    for i, (x, y) in enumerate(nodes):
        on = (i == 0) or ignite
        sx.add_patch(Ellipse((x, y), 4.4, 4.4 * (0.47 * 7.2) / (0.40 * 4.6), fc=OI['verm'] if on else 'white', ec=INK, lw=0.6))
    for i in range(1, len(nodes)):
        sx.plot([nodes[0][0], nodes[i][0]], [nodes[0][1], nodes[i][1]], color=OI['verm'] if ignite else '#BBBBBB', lw=1.2 if ignite else 0.6, ls='-' if ignite else ':', zorder=0)
sx.text(0, 92, r'Supra-threshold trials ($S_t>\theta_t$)', fontsize=6.6, fontweight='bold')
net(6, 58, True)
sx.text(46, 70, 'local responsive site → widespread\nfrontoparietal activation;\nhigh-gamma (70–150 Hz) increase', fontsize=6.0, va='center')
sx.text(0, 42, r'Sub-threshold trials ($S_t<\theta_t$)', fontsize=6.6, fontweight='bold')
net(6, 8, False)
sx.text(46, 20, 'local activation only;\nno propagation, no global\nhigh-gamma increase', fontsize=6.0, va='center')
save(fig, 'P2S1')
