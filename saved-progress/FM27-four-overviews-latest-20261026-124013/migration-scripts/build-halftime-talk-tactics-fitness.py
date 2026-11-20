from pathlib import Path
import json,re,types,colorsys
R=Path(__file__).parent
V='ui-tableviews_assets_all.bundle';VS=V+'::skin'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','halftime-talk-tactics-fitness-').replace('NAMES=[W,G,M,F]','NAMES=[W,F,V]')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if SKIN/n in before and n!=V:assert before[SKIN/n]==before[GAME/n]')
exec(compile(boot,'backup-current-independent-game-skin-packages','exec'))
env[VS]=UnityPy.load(before[SKIN/V]);objs[VS]={o.path_id:o for o in env[VS].objects};hashes[VS]={i:sha(o.get_raw_data()) for i,o in objs[VS].items()};changes[VS]={}
entries=[];source_lookup={};pid_guid={}
for bn in list(env):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
 source_lookup[bn]={}
 for guid,e in meta['m_Container']:
  pid=e['asset']['m_PathID'];pid_guid.setdefault((bn,pid),guid)
  source_lookup[bn].setdefault(guid,pid)
def guid_for(name):return uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/halftime-talk-tactics-fitness/'+name).hex
def clone(bn,source_pid,pid,name,tree=None,addressable=True):
 source=objs[bn][source_pid];assert pid not in objs[bn]
 tree=copy.deepcopy(tree if tree is not None else source.read_typetree());tree['m_Name']=name
 ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[bn][pid]=ob
 ob.save_typetree(tree);changes[bn][pid]=copy.deepcopy(tree)
 if addressable:
  guid=guid_for(name);entries.append({'bundle':bn,'pid':pid,'guid':guid,'source_guid':pid_guid[(bn,source_pid)],'name':name})
 else:guid=None
 return tree,guid
portrait=Doc(W,pid=-4028782843705546248);VE=next(i for i,x in portrait.r.items() if x.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
PIC=next(i for i,x in portrait.r.items() if x.get('data',{}).get('m_TemplateAlias')=='PersonPicture')
remapdonor=Doc(W,name='PlayerKitNameCell');REMAP=1007
helper=ast.parse((R/'build-match-ui-avatars-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['mapper','picture','replace_shirt']],type_ignores=[]),'native-avatar-helpers','exec'))
native=Doc(W,name='PlayerCellInMatch');pp=-981025000004000
pd=copy.deepcopy(native.d);ps=copy.deepcopy(native.s);pd['inlineSheet']['m_PathID']=pp-1
pd,portrait_guid=clone(W,native.obj.path_id,pp,'InMatchTacticsFitnessPortraitName',pd)
clone(W,native.sid,pp-1,'InMatchTacticsFitnessPortraitName_Style',ps,False)
photo=Doc(W,pid=pp,tree=pd,style=ps)
replace_shirt(photo,1014,'binding.Person',24)
photo.size(1004,24,24);photo.size(1007,24,24)
photo.data(1004)['Binding']={'m_kind':1,'m_direct':{'Path':{'m_path':'const.True'},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
photo.data(1004)['Binding_UxmlAttributeFlags']=1
photo.st(1004,[(131085,photo.num(0)),(131092,photo.px(4))])
photo.st(1001,[(131105,photo.pct(100)),(131097,photo.px(0)),(131083,photo.enum('row')),(131073,photo.enum('center'))])
photo.st(1005,[(131105,photo.px(0)),(131082,photo.px(0)),(131097,photo.px(0)),(131084,photo.num(1)),(131085,photo.num(1))])
photo.a(1031)['m_Classes']=list(dict.fromkeys(photo.a(1031)['m_Classes']+['content-ellipsis']))
photo.data(1031).update(displayTooltipWhenElided=1,displayTooltipWhenElided_UxmlAttributeFlags=1)
photo.save()

donor=find(F,'TacticTeamSelectionTableFactory').read_typetree();dc={c['m_id']:c for c in donor['m_rowData']}
assert dc['condition']['m_defaultWidth']==90 and dc['tactics-fatigue-value']['m_defaultWidth']==40
talk_src=find(F,'TeamTalkPlayerReactionTableFactory');talk_old=talk_src.read_typetree()
talk,talk_guid=clone(F,talk_src.path_id,-981025000004100,'HalfTimeTalkFitnessFactory',talk_old)
tc={c['m_id']:c for c in talk['m_rowData']}
assert tc['playerselection']['m_uxmlRef']['m_AssetGUID']=='70c87009add8c3047acf2b3fc12457d1'
tc['playerselection']['m_uxmlRef']=copy.deepcopy(tc['name']['m_uxmlRef'])
newcond=copy.deepcopy(dc['condition']);newcond['m_id']='halftime-condition-sharpness'
newcond['m_valueBindings'][0]['to']['m_path']='binding.Player.Person'
newcond['m_sortBinding']['m_path']='binding.Player.Condition'
fat=copy.deepcopy(dc['tactics-fatigue-value']);fat['m_valueBindings'][0]['to']['m_path']='binding.Player.Person.fatigue';fat['m_sortBinding']['m_path']='binding.Player.Person.fatigue'
talk['m_rowData'] += [newcond,fat]
objs[F][-981025000004100].save_typetree(talk);changes[F][-981025000004100]=copy.deepcopy(talk)
tactic_src=find(F,'TacticTeamSelectionTableFactoryInMatch');tactic_old=tactic_src.read_typetree()
tactic,tactic_guid=clone(F,tactic_src.path_id,-981025000004110,'InMatchTacticsFitnessFactory',tactic_old)
cols=tactic['m_rowData'];ci=next(i for i,c in enumerate(cols) if c['m_id']=='condition')
c=copy.deepcopy(dc['condition']);c['m_valueBindings'][0]['to']['m_path']='binding.Person';c['m_sortBinding']['m_path']='binding.Condition';cols[ci]=c
f=copy.deepcopy(dc['tactics-fatigue-value']);f['m_valueBindings'][0]['to']['m_path']='binding.Person.fatigue';f['m_sortBinding']['m_path']='binding.Person.fatigue';cols.insert(ci+1,f)
next(c for c in cols if c['m_id']=='name')['m_uxmlRef']['m_AssetGUID']=portrait_guid
objs[F][-981025000004110].save_typetree(tactic);changes[F][-981025000004110]=copy.deepcopy(tactic)

def compact_view(tree,half=False):
 cfg=tree['m_tableView']['m_tableConfig'];old=copy.deepcopy(cfg)
 cfg[:]=[c for c in cfg if c['m_columnID'] not in ['sharpness','tactics-fatigue-value']]
 i=next(i for i,c in enumerate(cfg) if c['m_columnID']=='condition');condition=cfg[i]
 if half:condition['m_columnID']='halftime-condition-sharpness'
 condition['m_columnMetadata'].update(m_widthOverride=90.,m_minWidthOverride=90.,m_required=1,m_applicableBreakpoints=-1)
 f=copy.deepcopy(condition);f['m_columnID']='tactics-fatigue-value';f['m_columnMetadata'].update(m_widthOverride=40.,m_minWidthOverride=40.);f['m_columnMetadata']['m_titleTranslationIdOverride']['GameID']=0;cfg.insert(i+1,f)
 assert [c for c in cfg if c['m_columnID'] not in ['condition','halftime-condition-sharpness','tactics-fatigue-value']]==[c for c in old if c['m_columnID'] not in ['condition','sharpness','tactics-fatigue-value']]
 return tree
maps={};view_audits=[]
for bn in [V,VS]:
 memo={};next_pid=-981025000004200
 def clone_graph(pid):
  global next_pid
  if pid in memo:return memo[pid]
  native=objs[bn][pid];tree=native.read_typetree();name=tree['m_Name'];newpid=next_pid;next_pid-=10;memo[pid]=newpid
  half=name=='TeamTalksTableHalfTime'
  if 'm_tableView' in tree:compact_view(tree,half)
  if 'm_tableViewSettings' in tree:
   def remap_refs(value):
    if isinstance(value,dict):
     if set(value)=={'m_FileID','m_PathID'} and value['m_FileID']==0 and value['m_PathID'] in objs[bn]:
      obj=objs[bn][value['m_PathID']]
      if obj.type.name=='MonoBehaviour' and obj.peek_name().startswith('TacticTeamSelectionTableView'):value['m_PathID']=clone_graph(value['m_PathID'])
     else:
      for v in value.values():remap_refs(v)
    elif isinstance(value,list):
     for v in value:remap_refs(v)
   remap_refs(tree['m_tableViewSettings'])
   menu=tree['m_contextMenuData'];menu[:]=[x for x in menu if x.get('PropertyValue')!='sharpness']
   i=next(i for i,x in enumerate(menu) if x.get('PropertyValue')=='condition');f=copy.deepcopy(menu[i]);f['PropertyValue']='tactics-fatigue-value';f['DisplayValue']={'GameID':3251};menu.insert(i+1,f)
  newname='HalfTimeFitness_'+name
  tree,newguid=clone(bn,pid,newpid,newname,tree,addressable=(bn,pid) in pid_guid)
  if 'm_tableView' in tree:view_audits.append({'bundle':bn,'view':name,'columns':[(c['m_columnID'],c['m_columnMetadata']['m_widthOverride']) for c in tree['m_tableView']['m_tableConfig']]})
  return newpid
 roots=['f84575a90dbba5440ac691852dbe1c09','7745afe40eb0a2b4bb6ead8faa41b170','79b3b1aaf3aec8f429211e88a3137d47','11a92d57eea45da4894c9b05b3caf215','76b785c1cd7000c4ea136ed4c5d01a00','579e5a090c6f34443a2ac136931d93e3']
 maps[bn]={}
 for guid in roots:
  pid=source_lookup[bn][guid];clone_graph(pid);maps[bn][guid]=guid_for('HalfTimeFitness_'+objs[bn][pid].peek_name())
 assert len(memo)==11,(bn,len(memo))
assert maps[V]==maps[VS]

talkdoc=Doc(W,name='TeamTalkBlock');before_talk=copy.deepcopy(talkdoc.d)
v=talkdoc.r[1048]['data'];v['FactoryAsset']['m_AssetGUID']=talk_guid
raw=bytes(v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert raw.count(b'f84575a90dbba5440ac691852dbe1c09')==1
v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw.replace(b'f84575a90dbba5440ac691852dbe1c09',maps[V]['f84575a90dbba5440ac691852dbe1c09'].encode()))
assert all(talkdoc.r[i]==r for i,r in refs(before_talk).items() if i!=1048);talkdoc.save()
tdoc=Doc(W,name='TacticalPlannerTeamShape');old=copy.deepcopy(tdoc.d)
changed_nodes=[]
for rid in [1062,1070,1078,1086,1094,1102,1110]:
 v=tdoc.r[rid]['data'];assert v['FactoryAsset']['m_AssetGUID']=='b5090156c576f8543bf6b6699770f436';v['FactoryAsset']['m_AssetGUID']=tactic_guid
 raw=bytes(v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);hits=re.findall(rb'[0-9a-f]{32}',raw);assert len(hits)==1 and hits[0].decode() in maps[V]
 v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw.replace(hits[0],maps[V][hits[0].decode()].encode()));changed_nodes.append(rid)
assert all(tdoc.r[i]==r for i,r in refs(old).items() if i not in changed_nodes);tdoc.save()

def allptr(value):
 if isinstance(value,dict):
  if set(value)=={'m_FileID','m_PathID'}:
   if value['m_PathID']:yield value
  else:
   for v in value.values():yield from allptr(v)
 elif isinstance(value,list):
  for v in value:yield from allptr(v)
for bn in list(env):
 registrations=[c for c in entries if c['bundle']==bn]
 if not registrations:continue
 mo=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();prior=copy.deepcopy(meta['m_Container'])
 for c in registrations:
  ptr={'m_FileID':0,'m_PathID':c['pid']};refs_list=[ptr]+list(allptr(changes[bn][c['pid']]))
  idx=len(meta['m_PreloadTable']);meta['m_PreloadTable']+=refs_list
  meta['m_Container'].append((c['guid'],{'preloadIndex':idx,'preloadSize':len(refs_list),'asset':ptr}))
 assert meta['m_Container'][:len(prior)]==prior;mo.save_typetree(meta);changes[bn][mo.path_id]=meta
spec=importlib.util.spec_from_file_location('fitness_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin'];unique={c['guid']:c for c in entries if c['bundle']!=VS}
for c in unique.values():
 cat=cm.Catalog(catalog);loc=cat.locations(c['source_guid'])[0];catalog=cat.add_key_location(c['guid'],loc,loc)
cat=cm.Catalog(catalog);preload_key='GameWorldVisualTreeAssetPreload';extra=[cat.locations(c['guid'])[0] for c in entries if c['bundle']==W]
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==preload_key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+extra
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);newcat=cm.Catalog(catalog);newkeys=dict(newcat.keys())
assert set(newkeys)==set(dict(oldcat.keys()))|set(unique)
for k,l in oldcat.keys():assert [x[0] for x in newcat.array(newkeys[k],'I')]==[x[0] for x in oldcat.array(l,'I')]+(extra if k==preload_key else [])

verification_source=(R/'verify-halftime-fitness-components.py').read_text('utf8')
exec(compile(verification_source,'verify-reused-components','exec'))
outputs={};tx=[]
for bn in list(env):
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated original asset changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',bn,pid)
 for doc in [d for d in documents if d.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/('output-skin' if bn==VS else 'output-game')/(V if bn==VS else bn);dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);outputs[bn]=dest
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for name in NAMES:
  src=outputs[VS if name==V and tag=='skin' else name];p=folder/name
  tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[p]),'after':sha(src.read_bytes())})
 for name,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  src=OUT/name;src.write_bytes(data);p=(folder.parent if tag=='game' else folder)/name
  tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[p]),'after':sha(data)})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'output':str(OUT),'combined_width':90,'fatigue_width':40,'rings_px':[22,12],'native_pre_full_talk_and_penalties_factories_views_preserved':True,'private_view_audits':view_audits,'component_checks':component_checks,'all_existing_game_skin_view_differences_preserved':True,'serialization_roundtrip':True,'unrelated_objects_and_catalog_locations_unchanged':True,'new_assets':entries,'changes':{bn:{str(i):t.get('m_Name','AssetBundle') for i,t in cs.items()} for bn,cs in changes.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(component_checks,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('中场球队训话实际playerselection列接入24px头像；私有工厂增加90px体能/比赛状态合并列、紧接40px原始疲劳值。比赛内战术私有姓名单元格保留原有导航、下拉菜单和提示，球衣换24px头像；5套展开/收起/有无球视图及5套集合独立克隆。中场独立视图替换InitFunction中对应GUID，赛前/赛后训话视图与数据列不改；点球和普通赛前战术工厂/视图不改。复用已安装22px/12px同心环、0..100直接百分比与疲劳渐变，明确匹配MatchPlayer.Person上下文。游戏和皮肤表格包分别修改，保留原有差异。静态遍历、序列化回读和所有原对象/目录检查通过；游戏内未验证。游戏运行中等待正常退出后安装；restore.ps1恢复本次资源。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'new_addressable_assets':len(unique),'private_views':len(view_audits)//2,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
