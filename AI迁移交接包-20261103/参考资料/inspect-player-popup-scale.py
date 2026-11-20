from pathlib import Path
import sys,json
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
P=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
e=UnityPy.load(str(P/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));oo={o.path_id:o for o in e.objects}
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988]:
 d=oo[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=oo[d['inlineSheet']['m_PathID']].read_typetree()
 print('ASSET',d['m_Name'],'root',d['m_VisualTree'])
 for r in rr.values():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if 'm_Parent' not in a:continue
  idx=a.get('m_RuleIndex',-1);props=s['m_Rules'][idx]['m_Properties'] if idx>=0 else []
  v={p['m_Id']:[s[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h for h in p['m_Values']] for p in props}
  if sd.get('name','').startswith('Fixed_'):continue
  if pid==-498859349613660051 and not ('FixedPlayer' in sd.get('name','') or 1342 in [x.get('value') for vs in v.values() for x in vs if isinstance(x,dict)] or r['rid']==70007):continue
  print(r['rid'],a.get('m_FullTypeName'),sd.get('name'),a['m_Parent'],a.get('m_Children'),v)
