from pathlib import Path
import json,copy,ast,uuid,struct,hashlib,importlib.util
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','small-substitutes-lower-hide-rating-').replace("'NAMES=[W,G]'","'NAMES=[W,G,M]'").replace('bases=(W,G)','bases=(G,M)')
exec(compile(prefix,'backup-small-sub-cards','exec'))
resource_bases=(W,G,M)
for file,functions in [('build-highlight-five-column-native-player-lists.py',['register_clone','clone_doc']),('build-highlight-lower-five-by-three-with-charts.py',['copy_style','clone_native'])]:
 module=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in functions],type_ignores=[]),'private-card-tools','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
asset_clones=[];new_guids={};clone_audits=[];audits=[];tx=[];cats={}
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G,M=[n+suffix for n in resource_bases];source=Doc(W,name='SquadOverviewPlayerBlockSmall');main=Doc(G,name='MatchManySubstitutesSmallCard');d,guid=clone_doc(source,'SmallSubstituteCardLowerNoRating',-981109000010000)
 switch=d.add(d,1025,1002,'OnlySmallSubstitutePresentation');assert d.data(switch)['Binding']==source.data(1025)['Binding'];d.move(1006,switch)
 modified,mapping=clone_native(source,1006,switch);assert d.a(switch)['m_Children']==[{'rid':1006},{'rid':modified}]
 d.st(switch,[(131084,d.num(1)),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0))])
 d.st(modified,[(131102,d.enum('relative')),(131104,d.px(16))]);d.st(mapping[1050],[(131081,d.enum('none'))])
 hidden=[]
 for old,new in mapping.items():
  a=source.r[old].get('data',{})
  if 'm_SerializedData' not in a:continue
  s=source.data(old)
  if s.get('name')=='Number' and s.get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path')=='playerinfo.SquadNumber':d.st(new,[(131081,d.enum('none'))]);hidden.append(old)
 assert hidden
 right=source.named('MatchCardShirtNumber');expected=copy.deepcopy(source.data(right));expected['uxmlAssetId']=d.data(mapping[right])['uxmlAssetId'];assert d.data(mapping[right])==expected
 # Every original first-team row and all existing serialized bindings are kept.
 for rid in mapping:
  if 'm_Parent' not in source.r[rid].get('data',{}):
   assert d.r[mapping[rid]]['data'].get('uxmlAssetId') is not None or d.r[mapping[rid]]['data']==source.r[rid]['data']
 d.save()
 overview=Doc(M,name='SquadOverview');previous={i:copy.deepcopy(overview.data(i)) for i in [1038,1041,1073,1087,1088]}
 for i in [1041,1073,1088]:
  assert overview.data(i)['RowTemplate']['m_AssetGUID']=='eb433e33a56539049910c63aabdec0d2'
  overview.data(i)['RowTemplate']['m_AssetGUID']=guid;overview.data(i)['RowTemplate_UxmlAttributeFlags']=1
  before_data=copy.deepcopy(previous[i]);before_data['RowTemplate']['m_AssetGUID']=guid;before_data['RowTemplate_UxmlAttributeFlags']=1;assert overview.data(i)==before_data
 assert overview.data(1038)==previous[1038] and overview.data(1087)==previous[1087];overview.save()
 for bn in [G,M]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  if bn==G:meta['m_Container'].append((guid,{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':d.obj.path_id}}))
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid==d.obj.path_id:ptrs(d.s,span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  meta['m_Container'].sort(key=lambda x:x[0]);ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';cat=cm.Catalog(before[cp]);oldloc=cat.locations('d8b28e612b34531ba0f09ff5a425e022')[0];raw=cat.add_key_location(guid,oldloc,oldloc);cat=cm.Catalog(raw);loc=cat.locations(guid)[0]
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records);values=[v[0] for v in cat.array(ls,'I')]+[loc];records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in values),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cats[tag]=bytes(cat.data)
 check=cm.Catalog(cats[tag]);record=check.location(check.locations(guid)[0]);assert G.split('::')[0] in check.location(record['dependencies'][0])['internal'];assert check.locations(guid)[0] in [v[0] for v in check.array(check.key_records[idx][1],'I')]
 audits.append({'variant':tag,'small_subs_only':True,'body_offset':16,'rating_hidden':1050,'legacy_numbers_hidden':hidden,'right_number_binding_preserved':True,'large_list_properties_preserved':True,'first_team_small_original_branch_preserved':True,'new_guid':guid})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
  for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
 for name,data in [('catalog.bin',cats[tag]),('catalog.hash',hashlib.md5(cats[tag]).hexdigest().encode('ascii'))]:
  target=GAME.parent/name if tag=='game' else SKIN/name;src=OUT/(tag+'-'+name);src.write_bytes(data);tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[target]),'after':sha(data)})
report={'installed':False,'runtime_verified':False,'checks':audits,'clone_checks':clone_audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅小卡片的替补分支调整：当前小卡片完整复制为私有模板，通过原生playerinfo.IsSub标题开关决定显示，首发分支保留当前完整小卡片，替补分支整体下移16px、隐藏评分1050、隐藏头像上方旧Number(playerinfo.SquadNumber)，右侧MatchCardShirtNumber及头像/国旗/体能/状态/事件保留。小分辨率列表1041/1073和原生多人数小卡片分支1088引用该模板；大卡片列表1038/1087及其分页/宽度/位置不变。原W卡片模板不改。新行GUID登记Global及GlobalVisualTreeAssetPreload。游戏和皮肤独立备份与修改，序列化及无关对象检查通过；实际位置和状态显示待游戏验证。restore.ps1带哈希保护。','utf8')
print(OUT)
