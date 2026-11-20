"""Remove avatar clipping in news and inbox templates, preserving match dependencies."""
from pathlib import Path
R=Path(__file__).resolve().parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','news-inbox-original-portraits-').replace('NAMES=[W,G,M,F]','NAMES=[W,G]').replace('hours=-4','hours=-6')
exec(compile(boot,'current-bundles-and-codecs','exec'))
import re
V='ui-tableviews_assets_all.bundle'
plan=(R/'plan-outside-match-portraits.py').read_text('utf8')
plan=plan[plan.index('env={n:'):plan.index("out={'bases'")]
plan=plan.replace("env={n:UnityPy.load(str(GAME/n)) for n in [W,G,M,F,V]}","env.update({n:UnityPy.load(str(GAME/n)) for n in [M,F,V]})")
exec(compile(plan,'match-dependency-audit','exec'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(t['path_id']) for t in reserved}|{-910000000000146}
protected.update({p:sha(p.read_bytes()) for p in [R/'current-custom-textures.json',R/'reserved-texture-ids.json']})
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
radius=[458759,458760,458764,458765]
edits=[];skipped=[]
def properties(doc,i):
 idx=doc.a(i).get('m_RuleIndex',-1)
 return {p['m_Id']:p for p in doc.s['m_Rules'][idx]['m_Properties']} if idx>=0 else {}
def circular_inline(doc,i):
 for k,p in properties(doc,i).items():
  if k not in radius:continue
  for v in p['m_Values']:
   if v['m_ValueType']==3 and doc.s['dimensions'][v['valueIndex']]['value']>0:return True
 return False
def flatten(doc,i,transparent=False,fit=False):
 a=doc.a(i)
 a['m_Classes']=[c for c in a.get('m_Classes',[]) if c!='person-picture-circle-frame']
 props=[(p,doc.px(0)) for p in radius]+[(458768,doc.enum('visible'))]
 if transparent:props.append((458752,doc.val(4,{'r':0.,'g':0.,'b':0.,'a':0.})))
 if fit:props.append((262153,doc.enum('scale-to-fit')))
 doc.st(i,props)
 if 'SIImage' in a.get('m_FullTypeName',''):
  doc.data(i).update(scaleMode=2,scaleMode_UxmlAttributeFlags=1,ScaleMode=2,ScaleMode_UxmlAttributeFlags=1)
for (n,pid),tree in sorted(docs.items()):
 if n not in NAMES or 'inlineSheet' not in tree:continue
 name=tree['m_Name']
 if not re.search('news|inbox|message|sender|feed|social|interaction-hub',name,re.I):continue
 sid=tree['inlineSheet']['m_PathID']
 if not sid or sid not in objs[n]:continue
 doc=Doc(n,pid=pid)
 portraits=[]
 for i,x in doc.r.items():
  a=x.get('data',{})
  if 'm_Parent' not in a or a.get('m_Classes') is None:continue
  typ=a.get('m_TemplateAlias') or a.get('m_FullTypeName','');nm=doc.data(i).get('name','')
  if re.search('PersonPicture|person-picture',typ) or ('SIImage' in typ and re.search('PersonImage|Portrait',nm,re.I)):portraits.append(i)
 if not portraits:continue
 if (n,pid) in closure:skipped.append({'name':name,'pid':pid,'reason':'match dependency preserved'});continue
 touched={};original=copy.deepcopy(doc.d)
 for i in portraits:
  flatten(doc,i,transparent=True,fit=True);touched[i]='portrait'
  parent=doc.a(i)['m_Parent']['rid']
  while parent in doc.r and parent!=1000:
   a=doc.a(parent);nm=doc.data(parent).get('name','')
   if a.get('m_Classes') is not None and (circular_inline(doc,parent) or re.fullmatch('picture|portrait|avatar',nm,re.I)):
    flatten(doc,parent,transparent=True);touched[parent]='avatar container'
   parent=a.get('m_Parent',{}).get('rid')
 # Letter-based fallbacks in the same inbox avatar should follow its square shape.
 if 'speakto-messages-avatar' in name:
  for i,x in doc.r.items():
   if x.get('data',{}).get('m_Classes') is not None and doc.data(i).get('name')=='PersonInitials':
    flatten(doc,i);touched[i]='initials fallback'
 # Verify that bindings, events, hierarchy and sizes have stayed identical.
 wanted=copy.deepcopy(original);wr=refs(wanted)
 for i in touched:
  wr[i]['data']['m_RuleIndex']=doc.a(i)['m_RuleIndex'];wr[i]['data']['m_Classes']=copy.deepcopy(doc.a(i)['m_Classes'])
  if 'SIImage' in doc.a(i).get('m_FullTypeName',''):
   sd0=wr[wr[i]['data']['m_SerializedData']['rid']]['data']
   for k in ['scaleMode','scaleMode_UxmlAttributeFlags','ScaleMode','ScaleMode_UxmlAttributeFlags']:sd0[k]=doc.data(i)[k]
 assert wanted==doc.d,('Unexpected binding or structural change',name)
 for i in touched:
  ps=properties(doc,i)
  assert all(doc.s['dimensions'][ps[k]['m_Values'][0]['valueIndex']]=={'unit':1,'value':0.} for k in radius)
 doc.save();edits.append({'bundle':n,'name':name,'pid':pid,'nodes':{str(k):v for k,v in touched.items()}})
assert any(x['name']=='speakto-messages-avatar-default' for x in edits)
assert any(x['name']=='PortalMessagesContentBlock' for x in edits)
assert any(x['name']=='NewsItemPortalMessagesSearch' for x in edits)
for n,pid in closure:
 if n not in changes:continue
 assert pid not in changes[n]
 sid=docs[n,pid].get('inlineSheet',{}).get('m_PathID')
 assert not sid or sid not in changes[n]
outputs={}
for n in NAMES:
 b=env[n].file.save(packer='lz4');oo={o.path_id:o for o in UnityPy.load(b).objects}
 assert set(oo)==set(objs[n]);assert banned.isdisjoint(oo)
 for pid,h in hashes[n].items():
  if pid not in changes[n]:assert sha(oo[pid].get_raw_data())==h,('Unrelated object changed',n,pid)
 for pid,d in changes[n].items():assert oo[pid].read_typetree()==d
 (OUT/n).write_bytes(b);outputs[n]=b
# Check existing typed GUID registrations, bundle ownership and actual objects for
# changed templates and their transitive template/function references.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog(before[GAME.parent/'catalog.bin']);keys=dict(cat.keys());out=OUT;tx={'game':str(GAME)}
source=(R/'finish-outside-match-square-portraits.py').read_text('utf8')
exec(compile(source[source.index('loaded={};'):source.index("for c in m['clones']:")],'addressables-audit','exec'))
reverseguid={v:k for k,v in guidmap.items()}
for a in edits:
 key=(a['bundle'],a['pid']);assert key in reverseguid;audit(reverseguid[key])
payloads={p:outputs[p.name] for p in before if p.name in outputs}
manifest={'installed':False,'runtime_verified':False,'edits':edits,'match_dependency_objects_preserved':len(closure),'match_shared_templates_skipped':skipped,'catalog_templates_and_functions_verified':len(audits),'catalog_unchanged':True,'object_inventory_unchanged':True,'unrelated_objects_byte_identical':True,'bindings_events_hierarchy_and_sizes_preserved':True,'before_sha256':{str(p):sha(before[p]) for p in payloads},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'catalog-audits.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2),'utf8')
tx={'game':str(GAME),'skin':str(SKIN),'sources':{str(p):str(OUT/p.name) for p in payloads},'before':{str(p):str(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name) for p in payloads}}
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for mode,flag in [('install',''),('restore',' --restore')]:
 (OUT/(mode+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('新闻和收件箱头像恢复原图形状：清除头像实例及圆形外层容器的四个长格式圆角属性，去掉圆形头像边框类，关闭头像裁切，图片等比完整显示，头像背景透明。收件箱文字缩写回退改为方角。原尺寸、位置、事件、绑定、层级和消息状态指示不变。仅在当前安装包上修改新闻/消息模板；比赛依赖对象、背景图片、catalog均不变。资源读回及目录核对通过，实际游戏显示待启动确认。restore.ps1 可回退本次修改。','utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'output':str(OUT),'templates':len(edits),'avatar_and_container_nodes':sum(len(x['nodes']) for x in edits),'typed_resources_verified':len(audits),'match_dependency_objects_preserved':len(closure)},ensure_ascii=False),flush=True)
