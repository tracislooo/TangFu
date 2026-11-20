from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,subprocess
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.classes import PPtr
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';BG='ui-backgrounds_assets_common.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
records={x['name']:x for x in registry['textures']}
before={};outputs={};changes=[];audit=[]
for folder in [GAME,SKIN]:
 p=folder/W;before[p]=p.read_bytes();env=UnityPy.load(before[p]);a=env.assets[0];obs=a.objects
 bgbytes=(folder/BG).read_bytes();bg=UnityPy.load(bgbytes).assets[0]
 assert reserved.isdisjoint(bg.objects)
 meta=next(o.read_typetree() for o in bg.objects.values() if o.type.name=='AssetBundle')
 assert all(v['asset']['m_PathID'] not in reserved for k,v in meta['m_Container'])
 assert all(v['m_PathID'] not in reserved for v in meta['m_PreloadTable'])
 for name in ['TFWX','BB','DY']:
  t=records[name];ob=bg.objects[int(t['path_id'])];assert ob.peek_name()==name and sha(ob.get_raw_data())==t['texture_sha256']
 fid=next(i+1 for i,x in enumerate(a.externals) if x.path==f'archive:/{bg.name}/{bg.name}')
 proto=next(o.read_typetree() for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AccessibilityPreferencesTile_4x2')
 pr={r['rid']:r for r in proto['references']['RefIds']};pn=pr[1004];ps=pr[pn['data']['m_SerializedData']['rid']]
 expected={};guids=[]
 for name,header,parent,decor,pictures in [('OnlineGamePreferencesTile_4x2',1004,1002,1006,['TFWX']),('AccessibilityPreferencesTile_4x2',1002,1001,1009,['BB','DY'])]:
  ob=next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
  d=ob.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
  so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  st.edit(rr[parent],[st.p(131102,st.en('relative')),st.p(131087,st.pct(100))])
  st.edit(rr[header],[st.p(131087,st.px(110)),st.p(131096,st.px(110)),st.p(131094,st.px(110)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131105,st.pct(100))])
  st.edit(rr[decor],[st.p(458767,st.num(0))])
  def add(parent,name):
   rid=max(rr)+1;n=copy.deepcopy(pn);sd=copy.deepcopy(ps);uid=1987000000+rid
   n['rid']=rid;sd['rid']=rid+1;n['data'].update(m_Id=uid,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_RuleIndex=-1,m_SerializedData={'rid':rid+1})
   sd['data'].update(uxmlAssetId=uid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
   d['references']['RefIds'] += [n,sd];rr[rid]=n;rr[rid+1]=sd;rr[parent]['data']['m_Children'].append({'rid':rid})
   return n
  box=add(parent,'PreferencePictures')
  st.edit(box,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(122)),st.p(131075,st.px(0)),st.p(131105,st.pct(100))],reset=True)
  for i,picture in enumerate(pictures):
   n=add(box['rid'],'PreferencePicture'+picture);ptr={'m_FileID':fid,'m_PathID':int(records[picture]['path_id'])}
   st.edit(n,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.pct(i*52)),st.p(131105,st.pct(100)),st.p(131087,st.pct(100 if len(pictures)==1 else 48)),st.p(458753,st.h(6,ptr)),st.p(262153,st.en('scale-to-fit'))],reset=True)
  ob.save_typetree(d);so.save_typetree(s);expected[ob.path_id]=d;expected[so.path_id]=s
  bm=next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle');guid=next(k for k,v in bm['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':ob.path_id});guids.append(guid)
  changes.append({'folder':str(folder),'template':name,'guid':guid,'header_height':110,'pictures':pictures})
 payload=env.file.save(packer='lz4');checked=UnityPy.load(payload).assets[0]
 assert set(checked.objects)==set(obs)
 original=UnityPy.load(before[p]).assets[0]
 for pid,obj in checked.objects.items():
  if pid in expected:assert obj.read_typetree()==expected[pid]
  else:assert obj.get_raw_data()==original.objects[pid].get_raw_data(),pid
 linked=UnityPy.load(payload,bgbytes);la=next(x for x in linked.assets if x.name==a.name)
 for name in ['TFWX','BB','DY']:
  obj=PPtr(m_FileID=fid,m_PathID=int(records[name]['path_id']),assetsfile=la).deref();assert sha(obj.get_raw_data())==records[name]['texture_sha256']
 outputs[p]=payload
 sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
 cp=(GAME.parent if folder==GAME else folder)/'catalog.bin';before[cp]=cp.read_bytes();c=cm.Catalog(before[cp]);locs={l for _,ptr in c.keys() for (l,) in c.array(ptr,'I')}
 def bl(n):return next(l for l in locs if c.location(l)['provider'].endswith('.AssetBundleProvider') and c.location(l)['internal'].endswith('\\'+n))
 own=bl(W);bgl=bl(BG)
 for loc in locs:
  deps=c.location(loc)['dependencies']
  if own in deps and bgl not in deps:
   pos=c.append(struct.pack('<'+'I'*(len(deps)+1),*(deps+[bgl])),True);struct.pack_into('<I',c.data,loc+12,pos)
 for guid in guids:
  assert c.locations(guid)
  for loc in c.locations(guid):
   v=c.location(loc);assert v['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','UnityEngine.UIElements.StyleSheet'] and v['dependencies'][0]==own and bgl in v['dependencies']
 audit.append({'catalog':str(cp),'template_guids':guids,'background_dependency_verified':True})
 if bytes(c.data)!=before[cp]:
  outputs[cp]=bytes(c.data);hp=cp.with_name('catalog.hash');before[hp]=hp.read_bytes();outputs[hp]=hashlib.md5(outputs[cp]).hexdigest().encode('ascii')
out=R/('preferences-picture-panels-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir()
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p not in outputs}
for p in [R/'current-custom-textures.json',R/'reserved-texture-ids.json']:
 protected[str(p)]=sha(p.read_bytes())
tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in outputs.items():
 tag='game' if p.parent in [GAME,GAME.parent] else 'skin';dst=out/tag/p.name;bak=out/('backup-'+tag)/p.name
 dst.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'changes':changes,'catalog_audits':audit,'before_sha256':{str(p):sha(before[p]) for p in outputs},'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_sha256':protected,'unrelated_objects_preserved':True,'texture_references_verified':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"'"+flag+'\n','utf8')
print(out,flush=True)
subprocess.run([sys.executable,str(R/'install-native-background-overrides.py'),str(out)],check=True)
