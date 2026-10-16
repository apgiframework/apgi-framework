"""Data-grounded protocol diagrams; no simulated patient outcomes."""
from style import *

def build(protocols):
 def finish(fig,name,n,note=''):
  fig.subplots_adjust(top=.84,bottom=.16,wspace=.35,hspace=.65)
  save(fig,name,'Prospective protocol schematic',f'Protocol {n}, specification 1.1.0. No observed outcomes. '+note)
 def title(fig,s):fig.suptitle(s,x=.04,ha='left',fontsize=15,weight='bold')
 def flow(ax,labels,colors=None):
  ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
  h=80/len(labels)-3
  for j,(head,body) in enumerate(labels):
   y=94-j*(h+3)-h;col=(colors or [OI['blue']]*len(labels))[j]
   box(ax,0,y,100,h,fc='#F3F7FA',ec=col,r=1)
   ax.text(3,y+h-4,head,va='top',weight='bold',color=col,fontsize=10)
   ax.text(3,y+h-14,body,va='top',fontsize=9,linespacing=1.5)
 def timeline(ax,segments,xlabel='Time (s)'):
  for start,width,label,col in segments:
   ax.broken_barh([(start,width)],(.2,.55),facecolors=col,alpha=.85)
   ax.text(start+width/2,.88,label,ha='center',va='bottom',fontsize=9)
  ax.set(ylim=(0,1.6),yticks=[],xlabel=xlabel);ax.spines['left'].set_visible(False)

 # Proxy validation: actual thresholds, not invented correlations or p-values.
 fig,axs=plt.subplots(1,3,figsize=(12,4.8));title(fig,'Protocol 0 / Three independent HEP proxy tests')
 for ax in axs:ax.set_ylim(0,1);ax.set_yticks([]);ax.spines['left'].set_visible(False)
 axs[0].axvspan(.35,1,color=OI['green'],alpha=.18);axs[0].axvline(.35,color=OI['green'])
 axs[0].axvspan(0,.2,color=OI['verm'],alpha=.12);axs[0].set(xlim=(0,.65),xlabel='HEP–discrimination correlation r',title='A  Behavioral validity')
 axs[0].text(.03,.83,'Primary r > .35; p < .01\nIndependent replication N ≥30',fontsize=9)
 axs[0].text(.03,.24,'Evidence against requires the\n95% upper bound <.20 in\neach of two samples.',fontsize=9)
 axs[1].axvspan(15,30,color=OI['green'],alpha=.18);axs[1].axvline(15,color=OI['green']);axs[1].set(xlim=(0,30),xlabel='HEP increase versus placebo (%)',title='B  Pharmacological validity')
 axs[1].text(1,.83,'≥15% + d ≥.50 + BF10 ≥100',fontsize=9)
 axs[1].text(1,.24,'Central EEG engagement\nmust be locked and verified;\npupil change is insufficient.',fontsize=9)
 bound=np.sqrt(.02);axs[2].axvspan(-bound,bound,color=OI['orange'],alpha=.25)
 axs[2].set(xlim=(-.4,.5),xlabel='Within-participant HEP–aINS r',title='C  Anatomical validity')
 axs[2].axvline(.3,color=OI['green']);axs[2].text(-.38,.83,'Confirmation: r > .30',fontsize=9)
 axs[2].text(-.38,.24,'Equivalence: 90% interval\ninside ±√.02 (±.1414);\nresponsive localizer required.',fontsize=9)
 finish(fig,'PRF1',0,'Colored regions are decision boundaries, not measurements.')

 fig=plt.figure(figsize=(12,6));gs=fig.add_gridspec(2,2,width_ratios=[1.3,1]);ax=fig.add_subplot(gs[:,0]);bx=fig.add_subplot(gs[0,1]);cx=fig.add_subplot(gs[1,1])
 title(fig,'Protocol 1 / Cardiac timing and behavioral steepness')
 t=np.linspace(-100,1000,2000);ecg=np.zeros_like(t)
 for mu,amp,sd in [(0,1,9),(35,-.2,13),(160,.12,20),(330,.25,35),(1000,1,9)]:ecg+=amp*np.exp(-.5*((t-mu)/sd)**2)
 ax.plot(t,ecg+2,color=INK,lw=1);ax.axvspan(250,400,color=OI['verm'],alpha=.18);ax.axvspan(500,900,color=OI['blue'],alpha=.12)
 ax.text(325,3.15,'Systole\nR+250 → T-end',ha='center',fontsize=9);ax.text(700,3.15,'Diastole\nT-end+100 → next R−100',ha='center',fontsize=9)
 for y,start,label,col in [(1.15,300,'Systolic example',OI['verm']),(.25,650,'Diastolic example',OI['blue'])]:
  ax.plot(start,y,'|',ms=22,mew=3,color=col);ax.text(start-20,y,label,ha='right',va='center',fontsize=9)
 ax.set(xlim=(-100,1050),ylim=(-.15,3.8),yticks=[],xlabel='Time from R peak (ms); schematic RR = 1,000 ms');ax.spines['left'].set_visible(False)
 ax.text(-80,-.95,'Individual T-wave end determines timing.\nFixed values above illustrate T-end=400 ms only.',fontsize=9)
 contrasts=protocols[1]['blocks']['contrast_multipliers_c50']
 bx.scatter(contrasts,[0]*6,s=90,color=OI['blue']);bx.set(xlim=(.4,1.6),ylim=(-.6,.6),yticks=[],xlabel='Fixed contrast / c50',title='Six contrast levels; 480 main trials/session');bx.spines['left'].set_visible(False)
 c=np.linspace(0,1.8,400)
 for k,col in [(3,OI['grey']),(5,OI['orange']),(10,OI['blue']),(15,OI['green'])]:cx.plot(c,.05+.93*(1-np.exp(-np.log(2)*c**k)),color=col,label=f'k={k}')
 cx.set(xlabel='Linear contrast / illustrative c50',ylabel='Detection probability',title='Weibull shape k ≡ αpsy, not γsig');cx.legend(ncol=2,fontsize=8,frameon=False)
 finish(fig,'PRF2',1,'Curves illustrate shape only; Pred 1.E also requires interval and comparator evidence. QUEST count unresolved.')
 # Same artwork for the corresponding legacy supplemental mapping.
 import shutil
 for ext in ['png','pdf','svg']:shutil.copyfile(OUT/f'PRF2.{ext}',OUT/f'P1S3.{ext}')
 RECORDS['P1S3']={**RECORDS['PRF2'],'note':'Shared Protocol 1 artwork (PRF2); replaces legacy Paper 1 Figure S3.'}

 fig,axs=plt.subplots(1,2,figsize=(12,5.3));title(fig,'Protocol 2 / Separate calibration, simulation and human tests')
 flow(axs[0],[('1 · Independent calibration','Published CP-3a data: N≥60\nFreeze parameter and observation manifest'),('2 · Simulation','7 architectures × 1,000 seeds per condition\n500 trials/environment; seed-level inference'),('3 · Human model comparison','Independent IGT test cohort: N=80\nΔBIC≥10 against each alternative; CV evidence')])
 vols=protocols[2]['blocks']['volatility_schedule'];axs[1].stairs(vols,np.arange(6)*100,color=OI['blue'],linewidth=2,fill=True,alpha=.4)
 axs[1].set(xlabel='Trial within seed / environment',ylabel='Volatility',ylim=(0,.7),title='Five 100-trial blocks')
 axs[1].text(15,.63,'Lead–lag window: ±5 trials',fontsize=10);axs[1].text(15,.49,'Median within-seed Kendall τ\nwith seed-level bootstrap interval',fontsize=9)
 finish(fig,'PRF3',2,'Exploratory 2.F / 2.G carry no independent empirical confirmation.')

 fig,axs=plt.subplots(2,1,figsize=(12,5.5),gridspec_kw={'height_ratios':[1,1.2]});title(fig,'Protocol 3 / Anticipation separated from outcome')
 timeline(axs[0],[(0,4,'Choice\n4 s',OI['blue']),(4,3,'Foreperiod\n0 or 2–4 s',OI['orange']),(7,2,'Outcome\n2 s',OI['verm']),(9,8,'ITI\n6–10 s',OI['grey'])]);axs[0].set_xlim(0,17)
 axs[1].set(xlim=(0,100),ylim=(0,100));axs[1].axis('off')
 for x,txt,col in [(5,'vmPFC\nexpected value',OI['blue']),(43,'aINS\nprecision gain',OI['verm']),(78,'pIC\nsensory control',OI['grey'])]:
  box(axs[1],x,40,20,45,fc='white',ec=col,r=2);axs[1].text(x+10,62,txt,ha='center',va='center',color=col,fontsize=11)
 arr(axs[1],(25,65),(43,65),OI['verm']);arr(axs[1],(25,42),(78,42),OI['grey'],ls='--')
 axs[1].text(50,10,'Pred 3.B: anticipation-versus-outcome pathway dissociation\nN=40 enrolled / 36 analyzable · 2 runs ×100 trials · value/contrast controls',ha='center',fontsize=10)
 finish(fig,'PRF4',3,'Timeline illustrates a 3 s foreperiod and 8 s ITI; post-shock ITI ≥8 s.')
 for ext in ['png','pdf','svg']:shutil.copyfile(OUT/f'PRF4.{ext}',OUT/f'P1S4.{ext}')
 RECORDS['P1S4']={**RECORDS['PRF4'],'note':'Shared Protocol 3 artwork (PRF4); replaces legacy Paper 1 Figure S4.'}

 fig,axs=plt.subplots(1,2,figsize=(12,5));title(fig,'Protocol 4 / State × interoceptive load crossover')
 axs[0].set(xlim=(-.6,1.6),ylim=(-.6,1.6),xticks=[0,1],xticklabels=['Rested','Depleted'],yticks=[0,1],yticklabels=['Neutral','High interoceptive'])
 for x in [0,1]:
  for y in [0,1]:
   axs[0].add_patch(Rectangle((x-.4,y-.4),.8,.8,fc='#E6F1F7' if y==0 else '#FBECE4',ec='white'))
   axs[0].text(x,y,'d′ and P3b\nmeasured here',ha='center',va='center',fontsize=10)
 axs[0].set_title('Within-participant factorial contrast');axs[0].set_aspect('equal')
 flow(axs[1],[('Signed margin (Pred 4.A)',"Δ = depleted − rested\nΔd′extero − Δd′intero ≥ .15 × rested d′intero"),('Neural contrast (Pred 4.B)','Selective P3b reduction ≥1.5 μV\nRegistered interaction evidence required'),('Adjustment (Pred 4.C)','Trial pupil and block RMSSD are covariates\nAdjustment does not establish metabolic mediation')])
 finish(fig,'PRF5',4,'Enroll 64 / target 55 / minimum 48; two labs. Positive baseline d′ required for proportional margin.')

 fig,axs=plt.subplots(1,2,figsize=(12,5));title(fig,'Protocol 5 / Matched interventions and equivalence')
 flow(axs[0],[('aINS intervention','tFUS / dTMS hierarchy\nIndependent engagement gate + matched sham'),('Frontoparietal interventions','dlPFC / PPC TMS + registered reference\nUse direct dissociation contrasts'),('PCImax measurement','Separate resting pre/post probes\n≥150 clean pulses each; not task trials')])
 ax=axs[1];ax.axvspan(-.15,.15,color=OI['green'],alpha=.2);ax.axvline(-.15,color=OI['green']);ax.axvline(.15,color=OI['green'])
 ax.set(xlim=(-.5,.5),ylim=(0,1),yticks=[],xlabel='Paired standardized HEP effect d',title='Pred 5.E / dlPFC HEP equivalence');ax.spines['left'].set_visible(False)
 ax.text(0,.8,'ROPE = [−.15, +.15]',ha='center',fontsize=12,color=OI['green'])
 ax.text(0,.5,'95% HDI entirely inside ROPE\nAND BF01 ≥6',ha='center',fontsize=12)
 ax.text(0,.15,'No posterior distribution is plotted.\nNonsignificance alone is insufficient.',ha='center',fontsize=9)
 finish(fig,'PRF6',5,'Enroll 52 / analyzable target 44; 5.C / 5.D moderation requires multiplicity lock.')

 fig,axs=plt.subplots(1,2,figsize=(12,5));title(fig,'Protocol 6 / Fixed contrasts and a validation-gated analysis')
 grid=protocols[6]['blocks']['absolute_michelson_contrasts'];counts=[150,75,75,75,75,150]
 axs[0].bar(np.arange(6),counts,color=[OI['grey']]+[OI['blue']]*4+[OI['green']]);axs[0].set_xticks(range(6),[str(x) for x in grid])
 axs[0].set(xlabel='Absolute Michelson contrast',ylabel='Planned trials',ylim=(0,180),title='600 trials across eight blocks')
 for i,n in enumerate(counts):axs[0].text(i,n+3,str(n),ha='center',fontsize=10)
 flow(axs[1],[('Fixed-contrast mixture test','6.A: dip + mixture evidence, not pooled contrasts\n6.B: direct regional comparison + control model'),('AC1 validation hold','6.C deferred pending estimator recovery/power\nFive samples per 50 ms window at 100 Hz'),('Coverage-specific timescales','6.E: ≥3 dissociable scales + surrogate controls\naINS subset; independent replication needed')])
 finish(fig,'PRF7',6,'Target N=20 / minimum 12; confirmatory–exploratory. 500 ms fixation → 33 ms target → 1 s delay.')

 def clinical(name):
  fig,axs=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[.9,1.3]});title(fig,'Protocol 7 / Cohort and longitudinal outcomes')
  ns=list(protocols[7]['participants']['groups'].values());groups=['VS/UWS','MCS','EMCS','Controls'];cols=[OI['verm'],OI['orange'],OI['sky'],OI['blue']]
  axs[0].barh(groups[::-1],ns[::-1],color=cols[::-1]);axs[0].set(xlim=(0,36),xlabel='Planned participants',title='80 patients + 30 baseline-only controls')
  for i,n in enumerate(ns[::-1]):axs[0].text(n+.6,i,str(n),va='center')
  ax=axs[1];ax.set(xlim=(-.6,2.6),ylim=(-.8,3.6),xticks=[0,1,2],xticklabels=['Baseline','3 months','6 months'],yticks=[0,1,2,3],yticklabels=groups[::-1]);ax.invert_yaxis()
  for row,group in enumerate(groups[::-1]):
   for col in range(3):
    active=col==0 or group!='Controls'
    ax.add_patch(Rectangle((col-.43,row-.35),.86,.7,fc='#E6F1F7' if active else '#F0F0F0',ec='white'))
    txt=('HEP / PCI*\nfMRI' if group=='Controls' else 'HEP / PCI*\nfMRI / CRS-R') if col==0 else ('—' if not active else ('CRS-R' if col==1 else 'CRS-R\nGOS-E'))
    ax.text(col,row,txt,ha='center',va='center',fontsize=8)
  ax.set_title('Outcomes follow patients, not healthy controls');ax.spines['left'].set_visible(False)
  fig.text(.06,.035,'Primary 7.G: baseline HEP → 3-month CRS-R; positive effect and LRT p<.048.\n*PCI-eligible subset. Joint HEP+PCI (7.A) is estimation-first; 7.D prognosis emphasizes 6 months.',fontsize=10)
  finish(fig,name,7,'≥300 clean heartbeats; absolute mean Cz HEP, 250–400 ms. No synthetic clinical separation is shown.')
 clinical('PRF8');clinical('P3F5')
