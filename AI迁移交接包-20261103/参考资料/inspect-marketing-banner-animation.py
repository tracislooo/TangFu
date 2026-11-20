import sys,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
E=UnityPy.load(str(G/'ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle'))
O=R/'marketing-banner-animation-inspection';O.mkdir(exist_ok=True)
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
c=cm.Catalog((G.parent/'catalog.bin').read_bytes())
for loc in c.locations('073b324505f39d44796109e923324e46'):
 v=c.location(loc);print('RENDER_TEXTURE_LOCATION',v)
 for dep in v['dependencies']:
  dv=c.location(dep)
  if dv['provider'].endswith('.AssetBundleProvider'):
   print('DEPENDENCY',dv['internal'])
   if dv['internal'].endswith('.bundle'):
    filename=dv['internal'].split('\\')[-1]
    env=UnityPy.load(str(G/filename))
    meta=next(o.read_typetree() for o in env.objects if o.type.name=='AssetBundle')
    for k,entry in meta['m_Container']:
     if k!='073b324505f39d44796109e923324e46':continue
     ob=env.assets[0].objects[entry['asset']['m_PathID']]
     print('RENDER_TEXTURE',filename,ob.path_id,ob.type.name,ob.read_typetree())
if '--catalog-only' in sys.argv:
 for filename in ['promobanner_assets_all.bundle','videos-pc_assets_all.bundle','videos_assets_all.bundle']:
  env=UnityPy.load(str(G/filename));print('BUNDLE',filename,'OBJECTS',len(env.objects))
  for ob in env.objects:
   print('OBJECT',ob.path_id,ob.type.name,ob.peek_name())
   if ob.type.name in ['MonoBehaviour','VideoPlayer','VideoClip','GameObject','Animation','Animator','AnimationClip']:
    tree=ob.read_typetree();(O/(filename+'-'+str(ob.path_id)+'.json')).write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8');print('DATA',json.dumps(tree,ensure_ascii=False))
 sys.exit(0)
for o in E.objects:
 if o.type.name!='MonoBehaviour' or o.peek_name()!='MarketingBannerTile_8x2':continue
 d=o.read_typetree();(O/'MarketingBannerTile_8x2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
 rr={r['rid']:r for r in d['references']['RefIds']}
 def visit(i,depth=0):
  r=rr[i]['data'];data=rr.get(r.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*depth,i,r.get('m_FullTypeName',r.get('m_TemplateAlias')),r.get('m_Classes'))
  print(json.dumps(data,ensure_ascii=False))
  for ch in r.get('m_Children',[]):visit(ch['rid'],depth+1)
 visit(d['m_VisualTree']['rid'])
 s=o.assets_file.objects[d['inlineSheet']['m_PathID']].read_typetree()
 (O/'style.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
 print('STYLES',json.dumps(s,ensure_ascii=False))
