"""APGI 1.1 plotting utilities, adapted from the supplied October bundle."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for font_file in (Path(matplotlib.get_data_path()) / 'fonts' / 'ttf').glob('*.ttf'):
 font_manager.fontManager.addfont(str(font_file))
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse, Circle, Polygon
import numpy as np
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
OI = dict(black='#20262E', orange='#E69F00', sky='#56B4E9', green='#009E73', yellow='#F0E442',
          blue='#0072B2', verm='#D55E00', purple='#CC79A7', gray='#7F7F7F')
TIER = {3: OI['blue'], 2: OI['green'], 1: OI['verm']}
TIER_LIGHT = {3: '#E6F1F7', 2: '#E5F4EE', 1: '#FBECE4'}
INK = '#20262E'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,
 'axes.labelsize':9,'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.7,'mathtext.fontset':'dejavusans','pdf.fonttype':42,'svg.fonttype':'none',
 'svg.hashsalt':'apgi-1.1'})
RECORDS = {}
OVERRIDES = {}
def panel(ax, letter, x=-.12, y=1.04):
 ax.text(x,y,letter,transform=ax.transAxes,fontsize=11,weight='bold',va='bottom')
def box(ax,x,y,w,h,fc='white',ec=INK,lw=.8,r=.02,z=1,ls='-'):
 p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=fc,ec=ec,lw=lw,zorder=z,ls=ls);ax.add_patch(p);return p
def arr(ax,p0,p1,color=INK,lw=1,ms=8,style='-|>',ls='-',z=3,cs='arc3'):
 p=FancyArrowPatch(p0,p1,arrowstyle=style,mutation_scale=ms,color=color,lw=lw,linestyle=ls,zorder=z,connectionstyle=cs);ax.add_patch(p);return p
def save(fig,name,kind='Conceptual schematic',note=''):
 kind,note=OVERRIDES.get(name,(kind,note))
 OUT.mkdir(exist_ok=True)
 fig.text(.01,-.055,f'APGI 1.1  /  {name}  /  {kind}',fontsize=7,color='#59636F',va='top')
 if note:fig.text(.01,-.095,note,fontsize=7,color='#59636F',va='top')
 for ext in ['png','pdf','svg']:
  metadata={'Creator':'APGI figure release 1.1','CreationDate':None,'ModDate':None} if ext=='pdf' else ({'Date':None} if ext=='svg' else None)
  fig.savefig(OUT/f'{name}.{ext}',dpi=300,bbox_inches='tight',pad_inches=.15,facecolor='white',metadata=metadata)
 RECORDS[name]={'kind':kind,'note':note}
 plt.close(fig)
