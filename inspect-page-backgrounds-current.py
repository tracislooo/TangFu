from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
rows=[]
for p in G.glob('*visualtree*.bundle'):
 e=UnityPy.load(str(p));oo={o.path_id:o for o in e.objects}
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']}
  for r in rr.values():
   a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   if sd.get('name')=='Card-frame' or (d['m_Name']=='GameWorldBackground' and 'm_FullTypeName' in a):
    sh=oo.get(d['inlineSheet']['m_PathID']);sh=sh.read_typetree() if sh else {};i=a.get('m_RuleIndex',-1)
    ps=[x for x in sh.get('m_Rules',[])[i]['m_Properties'] if x['m_Id'] in [458752,458753,262153]] if i>=0 else []
    rows.append({'bundle':p.name,'pid':o.path_id,'template':d['m_Name'],'rid':r['rid'],'type':a.get('m_FullTypeName'),'sd':sd,'classes':a.get('m_Classes'),'props':ps})
(R/'inspect-page-backgrounds-current.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
print([(x['template'],x['rid'],x['type']) for x in rows])
e=UnityPy.load(str(G/'ui-backgrounds_assets_common.bundle'));o=next(o for o in e.objects if o.path_id==-910000000000149);assert o.peek_name()=='TF skin V1';o.read().image.save(str(R/'TF-skin-V1-current-preview.png'))
print('TF skin V1 extracted')
