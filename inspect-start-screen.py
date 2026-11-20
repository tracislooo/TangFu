import sys,json,importlib.util
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
c=cm.Catalog((G.parent/'catalog.bin').read_bytes())
for n in ['ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_initvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/n));a=e.assets[0];meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
 print('BUNDLE',n,'externals',[(i+1,x.path) for i,x in enumerate(a.externals)])
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name()
  if not any(x.lower() in name.lower() for x in ['MainMenu','StartJourneyBackground','Intro','Background']):continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  print('TEMPLATE',name,o.path_id,'guid',[k for k,v in meta['m_Container'] if v['asset']['m_PathID']==o.path_id])
  out=R/'start-screen-inspection';out.mkdir(exist_ok=True)
  if name not in ['MainMenuBackground']:continue
  (out/(name+'.json')).write_text(json.dumps(d,indent=2),'utf8')
  s=a.objects[d['inlineSheet']['m_PathID']].read_typetree();(out/(name+'-style.json')).write_text(json.dumps(s,indent=2),'utf8')
  rr={r['rid']:r for r in d['references']['RefIds']}
  def visit(i,depth=0):
   r=rr[i]['data'];sd=rr.get(r.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   print(' '*depth,i,r.get('m_FullTypeName',r.get('m_TemplateAlias')),sd.get('name'),r.get('m_Classes'),r.get('m_RuleIndex'))
   if r.get('m_RuleIndex',-1)>=0:print(' '*depth,'STYLE',s['m_Rules'][r['m_RuleIndex']]['m_Properties'])
   if any(x in str(sd).lower() for x in ['rendertexture','portrait','model']):print(' '*depth,'DATA',sd)
   for ch in r.get('m_Children',[]):visit(ch['rid'],depth+1)
  visit(d['m_VisualTree']['rid'])
for loc in c.locations('94f5bb180219bb54f9ac08e198272e18'):print('BACKGROUND_LOCATION',c.location(loc))
