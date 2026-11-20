"""Install square, contained portraits outside matches; preserve the match dependency closure."""
from pathlib import Path
R=Path(__file__).resolve().parent
V='ui-tableviews_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','outside-match-square-portraits-').replace('NAMES=[W,G,M,F]','NAMES=[W,G,F,V]').replace('hours=-4','hours=-6')
exec(compile(boot,'bundle-codecs','exec'))
import re,subprocess,os
plan=(R/'plan-outside-match-portraits.py').read_text('utf8')
plan=plan[plan.index('env={n:'):plan.index("out={'bases'")]
plan=plan.replace("env={n:UnityPy.load(str(GAME/n)) for n in [W,G,M,F,V]}","env[M]=UnityPy.load(str(GAME/M))")
exec(compile(plan,'match-dependency-closure','exec'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(x['path_id']) for x in reserved}|{-910000000000146}
protected.update({p:sha(p.read_bytes()) for p in [R/'current-custom-textures.json',R/'reserved-texture-ids.json']})
reverseguid={k:g for g,k in guidmap.items()}
# An unused historical player cell has no callers and needs no new copy.
clones={k for k in clones if k in reverseguid and reverse.get(k)}
base &= clones
gmap={reverseguid[k]:uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/outside-match-square/'+k[0]+'/'+str(k[1])).hex for k in clones}
newids={};nextpid=-990000000060000
for key in sorted(clones):
 while nextpid in banned or any(nextpid in o for o in objs.values()):nextpid-=1
 newids[key]=nextpid;nextpid-=2
allchanged={};cloneaudit=[];shapeaudit=[];nameaudit=[]

def put(n,pid,source,d):
 if pid not in objs[n]:
  ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[n][pid]=ob
 objs[n][pid].save_typetree(d);changes[n][pid]=copy.deepcopy(d)

def rewrite(v,mapping):
 if isinstance(v,dict):return {k:rewrite(x,mapping) for k,x in v.items()}
 if isinstance(v,tuple):return tuple(rewrite(x,mapping) for x in v)
 if isinstance(v,list):
  if v and all(isinstance(x,int) and 0<=x<256 for x in v):
   b=bytes(v)
   for a,z in mapping.items():b=b.replace(a.encode(),z.encode())
   return list(b)
  return [rewrite(x,mapping) for x in v]
 if isinstance(v,str):
  for a,z in mapping.items():v=v.replace(a,z)
 return v

picbase=next(k for k in base if docs[k]['m_Name']=='PersonPicture')
thumbbase=next(k for k in base if docs[k]['m_Name']=='thumbnails-alt-person-picture')
picguid=gmap[reverseguid[picbase]]
namebases={k for k in base if docs[k]['m_Name'].startswith('PlayerNameCell')}
nameguids={reverseguid[k] for k in namebases}
originalpics={reverseguid[picbase],reverseguid[thumbbase]}
donor=Doc(W,pid=-4028782843705546248)
PIC=next(i for i,x in donor.r.items() if x.get('data',{}).get('m_TemplateAlias')=='PersonPicture')
mapperdonor=Doc(W,name='PlayerKitNameCell')

def unround(d,i):
 d.st(i,[(p,d.px(0)) for p in [262144,262145,262146,262147]]+[(458768,d.enum('visible'))])

for key in sorted(clones | (affected-closure)):
 n,pid=key
 if n==M or key in roots:continue
 original=docs[key];mapping=dict(gmap)
 direct={u['path'] for u in original.get('m_Usings',[])}
 # Existing portrait/name rows keep their original inner name cell, avoiding two photos.
 hasportrait=bool(direct & originalpics) or 'Portrait' in original['m_Name']
 if hasportrait:
  for g in nameguids:mapping.pop(g,None)
 tree=rewrite(copy.deepcopy(original),mapping)
 isclone=key in clones;dest=newids[key] if isclone else pid
 if 'inlineSheet' not in tree:
  if tree!=original or isclone:
   if isclone:tree['m_Name']='OutsideMatchSquare_'+tree['m_Name'];cloneaudit.append({'bundle':n,'source_pid':pid,'pid':dest,'source_guid':reverseguid[key],'guid':gmap[reverseguid[key]],'kind':'factory'})
   put(n,dest,objs[n][pid],tree)
  continue
 sheet=copy.deepcopy(objs[n][tree['inlineSheet']['m_PathID']].read_typetree())
 if isclone:
  tree['m_Name']='OutsideMatchSquare_'+tree['m_Name'];tree['inlineSheet']['m_PathID']=dest-1;sheet['m_Name']=tree['m_Name']+'Style'
  put(n,dest,objs[n][pid],tree);put(n,dest-1,objs[n][original['inlineSheet']['m_PathID']],sheet)
 d=Doc(n,pid=dest,tree=tree,style=sheet)
 localshape=[]
 if key==picbase:
  # All licensed, database, generated and fallback branches retain the native bindings.
  for i,x in d.r.items():
   a=x.get('data',{});typ=a.get('m_FullTypeName','')
   if 'm_Parent' not in a or typ.endswith('UXML'):continue
   if a.get('m_Classes') is not None:
    unround(d,i)
    if 'SIImage' in typ:
     d.data(i).update(ScaleMode=2,ScaleMode_UxmlAttributeFlags=1,scaleMode=2,scaleMode_UxmlAttributeFlags=1)
     d.st(i,[(262153,d.enum('scale-to-fit'))])
  # Cancel the inherited 75% portrait scale only in this new outside-match copy.
  for i,x in d.r.items():
   if 'SIAspectRatioFitter' in x.get('data',{}).get('m_FullTypeName',''):
    d.st(i,[(327681,[d.num(1),d.num(1)]),(131105,d.pct(100)),(131087,d.pct(100)),(131096,d.px(0)),(131097,d.px(0))])
 if key in namebases:
  parent=1002 if pid==3076847569483052660 else 1001
  assert parent in d.r
  m=d.add(mapperdonor,1007,parent,'OutsideMatchPlayerPortraitBinding')
  d.data(m).update(Mappings=[{'m_serialisedType':0,'from':'person','to':{'m_path':'binding'},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1)
  d.size(m,24,24);d.st(m,[(131090,d.px(5))]);d.move(m,parent,0)
  p=d.add(donor,PIC,m,'OutsideMatchPlayerPortrait');d.fill(p);unround(d,p)
  if not any(u['alias']=='PersonPicture' for u in d.d['m_Usings']):d.d['m_Usings'].append({'alias':'PersonPicture','path':picguid,'asset':{'m_FileID':0,'m_PathID':0}})
  d.st(parent,[(131083,d.enum('row')),(131073,d.enum('center'))])
  nameaudit.append({'source':original['m_Name'],'pid':dest,'size':24,'binding':'binding -> person'})
 # Override rounding on portrait instances; selectors from inherited thumbnail classes
 # otherwise impose a circular clip even when PersonPicture itself is rectangular.
 aliases={u['alias'] for u in d.d['m_Usings'] if u['path'] in originalpics or u['path'] in {gmap[g] for g in originalpics}}
 for i,x in list(d.r.items()):
  a=x.get('data',{})
  if a.get('m_TemplateAlias') not in aliases:continue
  unround(d,i);localshape.append(i)
  if 'Circle' in original['m_Name']:
   parent=a['m_Parent']['rid']
   if parent in d.r and parent!=1000:unround(d,parent)
 if key==thumbbase:unround(d,1001)
 if isclone or d.d!=original or d.s!=sheet:
  d.save();allchanged[key]=dest
  if localshape:shapeaudit.append({'name':original['m_Name'],'bundle':n,'nodes':localshape})
  if isclone:cloneaudit.append({'bundle':n,'source_pid':pid,'pid':dest,'style':dest-1,'source_guid':reverseguid[key],'guid':gmap[reverseguid[key]],'kind':'template'})

# Add new entries using the source preload span, then include the new style/object.
for n in NAMES:
 mo=next(o for o in objs[n].values() if o.type.name=='AssetBundle');mt=mo.read_typetree()
 for c in [c for c in cloneaudit if c['bundle']==n]:
  source=next(v for g,v in mt['m_Container'] if g==c['source_guid'] and v['asset']=={'m_FileID':0,'m_PathID':c['source_pid']})
  span=copy.deepcopy(mt['m_PreloadTable'][source['preloadIndex']:source['preloadIndex']+source['preloadSize']])
  oldstyle=docs[n,c['source_pid']].get('inlineSheet',{}).get('m_PathID')
  for ptr in span:
   if ptr=={'m_FileID':0,'m_PathID':c['source_pid']}:ptr['m_PathID']=c['pid']
   elif oldstyle and ptr=={'m_FileID':0,'m_PathID':oldstyle}:ptr['m_PathID']=c['style']
  for p in [c['pid']]+([c['style']] if 'style' in c else []):
   if {'m_FileID':0,'m_PathID':p} not in span:span.append({'m_FileID':0,'m_PathID':p})
  mt['m_Container'].append((c['guid'],{'preloadIndex':len(mt['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':c['pid']}}));mt['m_PreloadTable'].extend(span)
 mt['m_Container'].sort(key=lambda x:x[0]);put(n,mo.path_id,mo,mt)

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin'];originalcat=cm.Catalog(catalog)
# Catalog keys are immutable between append operations; avoid repeatedly decoding
# the entire key table for each GUID lookup.
def cached_locations(self,key):
 if not hasattr(self,'_key_index'):self._key_index=dict(self.keys())
 return [p[0] for p in self.array(self._key_index[key],'I')]
cm.Catalog.locations=cached_locations
for c in cloneaudit:
 cat=cm.Catalog(catalog);locations=cat.locations(c['source_guid'])
 assert locations,('Source absent from catalog',c)
 kind='UnityEngine.UIElements.VisualTreeAsset' if c['kind']=='template' else None
 loc=next((l for l in locations if not kind or cat.location(l)['type'][1]==kind),None);assert loc
 catalog=cat.add_key_location(c['guid'],loc,loc)
cat=cm.Catalog(catalog)
# Every new resource inherits its source type and owning bundle. Include transitive
# bundle dependencies of rewritten children for Addressables, not just local PPtrs.
clonebyguid={c['guid']:c for c in cloneaudit}
def deps(g,seen=None):
 seen=set() if seen is None else seen
 if g in seen:return []
 seen.add(g);c=clonebyguid[g];loc=cat.location(cat.locations(g)[0]);ret=list(loc['dependencies'])
 for child in guids(changes[c['bundle']][c['pid']]) & clonebyguid.keys():
  for b in deps(child,seen):
   if b not in ret:ret.append(b)
 return ret
for c in cloneaudit:
 for loc in cat.locations(c['guid']):
  q=cat.location(loc);assert cat.location(q['dependencies'][0])['internal'].replace('\\','/').endswith('/'+c['bundle'])
  dl=deps(c['guid']);struct.pack_into('<I',cat.data,loc+12,cat.append(b''.join(struct.pack('<I',v) for v in dl),True))
# Do not change existing catalog locations or preload labels used by match screens.
catalog=bytes(cat.data);cat=cm.Catalog(catalog)
originalkeys=dict(originalcat.keys());finalkeys=dict(cat.keys())
for g,ptr in originalcat.keys():
 assert finalkeys[g]==ptr
 for (loc,) in originalcat.array(ptr,'I'):assert cat.location(loc)==originalcat.location(loc)
for c in cloneaudit:
 q=cat.location(cat.locations(c['guid'])[0]);src=originalcat.location(originalcat.locations(c['source_guid'])[0]);assert q['type']==src['type']
 if c['kind']=='template':assert q['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'

# None of the pre-existing objects in the full match dependency closure may change.
for n,pid in closure:
 if n not in changes:continue
 assert pid not in changes[n],('Match object modified',n,docs[n,pid]['m_Name'])
 sid=docs[n,pid].get('inlineSheet',{}).get('m_PathID')
 if sid:assert sid not in changes[n],('Match style modified',n,sid)
outputs={}
for n in NAMES:
 b=env[n].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 assert set(check)==set(objs[n]);assert banned.isdisjoint(check)
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h,('Unrelated object modified',n,i)
 for i,d in changes[n].items():assert check[i].read_typetree()==d,('Roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b);outputs[n]=b
(OUT/'catalog.bin').write_bytes(catalog);(OUT/'catalog.hash').write_bytes(hashlib.md5(catalog).hexdigest().encode('ascii'))
payloads={p:outputs[n] for p in before for n in NAMES if p.name==n}
for p in before:
 if p.name in ['catalog.bin','catalog.hash']:payloads[p]=(OUT/p.name).read_bytes()
manifest={'installed':False,'runtime_verified':False,'portrait_size':24,'name_cells':nameaudit,'shape_changes':shapeaudit,'clones':cloneaudit,'match_roots_preserved':len(roots),'match_dependency_objects_preserved':len(closure),'existing_catalog_locations_unchanged':True,'unrelated_objects_byte_identical':True,'before_sha256':{str(p):sha(before[p]) for p in payloads},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'changed_counts':{n:len(v) for n,v in changes.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
tx={'game':str(GAME),'skin':str(SKIN),'sources':{str(p):str(OUT/p.name) for p in payloads},'before':{str(p):str(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name) for p in payloads}}
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-primary-navigation-patch.py').read_text('utf8').replace("[Path(tx['game']).resolve(),Path(tx['skin']).resolve()]","[Path(tx['game']).resolve(),Path(tx['game']).parent.resolve(),Path(tx['skin']).resolve()]")
(OUT/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('比赛外球员列表姓名前新增24×24头像；图片等比完整显示，保留原图透明轮廓。比赛外头像实例取消圆形裁切。共享模板复制为独立资源，原比赛模板、样式及完整依赖闭包保持原始字节；比赛资源包、背景图片与禁用资源清单保持不变。已完成序列化读回和Addressables目录检查，游戏内显示待重启确认。restore.ps1 可回退本次修改。','utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'output':str(OUT),'clones':len(cloneaudit),'name_cells':len(nameaudit),'avatar_templates':len(shapeaudit),'changed':manifest['changed_counts']},ensure_ascii=False),flush=True)
