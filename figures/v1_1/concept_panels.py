"""Scientific schematics preserving the spatial structure of the legacy figures."""
from style import *

def build():
 fig=plt.figure(figsize=(12,6));left=fig.add_axes([.02,.12,.47,.76]);right=fig.add_axes([.53,.17,.45,.68])
 fig.suptitle('Nested functional levels; distinct operational and spectral timescales',x=.03,ha='left',fontsize=15,weight='bold')
 left.set(xlim=(-5.5,5.5),ylim=(-5.5,5.5),aspect='equal');left.axis('off')
 cols=[OI['grey'],OI['blue'],OI['green'],OI['purple'],OI['verm']]
 for i in range(4,-1,-1):left.add_patch(Circle((0,0),i+1,fc=['#F4F4F4','#E6F1F7','#E5F4EE','#F5EAF1','#FBECE4'][i],ec=cols[i],lw=1.2,hatch='////' if i==0 else None))
 labels=['L0\nReflexive\nsub-APGI','L1 · Perceptual','L2 · Task','L3 · Narrative','L4 · Identity']
 left.text(0,0,labels[0],ha='center',va='center',fontsize=9)
 for i in range(1,5):left.text(0,i+.52,labels[i],ha='center',va='center',fontsize=10,color=cols[i],weight='bold')
 arr(left,(-4,-2.2),(-1.1,-.6),OI['blue'],ms=12,lw=1.4);left.text(-4.8,-3,'Threshold\nmodulation',color=OI['blue'],fontsize=9)
 arr(left,(1.1,-.6),(4,-2.2),OI['green'],ms=12,lw=1.4);left.text(1.6,-3.4,'Bottom-up\nstandardized-error\nprecision modulation',color=OI['green'],fontsize=9)
 right.axis('off')
 rows=[['L0','10–100 ms','50 ms'],['L1','100 ms–3 s','6.6 s'],['L2','Minutes','15 min'],['L3','Hours–days','1.4 d'],['L4','Months–years','6 months']]
 tab=right.table(cellText=rows,colLabels=['Level','Operational band','OU pole τ'],colWidths=[.17,.43,.4],cellLoc='center',bbox=[0,.28,1,.72]);tab.auto_set_font_size(False);tab.set_fontsize(10)
 for (r,c),cell in tab.get_celld().items():
  cell.set_edgecolor('white')
  if r==0:cell.set_facecolor(OI['blue']);cell.set_text_props(color='white',weight='bold')
  else:cell.set_facecolor('#EDF3F7' if r%2 else '#F7F9FB')
 right.text(0,.18,'L0 has no ignition threshold.\nNeuroendocrine priors set L4 cortical thresholds.\nOU poles are conditional geometric model parameters.',va='top',fontsize=10,linespacing=1.5)
 save(fig,'P3F1','Hierarchical model schematic','Paper 3 §2.1: nesting is computational, not literal anatomy; operational windows are not the OU spectral poles.')

 fig,axs=plt.subplots(1,2,figsize=(12,5.4),gridspec_kw={'width_ratios':[1.5,1]});fig.subplots_adjust(top=.82,bottom=.18,wspace=.35)
 fig.suptitle('Biological constraints and architecture audit',x=.03,ha='left',fontsize=16,weight='bold')
 ax=axs[0];ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
 rows=[('High-dimensional\ntransients','Separate error\nchannels'),('Fading memory\n~200–500 ms','Accumulation\nwindow'),('Nonlinear\nseparability','Ignition\nsigmoid'),('Sparse, event-driven\nactivity','Allostatic\nthreshold')]
 for j,(a,b) in enumerate(rows):
  y=80-j*24
  for x,txt in [(0,a),(62,b)]:
   box(ax,x,y,38,18,fc='#EDF3F7',ec=OI['blue'],r=1);ax.text(x+19,y+9,txt,ha='center',va='center',fontsize=9)
  arr(ax,(38,y+9),(62,y+9),OI['blue'])
 ax.text(50,102,'Biological constraint  →  APGI requirement',ha='center',fontsize=11,weight='bold')
 names=['LSM/LNN','Attractor','Transformer','Feedforward'];counts=[4,3,2,2]
 axs[1].barh(names[::-1],counts[::-1],color=[OI['grey']]*3+[OI['blue']]);axs[1].set(xlim=(0,4.5),xticks=range(5),xlabel='Constraints satisfied (analytical audit)',title='Properties of defining equations')
 for i,(n,txt) in enumerate(zip(counts[::-1],['Fails C1 / C2','Fails C2 / C4','Fails C2','All four'])):axs[1].text(.1,i,txt,va='center',color='white',fontsize=9)
 save(fig,'P2F1','Analytical architecture comparison','Paper 2 §2.5 / Fig 1. Scores describe defining properties without additional machinery; not experimental benchmark results.')
