"""Native squad A/B views and scoped menu labels, preserving the working hidden entry."""
from pathlib import Path
import sys,json,copy,ast,hashlib,struct,uuid,datetime,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages']);assert 'Football Manager 27' in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';V='ui-tableviews_assets_all.bundle';F='ui-tablefactories_assets_all.bundle'
OUT=R/('tangfu-ab-native-selector-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'templates').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
extract('add-card-six-ratings.py',{'validate_ui'});extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def locations(self,key):
 if not hasattr(self,'index'):self.index=dict(self.keys())
 return [x[0] for x in self.array(self.index[key],'I')]
cm.Catalog.locations=locations
AP,BP,RP,SP=-991111000002000,-991111000002001,-991111000002010,-991111000002011
guid=lambda s:uuid.uuid5(uuid.NAMESPACE_URL,'tf27/TangFu/native-squad/'+s).hex
AG,BG,RG=guid('A'),guid('B'),guid('dropdown-row')
SWITCH='f6f314e9db56227459137669d87c44e9';COLLECTION_GUID='6e59432dfa6b8b84f98b8b300ff37d2b'
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']};assert reserved.isdisjoint([AP,BP,RP,SP])
before={};backups={};payloads={};protected={};reports=[];audits=[]
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def switch_args(limit):
 args=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',4)),('SI.VisualScripting.Int32VisualArg',struct.pack('<i',limit)),('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string('row.PropertyValue'))]
 return list(bytes([len(args)])+b''.join(struct.pack('<I',len(string(t)+v))+string(t)+v for t,v in args))
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 tagout=OUT/tag;tagout.mkdir()
 for name in [W,G,V,'catalog.bin','catalog.hash']:
  p=GAME.parent/name if folder==GAME and name.startswith('catalog.') else folder/name
  if not p.exists() and name=='catalog.hash':continue
  before[str(p)]=p.read_bytes();bp=OUT/('backup-'+tag)/name;bp.parent.mkdir(exist_ok=True);bp.write_bytes(before[str(p)]);backups[str(p)]=str(bp)
 for p in folder.glob('*.bundle'):
  if p.name not in [W,G,V]:protected[str(p)]=sha(p.read_bytes())
 env={n:UnityPy.load(before[str(folder/n)]) for n in [W,G,V]};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()};changes={n:{} for n in env};documents=[]
 def put(n,pid,source,d):
  if pid not in objs[n]:
   ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[n][pid]=ob
  objs[n][pid].save_typetree(d);changes[n][pid]=copy.deepcopy(d)
 metas={n:next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle') for n,oo in objs.items()}
 def key_for(n,pid):return next(g for g,v in metas[n]['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
 selection=find(V,'FirstTeamTableSelectionInfo');collection=find(V,'FirstTeamSquadAndYouthTeamSquadCollection');hidden=find(V,'FirstTeamTableHidden')
 source=selection.read_typetree();cd=collection.read_typetree();oldcd=copy.deepcopy(cd)
 base=json.loads((R/'tangfu-squad-view-20261111-015242/TangFu.json').read_text('utf8'))
 fe=UnityPy.load(str(folder/F));factory=next(o.read_typetree() for o in fe.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerTableFactory');fc={c['m_id']:c for c in factory['m_rowData']}
 views={}
 for title,pid,g,newids in [('tangfu A',AP,AG,['scout-opinion-current-ability','scout-opinion-potential-ability']),('tangfu B',BP,BG,['hidden-current-ability','hidden-potential-ability'])]:
  assert pid not in objs[V]
  tree=copy.deepcopy(source);tree['m_Name']=title;tree['m_tableView']=copy.deepcopy(base);tree['m_tableView']['m_viewName']={'GameID':17890}
  columns=tree['m_tableView']['m_tableConfig']
  for c in columns:
   if c['m_columnID'] in ['current-ability-stars','potential-ability-stars']:
    idx=['current-ability-stars','potential-ability-stars'].index(c['m_columnID']);c['m_columnID']=newids[idx]
    width=100. if pid==AP else 64.;c['m_columnMetadata'].update(m_widthOverride=width,m_minWidthOverride=width)
  assert all(c['m_columnID'] in fc for c in columns)
  assert columns[-1]['m_columnID']=='tangfu-happiness-icon' and columns[-1]['m_columnMetadata']['m_widthOverride']==28.
  put(V,pid,selection,tree);views[title]=tree
 # Keep all the original remaining entries in their original relative order.
 original_rows=cd['m_tableViewSettings'];selrow=next(r for r in original_rows if r['PropertyValue']=={'m_FileID':0,'m_PathID':selection.path_id});hidrow=next(r for r in original_rows if r['PropertyValue']=={'m_FileID':0,'m_PathID':hidden.path_id})
 def entry(pid,title):
  r=copy.deepcopy(selrow);r.update(name=title,debug_name=title,Disable=0,AddSpacerBefore=0,ChildList=[],PropertyValue={'m_FileID':0,'m_PathID':pid},DisplayValue={'GameID':17890},Requirement={'m_FileID':0,'m_PathID':0});return r
 rest=[r for r in original_rows if r is not selrow and r is not hidrow]
 cd['m_tableViewSettings']=[entry(AP,'tangfu A'),entry(BP,'tangfu B'),copy.deepcopy(hidrow),copy.deepcopy(selrow)]+rest
 assert cd['m_tableViewSettings'][2]==hidrow and cd['m_tableViewSettings'][3]==selrow and cd['m_tableViewSettings'][4:]==rest
 put(V,collection.path_id,collection,cd)
 # Clone only the row renderer used by this squad dropdown. Other selectors keep
 # the shared original. Both dropdown rows and selected header use this renderer.
 rowob=next(o for o in objs[G].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='GenericDisplayValuePairDropdownRow')
 row=Doc(G,pid=rowob.path_id);tree=copy.deepcopy(row.d);sheet=copy.deepcopy(row.s);tree.update(m_Name='TangFuABSquadViewRow');tree['inlineSheet']['m_PathID']=SP;sheet['m_Name']='TangFuABSquadViewRowStyle'
 assert RP not in objs[G] and SP not in objs[G];put(G,RP,rowob,tree);put(G,SP,objs[G][row.sid],sheet)
 rd=Doc(G,pid=RP,tree=tree,style=sheet)
 donor=next(Doc(W,pid=o.path_id) for o in objs[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='TacticsConditionPercentageCell')
 sw=next(i for i,r in donor.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement')
 parent=rd.a(1008)['m_Parent']['rid'];index=rd.a(parent)['m_Children'].index({'rid':1008})
 s0=rd.add(donor,sw,parent,'TangFuViewAfterA');rd.move(s0,parent,index)
 s1=rd.add(donor,sw,s0,'TangFuViewAfterB')
 for i,limit in [(s0,0),(s1,1)]:
  rd.data(i).update(Binding={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':SWITCH},'m_inputs':{'m_variable':{'m_argumentBytes':switch_args(limit)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,Preview={'Mask':3},Preview_UxmlAttributeFlags=1)
  rd.st(i,[(131084,rd.num(1)),(131085,rd.num(1))])
 a=rd.add(row,1008,s0,'TangFuATitle');b=rd.add(row,1008,s1,'TangFuBTitle')
 for i,title in [(a,'tangfu A'),(b,'tangfu B')]:
  rd.a(i)['m_Classes']=copy.deepcopy(row.a(1008)['m_Classes']);rd.data(i).update(text=title,text_UxmlAttributeFlags=1,TextBinding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
 rd.move(a,s0,0);rd.move(b,s1,0);rd.move(1008,s1);rd.save()
 dropdowns=[]
 for ob in list(objs[W].values()):
  if ob.type.name!='MonoBehaviour':continue
  tree=ob.read_typetree()
  if 'inlineSheet' not in tree:continue
  edited=[]
  for r in tree['references']['RefIds']:
   data=r.get('data',{});args=data.get('BindChoicesFunction',{}).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
   if COLLECTION_GUID.encode() not in bytes(args):continue
   data['RowTemplate']['m_AssetGUID']=RG;data.update(RowTemplate_UxmlAttributeFlags=1,UseRowTemplateToShowSelectedValue=1,UseRowTemplateToShowSelectedValue_UxmlAttributeFlags=1,ForceRefreshOnNewChoices=1,ForceRefreshOnNewChoices_UxmlAttributeFlags=1);edited.append(r['rid'])
  if edited:put(W,ob.path_id,ob,tree);dropdowns.append({'name':tree['m_Name'],'pid':ob.path_id,'overrides':edited})
 assert dropdowns and any(x['name']=='TeamSquadBlock' for x in dropdowns)
 clones=[(V,AP,selection.path_id,AG,None),(V,BP,selection.path_id,BG,None),(G,RP,rowob.path_id,RG,SP)]
 for n,oo in objs.items():
  mo=next(o for o in oo.values() if o.type.name=='AssetBundle');mt=copy.deepcopy(metas[n])
  for cn,pid,origin,guid,sid in clones:
   if cn!=n:continue
   en=next(v for _,v in metas[n]['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':origin});span=copy.deepcopy(mt['m_PreloadTable'][en['preloadIndex']:en['preloadIndex']+en['preloadSize']])
   oldsid=objs[n][origin].read_typetree().get('inlineSheet',{}).get('m_PathID')
   for ptr in span:
    if ptr=={'m_FileID':0,'m_PathID':origin}:ptr['m_PathID']=pid
    elif sid and ptr=={'m_FileID':0,'m_PathID':oldsid}:ptr['m_PathID']=sid
   for ident in [pid]+([sid] if sid else []):
    if {'m_FileID':0,'m_PathID':ident} not in span:span.append({'m_FileID':0,'m_PathID':ident})
   mt['m_Container'].append((guid,{'preloadIndex':len(mt['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));mt['m_PreloadTable'].extend(span)
  if n==V:
   for _,entry0 in mt['m_Container']:
    if entry0['asset']!={'m_FileID':0,'m_PathID':collection.path_id}:continue
    span=copy.deepcopy(mt['m_PreloadTable'][entry0['preloadIndex']:entry0['preloadIndex']+entry0['preloadSize']])+[{'m_FileID':0,'m_PathID':AP},{'m_FileID':0,'m_PathID':BP}]
    entry0.update(preloadIndex=len(mt['m_PreloadTable']),preloadSize=len(span));mt['m_PreloadTable'].extend(span)
  mt['m_Container'].sort(key=lambda x:x[0]);put(n,mo.path_id,mo,mt)
 cp=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';catalog=before[str(cp)]
 for n,pid,origin,guid,sid in clones:
  cat=cm.Catalog(catalog);loc=cat.locations(key_for(n,origin))[0];catalog=cat.add_key_location(guid,loc,loc)
 cat=cm.Catalog(catalog);loc=cat.locations(RG)[0];dep=list(cat.location(loc)['dependencies']);functiondeps=cat.location(cat.locations(SWITCH)[0])['dependencies']
 for d in functiondeps:
  if d not in dep:dep.append(d)
 struct.pack_into('<I',cat.data,loc+12,cat.append(b''.join(struct.pack('<I',x) for x in dep),True))
 label='GlobalVisualTreeAssetPreload';idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==label);ko,ls=cat.key_records[idx];records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in [y[0] for y in cat.array(ls,'I')]+cat.locations(RG)),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*x) for x in records),True));catalog=bytes(cat.data)
 for n,e in env.items():
  raw=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(objs[n]) and reserved.isdisjoint(check)
  for pid,h in hashes[n].items():
   if pid not in changes[n]:assert sha(check[pid].get_raw_data())==h,(tag,n,pid)
  for pid,tree in changes[n].items():assert check[pid].read_typetree()==tree,(tag,n,pid)
  destination=tagout/n;destination.write_bytes(raw);payloads[str(folder/n)]=str(destination)
 for name,raw in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode())]:
  p=GAME.parent/name if folder==GAME else folder/name
  if str(p) not in before:continue
  destination=tagout/name;destination.write_bytes(raw);payloads[str(p)]=str(destination)
 # Audit new menu VTA, its native function, and both views' actual column cells.
 cat=cm.Catalog(catalog);keys=dict(cat.keys());out=tagout;tx={'game':str(folder)}
 audit_src=(R/'finish-outside-match-square-portraits.py').read_text('utf8');audit_src=audit_src[audit_src.index('loaded={};'):audit_src.index("for c in m['clones']:")]
 audit_src=audit_src.replace("e=UnityPy.load(str(path));","\n  if not path.exists():path=GAME/bundle\n  e=UnityPy.load(str(path));")
 exec(compile(audit_src,'prepared-native-template-audit','exec'))
 audit(RG)
 for tree in views.values():
  for c in tree['m_tableView']['m_tableConfig']:audit(fc[c['m_columnID']]['m_uxmlRef']['m_AssetGUID'])
 audits.extend([dict(x,folder=tag) for x in globals()['audits']]) if False else None
 # Both menu views differ solely in their ability/potential column definitions.
 ac=views['tangfu A']['m_tableView']['m_tableConfig'];bc=views['tangfu B']['m_tableView']['m_tableConfig'];assert len(ac)==len(bc)
 differing=[i for i,(x,y) in enumerate(zip(ac,bc)) if x!=y];assert len(differing)==2
 reports.append({'folder':tag,'selector_order':['tangfu A','tangfu B','隐藏','选择信息'],'other_entries_preserved':True,'ability_column_differences':differing,'dropdowns':dropdowns,'typed_template_functions_verified':len(globals()['audits']),'a_columns':[c['m_columnID'] for c in ac],'b_columns':[c['m_columnID'] for c in bc]})
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/FirstTeamSquadAndYouthTeamSquadCollection/TangFu.json')
if cache.exists():
 before[str(cache)]=cache.read_bytes();bp=OUT/'backup-user-TangFu.json';bp.write_bytes(before[str(cache)]);backups[str(cache)]=str(bp);payloads[str(cache)]=None
for p,b in before.items():assert Path(p).read_bytes()==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
m={'installed':False,'runtime_verified':False,'reports':reports,'before_sha256':{p:sha(b) for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) if s else None for p,s in payloads.items()},'protected_sha256':protected,'removed_old_custom_file':str(cache),'native_menu_connection':True,'no_added_portraits':True}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps({'sources':payloads,'before':backups},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-tangfu-squad-view.py').read_text('utf8').replace("assert sha(Path(source).read_bytes())==m['after_sha256'][p]","assert (sha(Path(source).read_bytes()) if source else None)==m['after_sha256'][p]").replace("assert str(p)==m['custom_view_file']","assert str(p)==m['removed_old_custom_file']").replace("else Path(s).read_bytes();write(p,b)","else (Path(s).read_bytes() if s else None);write(p,b)")
(OUT/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('阵容选择器接入原生视图：tangfu A、tangfu B、隐藏、选择信息，其余原生项目相对顺序保留。B的能力/潜力为数值，A改为原生球探评估五星；其他栏目相同，保留双环、数字士气和末列28px满意度图标。新增两份原生TableViewSettings，复用已有列；仅阵容TeamSquadBlock的选择器指定私有行模板并用于当前选中值显示，原生整数比较函数按菜单索引显示A/B文字，其余行保留原始DisplayValue。目录/预加载同步；不再依赖上次未显示的TangFu.json，旧文件备份后移出。游戏与独立主皮肤分别增量处理，未修改比赛列表、原隐藏与选择信息视图或新增头像。静态与安装校验不能代替实际界面验证；未启动游戏或操作桌面。游戏更新后应以新原包增量重做，禁止旧整包覆盖。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'reports':reports},ensure_ascii=False),flush=True)
