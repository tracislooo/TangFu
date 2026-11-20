from pathlib import Path
import json,hashlib,shutil,os,copy
R=Path.cwd();ctx=json.loads((R/'warning-diff-context.json').read_text('utf8'));B=Path(ctx['base']);O=Path(json.loads((R/'current-warning-bundle-diff.json').read_text('utf8'))['archive']);old=json.loads((B/'manifest.json').read_text('utf8'));new=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();replaced={r['bundle'] for r in new['bundles'] if r['mode']=='main'}
for row in old['bundles']:
 if row['mode']=='main' and row['bundle'] in replaced:continue
 row=copy.deepcopy(row);row['snapshot_source']=old['snapshot'];row['original_record']=str(B)
 for ob in row['objects']:ob['detail']=os.path.relpath(B/ob['detail'],O).replace('\\','/')
 new['bundles'].append(row)
new['parent_record']=str(B);new['sidebar_warning_fix_status']='previous sidebar snapshot retained; fixes not rebased into sidebar';new['source_thread']='01a1bc2d-8684-7f42-963d-ace38f61981c'
for p in (B/'original').rglob('*'):
 if p.is_file():
  q=O/'original'/p.relative_to(B/'original');q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():shutil.copy2(p,q)
shutil.copy2(B/'original-all-bundle-hashes.json',O/'original-all-bundle-hashes.json')
proof=O/'本次修复依据';proof.mkdir(exist_ok=True)
for folder in ['retired-image-cleanup-20261111-192849','game-retired-image-cleanup-20261111-195101','game-retired-image-cleanup-20261111-195226','small-match-texture-fix-20261111-201626']:
 for n in ['manifest.json','combined-manifest.json']:
  p=R/folder/n
  if p.exists():shutil.copy2(p,proof/(folder+'-'+n))
errors=[]
for row in new['bundles']:
 if row.get('original_record'):continue
 for ob in row['objects']:
  for side,k in [('original','before_raw_sha256'),('modified','after_raw_sha256')]:
   if ob[k] and sha(O/ob['detail']/(side+'.bin'))!=ob[k]:errors.append(ob['detail'])
notes='''# 纹理警告修复已合并到修改清单

本次沿用上次保存的真正原版作基线，没有把当前已修复的游戏目录当作原版。

main：当前游戏中已经安装修复的主皮肤，这5包替代旧主清单的同名包记录；其他包沿用上次记录。
independent-main：当前独立工程中这5包另行对比，保留与游戏版本的实际差异，不能假定修复完全同步。
sidebar：保留之前侧边栏存档和对比；尚未把这轮修复迁移进去。以后启用侧边栏要在修复后的最新主版上迁移侧栏差异，不能直接覆盖旧包。

本轮内容：清理无效伪类/废弃空背景节点及非法图片值（具体字段见逐对象记录）；补Small比赛布局副本及预加载；23张自定义或已覆盖纹理转RGBA32，保持尺寸和解码像素。两背景包的最新版本以本次快照为准，不再恢复旧格式。修复事务原始manifest保存在“本次修复依据”。

来源聊天在用户重启后的日志中报告这五类相关警告为0；仍有Refid -2、主题样式表及退出时JobTempAlloc提示，不能标记为所有警告或闪退已修复。本次只更新记录，未启动游戏或修改游戏资源。

完整改动由原版与新快照重新计算，不仅记录历史说明。完整新bundle保存在manifest.snapshot指向的快照，原始基线和旧记录同样保留，不能删除旧存档。二进制数据流随完整bundle保存。
'''
(O/'本次更新说明.md').write_text(notes,'utf8')
lines=['# 最新完整修改清单','','[本次更新说明](本次更新说明.md)；本次5包已替代旧主皮肤同名记录，侧边栏尚未迁移修复。','','|版本|包|对象|类型|Path ID|状态|字段数|记录|','|---|---|---|---|---|---|---|---|']
for row in new['bundles']:
 for ob in row['objects']:
  vals=[row['mode'],row['bundle'],ob['name'],ob['type'],ob['path_id'],ob['status'],ob['field_changes'],f'[查看]({ob["detail"]}/修改位置.md)'];lines.append('|'+'|'.join(str(v).replace('|','\\|') for v in vals)+'|')
(O/'修改总清单.md').write_text('\n'.join(lines),'utf8');(O/'manifest.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),'utf8');(O/'verification-update.json').write_text(json.dumps({'errors':errors,'updated_bundle_pairs':10,'verified':not errors},ensure_ascii=False,indent=2),'utf8');assert not errors
for script in ['compare-future-original-bundles.py','export-warning-updated-diff.py','finalize-warning-diff.py']:shutil.copy2(R/script,O/script)
shutil.copy2(B/'更新迁移说明.md',O/'更新迁移说明.md')
(R/'current-original-bundle-diff.json').write_text(json.dumps({'archive':str(O),'manifest':str(O/'manifest.json'),'parent_record':str(B),'snapshot':new['snapshot'],'source_thread':new['source_thread'],'sidebar_warning_fix_status':new['sidebar_warning_fix_status'],'errors':0},ensure_ascii=False,indent=2),'utf8')
p=B/'修改总清单.md';txt=p.read_text('utf8');p.write_text('> 后续纹理警告修复已更新：[最新完整清单]('+os.path.relpath(O/'修改总清单.md',B).replace('\\','/')+')。本文件保留历史版本。\n\n'+txt,'utf8')
print(json.dumps({'output':str(O),'objects':sum(len(r['objects']) for r in new['bundles']),'errors':errors},ensure_ascii=False))
