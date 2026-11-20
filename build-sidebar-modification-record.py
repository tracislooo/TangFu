from pathlib import Path
import json,hashlib,shutil,datetime,ast,sys,os
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy;import xml.etree.ElementTree as ET
B=R/'saved-progress/FM27-original-diff-20261111-191041';old=json.loads((B/'manifest.json').read_text('utf8'));S=Path(old['snapshot']);T=R/'sidebar-updated-replacement-20261111-040334';O=sorted((R/'saved-progress').glob('FM27-sidebar-change-record-*'))[-1];O.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
# Reuse the export helpers without executing the earlier audit.
mod=ast.parse((R/'export-original-bundle-diff.py').read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))],type_ignores=[]),'audit-helpers','exec'))
checks=[]
for p in (T/'packages').iterdir():
 if not p.is_file():continue
 q=S/'sidebar/aa'/(p.name if p.name.startswith('catalog.') else 'StandaloneWindows64/'+p.name)
 # Record later snapshot differences without replacing it with the earlier installer.
 checks.append({'file':p.name,'sha256':sha(p.read_bytes()),'matches_saved_snapshot':sha(p.read_bytes())==sha(q.read_bytes()),'saved_snapshot_sha256':sha(q.read_bytes())})
rows=[r for r in old['bundles'] if r['mode']=='sidebar'];man={**old,'output':str(O),'bundles':rows,'snapshot':str(S),'user_current_assessment':'User reports latest sidebar should be working normally; no new runtime test performed','sidebar_version':str(T),'errors':[]}
# Copy existing exports into this independent record.
shutil.copytree(B/'sidebar',O/'sidebar',dirs_exist_ok=True)
shutil.copytree(B/'original',O/'original',dirs_exist_ok=True)
shutil.copytree(S/'sidebar',O/'modified-sidebar',dirs_exist_ok=True)
for n in ['original-all-bundle-hashes.json','texture-payload-changes.json','更新迁移说明.md']:
 shutil.copy2(B/n,O/n)
summary=['# 侧边栏整版修改清单','','最新版来源：20261111-185153侧边栏快照。相对040334安装包，5文件一致，gameworld含后续差异；本清单保留较晚快照。','','用户当前反馈：最新版应该没有问题。本次未运行游戏。','','[侧边栏专属改动](侧边栏专属修改清单.md) · [使用说明](README.md)','','|包|对象|类型|Path ID|状态|字段数|具体位置|','|---|---|---|---|---|---|---|']
for r in rows:
 for ob in r['objects']:
  vals=[r['bundle'],ob['name'],ob['type'],ob['path_id'],ob['status'],ob['field_changes'],f'[查看]({ob["detail"]}/修改位置.md)'];summary.append('|'+'|'.join(str(v).replace('|','\\|') for v in vals)+'|')
(O/'侧边栏完整修改清单.md').write_text('\n'.join(summary),'utf8')
deltas=[];lines=['# 侧边栏专属修改清单','','基准：该侧边栏安装前同时保存的non-sidebar-backup。此处提取040334安装时的侧边栏增量；较晚快照gameworld另有变化，完整最新内容见整版清单。','','|包|对象|Path ID|状态|字段数|具体位置|','|---|---|---|---|---|---|']
for p in sorted((T/'packages').glob('*.bundle')):
 before=T/'non-sidebar-backup'/p.name;ae,aa=env(before);be,bb=env(p)
 for k in sorted(set(aa)|set(bb)):
  a=aa.get(k);b=bb.get(k)
  if a and b and a.get_raw_data()==b.get_raw_data():continue
  obj=b or a;pid=str(obj.path_id);folder=O/'sidebar-only'/p.name/k[0]/pid;at,err1=save_obj(a,folder/'original') if a else (None,None);bt,err2=save_obj(b,folder/'modified') if b else (None,None);assert not err1 and not err2,(err1,err2)
  changes=list(delta(at,bt)) if at is not None and bt is not None else [];dump(folder/'changes.json',changes)
  rec={'bundle':p.name,'name':obj.peek_name(),'path_id':pid,'status':'added' if a is None else 'deleted' if b is None else 'modified','field_changes':len(changes),'detail':str(folder.relative_to(O)).replace('\\','/')};deltas.append(rec)
  (folder/'修改位置.md').write_text('# '+str(rec['name'])+'\n\n```json\n'+json.dumps(changes,ensure_ascii=False,indent=2)+'\n```\n','utf8')
  vals=[p.name,rec['name'],pid,rec['status'],len(changes),f'[查看]({rec["detail"]}/修改位置.md)'];lines.append('|'+'|'.join(str(v).replace('|','\\|') for v in vals)+'|')
shutil.copytree(T/'packages',O/'sidebar-only-bundles');shutil.copytree(T/'non-sidebar-backup',O/'sidebar-only-baseline')
for n in ['manifest.json','transaction.json','migration-source.py']:
 if (T/n).exists():shutil.copy2(T/n,O/('sidebar-source-'+n))
(O/'侧边栏专属修改清单.md').write_text('\n'.join(lines),'utf8');dump(O/'sidebar-only-deltas.json',deltas)
(O/'README.md').write_text('''# 独立侧边栏修改记录

侧边栏完整修改清单.md：整个侧边栏版与上次用户确认的游戏原版逐对象对比，涵盖UXML、样式、布局、函数、字体、图片及其他对象。original/aa保留原版，modified-sidebar/aa保留侧边栏整版，sidebar/保留完整对象导出及字段前后值。UXML为阅读用重建，准确绑定及覆盖以JSON/二进制为准。

侧边栏专属修改清单.md：最新版侧边栏相对安装前主皮肤的增量，便于以后在新主版上迁移侧边栏。sidebar-only-baseline和sidebar-only-bundles保留该差异的两端，包含目录文件。完整原版目录差异见sidebar/catalog-changes.json.gz。

当前用户反馈最新版应该没有问题。未重新启动游戏验证。本记录采用较晚的185153侧边栏快照。相对040334安装包有5文件一致，仅gameworld不同；不是以旧安装包替换较晚快照。

本次只生成清单，不修改游戏或皮肤。此前聊天的纹理警告修复没有证据已合并至这份侧边栏快照；这是版本内容记录，不表示这份侧边栏当前存在故障。以后需要同时保留那些公共修复时，在新主版上重新迁移sidebar-only增量，禁止旧整包覆盖。

未来更新先比较原始基线与新版原包，再按记录迁移字段及新增对象。官方改动的字段、结构、ID、GUID、catalog/预加载依赖需适配。compare-future-original-bundles.py可只读生成更新对比报告。两个原始基准不同，整版清单和侧栏专属增量不可混用。
''','utf8')
man['snapshot']=str(O/'modified-sidebar');dump(O/'manifest.json',man);shutil.copy2(R/'compare-future-original-bundles.py',O/'compare-future-original-bundles.py')
verify={'latest_sidebar_matches_saved_snapshot':checks,'full_object_records':sum(len(r['objects']) for r in rows),'sidebar_only_objects':len(deltas),'decode_errors':0,'runtime_tested_this_task':False};dump(O/'verification.json',verify);dump(R/'current-sidebar-modification-list.json',{'archive':str(O),'manifest':str(O/'manifest.json'),'sidebar_version':str(T),'verified':True,'user_current_assessment':man['user_current_assessment']});print(json.dumps({'archive':str(O),**verify},ensure_ascii=False))


