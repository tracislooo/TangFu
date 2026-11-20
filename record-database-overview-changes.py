from pathlib import Path
import sys,ast,json,hashlib,datetime,shutil,xml.etree.ElementTree as ET,importlib.util,gzip
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
P=R/'database-overview-hidden-20261112-022724';B=R/'saved-progress/FM27-original-diff-20261111-191041';I=json.loads((R/'current-original-bundle-diff.json').read_text('utf8'));M=Path(I['archive']);O=R/'saved-progress'/('FM27-18-database-change-record-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));O.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
mod=ast.parse((R/'export-original-bundle-diff.py').read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'export-helpers','exec'))
rows=[];files=[];errors=[]
for mode in ['game','skin']:
 for p in sorted((P/mode).iterdir()):
  if not p.is_file():continue
  before=P/('backup-'+mode)/p.name
  if not before.exists():continue
  for side,src in [('before',before),('after',p)]:
   dst=O/'saved-files'/mode/side/p.name;dst.parent.mkdir(parents=True,exist_ok=True);h=sha(src.read_bytes());shutil.copy2(src,dst);assert sha(dst.read_bytes())==h;files.append({'mode':mode,'side':side,'file':p.name,'sha256':h,'source':str(src)})
  if p.suffix!='.bundle':continue
  ae,aa=env(before);be,bb=env(p);native=B/'original/aa/StandaloneWindows64'/p.name;ce,cc=env(native) if native.exists() else (None,{})
  for key in sorted(set(aa)|set(bb)):
   a=aa.get(key);b=bb.get(key)
   if a and b and a.get_raw_data()==b.get_raw_data():continue
   obj=b or a;pid=str(obj.path_id);d=O/'objects'/mode/p.name/key[0]/pid;at,err1=save_obj(a,d/'before') if a else (None,None);bt,err2=save_obj(b,d/'after') if b else (None,None);c=cc.get(key);ct,err3=save_obj(c,d/'native-original') if c else (None,None)
   if any([err1,err2,err3]):errors.append([str(d),err1,err2,err3])
   changes=list(delta(at,bt)) if at is not None and bt is not None else [{'path':'','op':'add' if a is None else 'remove','note':'Full object preserved in after/before JSON and BIN.'}]
   native_changes=list(delta(ct,bt)) if ct is not None and bt is not None else []
   dump(d/'changes.json',changes);dump(d/'native-to-current-changes.json',native_changes)
   row={'mode':mode,'bundle':p.name,'cab':key[0],'path_id':pid,'name':obj.peek_name(),'type':obj.type.name,'status':'added' if a is None else 'deleted' if b is None else 'modified','field_changes':len(changes),'detail':str(d.relative_to(O)).replace('\\','/'),'before_sha256':sha(a.get_raw_data()) if a else None,'after_sha256':sha(b.get_raw_data()) if b else None,'original_object_found':c is not None};rows.append(row)
   (d/'修改位置.md').write_text('# '+str(row['name'])+'\n\n本次补丁修改前后字段差异：\n\n```json\n'+json.dumps(changes,ensure_ascii=False,indent=2)+'\n```\n\n完整数据见before/after；native-original为此前保存的游戏原版对象。\n','utf8')
 print(mode,'objects exported',sum(r['mode']==mode for r in rows),flush=True)
# Catalog comparison reads saved patch files only.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def catalog(p):
 c=cm.Catalog(p.read_bytes());cache={};out={}
 def location(off):
  if off not in cache:
   r=c.location(off);cache[off]={'primary':r['primary'],'internal':r['internal'],'provider':r['provider'],'type':r['type'],'dependencies':[c.location(x)['primary'] for x in r['dependencies']]}
  return cache[off]
 for k,l in c.keys():out[str(k)]=[location(x[0]) for x in c.array(l,'I')]
 return out
for mode in ['game','skin']:
 a=catalog(P/('backup-'+mode)/'catalog.bin');b=catalog(P/mode/'catalog.bin');changes=[{'key':k,'before':a.get(k),'after':b.get(k)} for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
 with gzip.open(O/(mode+'-catalog-changes.json.gz'),'wt',encoding='utf8') as f:json.dump(changes,f,ensure_ascii=False,indent=2)
for n in ['manifest.json','transaction.json','verification-installed.json','verification-prepared.json','说明.md','add-database-overview-hidden.py','verify-database-overview-hidden.py','current-player-database-views.json']:
 if (P/n).exists():shutil.copy2(P/n,O/('source-'+n))
lines=['# 18.添加总览+隐藏球员列表：修改清单','','仅使用已保存的补丁成品、修改前备份、原版存档和验证记录。没有读取当前游戏目录，未检查更新后的游戏资源。','','- 总览后新增“总览+隐藏”；新表能力/潜力改为隐藏数值，其他总览列保留。','- 两表知识后加入数据-俱乐部的平均评分。','- 效果120→125px，知识160→130px，俱乐部200→170px。','- 记录私有菜单标题模板、原生绑定、资源登记和实际预加载。','- 游戏主版与独立工程分别保存；此补丁未证明已迁移至侧边栏快照，不改写侧边栏的已归档内容。','','本次修改前后位置见changes.json及修改位置.md；与旧游戏原版的差异见native-to-current-changes.json。新增对象完整保存在after.json/.bin；阅读用UXML不等同于可直接导入的原始源代码。完整bundle及catalog两端均在saved-files。','','来源补丁的安装后验证通过，但未运行验证；这里没有把新更新的游戏当作旧原版。','','|版本|bundle|对象|Path ID|状态|字段数|具体修改|','|---|---|---|---|---|---|---|']
for row in rows:
 vals=[row['mode'],row['bundle'],row['name'],row['path_id'],row['status'],row['field_changes'],f'[查看]({row["detail"]}/修改位置.md)'];lines.append('|'+'|'.join(str(v).replace('|','\\|') for v in vals)+'|')
(O/'修改清单.md').write_text('\n'.join(lines),'utf8');dump(O/'manifest.json',{'source_thread':'01a1cf08-2456-7b33-bc20-cd006ee421ac','patch':str(P),'previous_master':str(M),'native_baseline':str(B),'current_game_read':False,'objects':rows,'files':files,'errors':errors});assert not errors
for row in rows:
 for side,k in [('before','before_sha256'),('after','after_sha256')]:
  if row[k]:assert sha((O/row['detail']/(side+'.bin')).read_bytes())==row[k]
dump(O/'verification.json',{'saved_file_copies':len(files),'object_exports':len(rows),'errors':errors,'current_game_read':False})
# Add an explicit supplement, retaining all earlier records and their baselines.
entry={'title':'18.添加总览+隐藏球员列表','archive':str(O),'manifest':str(O/'manifest.json'),'source_thread':'01a1cf08-2456-7b33-bc20-cd006ee421ac','order':'apply after previous master; scoped to changed objects and catalog entries'}
m=json.loads((M/'manifest.json').read_text('utf8'));m.setdefault('supplements',[]).append(entry);dump(M/'manifest.json',m);I.setdefault('supplements',[]).append(entry);dump(R/'current-original-bundle-diff.json',I);dump(R/'current-database-modification-list.json',entry)
link=str(O/'修改清单.md').replace('\\','/');p=M/'修改总清单.md';p.write_text('> 新增补充：[18.添加总览+隐藏球员列表]('+link+')。更新后的游戏文件未读取。\n\n'+p.read_text('utf8'),'utf8');shutil.copy2(R/'record-database-overview-changes.py',O/'record-database-overview-changes.py');print(json.dumps({'archive':str(O),'objects':len(rows),'errors':errors,'current_game_read':False},ensure_ascii=False))
