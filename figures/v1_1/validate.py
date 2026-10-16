"""Validate release completeness, provenance, vector exports and readable files."""
from pathlib import Path
import hashlib
import json
import platform
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate():
 m=json.loads((ROOT/'MANIFEST.json').read_text())
 errors=[];checked=[]
 ids=[r['id'] for r in m['figures']]
 expected={'GA',*[f'P1F{i}' for i in range(1,6)],*[f'P1S{i}' for i in range(1,5)],*[f'P2F{i}' for i in range(1,5)],'P2S1',*[f'P3F{i}' for i in range(1,7)],*[f'P4F{i}' for i in range(1,4)],*[f'PRF{i}' for i in range(1,9)]}
 if set(ids)!=expected or len(ids)!=len(expected):errors.append('Figure IDs differ from the expected 32-set release')
 old={p.relative_to(ROOT.parent).with_suffix('').as_posix() for p in ROOT.parent.glob('**/output/*.png') if ROOT not in p.parents}
 mapped={r['previous'] for r in m['figures'] if r['previous']}
 if old!=mapped:errors.append(f'Legacy coverage differs: {old^mapped}')
 for name,value in m['protocol_inputs'].items():
  if digest(REPO/'protocols'/name)!=value:errors.append(f'Protocol changed since generation: {name}')
 for r in m['figures']:
  if r['previous'] and digest(ROOT.parent/(r['previous']+'.png'))!=r['previous_sha256']:errors.append(f'Baseline changed: {r["previous"]}')
  for name,sha in r['outputs'].items():
   p=ROOT/'output'/name
   if not p.exists():errors.append(f'Missing output: {name}');continue
   if digest(p)!=sha:errors.append(f'Checksum mismatch: {name}')
   try:
    if p.suffix=='.png':
     with Image.open(p) as im:
      if min(im.size)<500:errors.append(f'Unexpectedly small raster: {name}')
      if abs(im.info.get('dpi',(0,0))[0]-300)>1:errors.append(f'Not 300 dpi: {name}')
      im.verify()
    elif p.suffix=='.pdf':
     doc=PdfReader(p)
     if len(doc.pages)!=1:errors.append(f'Expected single-page figure: {name}')
     if 'APGI 1.1' not in doc.pages[0].extract_text():errors.append(f'Release label absent: {name}')
    else:
     svg=ET.parse(p).getroot()
     if svg.findall('.//{http://www.w3.org/2000/svg}image'):errors.append(f'Raster embedded in vector export: {name}')
   except Exception as exc:errors.append(f'Unreadable {name}: {exc}')
  checked.append(r['id'])
 # Verify the preserved supplied source independently of generated files.
 prov=json.loads((ROOT/'PROVENANCE.json').read_text())
 for path,sha in prov['files'].items():
  p=Path(path)
  if '/bundle/code/' in path and digest(ROOT/'source'/p.name)!=sha:errors.append(f'Archived supplied source modified: {p.name}')
 report={'release':'1.1','passed':not errors,'figure_sets':len(checked),'exports':sum(len(r['outputs']) for r in m['figures']),'legacy_figures_mapped':len(mapped),'checks':['Expected IDs and complete legacy mapping','Protocol input hashes','Unchanged baseline PNG hashes','All output checksums','PNG decode and 300-dpi metadata','One-page readable PDFs with release labels','Parsed SVGs without embedded rasters','Preserved supplied code hashes'],'quantitative_panels_pending':['P1S1','P1S2'],'scientific_validation_performed':False,'errors':errors,'python':platform.python_version()}
 (ROOT/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':validate()
