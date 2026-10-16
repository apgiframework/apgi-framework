from style import *
from nilearn import plotting

TARGETS = [  # name, coords, colour, modality
    ('aINS', (34, 14, 0), OI['verm'], 'tFUS'),
    ('dlPFC', (-44, 36, 20), OI['blue'], 'TMS'),
    ('PPC (R)', (28, -60, 46), OI['purple'], 'TMS'),
    ('PPC (L)', (-28, -60, 46), OI['purple'], 'TMS'),
    ('vertex sham', (0, -30, 70), '#777777', 'TMS'),
]

def glass(ax, size=60):
    coords = [t[1] for t in TARGETS]
    cols = [t[2] for t in TARGETS]
    d = plotting.plot_markers(np.ones(len(coords)), coords, node_cmap=None, node_size=size, display_mode='lzr',
                              axes=ax, colorbar=False, node_vmin=0, node_vmax=1, alpha=1.0, annotate=False)
    return d

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(7, 2.4))
    coords = [t[1] for t in TARGETS]
    d = plotting.plot_connectome(np.zeros((len(coords), len(coords))), coords, node_color=[t[2] for t in TARGETS], node_size=45,
                                 display_mode='lzr', axes=ax, annotate=True)
    fig.savefig('tmp/brain_test.png', dpi=200)
