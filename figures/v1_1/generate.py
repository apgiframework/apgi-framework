"""Generate the APGI 1.1 review series from supplied code and local specifications.
Run from any directory with Python, numpy, matplotlib and Pillow installed.
The legacy library is not treated as a validated implementation of the 1.1 model.
"""
from style import *
import json, runpy, textwrap, hashlib, html

REPO=ROOT.parents[1]
PROTOCOLS={n:json.loads(next((REPO/'protocols').glob(f'protocol_{n}_*.json')).read_text()) for n in range(8)}
MANUSCRIPT=json.loads((ROOT/'manuscript_data.json').read_text())
CAPTIONS=json.loads((ROOT/'captions.json').read_text())
def wrap(s,n=48):return '\n'.join(textwrap.wrap(s,n,break_long_words=False))
def canvas(title,height=5.5):
 fig,ax=plt.subplots(figsize=(11,height));fig.subplots_adjust(top=.86,bottom=.08,left=.02,right=.98)
 ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off');fig.suptitle(title,x=.03,ha='left',fontsize=16,weight='bold',color=INK)
 return fig,ax
def card(ax,x,y,w,h,title,body,color=OI['blue'],size=9):
 box(ax,x,y,w,h,fc='#F7F9FB',ec='#CCD5DD',r=1)
 ax.plot([x,x+w],[y+h,y+h],color=color,lw=3,solid_capstyle='butt')
 ax.text(x+2,y+h-4,title,va='top',weight='bold',fontsize=10,color=color)
 ax.text(x+2,y+h-13,body,va='top',fontsize=size,linespacing=1.5)
def table(title,headers,rows,widths,name,kind='Specification schematic',note='',fontsize=9):
 height=max(4,1.6+sum(max(str(c).count('\n')+1 for c in r) for r in rows)*.22)
 fig,ax=plt.subplots(figsize=(12,height));ax.axis('off');fig.suptitle(title,x=.03,ha='left',fontsize=15,weight='bold')
 tab=ax.table(cellText=rows,colLabels=headers,colWidths=widths,loc='center',cellLoc='left')
 tab.auto_set_font_size(False);tab.set_fontsize(fontsize)
 total=sum(max(str(c).count('\n')+1 for c in r)+1.8 for r in rows)+3
 for (r,c),cell in tab.get_celld().items():
  cell.set_edgecolor('white');cell.PAD=.06
  if r==0:cell.set_facecolor(OI['blue']);cell.set_text_props(color='white',weight='bold');cell.set_height(3/total)
  else:
   cell.set_facecolor('#EDF3F7' if r%2 else '#F7F9FB')
   key=str(rows[r-1][0]);tier=next((t for t in [1,2,3] if key.startswith(f'Tier {t}') or key.startswith(f'{t} ·') or key.endswith(f'/ T{t}')),None)
   if tier:
    cell.set_facecolor(TIER_LIGHT[tier])
    if c==0:cell.set_facecolor(TIER[tier]);cell.set_text_props(color='white',weight='bold')
   cell.set_height((max(str(v).count('\n')+1 for v in rows[r-1])+1.8)/total)
 fig.subplots_adjust(top=.88,bottom=.04,left=.02,right=.98)
 fig.canvas.draw()
 renderer=fig.canvas.get_renderer()
 for (r,c),cell in tab.get_celld().items():
  tb=cell.get_text().get_window_extent(renderer); cb=cell.get_window_extent(renderer)
  if tb.width > cb.width*.96 or tb.height > cb.height*.96:
   raise ValueError(f'{name}: text does not fit table cell {r},{c}')
 save(fig,name,kind,note)

def architecture(name='P1F1'):
 fig,ax=canvas('From prediction error to conscious access',6)
 labels=[('01  Reference errors','Separate causal reference\nwindows for each channel\n\n'+r'$z=(\epsilon-\mu_{ref})/\sigma_{ref}$'),
 ('02  Effective gains','ACh → exteroceptive gain\nNE + somatic marker →\ninteroceptive gain\n\nClamp, then normalize'),
 ('03  Excess surprise',r'$|z|_{ex}=|z|-\sqrt{2/\pi}$'+'\n\nRelative effective gains\nweight channel-specific\nexcess magnitudes'),
 ('04  Accumulation',r'$S_{inst}=\sum_j\Pi^{eff}_{rel,j}|z_j^{eff}|_{ex}$'+'\n\nLeaky integration → '+r'$S_t$'+'\nSignal may be negative'),
 ('05  Ignition',r'$S_t>\theta_{eff,t}$'+'\n\nGlobal workspace\nbroadcast; partial reset\nand refractory dynamics')]
 for i,(title,body) in enumerate(labels):
  x=i*20;card(ax,x,36,18.5,57,title,body,size=7.8)
  if i<4:arr(ax,(x+18.5,64),(x+20,64),ms=10)
 card(ax,0,0,58,26,'Somatic-marker pathway',r'$\Pi_i^{eff}=g_{NE}\Pi_i\exp(\beta_{SM}\hat{M}(c,a))$'+'   (before clamping)',OI['verm'],10)
 card(ax,61,0,37.5,26,'Allostatic control','Cost raises θ; expected value lowers θ.',OI['green'],9)
 save(fig,name,'Model schematic','Mathematical Specification §§2–4, 13; normalization follows clamping. Default untransformed error channels shown.')
architecture();architecture('GA')

def circuit(name,laminar=False):
 fig,ax=canvas('Proposed cortical implementation of somatic-marker gain',6)
 for x,title,body,col in [(0,'vmPFC','Retrieval of the\nsomatic marker\n'+r'$\hat{M}(c,a)$',OI['purple']),(26,'VIP⁺ interneuron','Excitation from vmPFC\n\nInhibits SST⁺',OI['green']),(52,'SST⁺ interneuron','Reduced dendritic\ninhibition during\nmarker retrieval',OI['orange']),(78,'Pyramidal cell','Disinhibited dendrite\n\nInteroceptive\ngain increases',OI['verm'])]:
  card(ax,x,45,22,48,title,body,col)
 for x in [22,48,74]:arr(ax,(x,68),(x+4,68),style='-|>' if x==22 else '-[')
 if laminar:
  card(ax,0,0,48,31,'Laminar routes','L1: apical input · L4: thalamic evidence\nL2/3: PV⁺/VIP⁺/SST⁺ gain circuitry\nL5: burst output · L6: thalamic feedback',size=9)
  card(ax,52,0,48,31,'Apical–basal comparison','Prediction and evidence converge on L5 cells.\nPlateau physiology does not establish the\nproposed prediction-error computation.',OI['verm'],9)
 else:
  card(ax,0,0,100,30,'Interpretation','Proposed gain pathway; the physiological circuit does not by itself validate APGI.\nA causal circuit dissociation is required. Effective gains are clamped and causally normalized.',size=10)
 save(fig,name,'Proposed mechanism','Paper 1 Fig 2 / Paper 2 Fig 2; arrows specify proposed functional interactions.')
circuit('P1F2');circuit('P2F2',True)

fig,ax=canvas('Energy accounting and the uncalibrated information bridge',6)
card(ax,0,48,100,44,'Event-energy accounting',r'$2.4\times10^{18}$ ATP/event  ×  $5.07\times10^{-20}$ J/ATP  ≈  0.12 J/event'+'\n\nIndependent accounting estimate; not empirical calorimetry.',size=13)
card(ax,0,0,48,36,'κ: event-information bridge','ATP per bit of ignition-event information\nUncalibrated; no adopted numerical value\nMatched energy/information measurement required',OI['verm'])
card(ax,52,0,48,36,'Landauer: erasure consistency floor','Full reset: ~13–27 bits erased\nCanonical partial reset: ~1.0–3.3 bits erased\nErasure bits differ from broadcast-information bits',OI['green'])
save(fig,'P1F3','Derivation schematic','Paper 1 §4.6; Paper 4 Fig 1. Standard-state ATP conversion; κ and whole-event erasure ratio are distinct.')
runpy.run_path(str(ROOT/'f_p1f4.py'))
rows=[['Tier 3\nComputational','Protocols 2–3',wrap('Human model comparison; anticipation and precision-gain pathway',32),wrap('Prediction-specific model evidence; a single nonsignificant test is not framework falsification.',48)],
 ['Tier 2\nInformation-\ntheoretic','Protocol 1',wrap('Cardiac gating and behavioral Weibull shape k; distinct from intrinsic sigmoid gain.',32),wrap('Pred 1.E: 95% interval lower ≥10 AND ΔAIC >10; opposing or intermediate outcomes remain indeterminate.',48)],
 ['Tier 1\nThermodynamic','Protocol 4;\nmatched calibration',wrap('State × load interactions; κ remains uncalibrated.',32),wrap('Signed 15% d′ margin and registered evidence; covariate adjustment is not metabolic mediation.',48)]]
table('Epistemic tiers and their tests',['Tier','Design','Quantity','Decision context'],rows,[.13,.17,.30,.40],'P1F5',note='Protocol 0 gates HEP-dependent claims. Full interval rules and unresolved locks remain in protocols/*.json.')

for name,title,items in [
 ('P1S1','Parameter recovery: verification requirements',[
 ('Independent calibration','Freeze parameters and the observation model; keep calibration and human test data disjoint.'),
 ('Synthetic recovery','Generate from the frozen model, refit, and evaluate bias, interval coverage and parameter trade-offs.'),
 ('Identifiability gate','Use scaled information-matrix diagnostics and registered tolerances before confirmatory tests.'),
 ('Missing source results','The supplied image contains recovery statistics without the generating fits. They are not reasserted here.')]),
 ('P1S2','Sensitivity and robustness: verification requirements',[
 ('Freeze the model','Use relative effective precision and excess-surprise accumulation; enforce all gain constraints.'),
 ('Controlled perturbations','Vary parameters over specified ranges; track both sign and magnitude of changes.'),
 ('Independent realizations','Archive seeds, per-run outcomes and pass criteria; distinguish robustness from empirical validation.'),
 ('Unverified legacy values','The supplied code hard-codes ±50% effects and 10,000-run percentages. No raw sweep is included.')])]:
 fig,ax=canvas(title,5.5)
 for j,(a,b) in enumerate(items):card(ax,(j%2)*51,50-(j//2)*50,48,43,a,wrap(b,55),size=10)
 save(fig,name,'Analysis-design replacement','Quantitative panels pending verified recovery/sweep outputs from the canonical 1.1 implementation.')

rows=[['High-dimensional transient dynamics','Separate exteroceptive / interoceptive errors'],['Fading memory (~200–500 ms)','Evidence accumulation window'],['Nonlinear separability','Precision-dependent ignition probability'],['Sparse event-driven activity','Metabolic / allostatic threshold']]
table('Biological constraints and computational requirements',['Biological constraint','APGI requirement'],rows,[.5,.5],'P2F1',note='Paper 2 §2.5: conceptual analytical mapping; not a benchmark measurement.')

fig,axs=plt.subplots(1,2,figsize=(11,4.5));fig.subplots_adjust(wspace=.32,top=.82,bottom=.18)
a=np.linspace(.0001,.9999,40000); w=(.575+np.log(a/(1-a))/4)/a
ix=np.where(np.diff(np.sign(np.gradient(w,a))))[0];rho=w*(.95/w[ix[1]])
for mask,col,ls in [(a<=a[ix[0]],OI['blue'],'-'),((a>a[ix[0]])&(a<a[ix[1]]),INK,'--'),(a>=a[ix[1]],OI['verm'],'-')]:axs[0].plot(rho[mask],a[mask],ls,color=col)
axs[0].axvline(.95,color=INK,ls=':',lw=.8);axs[0].set(xlim=(.7,1.08),ylim=(0,1),xlabel='Scaled reduced-model control parameter',ylabel='Steady-state activity (normalized)',title='A  Reduced bistability illustration')
axs[0].text(.71,.88,'Fold fixed at 0.95 by rescaling\nSecond fold ≈1.02; not reservoir evidence',fontsize=8)
x=np.linspace(-2,2,500)
for pi in [.3,1,3,10]:axs[1].plot(x,1/(1+np.exp(-4*pi*x)),label=f'Π = {pi:g}')
axs[1].set(xlabel='Error-referred distance from threshold (AU)',ylabel='Ignition probability',title='B  Fixed intrinsic sigmoid gain γ = 4');axs[1].legend(frameon=False)
fig.suptitle('Reduced dynamics and precision-dependent ignition',x=.03,ha='left',fontsize=15,weight='bold')
save(fig,'P2F3','Reduced-model illustration','Π ≤ 10; γsig is not behavioral Weibull shape k. This hysteresis is not a result from the full reservoir model.')
runpy.run_path(str(ROOT/'f_p2f4.py'))

rows=[['L0','Reflexive sensory substrate','10–100 ms','50 ms','No ignition threshold'],['L1','Cortical reservoir','100 ms–3 s','6.6 s','Perceptual access'],['L2','Prefrontal–hippocampal','Minutes','15 min','Task integration'],['L3','Hippocampal–cortical','Hours–days','1.4 d','Situational / narrative'],['L4','DMN / medial prefrontal','Months–years','6 months','Identity; endocrine priors\nset cortical thresholds']]
table('Five levels: operational windows and spectral parameters',['Level','Substrate','Operational band','OU pole τ','Role'],rows,[.08,.25,.18,.14,.35],'P3F1',note='Paper 3 §2.1. Geometric poles are hypotheses; L0 is sub-APGI. Neuroendocrine systems set thresholds rather than ignite.')
runpy.run_path(str(ROOT/'f_p3f2.py'))
fig,ax=canvas('Fast and slow neuromodulatory influences',6)
card(ax,0,45,48,48,'Fast: ACC → locus coeruleus','Level-3 cortical signal → brainstem relay\nPhasic NE modulates Level-1 threshold\nTonic NE can alter Level-0 gain\nLC is a relay, not a hierarchical stratum',OI['blue'],11)
card(ax,52,45,48,48,'Slow: PVN → HPA axis','CRH → ACTH → cortisol\nRapid membrane-MR facilitation\nSustained GR suppression\nNeuroendocrine priors modulate cortex',OI['verm'],11)
card(ax,0,0,100,30,'Coupling notation',r'$\alpha_{31}=\kappa_{12}\kappa_{23}$     $\alpha_{41}=\kappa_{12}\kappa_{23}\kappa_{34}$'+'\nMulti-step influences are compositions, not independent free parameters.',size=12)
save(fig,'P3F3','Proposed mechanism','Paper 3 §3 / Fig 3. Subscripted coupling κ differs from the ATP/bit bridge κ.')
rows=[['Major depression','L1 interoceptive precision ↓;\nmultilevel threshold changes','Prespecified APGI profile\nversus generic EEG features'],['Schizophrenia','L2 precision genotype-dependent;\ncross-level coupling disruption','Do not impose one universal\nprecision direction'],['Disorders of consciousness','Clinical biomarker study;\nHEP and PCI eligibility differ','Pred 7.G primary prognosis;\njoint biomarker estimative']]
table('Clinical profiles require specificity controls',['Profile','Proposed disturbance','Evaluation'],rows,[.22,.40,.38],'P3F4',note='Paper 3: AUC ≥0.75, within-site label permutations, ΔAUC ≥0.05 beyond generic EEG features with BCa CI excluding zero.')
runpy.run_path(str(ROOT/'f_p3f6.py'))
rows=[['3 · Computational','Relative precision × excess error;\nleaky accumulation and access gate','Approximate inference bridge:\nnot validated in vivo'],['2 · Information-theoretic','Bits per ignition event;\nevent definition must be fixed','κ in ATP / event-information bit:\nuncalibrated'],['1 · Thermodynamic','Matched event energy\nin ATP or joules','Compare with independent accounting;\nLandauer is an erasure floor only']]
table('Epistemic tiers and the double-bridge chain',['Tier','Currency','Bridge / interpretation'],rows,[.20,.40,.40],'P4F1',note='Paper 4 Fig 1: ignition information and erased information have different denominators; upward bridges remain unspecified.')
scores={name:[np.nan if v is None else v for v in values] for name,values in MANUSCRIPT['Paper4']['audit_scores'].items()}
fig,ax=plt.subplots(figsize=(12,5));fig.subplots_adjust(top=.78,bottom=.24)
x=np.arange(7);colors=[OI['sky'],OI['orange'],OI['grey'],OI['purple']]
for j,(label,values) in enumerate(scores.items()):
 xx=x+(j-1.5)*.2;ax.bar(xx,values,.18,label=label,color=colors[j],hatch='///' if j==3 else None)
 for xi,v in zip(xx,values):
  if np.isnan(v):ax.text(xi,.04,'N/A',ha='center',rotation=90,fontsize=8)
  elif v==0:ax.text(xi,.04,'0',ha='center',fontsize=8)
ax.errorbar(x[[2,3]]+.3,[4/3]*2,yerr=[[1/3]*2,[2/3]*2],fmt='none',ecolor=INK,capsize=4)
ax.axhline(1.1,ls='--',color=INK,lw=.8);ax.set_ylim(0,2.15);ax.set_ylabel('Author-assigned coarse score (0–2)')
ax.set_xticks(x,['C1\nTier transparency','C2\nBridge principles','C3\nQuantitative\nbenchmarks','C4\nFalsification','C5\nAlternative\ncomparison','C6\nEvolutionary\nplausibility','C7\nCausal roadmap'])
ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,1.22),frameon=False)
fig.suptitle('Comparative audit: manuscript Table 8',x=.03,ha='left',fontsize=16,weight='bold')
fig.text(.08,.03,'C3 / C4 bars: tier range, not uncertainty. IIT C6 is excluded from its denominator.\nAggregate scores: GNWT 7/14 · IIT 4/12 · PP/FEP 6/14 · APGI 9⅔/14. Foundational gates also apply.',fontsize=9)
save(fig,'P4F2','Single-author provisional audit','No independent scoring performed. Dashed 1.1 line is the 55/100 canonical threshold; coarse acceptance ≥8/14 (≥7/12 for IIT).')
rows=[]
for p in MANUSCRIPT['Paper4']['predictions']:
 rows.append([p['id'].replace('Prediction ','P')+' / T'+p['tier'],wrap(p['prediction'],35),wrap(p['target'],39),wrap(p['falsification'],43),wrap(p['horizon']+'; '+p['status'],30)])
table('Twelve forward predictions: Paper 4 Table S4',['ID / tier','Prediction','Target','Evidence against','Horizon / current status'],rows,[.09,.23,.24,.26,.18],'P4F3',kind='Prospective prediction matrix',note='Paper 4 exposition IDs differ from Protocol Pred IDs. Pending registration and calibration are retained.',fontsize=8)

fig,ax=canvas('Stimulation and intracranial recording test distinct predictions',6)
card(ax,0,0,48,93,'Protocol 5 / non-invasive intervention','Right aINS: tFUS / dTMS + matched sham\ndlPFC / PPC: TMS reference comparisons\n\nTarget engagement gates aINS inference.\nSeparate resting PCI probes.\n95% HDI + BF evidence for HEP equivalence.\n\nNo universal vertex-sham assumption.',size=11)
card(ax,52,0,48,93,'Protocol 6 / implanted electrodes','500 ms fixation → 33 ms Gabor → 1 s delay\n600 trials on an absolute contrast grid\n\nClinically indicated electrodes only.\nFixed-contrast bimodality; regional controls.\nAC1 estimation requires validation.\n\nCoverage-specific sample sizes reported.',OI['green'],11)
save(fig,'P2S1','Prospective design schematic','Protocol JSON overrides the older manuscript/bundle 60 ms target and 250 ms response schematic.')

from protocol_panels import build as build_protocol_panels
build_protocol_panels(PROTOCOLS)
from concept_panels import build as build_concept_panels
build_concept_panels()

MAPPING={
'GA':None,'P1F1':'v1_0/paper1/output/fig1_architecture_pipeline','P1F2':'v1_0/paper1/output/fig2_somatic_marker_circuit','P1F3':'v1_0/paper1/output/fig3_thermodynamic_bridge','P1F4':'v1_0/paper1/output/fig4_onset_ignition_timeline','P1F5':'v1_0/paper1/output/fig5_epistemic_tier_falsification_mapping','P1S1':'v1_0/paper1/output/figS1_parameter_recovery','P1S2':'v1_0/paper1/output/figS2_sensitivity_tornado','P1S3':'v1_0/paper1/output/figS3_protocol1_trial_timeline','P1S4':'v1_0/paper1/output/figS4_protocol3_fmri_trial',
'P2F1':'v1_0/paper2/output/fig1_biological_constraints_lsm','P2F2':'v1_0/paper2/output/fig2_cortical_microcircuit','P2F3':'v1_0/paper2/output/fig3_bifurcation_analysis','P2F4':'v1_0/paper2/output/fig4_visual_masking_trajectories','P2S1':'v1_0/paper2/output/figS1_ep2_ep6_protocol_schematics','P3F1':'v1_0/paper3/output/fig1_russian_doll_hierarchy','P3F2':'v1_0/paper3/output/fig2_1f_power_spectrum','P3F3':'v1_0/paper3/output/fig3_neuromodulatory_coupling','P3F4':'v1_0/paper3/output/fig4_psychiatric_disorder_profiles','P3F5':'v1_0/paper3/output/figS1_protocol7_clinical_design','P3F6':'v1_0/paper3/output/fig5_developmental_maturation_spectral','P4F1':'v1_0/paper4/output/fig1_three_tier_epistemic_architecture','P4F2':'v1_0/paper4/output/fig2_comparative_audit_bar_chart','P4F3':'v1_0/paper4/output/figS1_twelve_prediction_matrix',**{f'PRF{i}':f'v1_0/output/figure{i}' for i in range(1,9)}}
assert set(RECORDS)==set(MAPPING),(set(RECORDS)^set(MAPPING))
manifest={'release':'1.1','status':'review series; quantitative recovery and sensitivity panels pending','figures':[],'protocol_inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((REPO/'protocols').glob('protocol_*.json'))}}
sections=[]
for name,old in MAPPING.items():
 rec={'id':name,'previous':old,**RECORDS[name],'caption':CAPTIONS[name],'outputs':{}}
 for ext in ['png','pdf','svg']:
  p=OUT/f'{name}.{ext}';rec['outputs'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 if old:rec['previous_sha256']=hashlib.sha256((ROOT.parent/(old+'.png')).read_bytes()).hexdigest()
 manifest['figures'].append(rec)
 before=f'<img loading="lazy" src="../{old}.png" alt="Existing version 1.0 {name}">' if old else '<p>New graphical abstract</p>'
 sections.append(f'<section id="{name}"><h2>{name}</h2><p>{html.escape(rec["kind"])} · {html.escape(rec["note"])}</p><p>{html.escape(CAPTIONS[name])}</p><div class="pair"><figure><figcaption>Existing 1.0</figcaption>{before}</figure><figure><figcaption>Updated 1.1 · <a href="output/{name}.pdf">PDF</a> · <a href="output/{name}.svg">SVG</a> · <a href="output/{name}.png">PNG</a></figcaption><a href="output/{name}.png"><img loading="lazy" src="output/{name}.png" alt="Version 1.1 {name}"></a></figure></div></section>')
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(ROOT/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>APGI 1.1 figure comparison</title><style>body{font:16px system-ui;color:#20262e;margin:40px;background:#f5f7f9}h1{font-size:36px}section{background:white;padding:24px;margin:24px 0;border-radius:12px}p{max-width:1000px;line-height:1.5}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}figure{margin:0}figcaption{font-size:14px;margin:12px 0;color:#526273}img{width:100%;height:auto}a{color:#0072b2}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>APGI 1.1 / Figure comparison</h1><p>All 31 existing figures are mapped below, plus a new graphical abstract. The 1.0 baseline is preserved. Protocol figures show prospective designs, not observed results. Recovery and sensitivity results await verifiable source data; their replacements show the required analyses.</p><p><a href="README.md">Audit and reproduction notes</a> · <a href="MANIFEST.json">Output manifest</a></p>'''+''.join(sections)+'</html>')
print(f'Built {len(RECORDS)} figures, each in PNG, PDF and SVG. Gallery: {ROOT / "index.html"}')

(ROOT/'CAPTIONS.md').write_text('# Revised captions — APGI 1.1 review series\n\n'+ '\n\n'.join('## '+name+'\n\n'+CAPTIONS[name] for name in MAPPING)+'\n')
