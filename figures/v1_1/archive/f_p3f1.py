from style import *

fig = plt.figure(figsize=(7.2, 4.0))
ax = fig.add_axes([0.0, 0.02, 0.50, 0.96]); ax.set_xlim(-6.0, 5.6); ax.set_ylim(-5.6, 5.6); ax.set_aspect('equal'); ax.axis('off')
radii = [1.0, 2.0, 3.0, 4.0, 5.0]
fcs = ['white', '#E1EEF8', '#E2F2EB', '#ECE6F3', '#FBE7DA']
ecs = ['#666666', OI['blue'], OI['green'], OI['purple'], OI['verm']]
for r, fc, ec in list(zip(radii, fcs, ecs))[::-1]:
    ax.add_patch(Circle((0, 0), r, fc=fc, ec=ec, lw=1.0))
ax.add_patch(Circle((0, 0), 1.0, fc='white', ec='#666666', lw=1.0, hatch='////', alpha=0.6))
ax.text(0, 0.18, 'Level 0', ha='center', fontsize=7, fontweight='bold')
ax.text(0, -0.42, 'reflexive\nsub-APGI', ha='center', fontsize=5.6, va='center')
names = ['Level 1\nlocal microcircuits', 'Level 2\ncortical reservoirs', 'Level 3\nassociation networks', 'Level 4\nneuroendocrine']
for i, nm in enumerate(names):
    rr = radii[i] + 0.5
    ax.text(0, rr, nm, ha='center', va='center', fontsize=5.8, fontweight='bold', color=ecs[i + 1])
# carriers: inward arrows along a diagonal
carriers = [('cortisol', 4, 3), ('phasic NE', 3, 2), ('ACh', 2, 1), ('fast NE', 1, 0)]
ang = np.deg2rad(-40)
for lab, a, b in carriers:
    r0, r1 = radii[a] - 0.15, radii[b] + 0.05 if b > 0 else radii[0] + 0.02
    p0 = (r0 * np.cos(ang) if False else (radii[a] - 0.25) * np.cos(ang), (radii[a] - 0.25) * np.sin(ang))
    p1 = ((radii[b] - 0.05) * np.cos(ang) + 0.0, (radii[b] - 0.05) * np.sin(ang))
    p0 = ((radii[a] - 0.25) * np.cos(ang), (radii[a] - 0.25) * np.sin(ang))
    rb = radii[b] - 0.45 if b > 0 else radii[0] + 0.03
    p1 = (rb * np.cos(ang), rb * np.sin(ang))
    arr(ax, p0, p1, ecs[a], lw=1.2, ms=8)
    mid = (0.5 * (p0[0] + p1[0]) + 0.22, 0.5 * (p0[1] + p1[1]) + 0.12)
    ax.text(*mid, lab, fontsize=5.6, color=ecs[a], rotation=40, ha='center', va='center', style='italic')
ax.text(5.35 * np.cos(ang), 5.35 * np.sin(ang) - 0.1, 'carriers\n(top-down)', fontsize=5.6, ha='left', va='top', color='#444444')
# side arcs
th = np.linspace(np.deg2rad(150), np.deg2rad(210), 50)
ax.plot(5.35 * np.cos(th), 5.35 * np.sin(th), color=OI['blue'], lw=1.3)
arr(ax, (5.35 * np.cos(th[-2]), 5.35 * np.sin(th[-2])), (4.6 * np.cos(np.deg2rad(212)), 4.6 * np.sin(np.deg2rad(212))), OI['blue'], lw=1.3, ms=9)
ax.text(-5.95, 0.0, 'top-down threshold\nmodulation\n' + r'$\kappa_{down}$, $\kappa_{up}$', fontsize=5.8, color=OI['blue'], ha='left', va='center', rotation=90)
th2 = np.linspace(np.deg2rad(60), np.deg2rad(120), 50)
ax.plot(5.35 * np.cos(th2), 5.35 * np.sin(th2), color=OI['green'], lw=1.3)
arr(ax, (4.6 * np.cos(np.deg2rad(58)), 4.6 * np.sin(np.deg2rad(58))), (5.35 * np.cos(th2[1]), 5.35 * np.sin(th2[1])), OI['green'], lw=1.3, ms=9)
ax.text(0, 5.5, 'bottom-up prediction error ' + r'$\psi(\varepsilon)$' + ' (outward)', fontsize=5.8, color=OI['green'], ha='center', va='bottom')

# table
tx = fig.add_axes([0.50, 0.08, 0.50, 0.84]); tx.set_xlim(0, 100); tx.set_ylim(0, 100); tx.axis('off')
cols = [0, 12, 38, 57, 76, 100]
head = ['Level', 'Substrate', r'$\tau_{int}$' + '\n(integration\nwindow)', r'$\tau_\theta$' + '\n(spectral\npole)', 'Carrier received;\nAPGI parameters']
for i, h in enumerate(head):
    tx.text(0.5 * (cols[i] + cols[i + 1]), 95, h, ha='center', va='center', fontsize=5.8, fontweight='bold')
rows = [
    ('L0', 'brainstem,\nspinal reflex', '< 10 ms', '50 ms\n(gain process;\nno threshold)', 'fast NE;\nnone (sub-APGI)'),
    ('L1', 'local cortical\nmicrocircuits', '10–500 ms', '6.6 s', 'ACh;\n' + r'$\Pi_1,\theta_1,\tau_{ign,1}$'),
    ('L2', 'cortical\nreservoirs', '0.5–2 s', '15 min', 'phasic NE;\n' + r'$\Pi_2,\theta_2,\tau_{ign,2}$'),
    ('L3', 'association\nnetworks', 'seconds–\nminutes', '1.4 d', 'cortisol;\n' + r'$\Pi_3,\theta_3,\tau_{ign,3}$'),
    ('L4', 'neuroendocrine\n(HPA axis)', 'hours–years', '6 mo', '—;\n' + r'$\Pi_4,\theta_4,\tau_{ign,4}$'),
]
rh = 17
for j, row in enumerate(rows):
    y0 = 88 - (j + 1) * rh
    tx.add_patch(Rectangle((0, y0), 100, rh, fc=fcs[j] if j else '#F4F4F4', ec='#BBBBBB', lw=0.5))
    for i, v in enumerate(row):
        tx.text(0.5 * (cols[i] + cols[i + 1]), y0 + rh / 2, v, ha='center', va='center', fontsize=5.7,
                fontweight='bold' if i == 0 else 'normal', color=ecs[j] if i == 0 else INK)
tx.text(0, -4, r'$\tau_\theta$ chain: inter-level ratio $k\approx133$ (span 50 ms → ~6 months).', fontsize=5.6, color='#444444')
save(fig, 'P3F1')
