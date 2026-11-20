import sys,json
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
e=UnityPy.load(str(G/'ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle'))
obj=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MarketingBannerTile_8x2')
d=obj.read_typetree();s=obj.assets_file.objects[d['inlineSheet']['m_PathID']].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
print('template',obj.path_id,'style',d['inlineSheet'],'externals',[x.path for x in obj.assets_file.externals])
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for rid,r in rr.items():
 a=r.get('data',{})
 if 'm_Parent' not in a:continue
 sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 print('NODE',rid,a['m_FullTypeName'],sd.get('name'),a['m_Parent'],a['m_Children'],a.get('m_Classes'))
 print('STYLE',[(p['m_Id'],[s[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h for h in p['m_Values']]) for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']] if a.get('m_RuleIndex',-1)>=0 else [])
 if sd.get('name') in ['banner','SimpleBanner']:print('image',sd)
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
print('REGISTRY',registry['version'],registry['active_custom_texture_count'],[t for t in registry['textures'] if t['name']=='TFWX'])
print('STYLESHEETS',[p.name for p in G.glob('*style*.bundle')])
if '--styles' in sys.argv:
 for filename in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle','ui-styles_assets_.bundle']:
  env=UnityPy.load(str(G/filename))
  for ob in env.objects:
   if ob.type.name!='MonoBehaviour':continue
   try:t=ob.read_typetree()
   except Exception:continue
   if 'm_Rules' not in t:continue
   for rule in t['m_Rules']:
    if not any('logged-in-out-banner_8fps_en-1' in str(sel) for sel in rule.get('m_ComplexSelectors',[])):continue
    print('BANNER_STYLES',filename,ob.peek_name(),[(p['m_Id'],[t[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h for h in p['m_Values']]) for p in rule['m_Properties']])
