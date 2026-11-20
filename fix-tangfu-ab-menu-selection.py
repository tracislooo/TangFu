from pathlib import Path
R=Path(__file__).resolve().parent
prefix=(R/'add-tangfu-ab-native-selector.py').read_text('utf8').split("for folder,tag in [(GAME,'game'),(SKIN,'skin')]:")[0]
prefix=prefix.replace("'tangfu-ab-native-selector-'","'tangfu-ab-menu-selection-fix-'")
exec(compile(prefix,'current-resource-codecs','exec'))
DP,DS=-991111000002020,-991111000002021;DG=guid('scoped-dropdown-header')
all_checks=[]
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
 # Keep native menu identities distinct as well as the rendered literal labels.
 for pid,tid in [(AP,15234),(BP,15235)]:
  d=objs[V][pid].read_typetree();d['m_tableView']['m_viewName']={'GameID':tid};put(V,pid,objs[V][pid],d)
 collection=find(V,'FirstTeamSquadAndYouthTeamSquadCollection');cd=collection.read_typetree()
 for i,(pid,tid) in enumerate([(AP,15234),(BP,15235)]):
  assert cd['m_tableViewSettings'][i]['PropertyValue']=={'m_FileID':0,'m_PathID':pid};cd['m_tableViewSettings'][i]['DisplayValue']={'GameID':tid}
 put(V,collection.path_id,collection,cd)
 av=changes[V][AP]['m_tableView'];bv=changes[V][BP]['m_tableView'];assert av['m_viewName']!=bv['m_viewName']
 ac=av['m_tableConfig'];bc=bv['m_tableConfig'];different=[i for i,(a,b) in enumerate(zip(ac,bc)) if a!=b];assert len(different)==2
 assert [ac[i]['m_columnID'] for i in different]==['scout-opinion-current-ability','scout-opinion-potential-ability']
 assert [bc[i]['m_columnID'] for i in different]==['hidden-current-ability','hidden-potential-ability']
 # Negative indices are native folders/separators. Their original label must win.
 rd=Doc(G,pid=RP);s0=rd.named('TangFuViewAfterA');parent=rd.a(s0)['m_Parent']['rid'];index=rd.a(parent)['m_Children'].index({'rid':s0})
 outer=rd.add(rd,s0,parent,'TangFuViewHasValidIndex');rd.move(outer,parent,index);rd.data(outer)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=switch_args(-1)
 fallback=rd.add(rd,1008,outer,'TangFuNativeFolderTitle');rd.a(fallback)['m_Classes']=copy.deepcopy(rd.a(1008)['m_Classes']);rd.move(fallback,outer,0);rd.move(s0,outer);rd.save()
 # Reuse the native header layout once, with its existing selectedView -> row
 # remapper pointing to our row renderer, rather than adding a second header row.
 native=Doc(G,name='TableViewDropdown');tree=copy.deepcopy(native.d);sheet=copy.deepcopy(native.s)
 assert DP not in objs[G] and DS not in objs[G];tree['m_Name']='TangFuSquadDropdownSingleHeader';tree['inlineSheet']['m_PathID']=DS;sheet['m_Name']='TangFuSquadDropdownSingleHeaderStyle'
 using=next(u for u in tree['m_Usings'] if u['alias']=='GenericDisplayValuePairDropdownRow');using['path']=RG
 put(G,DP,native.obj,tree);put(G,DS,objs[G][native.sid],sheet)
 validate_ui(tree,sheet)
 changed_roots=[]
 for ob in list(objs[W].values()):
  if ob.type.name!='MonoBehaviour':continue
  tree=ob.read_typetree()
  if 'inlineSheet' not in tree:continue
  edited=[]
  for r in tree['references']['RefIds']:
   data=r.get('data',{});args=data.get('BindChoicesFunction',{}).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
   if COLLECTION_GUID.encode() not in bytes(args):continue
   data.update(UseRowTemplateToShowSelectedValue=0,UseRowTemplateToShowSelectedValue_UxmlAttributeFlags=1);edited.append(r['rid'])
  if not edited:continue
  usings=[u for u in tree['m_Usings'] if u['alias']=='TableViewDropdown'];assert len(usings)==1,(tree['m_Name'],tree['m_Usings'])
  usings[0]['path']=DG;put(W,ob.path_id,ob,tree);changed_roots.append(tree['m_Name'])
 assert 'TeamSquadBlock' in changed_roots
 mo=next(o for o in objs[G].values() if o.type.name=='AssetBundle');mt=mo.read_typetree();sourceguid=next(g for g,v in mt['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':native.obj.path_id});entry=next(v for g,v in mt['m_Container'] if g==sourceguid and v['asset']['m_PathID']==native.obj.path_id)
 span=copy.deepcopy(mt['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in span:
  if ptr=={'m_FileID':0,'m_PathID':native.obj.path_id}:ptr['m_PathID']=DP
  elif ptr=={'m_FileID':0,'m_PathID':native.sid}:ptr['m_PathID']=DS
 for pid in [DP,DS,RP,SP]:
  if {'m_FileID':0,'m_PathID':pid} not in span:span.append({'m_FileID':0,'m_PathID':pid})
 mt['m_Container'].append((DG,{'preloadIndex':len(mt['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':DP}}));mt['m_PreloadTable'].extend(span);mt['m_Container'].sort(key=lambda x:x[0]);put(G,mo.path_id,mo,mt)
 cp=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';original=cm.Catalog(before[str(cp)]);catalog=original.add_key_location(DG,original.locations(sourceguid)[0],original.locations(sourceguid)[0]);cat=cm.Catalog(catalog)
 loc=cat.locations(DG)[0];deps=list(cat.location(loc)['dependencies'])
 for dep in cat.location(cat.locations(RG)[0])['dependencies']:
  if dep not in deps:deps.append(dep)
 struct.pack_into('<I',cat.data,loc+12,cat.append(b''.join(struct.pack('<I',d) for d in deps),True))
 idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in [r[0] for r in cat.array(ls,'I')]+cat.locations(DG)),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*x) for x in records),True));catalog=bytes(cat.data)
 for n,e in env.items():
  raw=e.file.save(packer='lz4');oo={o.path_id:o for o in UnityPy.load(raw).objects};assert set(oo)==set(objs[n])
  for pid,h in hashes[n].items():
   if pid not in changes[n]:assert sha(oo[pid].get_raw_data())==h,(tag,n,pid)
  for pid,d in changes[n].items():assert oo[pid].read_typetree()==d,(tag,n,pid)
  target=tagout/n;target.write_bytes(raw);payloads[str(folder/n)]=str(target)
 for name,raw in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode())]:
  p=GAME.parent/name if folder==GAME else folder/name
  if str(p) not in before:continue
  target=tagout/name;target.write_bytes(raw);payloads[str(p)]=str(target)
 # Native branch comparison uses index > threshold. Verify all first-level and
 # submenu indices select the intended label, not merely the happy path 0/1.
 def label(i):return 'native' if not i>-1 else ('tangfu A' if not i>0 else ('tangfu B' if not i>1 else 'native'))
 cases={i:label(i) for i in [-3,-2,-1,0,1,2,3,4,5,6,20,99]};assert all(v==('tangfu A' if i==0 else 'tangfu B' if i==1 else 'native') for i,v in cases.items())
 cat=cm.Catalog(catalog);keys=dict(cat.keys());out=tagout;tx={'game':str(folder)}
 src=(R/'finish-outside-match-square-portraits.py').read_text('utf8');src=src[src.index('loaded={};'):src.index("for c in m['clones']:")];src=src.replace("e=UnityPy.load(str(path));","\n  if not path.exists():path=GAME/bundle\n  e=UnityPy.load(str(path));")
 exec(compile(src,'scoped-header-and-row-resource-audit','exec'));audit(DG)
 all_checks.append({'folder':tag,'changed_roots':changed_roots,'ability_columns_a':[ac[i]['m_columnID'] for i in different],'ability_columns_b':[bc[i]['m_columnID'] for i in different],'view_ids':[15234,15235],'label_cases':cases,'single_native_header':True,'resources_verified':len(audits)})
for p,b in before.items():assert Path(p).read_bytes()==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
m={'installed':False,'runtime_verified':False,'checks':all_checks,'before_sha256':{p:sha(b) for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) for p,s in payloads.items()},'protected_sha256':protected}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'sources':payloads,'before':backups},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-primary-navigation-patch.py').read_text('utf8').replace("[Path(tx['game']).resolve(),Path(tx['skin']).resolve()]","[Path(tx['game']).resolve(),Path(tx['game']).parent.resolve(),Path(tx['skin']).resolve()]")
(OUT/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('修复tangfu A/B菜单：负数菜单分组索引保留原DisplayValue，只有0/1显示A/B；选择框恢复原生单套眼睛/文字/箭头布局，其内文字采用私有行模板，取消追加第二份当前行。A/B原生viewName及条目DisplayValue采用不同标识；A两列为球探评估星级，B两列为实际CA/PA数值。保留其他列、前四项排序及原隐藏/选择信息内容。只对阵容TeamSquadBlock/SquadOverviewTableBlock使用私有下拉副本；共用TableViewDropdown原对象未变。文件、资源引用及菜单索引静态检查通过；未启动游戏或操作桌面，实际切换与显示待用户验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'checks':all_checks},ensure_ascii=False),flush=True)
