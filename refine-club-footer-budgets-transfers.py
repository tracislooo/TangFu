from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,subprocess,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
src=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['refs','sd','find','pointer_remap','import_types'] or isinstance(n,ast.ClassDef) and n.name=='Doc'],type_ignores=[]),'helpers','exec'))
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
assert 'Project Taco' not in str(GAME)
sha=lambda b:hashlib.sha256(b).hexdigest();stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
ROOTOUT=R/('club-footer-budgets-horizontal-transfers-'+stamp);ROOTOUT.mkdir();tx=[];audits=[];protected={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 OUT=ROOTOUT/tag;OUT.mkdir();(OUT/'templates').mkdir();backup=ROOTOUT/('backup-'+tag);backup.mkdir()
 before=(folder/W).read_bytes();env={W:UnityPy.load(before)};objs={W:{o.path_id:o for o in env[W].objects}};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()};changes={W:{}};documents=[]
 body=Doc(W,pid=-991100000000060);native=Doc(W,name='ClubSiteBlock')
 def import_branch(d,source,root,parent):
  def managed(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:
     if v['rid']!=-2:yield v['rid']
    else:
     for k,x in v.items():
      if k!='m_Parent':yield from managed(x)
   elif isinstance(v,list):
    for x in v:yield from managed(x)
  todo=[root];keep=set()
  while todo:
   i=todo.pop()
   if i in keep:continue
   keep.add(i);todo.extend(managed(source.r[i].get('data',{})))
  nr=max(d.r)+10;mapping={i:nr+j for j,i in enumerate(sorted(keep))};d.nr=nr+len(keep)+10
  eids={source.r[i]['data']['m_Id'] for i in keep if 'm_Id' in source.r[i].get('data',{})};ne=max(x.get('data',{}).get('m_Id',0) for x in d.r.values())+10;emap={i:ne+j for j,i in enumerate(sorted(eids))};d.nid=ne+len(emap)+10
  def remap(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:return {'rid':mapping.get(v['rid'],v['rid'])}
    return {k:emap.get(x,x) if k in ['m_Id','uxmlAssetId','m_ParentId'] and isinstance(x,int) else remap(x) for k,x in v.items()}
   if isinstance(v,list):return [remap(x) for x in v]
   return v
  rules={}
  for i in sorted(keep):
   r=remap(copy.deepcopy(source.r[i]));r['rid']=mapping[i];x=r.get('data',{})
   if i==root:x['m_Parent']={'rid':parent}
   ri=x.get('m_RuleIndex',-1)
   if ri>=0:
    if ri not in rules:
     rule=copy.deepcopy(source.s['m_Rules'][ri])
     for p in rule['m_Properties']:
      for v in p['m_Values']:
       if v['m_ValueType'] in poolmap:
        pool=poolmap[v['m_ValueType']];value=copy.deepcopy(source.s[pool][v['valueIndex']]);v['valueIndex']=len(d.s[pool]);d.s[pool].append(value)
     rules[ri]=len(d.s['m_Rules']);d.s['m_Rules'].append(rule)
    x['m_RuleIndex']=rules[ri]
   d.r[r['rid']]=r;d.d['references']['RefIds'].append(r)
  d.a(parent)['m_Children'].append({'rid':mapping[root]})
  for u in source.d['m_Usings']:
   if not any(x['alias']==u['alias'] for x in d.d['m_Usings']):d.d['m_Usings'].append(copy.deepcopy(u))
  return mapping
 # Restore the original controls and the native dock they toggle, retaining native events.
 footer=import_branch(body,native,1008,1004);dock=import_branch(body,native,1005,1001)
 footerid=footer[1008];dockid=dock[1005]
 body.st(footerid,[(131084,body.num(0)),(131085,body.num(0)),(131105,body.pct(100))])
 for i in [1004,1007]:body.st(i,[(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1))])
 # Keep all existing section/table bindings; change only top-row proportions.
 for i,grow in [(1014,2),(1016,2),(1018,3),(1020,1)]:body.st(i,[(131105,body.px(0)),(131097,body.px(0)),(131084,body.num(grow)),(131085,body.num(1))])
 body.move(1081,1034,len(body.a(1034)['m_Children'])-1)
 body.st(1081,[(131087,body.px(1)),(131085,body.num(0)),(131098,body.px(4)),(131090,body.px(4))])
 body.st(1061,[(131083,body.enum('row')),(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1))])
 for i in [1082,1083]:body.st(i,[(131105,body.px(0)),(131097,body.px(0)),(131087,body.pct(100)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(131098,body.px(0))])
 body.st(1082,[(131090,body.px(8))]);body.st(1083,[(131093,body.px(8))])
 divider=body.add(native,1015,1061,'ClubOverviewTransferInOutDivider');body.using(native,'layout-divider-solid-vertical');body.move(divider,1061,1)
 body.st(divider,[(131105,body.px(1)),(131085,body.num(0)),(131093,body.px(0)),(131090,body.px(0))])
 for i in [1108,1111]:body.st(i,[(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1))])
 body.st(body.named('财政Heading'),[(131081,body.enum('none'))]);body.save()
 # Replace only this Club-specific finance template with the actual native budget tile.
 finance=Doc(W,pid=-991100000000040);budget=Doc(W,name='RecruitmentBudgetsTile_4x2')
 tr=copy.deepcopy(budget.d);sheet=copy.deepcopy(budget.s);tr['m_Name']=finance.d['m_Name'];tr['inlineSheet']['m_PathID']=finance.sid;sheet['m_Name']=finance.s['m_Name']
 finance=Doc(W,pid=finance.obj.path_id,tree=tr,style=sheet)
 finance.st(1001,[(131105,finance.pct(100)),(131097,finance.px(0)),(131096,finance.px(0)),(131087,finance.pct(100)),(131085,finance.num(1))])
 finance.st(1002,[(131105,finance.pct(100)),(131096,finance.px(0)),(131087,finance.pct(100)),(131085,finance.num(1))])
 finance.st(1004,[(131105,finance.pct(100)),(131097,finance.px(0)),(131096,finance.px(0)),(131087,finance.pct(100)),(131085,finance.num(1))]);finance.save()
 # Original budget contents and all source template overrides stay byte-for-byte equal.
 for i,r in budget.r.items():
  actual=copy.deepcopy(finance.r[i])
  if 'm_RuleIndex' in r.get('data',{}):actual['data']['m_RuleIndex']=r['data']['m_RuleIndex']
  assert actual==r,(tag,'budget binding changed',i)
 # Verify restored control events match the native source after ID remapping.
 for mapping in [footer,dock]:
  for i,j in mapping.items():
   if i not in native.r:continue
   old=native.r[i].get('data',{});new=body.r[j].get('data',{})
   for key in ['Events','Binding','BindFunction','TextBinding','Bindings']:
    if key in old:assert new[key]==old[key],(tag,'native footer binding changed',i,key)
 # Preload references and styles for both changed templates; preserve existing catalog GUIDs.
 metaob=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=metaob.read_typetree()
 def ptrs(v,result):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'}:
    if v['m_PathID'] and v not in result:result.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,result)
  elif isinstance(v,(list,tuple)):
   for x in v:ptrs(x,result)
 for d in documents:
  for key,e in meta['m_Container']:
   if e['asset']!={'m_FileID':0,'m_PathID':d.obj.path_id}:continue
   span=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']]);ptrs(d.d,span);ptrs(d.s,span)
   e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 metaob.save_typetree(meta);changes[W][metaob.path_id]=meta
 result=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(result).objects};assert set(check)==set(objs[W])
 for i,h in hashes.items():
  if i not in changes[W]:assert sha(check[i].get_raw_data())==h,(tag,i)
 for i,d in changes[W].items():assert check[i].read_typetree()==d,(tag,i)
 for d in documents:validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
 assert (folder/W).read_bytes()==before
 source=OUT/W;source.write_bytes(result);bp=backup/W;bp.write_bytes(before);tx.append({'target':str(folder/W),'source':str(source),'backup':str(bp),'before':sha(before),'after':sha(result)})
 for p in folder.glob('*.bundle'):
  if p.name!=W:protected[str(p)]=sha(p.read_bytes())
 for p in [(folder.parent if tag=='game' else folder)/'catalog.bin',(folder.parent if tag=='game' else folder)/'catalog.hash']:protected[str(p)]=sha(p.read_bytes())
 audits.append({'target':tag,'footer_restored':True,'native_footer_events_and_dock_bindings_preserved':True,'top_columns_grow':[2,2,3,1],'transfer_in_out':'horizontal equal halves','budget_template':'RecruitmentBudgetsTile_4x2','budget_bindings_and_template_overrides_unchanged':True,'unrelated_objects_byte_identical':True,'changed_objects':list(changes[W]),'runtime_verified':False})
for p in [R/'current-custom-textures.json',R/'reserved-texture-ids.json',R/'current-game-location.json']:protected[str(p)]=sha(p.read_bytes())
manifest={'installed':False,'runtime_verified':False,'audits':audits,'protected_sha256':protected}
(ROOTOUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(ROOTOUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 text="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n";(ROOTOUT/(action+'.ps1')).write_text(text,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(ROOTOUT),'audits':audits},ensure_ascii=False),flush=True)
