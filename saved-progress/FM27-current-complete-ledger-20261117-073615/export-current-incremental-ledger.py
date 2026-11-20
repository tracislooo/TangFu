"""Read-only inventory of current FM27 bundles and lossless export of changes."""
from pathlib import Path
import sys,json,hashlib,datetime,shutil,gzip,base64,collections,xml.etree.ElementTree as ET,importlib.util,gc,copy,os
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');N=R/'saved-progress/FM27-new-update-main-review-20261112-031740';OLD=R/'saved-progress/FM27-original-diff-20261111-191041';O=R/'saved-progress'/('FM27-current-complete-ledger-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));O.mkdir(parents=True)
PREVIOUS=Path(json.loads((R/'current-complete-bundle-ledger.json').read_text('utf8'))['archive'])
PM=json.loads((PREVIOUS/'manifest.json').read_text('utf8'));PR={(r['mode'],r['bundle']):r for r in PM['bundles']}
sha=lambda b:hashlib.sha256(b).hexdigest()
def ph(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def norm(v):
 if isinstance(v,(bytes,bytearray)):return {'__bytes_base64__':base64.b64encode(v).decode('ascii')}
 if isinstance(v,dict):return {str(k):norm(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [norm(x) for x in v]
 return v
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.name.endswith('.gz'):
  with gzip.open(p,'wt',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,separators=(',',':'))
 else:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
def diff(a,b,path=''):
 if a==b:return
 if isinstance(a,dict) and isinstance(b,dict):
  for k in sorted(set(a)|set(b)):
   p=path+'/'+k.replace('~','~0').replace('/','~1')
   if k not in a:yield {'path':p,'op':'add','after':b[k]}
   elif k not in b:yield {'path':p,'op':'remove','before':a[k]}
   else:yield from diff(a[k],b[k],p)
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
  for i,(x,y) in enumerate(zip(a,b)):yield from diff(x,y,path+'/'+str(i))
 else:yield {'path':path,'op':'replace','before':a,'after':b}
def load(p):
 e=UnityPy.load(str(p));d={}
 for o in e.objects:
  k=(o.assets_file.name.lower(),str(o.path_id))
  if k in d:raise ValueError('Duplicate CAB/pathID')
  d[k]=o
 return e,d
def name(o):
 try:return o.peek_name() or o.type.name
 except Exception:return o.type.name
def metadata(e):
 out={}
 for af in e.assets:
  keys=collections.defaultdict(list)
  for o in af.objects.values():
   if o.type.name=='AssetBundle':
    t=o.read_typetree()
    for k,v in t['m_Container']:
     if v['asset']['m_FileID']==0:keys[str(v['asset']['m_PathID'])].append(k)
  out[af.name.lower()]={'unity_version':af.unity_version,'externals':[x.path for x in af.externals],'container_keys':dict(keys),'script_ids':sorted({o.serialized_type.script_id.hex() for o in af.objects.values() if o.serialized_type and o.serialized_type.script_id})}
 return out
def refs(t,af):
 out=set()
 def visit(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
    fid=v['m_FileID'];cab=(af.name if fid==0 else af.externals[fid-1].name if 0<fid<=len(af.externals) else 'INVALID_FILE_ID_'+str(fid)).lower();out.add((cab,str(v['m_PathID'])))
   else:
    for x in v.values():visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
 visit(t);return [{'cab':x,'path_id':y} for x,y in sorted(out)]
def uxml(t,p):
 if 'm_VisualTree' not in t:return
 rr={r['rid']:r for r in t.get('references',{}).get('RefIds',[])};root=ET.Element('UXML-inspection',{'name':t.get('m_Name',''),'note':'Inspection only. Full serialized bindings/overrides in adjacent JSON.gz; not directly importable.'})
 for u in t.get('m_Usings',[]):ET.SubElement(root,'Template',{'alias':str(u.get('alias','')),'guid-or-path':str(u.get('path',''))})
 def visit(rid,parent,seen):
  if rid in seen:return
  d=rr.get(rid,{}).get('data',{});node=ET.SubElement(parent,'Element',{'type':d.get('m_FullTypeName',''),'rid':str(rid),'element-id':str(d.get('m_Id','')),'classes':' '.join(d.get('m_Classes',[])),'style-rule':str(d.get('m_RuleIndex',-1))})
  if d.get('m_TemplateAlias'):node.set('template',str(d['m_TemplateAlias']))
  sd=rr.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  for k in ['name','text','bindingPath','templateId']:
   if isinstance(sd.get(k),(str,int,float)):node.set(k,str(sd[k]))
  ET.SubElement(node,'SerializedData').text=json.dumps(norm(sd),ensure_ascii=False,separators=(',',':'))
  if d.get('m_SerializedDataOverride'):ET.SubElement(node,'SerializedOverrides').text=json.dumps(norm(d['m_SerializedDataOverride']),ensure_ascii=False,separators=(',',':'))
  for c in d.get('m_Children',[]):visit(c['rid'],node,seen|{rid})
 visit(t['m_VisualTree']['rid'],root,set());ET.indent(root);ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
def payload(o):
 if not o or o.type.name!='Texture2D':return None
 t=o.read()
 if not t.image_data and (t.m_StreamData is None or t.m_StreamData.size==0):return b''
 return t.get_image_data()
def export(o,p):
 if o is None:return None
 p.parent.mkdir(parents=True,exist_ok=True);p.with_suffix('.bin').write_bytes(o.get_raw_data());t=o.read_typetree();dump(p.with_suffix('.json.gz'),norm(t));uxml(t,p.with_suffix('.uxml'));return norm(t)
def short(v):
 s=json.dumps(v,ensure_ascii=False,separators=(',',':'));return s if len(s)<500 else s[:450]+'…（完整值见changes.json.gz）'
baseinv={r['name']:r for r in json.loads((N/'updated-all-bundle-hashes.json').read_text('utf8'))};allfiles=sorted((G/'StandaloneWindows64').glob('*.bundle'));inventory=[];sourceguards=[];errors=[];bundles=[];reused={}
print('Hashing and archiving all installed bundles',len(allfiles),flush=True)
for p in allfiles:
 h=ph(p);q=O/'snapshot/current-game/aa/StandaloneWindows64'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert ph(q)==h;sourceguards.append((p,h));inventory.append({'bundle':p.name,'sha256':h,'bytes':p.stat().st_size,'baseline_sha256':baseinv.get(p.name,{}).get('sha256'),'status':'unchanged' if baseinv.get(p.name,{}).get('sha256')==h else 'added_bundle' if p.name not in baseinv else 'changed','snapshot':str(q.relative_to(O))})
for p in G.iterdir():
 if p.is_file():
  q=O/'snapshot/current-game/aa'/p.name;shutil.copy2(p,q);h=ph(p);assert ph(q)==h;sourceguards.append((p,h))
for p in S.iterdir():
 if p.is_file() and (p.suffix=='.bundle' or p.name.startswith('catalog.')):
  q=O/'snapshot/independent-main/aa'/(p.name if p.name.startswith('catalog.') else 'StandaloneWindows64/'+p.name);q.parent.mkdir(parents=True,exist_ok=True);h=ph(p);shutil.copy2(p,q);assert ph(q)==h;sourceguards.append((p,h))
dump(O/'all-installed-bundles.json',inventory)
# Materialize exact old native content when available. Unchanged game snapshot doubles as verified native content.
baselines={}
for row in inventory:
 n=row['bundle'];expected=row['baseline_sha256']
 if row['status']=='unchanged':baselines[n]=O/row['snapshot'];continue
 for candidate in [N/'updated-native/aa/StandaloneWindows64'/n,OLD/'original/aa/StandaloneWindows64'/n]:
  if candidate.exists() and ph(candidate)==expected:
   dst=O/'native-baseline/aa/StandaloneWindows64'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(candidate,dst);assert ph(dst)==expected;baselines[n]=dst;break
dump(O/'baseline-index.json',{'native_inventory_source':str(N),'bundles':[{**v,'materialized_native':str(baselines[n].relative_to(O)) if n in baselines else None} for n,v in baseinv.items()] if False else [{'bundle':n,'sha256':v['sha256'],'materialized_native':str(baselines[n].relative_to(O)) if n in baselines else None} for n,v in baseinv.items()]})
# Preserve native catalog for future three-way reconstruction.
for n in ['catalog.bin','catalog.hash','settings.json']:
 p=N/'updated-native/aa'/n
 if p.exists():q=O/'native-baseline/aa'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for mode in ['current-game','independent-main']:
 folder=O/'snapshot'/mode/'aa/StandaloneWindows64'
 for p in sorted(folder.glob('*.bundle')):
  n=p.name;h=ph(p);bh=baseinv.get(n,{}).get('sha256');row={'mode':mode,'bundle':n,'modified_sha256':h,'original_sha256':bh,'snapshot':str(p.relative_to(O)),'objects':[]};bundles.append(row)
  if h==bh:row['status']='unchanged';continue
  prior=PR.get((mode,n))
  if prior and prior.get('modified_sha256')==h and prior.get('original_sha256')==bh and not prior.get('decode_error') and prior.get('status') not in ['no_complete_native_baseline']:
   original=row['snapshot'];row.update(copy.deepcopy(prior));row['snapshot']=original;row['reused_prior_bundle_export']=str(PREVIOUS);row.pop('shared_export_from',None)
   if n in baselines:row['original_snapshot']=str(baselines[n].relative_to(O))
   for ob in row['objects']:ob['detail']=os.path.relpath(PREVIOUS/ob['detail'],O).replace('\\','/');ob['reused_export_verified_in']=str(PREVIOUS)
   if row.get('internal_resources'):row['internal_resources']['detail']=os.path.relpath(PREVIOUS/row['internal_resources']['detail'],O).replace('\\','/')
   continue
  base=baselines.get(n)
  if base is None:row['status']='no_complete_native_baseline';errors.append({'mode':mode,'bundle':n,'error':'No verified native bundle available; snapshot saved; object differences not inferred'});continue
  row['original_snapshot']=str(base.relative_to(O));cachekey=(n,h,bh)
  if cachekey in reused:
   prior=reused[cachekey];row['status']='changed_shared_export';row['objects']=prior['objects'];row['shared_export_from']=prior['mode'];row['bundle_metadata']=prior['bundle_metadata'];continue
  print('Comparing',mode,n,flush=True)
  ae,aa=load(base);be,bb=load(p);am=metadata(ae);bm=metadata(be);row['bundle_metadata']={'native':am,'modified':bm};allindex=[]
  for key in sorted(set(aa)|set(bb)):
   a=aa.get(key);b=bb.get(key);ar=a.get_raw_data() if a else None;br=b.get_raw_data() if b else None;ap=bp=None
   try:
    if (b or a).type.name=='Texture2D':ap=payload(a);bp=payload(b)
   except Exception as ex:errors.append({'mode':mode,'bundle':n,'identity':key,'error':'texture payload: '+str(ex)})
   ah=sha(ar) if ar is not None else None;bh2=sha(br) if br is not None else None;allindex.append({'cab':key[0],'path_id':key[1],'type':(b or a).type.name,'name':name(b or a),'native_raw_sha256':ah,'modified_raw_sha256':bh2})
   if ar==br and ap==bp:continue
   d=O/'objects'/mode/n/key[0]/key[1];at=bt=None;rec={'cab':key[0],'path_id':key[1],'name':name(b or a),'type':(b or a).type.name,'status':'added' if a is None else 'deleted' if b is None else 'modified','before_raw_sha256':ah,'after_raw_sha256':bh2,'native_keys':am.get(key[0],{}).get('container_keys',{}).get(key[1],[]),'modified_keys':bm.get(key[0],{}).get('container_keys',{}).get(key[1],[]),'detail':str(d.relative_to(O)).replace('\\','/')};row['objects'].append(rec)
   try:
    at=export(a,d/'original');bt=export(b,d/'modified');changes=list(diff(at,bt)) if at is not None and bt is not None else [{'path':'','op':'add' if a is None else 'remove','complete_object_file':'modified.json.gz' if a is None else 'original.json.gz'}];dump(d/'changes.json.gz',changes);rec['field_changes']=len(changes);rec['references']=refs(b.read_typetree(),b.assets_file) if b else [];rec['semantic_equal']=at==bt if at is not None and bt is not None else False
   except Exception as ex:rec['decode_error']=str(ex);errors.append({'mode':mode,'bundle':n,'identity':key,'error':str(ex)});changes=[];rec['field_changes']=0
   if ap!=bp:
    rec['texture_payload']={'native_sha256':sha(ap) if ap is not None else None,'modified_sha256':sha(bp) if bp is not None else None}
    for label,data in [('original',ap),('modified',bp)]:
     if data is not None:(d/(label+'.texture-data.bin')).write_bytes(data)
   notes=['# '+str(rec['name']),'',f'版本：{mode}；包：{n}；Path ID：{key[1]}；状态：{rec["status"]}','',f'完整字段改动{rec["field_changes"]}项，见changes.json.gz；对象完整数据在original/modified.json.gz及.bin。模板引用、绑定、完整覆盖和样式数据均保留。','']
   for change in changes[:60]:notes.extend(['- `'+change['path']+'`：'+change['op']+'；原值 '+short(change.get('before'))+'；新值 '+short(change.get('after'))])
   if len(changes)>60:notes.append('\n其余字段完整保存在changes.json.gz，未省略实际导出。')
   (d/'修改位置.md').write_text('\n'.join(notes),'utf8')
  row['status']='changed' if row['objects'] else 'packaging_only';dump(O/'indexes'/mode/(n+'.objects.json.gz'),allindex);reused[cachekey]=row;del ae,be,aa,bb;gc.collect();dump(O/'manifest.partial.json',{'bundles':bundles,'errors':errors})
# Canonical catalog comparison, including labels' actual location arrays and dependencies.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def catalog(p):
 c=cm.Catalog(p.read_bytes());cache={};out={}
 def loc(off):
  if off not in cache:
   v=c.location(off);cache[off]={'primary':v['primary'],'internal':v['internal'],'provider':v['provider'],'type':v['type'],'dependencies':[c.location(x)['primary'] for x in v['dependencies']]}
  return cache[off]
 for k,l in c.keys():out[str(k)]=[loc(x[0]) for x in c.array(l,'I')]
 return out
print('Comparing catalogs and recording provenance',flush=True);nativecat=catalog(O/'native-baseline/aa/catalog.bin');catalogs=[]
for mode in ['current-game','independent-main']:
 p=O/'snapshot'/mode/'aa/catalog.bin'
 if not p.exists():continue
 currentcat=catalog(p);changes=[{'key':k,'status':'added' if k not in nativecat else 'deleted' if k not in currentcat else 'modified','before':nativecat.get(k),'after':currentcat.get(k)} for k in sorted(set(nativecat)|set(currentcat)) if nativecat.get(k)!=currentcat.get(k)];dump(O/'catalogs'/(mode+'-changes.json.gz'),changes);catalogs.append({'mode':mode,'native_keys':len(nativecat),'modified_keys':len(currentcat),'change_count':len(changes),'counts':dict(collections.Counter(x['status'] for x in changes)),'binary_fields_note':'Summary omits opaque extraData and offset/hash internals; complete catalogs preserved.'})
context=O/'context';context.mkdir()
for p in list(R.glob('current*.json'))+[R/'AGENTS.md',R/'reserved-texture-ids.json']:
 if p.exists():shutil.copy2(p,context/p.name)
side=json.loads((R/'current-sidebar-version.json').read_text('utf8'));sidepath=Path(side['latest_saved_sidebar_archive']);sideinfo={'latest_archived_sidebar':str(sidepath),'current_game_mode_recorded':side.get('current_game_mode'),'sidebar_not_rebased_this_task':True}
# Save the actual latest sidebar archive's supplied files separately without treating it as today's game.
if sidepath.exists():
 for foldername in ['aa','packages','non-sidebar-backup']:
  folder=sidepath/foldername
  if folder.exists():
   for p in folder.rglob('*'):
    if p.is_file():q=O/'archived-sidebar'/foldername/p.relative_to(folder);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 for n in ['manifest.json','sidebar-state.json','transaction.json']:
  if (sidepath/n).exists():shutil.copy2(sidepath/n,O/'archived-sidebar'/n)
dump(O/'sidebar-provenance.json',sideinfo)
# Capture recent owning records; no installer or migration script is executed.
for p in R.glob('current*.json'):
 try:j=json.loads(p.read_text('utf-8-sig'))
 except Exception:continue
 for field in ['manifest','verification']:
  v=j.get(field)
  if isinstance(v,str):
   q=Path(v)
   if q.exists() and q.is_file() and q.suffix in ['.json','.md','.txt']:
    dest=context/'owning-records'/(p.stem+'-'+field+q.suffix);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
counts={mode:dict(collections.Counter(ob['status'] for row in bundles if row['mode']==mode for ob in row['objects'])) for mode in ['current-game','independent-main']};manifest={'format_version':2,'previous_ledger':str(PREVIOUS),'created':datetime.datetime.now().isoformat(),'native_baseline':str(N),'native_baseline_date':'2026-11-12','current_game_source':str(G),'game_modified':False,'bundles':bundles,'catalogs':catalogs,'counts':counts,'errors':errors,'removed_native_bundles':sorted(set(baseinv)-{p.name for p in allfiles}),'sidebar':sideinfo}
dump(O/'manifest.json',manifest)
lines=['# 当前全部bundle修改清单','','基于当前实际资源重新比较；原版基线为2026-11-12更新后、安装皮肤前的已验证存档。历史补丁仅作为需求上下文，实际清单以包内差异为准。','','[更新迁移说明](更新迁移说明.md) · [资源来源与限制](README.md)','','## 包清单','','|版本|bundle|状态|差异对象数|','|---|---|---|---|']
for row in bundles:
 if row['status']!='unchanged':lines.append('|'+ '|'.join([row['mode'],row['bundle'],row['status'],str(len(row['objects']))])+'|')
lines+=['','## 全部差异对象','','|版本|bundle|对象名|类型|Path ID|状态|字段数|具体修改|','|---|---|---|---|---|---|---|---|']
for row in bundles:
 for ob in row['objects']:
  values=[row['mode'],row['bundle'],ob['name'],ob['type'],ob['path_id'],ob['status'],ob['field_changes'],f'[查看]({ob["detail"]}/修改位置.md)'];lines.append('|'+'|'.join(str(v).replace('|','\\|').replace('\n',' ') for v in values)+'|')
(O/'修改总清单.md').write_text('\n'.join(lines),'utf8')
(O/'README.md').write_text('''# 当前实际资源的完整记录

snapshot/current-game/aa：当前游戏全部bundle及catalog等顶层文件，完整独立快照。snapshot/independent-main/aa：独立主皮肤实际资源，单独保留。

all-installed-bundles.json覆盖全部游戏bundle。原版同名文件完全一致者标为unchanged，其余完整导出新增、删除、修改对象。native-baseline为有差异的包保留原版；baseline-index.json为全部原版文件提供内容来源，其中完全未改的文件直接引用已验证相同哈希的当前快照，避免重复存储。构成完整原始内容来源，不把当前修改版当成原版。

每个差异对象有完整original/modified.bin、JSON.gz、字段changes.json.gz及修改位置.md。JSON中的字节使用可逆base64编码；Texture2D额外比较实际图像载荷并导出，包含.resS数据。完整bundle仍是数据流、对象类型、外部引用的最终恢复来源。若只是二进制布局变化而字段一致会单独标明semantic_equal。

.uxml为从序列化树重建的阅读文件，完整绑定、属性覆盖、节点ID等以JSON.gz和BIN为准，不可将重建UXML直接导回游戏。USS样式使用样式对象的完整序列化数据记录，包括选择器、规则、值表和资源引用。函数、布局、表格、字体、图片及容器/预加载也包括在内。

两种资源内容相同时复用同一套对象导出，来源在manifest.shared_export_from记录；原始快照仍各自保存。归档侧边栏只保存最新历史来源，不冒充今天主版，也未在本任务中迁移或安装。

目录语义记录覆盖键、类型、位置及按顺序排列的依赖和预加载标签location列表。extraData等二进制字段不由摘要完整解释，完整catalog.bin/hash保留供新版目录结构迁移使用。不能把语义摘要直接当成可安装目录。

当前索引及其拥有者manifest、验证说明在context保留；其中状态和运行验证结论各自有来源。本次只证明文件读取、导出与哈希一致，没有启动游戏验证显示。完全相同的资源包复用上次已验证的逐对象导出，manifest保留相对链接与previous_ledger，旧记录不可删除；当前完整资源快照仍独立保存。
''','utf8')
(O/'更新迁移说明.md').write_text('''# 游戏更新后的迁移步骤

1. 先保存新版原生bundle、catalog及哈希；与本记录baseline-index的原版内容比较。compare-update.py只读生成对比报告，不写游戏。
2. 按“旧原版→当前修改版”的记录，在新版原包上合并变化。新版原包与本原版完全一致时，对应完整修改包可作为复用候选；包有变化时按GUID/对象身份/具体字段迁移，并保留新版无关对象。
3. Unity重建可能改变CAB、Path ID、模板控件ID、managed-reference rid、数组结构和类型schema。container_keys、完整对象、引用和外部CAB映射已保留。不能直接按旧数组下标、旧valueIndex覆盖新表；样式须比较选择器、属性及索引解析后的真实值。原生元素覆盖必须核验完整m_ElementIdsPath。
4. 新增对象迁移需处理序列化类型、外部引用及数据流、AssetBundle容器与预加载；删除对象同时清理引用。遵守reserved-texture-ids及已停用资源规则。以本次实际纹理数据为恢复源，不要从旧图包全量恢复。新增图片/素材与原生背景覆盖均要保留。
5. 在新版catalog上登记模板与函数GUID，校验类型、实际对象、所属包首项依赖、跨包背景依赖和实际preload locations。新目录可能有官方变更，不能覆盖旧catalog。catalog.hash和相关bundle哈希按新版工具生成。
6. 冲突单独适配：新版删除/更名对象、改变同一字段、改模板结构或占用自定义ID时，不自动覆盖。本工具提供候选匹配和原包/对象变化报告，不能代替语义适配。
7. 先完成主皮肤，输出新目录并回读验证引用、目录、布局和无关对象；再由用户运行验证。之后才以新主版迁移侧边栏专属增量，生成必要替换包，不用历史侧边栏整包覆盖新修复。

本次是盘点、导出与存档，没有修改当前游戏或独立皮肤。原版基线以后若变动，必须另存新基线，不能将已经安装皮肤的资源登记为原版。
''','utf8')
print('Verifying archived objects and unchanged source files',flush=True)
verified=0
for row in bundles:
 if row.get('shared_export_from'):continue
 for ob in row['objects']:
  if ob.get('reused_export_verified_in'):continue
  for label,key in [('original','before_raw_sha256'),('modified','after_raw_sha256')]:
   if ob[key]:assert ph(O/ob['detail']/(label+'.bin'))==ob[key];verified+=1
assert all(ph(p)==h for p,h in sourceguards),'Source resources changed during audit; record must be refreshed'
verification={'verified_object_binaries':verified,'source_files_stable':True,'source_file_count':len(sourceguards),'errors':errors,'game_modified':False,'runtime_tested':False};dump(O/'verification.json',verification)
if errors:print('INCOMPLETE_ERRORS',len(errors),flush=True)
else:
 index={'archive':str(O),'manifest':str(O/'manifest.json'),'report':str(O/'修改总清单.md'),'format_version':2,'baseline':str(N),'counts':counts,'verified':True,'errors':0}
 dump(R/'current-original-bundle-diff.json',index);dump(R/'current-complete-bundle-ledger.json',index)
shutil.copy2(Path(__file__),O/Path(__file__).name);print(json.dumps({'output':str(O),'bundle_count':len(inventory),'changed_game_bundles':sum(x['status']!='unchanged' for x in inventory),'counts':counts,'errors':len(errors)},ensure_ascii=False),flush=True)
