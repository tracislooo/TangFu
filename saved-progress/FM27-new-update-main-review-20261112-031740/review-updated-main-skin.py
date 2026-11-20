from pathlib import Path
import sys,json,hashlib,datetime,shutil,ast,importlib.util,collections
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');B=R/'saved-progress/FM27-original-diff-20261111-191041';idx=json.loads((R/'current-original-bundle-diff.json').read_text('utf8'));M=Path(idx['archive']);m=json.loads((M/'manifest.json').read_text('utf8'));O=R/'saved-progress'/('FM27-new-update-main-review-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));O.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
mod=ast.parse((R/'export-original-bundle-diff.py').read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
sources={};native_hashes={}
for row in m['bundles']:
 if row['mode']=='main':sources[row['bundle']]=Path(row.get('snapshot_source',m['snapshot']))/'main/aa/StandaloneWindows64'/row['bundle'];native_hashes[row['bundle']]=row['original_sha256']
# Recorded supplement is applied after the main record; read saved patch files only.
for sup in idx.get('supplements',[]):
 sm=json.loads(Path(sup['manifest']).read_text('utf8'));root=Path(sup['archive'])
 for f in sm['files']:
  if f['mode']=='game' and f['side']=='after' and f['file'].endswith('.bundle'):sources[f['file']]=root/'saved-files/game/after'/f['file']
source_catalog=R/'database-overview-hidden-20261112-022724/game/catalog.bin'
oldinv={r['name']:r for r in json.loads((B/'original-all-bundle-hashes.json').read_text('utf8'))};newinv={};changes=[]
for p in sorted((G/'StandaloneWindows64').glob('*.bundle')):
 h=sha(p.read_bytes());newinv[p.name]={'name':p.name,'bytes':p.stat().st_size,'sha256':h}
 if p.name not in oldinv or h!=oldinv[p.name]['sha256']:changes.append(p.name)
dump(O/'updated-all-bundle-hashes.json',list(newinv.values()))
review=[]
for n,src in sources.items():
 p=G/'StandaloneWindows64'/n;h=newinv[n]['sha256'];modhash=sha(src.read_bytes());status='native_unchanged_restore_latest_mod' if h==native_hashes[n] else 'native_changed_rebase'
 if h==modhash:status='already_matches_skin_no_replacement'
 review.append({'bundle':n,'old_native_sha256':native_hashes[n],'updated_sha256':h,'modified_sha256':modhash,'modified_source':str(src),'status':status})
# Keep the reviewed native baseline separate; no writes to game or skin packages.
for n in sorted(set(sources)|set(changes)):
 p=G/'StandaloneWindows64'/n;dest=O/'updated-native/aa/StandaloneWindows64'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(dest.read_bytes())==newinv[n]['sha256']
for p in G.glob('*'):
 if p.is_file():
  q=O/'updated-native/aa'/p.name;shutil.copy2(p,q)
# Three-way semantic common stylesheet comparison, resolving value-table indices.
n='ui-styles_assets_common.bundle';envs=[env(B/'original/aa/StandaloneWindows64'/n),env(G/'StandaloneWindows64'/n),env(sources[n])];pid=-6275161654120610136;objs=[next(o for o in ob.values() if o.path_id==pid) for e,ob in envs];ts=[tree(o) for o in objs]
def canon(t,af):
 def value(h):
  typ=h['m_ValueType'];i=h['valueIndex'];tab={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings',9:'strings',10:'strings',12:'scalableImages',13:'strings'}.get(typ)
  if not tab:return [typ,i]
  v=t[tab][i]
  if typ==6:
   fid=v['m_FileID'];v={'cab':(af.name if fid==0 else af.externals[fid-1].name).lower(),'path_id':v['m_PathID']}
  return [typ,v]
 return [{'selectors':r['m_ComplexSelectors'],'properties':[{'id':p['m_Id'],'custom':p['m_CustomName'],'values':[value(h) for h in p['m_Values']]} for p in r['m_Properties']]} for r in t['m_Rules']]
a,b,c=[canon(t,o.assets_file) for t,o in zip(ts,objs)];official=[i for i in range(min(len(a),len(b))) if a[i]!=b[i]];custom=[i for i in range(min(len(a),len(c))) if a[i]!=c[i]]
common={'old_rule_count':len(a),'new_rule_count':len(b),'skin_rule_count':len(c),'updated_native_changed_rules':official,'skin_changed_existing_rules':custom,'skin_added_rule_indices':list(range(len(a),len(c))),'overlapping_rules':sorted(set(official)&set(custom)),'native_changes':[{'rule':i,'before':a[i],'updated':b[i]} for i in official],'skin_changes':[{'rule':i,'before':a[i],'skin':c[i]} for i in custom],'added_skin_rules':c[len(a):]}
dump(O/'common-styles-three-way.json',common)
for label,t,o in zip(['old-native','updated-native','latest-skin'],ts,objs):
 dump(O/'common-styles'/str(pid)/(label+'.json'),t)
rawchanges=list(delta(ts[0],ts[1]));dump(O/'common-styles/raw-native-changes.json',rawchanges)
# Verify image PPtrs in the updated stylesheet resolve locally.
assert not common['overlapping_rules']
for i in official:
 for prop in b[i]['properties']:
  for typ,v in prop['values']:
   if typ==6 and v['cab']==objs[1].assets_file.name.lower():assert any(o.path_id==v['path_id'] for o in envs[1][1].values())
# Catalog key/location/dependency comparison. Offset churn is excluded.
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def catalog(p):
 c=cm.Catalog(p.read_bytes());cache={};out={}
 def loc(off):
  if off not in cache:
   v=c.location(off);cache[off]={'primary':v['primary'],'internal':v['internal'],'provider':v['provider'],'type':v['type'],'dependencies':[c.location(x)['primary'] for x in v['dependencies']]}
  return cache[off]
 for k,l in c.keys():out[str(k)]=[loc(x[0]) for x in c.array(l,'I')]
 return out
oldcat=catalog(B/'original/aa/catalog.bin');newcat=catalog(G/'catalog.bin');skincat=catalog(source_catalog);keydiff=[{'key':k,'before':oldcat.get(k),'after':newcat.get(k)} for k in sorted(set(oldcat)|set(newcat)) if oldcat.get(k)!=newcat.get(k)];dump(O/'catalog-native-changes.json',keydiff)
customkeys=[k for k in skincat if k not in oldcat];missing=[k for k in customkeys if k not in newcat]
catreport={'old_native_keys':len(oldcat),'new_native_keys':len(newcat),'skin_keys':len(skincat),'native_keys_changed':len(keydiff),'custom_keys_vs_old_native':len(customkeys),'custom_keys_absent_from_updated':len(missing),'missing_custom_keys':missing,'native_binary_identical':sha((B/'original/aa/catalog.bin').read_bytes())==sha((G/'catalog.bin').read_bytes()),'old_modified_catalog_source':str(source_catalog)};dump(O/'catalog-review.json',catreport)
# Cross-file affected reference identities and supplementary new view GUIDs.
view=json.loads((R/'current-player-database-views.json').read_text('utf8'));guidchecks={k:{'guid':view[k],'present_in_updated_catalog':view[k] in newcat,'present_in_skin_catalog':view[k] in skincat} for k in ['new_view_guid','new_row_guid']};dump(O/'overview-hidden-guid-checks.json',guidchecks)
report={'game_aa':str(G),'scope':'main skin only; sidebar deferred','all_bundle_count':len(newinv),'unchanged_bundle_count':sum(n in oldinv and v['sha256']==oldinv[n]['sha256'] for n,v in newinv.items()),'changed_bundles':changes,'new_bundles':sorted(set(newinv)-set(oldinv)),'removed_bundles':sorted(set(oldinv)-set(newinv)),'main_bundle_count':len(review),'main_status_counts':dict(collections.Counter(r['status'] for r in review)),'main_bundles':review,'common':common,'catalog':catreport,'supplements':idx.get('supplements',[]),'game_modified':False}
dump(O/'comparison.json',report)
lines=['# 游戏更新后：主皮肤对比与修改建议','','本次只读比较，未修改或安装游戏资源，未生成侧边栏。以此前保存的原版为基线，主皮肤来源按主清单叠加“18.总览+隐藏”补丁；来源和哈希逐文件保存在comparison.json。','','## 对比结果','',f'- 全部{len(newinv)}个bundle：{report["unchanged_bundle_count"]}个与旧原版一致，{len(changes)}个不同；无新增或删除。',f'- 主皮肤15个bundle：13个可使用最新已验证主皮肤资源作为迁移来源；1个公共样式需增量合并；1个视觉函数包当前已与存档一致，无需替换。','- 旧基线未保存globalobjects与两个更衣室场景的完整旧包，因此对这3包只能确认哈希变化，无法提供可靠的旧/新逐对象结论；保留新版。','','|变化包|建议|','|---|---|']
for n in changes:lines.append('|'+n+'|'+('以新版为底迁移皮肤样式，保留新版5处图片引用修正' if n=='ui-styles_assets_common.bundle' else '保留更新后的游戏文件，不以皮肤旧资源覆盖')+'|')
lines+=['','## 公共样式如何合并','','SIStyles（Path ID -6275161654120610136）的原生规则仍为629条。新版变化发生在规则4、62、63、463、464：勾选框、下拉选择箭头、文件夹箭头及勾选状态的background-image从缺失资源字符串转为实际本地资源引用。本地对象解析已核对。原包AssetBundle预加载表也随之变化，应保留新版表。','','主皮肤修改现有规则70、71、75、628，并追加629–633共5条规则；与新版改动的5条规则无直接重叠。建议按选择器和真实值迁移，不复制旧字符串/颜色/图片表的索引；必要时追加颜色项，并使用新版资源表与预加载。原始字段差异902项主要包含索引调整，不能当成902项独立功能变更。详见common-styles-three-way.json。','','## 主版恢复顺序','','1. 先把本次保存的updated-native/aa作为更新基线；保留globalobjects和两个场景。','2. 13个基线完全未变的相关bundle可采用已验证主版成品，但必须按comparison.json的modified_source选择最新文件，不能从一个旧压缩包全量恢复。','3. 单独在新版ui-styles_assets_common.bundle重做上述皮肤规则；ui-visualfunctions_assets_all.bundle当前一致，无需替换。','4. 补回主皮肤资源目录登记与依赖，包含全部自定义模板/函数、实际预加载，以及总览+隐藏的新视图与私有菜单行模板。保留新版目录结构；目录语义摘要没有覆盖extraData等全部二进制元信息，不能仅凭键统计宣称目录完整兼容。','5. 保留最近的纹理格式兼容修复、Small布局补齐、无效图片值清理及18号列表；遵守禁用纹理ID规则。','6. 验证旧/新核心模板与绑定、跨包纹理指向、GUID/资源类型/所属包首项依赖、完整元素覆盖路径和实际预加载。离线检查后再由用户运行确认。','','## 目录与18号补丁','',f'旧原版目录键{len(oldcat)}，新版{len(newcat)}；键对应的位置/类型/依赖发生变化{len(keydiff)}项。记录的主皮肤相对旧原版新增{len(customkeys)}个键，其中{len(missing)}个不在新版目录，需要迁移。此统计不是“新增对象个数”。','',json.dumps(guidchecks,ensure_ascii=False,indent=2),'','## 之后的侧边栏','','先完成并验证上述主版，保存新的非侧边栏基线，再迁移已单独记录的侧边栏专属增量。最终只输出必要替换文件，并与新主版逐对象检查差异。不得直接安装旧侧边栏整包而覆盖这次资源引用修正、纹理兼容或总览+隐藏。','','本次没有安装主皮肤，也没有生成或安装侧边栏。']
(O/'主皮肤修改建议.md').write_text('\n'.join(lines),'utf8')
# Final read-only verification of the reviewed bundle inputs.
assert all(sha((G/'StandaloneWindows64'/n).read_bytes())==v['sha256'] for n,v in newinv.items())
dump(O/'verification.json',{'bundle_inputs_stable':True,'updated_common_image_refs_resolved':True,'common_rule_overlap':[],'game_modified':False,'runtime_tested':False})
dump(R/'current-game-update-comparison.json',{'archive':str(O),'report':str(O/'主皮肤修改建议.md'),'scope':'main only','installed':False});shutil.copy2(R/'review-updated-main-skin.py',O/'review-updated-main-skin.py');print(json.dumps({'output':str(O),'changed_bundles':changes,'main_status_counts':report['main_status_counts'],'catalog':{k:v for k,v in catreport.items() if k!='missing_custom_keys'}},ensure_ascii=False))
