import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse, Circle, Polygon
import numpy as np

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 8,
    'axes.titlesize': 8.5,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 6.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.7,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'mathtext.fontset': 'dejavusans',
    'savefig.dpi': 500,
    'figure.dpi': 100,
    'pdf.fonttype': 42,
})

# Okabe-Ito
OI = dict(black='#000000', orange='#E69F00', sky='#56B4E9', green='#009E73', yellow='#F0E442',
          blue='#0072B2', verm='#D55E00', purple='#CC79A7', grey='#7F7F7F')
# Canonical tier palette (series-wide): Tier 3 blue, Tier 2 green, Tier 1 vermillion
TIER = {3: OI['blue'], 2: OI['green'], 1: OI['verm']}
TIER_LIGHT = {3: '#D6E6F2', 2: '#D3EFE6', 1: '#F7DCCB'}
INK = '#222222'

def panel(ax, letter, x=-0.12, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=11, fontweight='bold', va='bottom', ha='left')

def save(fig, name):
    fig.savefig(f'out/{name}.png', dpi=500, bbox_inches='tight', pad_inches=0.04, facecolor='white')
    fig.savefig(f'out/svg/{name}.pdf', bbox_inches='tight', pad_inches=0.04, facecolor='white')
    plt.close(fig)

def box(ax, x, y, w, h, fc='white', ec=INK, lw=0.8, r=0.02, z=1, ls='-'):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z, ls=ls)
    ax.add_patch(p)
    return p

def arr(ax, p0, p1, color=INK, lw=1.0, ms=8, style='-|>', ls='-', z=3, cs='arc3'):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, linestyle=ls, zorder=z, connectionstyle=cs)
    ax.add_patch(a)
    return a

MH = r'$\hat{M}(c,a)$'
