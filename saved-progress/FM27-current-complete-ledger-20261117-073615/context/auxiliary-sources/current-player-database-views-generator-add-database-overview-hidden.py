"""Add the player database Overview + Hidden view on each current resource base."""
from pathlib import Path
import sys,json,copy,ast,hashlib,struct,uuid,datetime,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(cfg['bundle_root']),Path(cfg['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
V='ui-tableviews_assets_all.bundle';F='ui-tablefactories_assets_all.bundle'
OUT=R/('database-overview-hidden-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def locations(self,key):return [x[0] for x in self.array(dict(self.keys())[key],'I')]
cm.Catalog.locations=locations
VP,RP,SP=-991112000001000,-991112000001010,-991112000001011
VG=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/player-database/overview-hidden/view/v1').hex
RG=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/player-database/overview-hidden/menu-row/v1').hex
CG='545682b52c66d724fb294d0439a73661';SWITCH='f6f314e9db56227459137669d87c44e9'
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert reserved.isdisjoint([VP,RP,SP])
before={};backups={};payloads={};protected={};reports=[]
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def switch_args():
 args=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',2)),('SI.VisualScripting.Int32VisualArg',struct.pack('<i',1)),('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string('row.PropertyValue'))]
 return list(bytes([len(args)])+b''.join(struct.pack('<I',len(string(t)+v))+string(t)+v for t,v in args))
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 tagout=OUT/tag;tagout.mkdir()
 for name in [W,G,V,'catalog.bin','catalog.hash']:
  p=GAME.parent/name if folder==GAME and name.startswith('catalog.') else folder/name
  if not p.exists() and name=='catalog.hash':continue
  before[str(p)]=p.read_bytes();bp=OUT/('backup-'+tag)/name;bp.parent.mkdir(exist_ok=True);bp.write_bytes(before[str(p)]);backups[str(p)]=str(bp)
 for p in folder.glob('*.bundle'):
  if p.name not in [W,G,V]:protected[str(p)]=sha(p.read_bytes())
 env={n:UnityPy.load(before[str(folder/n)]) for n in [W,G,V]}
 objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
 hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()}
 changes={n:{} for n in env};documents=[]
 def put(n,pid,source,d):
  if pid not in objs[n]:
   ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[n][pid]=ob
  objs[n][pid].save_typetree(d);changes[n][pid]=copy.deepcopy(d)
 metas={n:next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle') for n,oo in objs.items()}
 def key_for(n,pid):return next(g for g,v in metas[n]['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
 sourceob=find(V,'SearchResultsTableOverview');collection=find(V,'PlayerSearchResultsViewCollection')
 original=sourceob.read_typetree();source=copy.deepcopy(original)
 clubstats=find(V,'SearchResultsTableStatsClub').read_typetree()
 rating=copy.deepcopy(next(c for c in clubstats['m_tableView']['m_tableConfig'] if c['m_columnID']=='average-rating'))
 fe=UnityPy.load(str(folder/F));factory=next(o.read_typetree() for o in fe.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerTableFactory')
 fc={c['m_id']:c for c in factory['m_rowData']}
 columns=source['m_tableView']['m_tableConfig'];widths=[]
 for c in columns:
  ident=c['m_columnID'];meta=c['m_columnMetadata']
  if ident in ['tactical-effectiveness-gauge-no-sort','knowledge','club-player-search']:
   oldwidth=meta['m_widthOverride'] or fc[ident]['m_defaultWidth']
   oldmin=meta['m_minWidthOverride'] or fc[ident]['m_minimumWidth']
   if ident=='tactical-effectiveness-gauge-no-sort':width,minimum=oldwidth+5,oldmin+5
   else:width,minimum=oldwidth-30,min(oldmin,oldwidth-30)
   meta.update(m_widthOverride=float(width),m_minWidthOverride=float(minimum))
   widths.append({'column':ident,'before':oldwidth,'after':width,'minimum':minimum})
 knowledge=next(i for i,c in enumerate(columns) if c['m_columnID']=='knowledge')
 assert not any(c['m_columnID']=='average-rating' for c in columns)
 columns.insert(knowledge+1,rating)
 put(V,sourceob.path_id,sourceob,source)
 hidden=copy.deepcopy(source);hidden['m_Name']='PlayerDatabaseOverviewHidden';hidden['m_tableView']['m_viewName']={'GameID':15275}
 replacements={'current-ability-stars':'hidden-current-ability','potential-ability-stars':'hidden-potential-ability'}
 for c in hidden['m_tableView']['m_tableConfig']:
  if c['m_columnID'] in replacements:
   c['m_columnID']=replacements[c['m_columnID']]
   c['m_columnMetadata'].update(m_widthOverride=64.,m_minWidthOverride=64.)
 assert VP not in objs[V];put(V,VP,sourceob,hidden)
 cd=collection.read_typetree();oldcd=copy.deepcopy(cd)
 entry=copy.deepcopy(cd['m_tableViewSettings'][0])
 entry.update(name='总览+隐藏',debug_name='Overview + Hidden',DisplayValue={'GameID':15275},PropertyValue={'m_FileID':0,'m_PathID':VP})
 cd['m_tableViewSettings'].insert(1,entry)
 assert cd['m_tableViewSettings'][:1]+cd['m_tableViewSettings'][2:]==oldcd['m_tableViewSettings']
 put(V,collection.path_id,collection,cd)
 # Scope the literal title to selectors using this exact collection. The native
 # integer selector compares row.PropertyValue == 1; all other rows keep their
 # original DisplayValue, as does the selected-value renderer.
 row=Doc(G,name='GenericDisplayValuePairDropdownRow');tree=copy.deepcopy(row.d);sheet=copy.deepcopy(row.s)
 tree['m_Name']='PlayerDatabaseOverviewHiddenMenuRow';tree['inlineSheet']['m_PathID']=SP;sheet['m_Name']='PlayerDatabaseOverviewHiddenMenuRowStyle'
 assert RP not in objs[G] and SP not in objs[G]
 put(G,RP,row.obj,tree);put(G,SP,objs[G][row.sid],sheet)
 rd=Doc(G,pid=RP,tree=tree,style=sheet)
 donor=Doc(W,name='TacticsConditionPercentageCell')
 sw=next(i for i,r in donor.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement')
 parent=rd.a(1008)['m_Parent']['rid'];position=rd.a(parent)['m_Children'].index({'rid':1008})
 gate=rd.add(donor,sw,parent,'DatabaseOverviewHiddenTitleSelector');rd.move(gate,parent,position)
 rd.data(gate).update(Binding={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':SWITCH},'m_inputs':{'m_variable':{'m_argumentBytes':switch_args()}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,Preview={'Mask':3},Preview_UxmlAttributeFlags=1)
 rd.st(gate,[(131084,rd.num(1)),(131085,rd.num(1))])
 rd.move(1008,gate) # false child retains the native display binding
 title=rd.add(row,1008,gate,'DatabaseOverviewHiddenTitle')
 rd.a(title)['m_Classes']=copy.deepcopy(row.a(1008)['m_Classes'])
 rd.data(title).update(text='总览+隐藏',text_UxmlAttributeFlags=1,TextBinding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
 assert rd.a(gate)['m_Children']==[{'rid':1008},{'rid':title}]
 for node in [gate,1008,title]:
  if 'm_ParentId' in rd.a(node):rd.a(node)['m_ParentId']=rd.a(rd.a(node)['m_Parent']['rid'])['m_Id']
 rd.save()
 dropdowns=[]
 for n in [G,W]:
  for ob in list(objs[n].values()):
   if ob.type.name!='MonoBehaviour' or ob.path_id in [RP,SP]:continue
   if CG.encode() not in ob.get_raw_data():continue
   tree=ob.read_typetree()
   if 'inlineSheet' not in tree:continue
   edited=[]
   for r in tree['references']['RefIds']:
    data=r.get('data',{});args=data.get('BindChoicesFunction',{}).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
    if CG.encode() not in bytes(args):continue
    data['RowTemplate']['m_AssetGUID']=RG
    data.update(RowTemplate_UxmlAttributeFlags=1,UseRowTemplateToShowSelectedValue=1,UseRowTemplateToShowSelectedValue_UxmlAttributeFlags=1,ForceRefreshOnNewChoices=1,ForceRefreshOnNewChoices_UxmlAttributeFlags=1)
    edited.append(r['rid'])
   if edited:put(n,ob.path_id,ob,tree);dropdowns.append({'bundle':n,'name':tree['m_Name'],'pid':ob.path_id,'overrides':edited})
 assert any(x['name']=='PersonSearchTableTopSection' for x in dropdowns)
 clones=[(V,VP,sourceob.path_id,VG,None),(G,RP,row.obj.path_id,RG,SP)]
 def local_closure(n,pid):
  seen=set()
  def visit(i):
   if i in seen:return
   seen.add(i)
   def walk(x):
    if isinstance(x,dict):
     if set(x)=={'m_FileID','m_PathID'} and x['m_FileID']==0 and x['m_PathID'] in objs[n]:visit(x['m_PathID'])
     else:
      for v in x.values():walk(v)
    elif isinstance(x,(list,tuple)):
     for v in x:walk(v)
   o=objs[n][i]
   if o.type.name=='MonoBehaviour':walk(changes[n].get(i) or o.read_typetree())
  visit(pid);return [{'m_FileID':0,'m_PathID':i} for i in sorted(seen)]
 for n,oo in objs.items():
  mo=next(o for o in oo.values() if o.type.name=='AssetBundle');mt=copy.deepcopy(metas[n])
  for cn,pid,origin,guid,sid in clones:
   if cn!=n:continue
   originentry=next(v for _,v in mt['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':origin})
   span=copy.deepcopy(mt['m_PreloadTable'][originentry['preloadIndex']:originentry['preloadIndex']+originentry['preloadSize']])
   span.extend(x for x in local_closure(n,pid) if x not in span)
   mt['m_Container'].append((guid,{'preloadIndex':len(mt['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));mt['m_PreloadTable'].extend(span)
  # Preserve original spans and append the newly referenced local dependency
  # closure for every changed asset which has a registered container entry.
  for _,entry0 in mt['m_Container']:
   pid=entry0['asset']['m_PathID']
   if entry0['asset']['m_FileID']!=0 or pid not in changes[n]:continue
   span=copy.deepcopy(mt['m_PreloadTable'][entry0['preloadIndex']:entry0['preloadIndex']+entry0['preloadSize']])
   span.extend(x for x in local_closure(n,pid) if x not in span)
   entry0.update(preloadIndex=len(mt['m_PreloadTable']),preloadSize=len(span));mt['m_PreloadTable'].extend(span)
  mt['m_Container'].sort(key=lambda x:x[0]);put(n,mo.path_id,mo,mt)
 cp=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';catalog=before[str(cp)]
 for n,pid,origin,guid,sid in clones:
  cat=cm.Catalog(catalog);loc=cat.locations(key_for(n,origin))[0];catalog=cat.add_key_location(guid,loc,loc)
 cat=cm.Catalog(catalog);loc=cat.locations(RG)[0];dep=list(cat.location(loc)['dependencies'])
 for d in cat.location(cat.locations(SWITCH)[0])['dependencies']:
  if d not in dep:dep.append(d)
 depbytes=b''.join(struct.pack('<I',x) for x in dep)
 import zlib
 struct.pack_into('<I',cat.data,loc+12,cat.append(depbytes,True));struct.pack_into('<I',cat.data,loc+16,zlib.crc32(depbytes))
 label='GlobalVisualTreeAssetPreload';idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==label);ko,ls=cat.key_records[idx]
 records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in [y[0] for y in cat.array(ls,'I')]+cat.locations(RG)),True))
 struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*x) for x in records),True));catalog=bytes(cat.data)
 for n,e in env.items():
  raw=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects}
  assert set(check)==set(objs[n])
  assert reserved.isdisjoint(set(check)-set(hashes[n]))
  for pid,h in hashes[n].items():
   if pid not in changes[n]:assert sha(check[pid].get_raw_data())==h,(tag,n,pid)
  for pid,tree in changes[n].items():assert check[pid].read_typetree()==tree,(tag,n,pid)
  destination=tagout/n;destination.write_bytes(raw);payloads[str(folder/n)]=str(destination)
 for name,raw in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode())]:
  p=GAME.parent/name if folder==GAME else folder/name
  if str(p) not in before:continue
  destination=tagout/name;destination.write_bytes(raw);payloads[str(p)]=str(destination)
 # Audit actual cell templates/functions through catalog, type and owner bundle.
 cat=cm.Catalog(catalog);keys=dict(cat.keys());catalog_audit=[]
 loaded={};seen=set()
 audit_source=(R/'add-squad-hidden-second-view.py').read_text('utf8')
 body=audit_source[audit_source.index(' def audit_guid(g):'):audit_source.index(' for col in cols:audit_guid')]
 # Read prepared VTA resources, including our new row, rather than old originals.
 body=body.replace('path=folder/bn','path=tagout/bn\n    if not path.exists():path=folder/bn')
 exec(compile(body[1:].replace('\n ','\n'),'database-native-cell-audit','exec'))
 for tree in [source,hidden]:
  for c in tree['m_tableView']['m_tableConfig']:
   assert c['m_columnID'] in fc
   audit_guid(fc[c['m_columnID']]['m_uxmlRef']['m_AssetGUID'])
 audit_guid(RG)
 for guid,pid,n in [(VG,VP,V),(RG,RP,G)]:
  locs=[cat.location(i) for i in cat.locations(guid)]
  assert locs and all(q['dependencies'] and cat.location(q['dependencies'][0])['internal'].replace('\\','/').endswith('/'+n) for q in locs)
  meta_pid=next(o.path_id for o in objs[n].values() if o.type.name=='AssetBundle')
  assert any(k==guid and p['asset']=={'m_FileID':0,'m_PathID':pid} for k,p in changes[n][meta_pid]['m_Container']),(guid,pid,n)
 assert cat.locations(RG)[0] in [x[0] for x in cat.array(dict(cat.keys())[label],'I')]
 for tree in [source,hidden]:
  cc=tree['m_tableView']['m_tableConfig'];k=next(i for i,c in enumerate(cc) if c['m_columnID']=='knowledge')
  assert cc[k+1]==rating
 diffs=[i for i,(a,b) in enumerate(zip(columns,hidden['m_tableView']['m_tableConfig'])) if a!=b]
 assert len(diffs)==4 and all(columns[i]['m_columnID'] in replacements for i in diffs)
 # Verify hidden fields against the existing native hidden view and factory.
 hd=find(V,'FirstTeamTableHidden').read_typetree()
 assert set(replacements.values())<={c['m_columnID'] for c in hd['m_tableView']['m_tableConfig']}
 assert fc['average-rating']['m_sortBinding']['m_path']=='binding.averagerating'
 reports.append({'folder':tag,'selector_order':['总览','总览+隐藏'],'widths':widths,'columns_overview':[c['m_columnID'] for c in columns],'columns_hidden':[c['m_columnID'] for c in hidden['m_tableView']['m_tableConfig']],'dropdowns':dropdowns,'resources_checked':len(catalog_audit),'changed_objects':{n:list(d) for n,d in changes.items()},'other_objects_byte_identical':True})
 (tagout/'resource-audit.json').write_text(json.dumps(catalog_audit,ensure_ascii=False,indent=2),'utf8')
 (tagout/'view-overview.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),'utf8')
 (tagout/'view-overview-hidden.json').write_text(json.dumps(hidden,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert Path(p).read_bytes()==b,('Baseline changed',p)
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,('Protected changed',p)
m={'installed':False,'runtime_verified':False,'reports':reports,'before_sha256':{p:sha(b) for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) for p,s in payloads.items()},'protected_sha256':protected,'no_texture_or_factory_changes':True,'new_view_guid':VG,'new_row_guid':RG}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'sources':payloads,'before':backups},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-tangfu-squad-view.py').read_bytes())
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('球员数据库“总览”下新增“总览+隐藏”。新表复制总览全部栏目，仅将能力/潜力五星替换为原生隐藏数值列（64px）。两表均在知识后加入数据-俱乐部的平均评分。效果120→125px、知识160→130px（最小130）、俱乐部200→170px（最小100）。保持原响应式分支、条件、筛选、评分绑定及其余菜单顺序。私有行模板仅接到实际引用PlayerSearchResultsViewCollection的选择器，第二项和选中标题显示总览+隐藏，其他行保留原始标题。新增视图及行模板登记目录，保留所属包首项依赖，补充Global预加载及本地对象引用闭包。基于游戏/独立主皮肤各自最新资源增量生成，其他对象逐字节验证。install.ps1安装，restore.ps1哈希保护回退；后续有修改须合并回退，不可旧整包覆盖。未启动游戏或控制桌面/浏览器，游戏显示待验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'reports':reports},ensure_ascii=False),flush=True)
