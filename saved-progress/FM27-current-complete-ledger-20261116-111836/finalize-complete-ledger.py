from pathlib import Path
import json,shutil,subprocess,sys,collections
R=Path(__file__).resolve().parent;O=Path(sys.argv[1]);P=Path('C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
shutil.copy2(R/'compare-complete-ledger-update.py',O/'compare-update.py');shutil.copy2(R/'supplement-ledger-internals.py',O/'supplement-ledger-internals.py')
# Tests only read this archive; they do not use or modify the live game.
for label,aa,expected in [('native-baseline',O/'native-baseline/aa','native_bundle_unchanged_reuse_candidate'),('modified-snapshot',O/'snapshot/current-game/aa','matches_archived_modified_bundle_check_native_assumption')]:
 dst=O/'tool-checks'/(label+'.json');r=subprocess.run([str(P),str(O/'compare-update.py'),'--record',str(O),'--updated-aa',str(aa),'--output',str(dst)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 j=json.loads(dst.read_text('utf8'));assert j['modified_bundle_reviews'] and all(x['status']==expected for x in j['modified_bundle_reviews']),[(x['bundle'],x['status']) for x in j['modified_bundle_reviews']]
# Exercise the changed-object branch with a deliberately older common stylesheet input.
testroot=O/'tool-checks/older-native-input/aa';p=testroot/'StandaloneWindows64/ui-styles_assets_common.bundle';p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'saved-progress/FM27-original-diff-20261111-191041/original/aa/StandaloneWindows64'/p.name,p);dst=O/'tool-checks/changed-object-case.json';r=subprocess.run([str(P),str(O/'compare-update.py'),'--record',str(O),'--updated-aa',str(testroot),'--output',str(dst)],capture_output=True,text=True);assert r.returncode==0,r.stderr;j=json.loads(dst.read_text('utf8'));rr=next(x for x in j['modified_bundle_reviews'] if x['bundle']==p.name);assert rr['status']=='native_bundle_changed_review_required' and rr['objects']
ctx=O/'context';lines=['# 近期修改来源索引','','以下为盘点时保存的各功能索引，供解释实际差异；实际变化以对象清单为准。失败试验、已回退或未安装的历史方案不应仅凭索引名称恢复。','','|功能索引|记录状态|拥有者记录|','|---|---|---|']
for p in sorted(ctx.glob('current*.json')):
 try:d=json.loads(p.read_text('utf-8-sig'))
 except Exception:continue
 if not isinstance(d,dict):continue
 state=d.get('status',d.get('installed','见索引'));owner=next(iter((ctx/'owning-records').glob(p.stem+'-manifest.*')),None)
 link=f'[保存的记录]({owner.relative_to(O).as_posix()})' if owner else f'[索引]({p.relative_to(O).as_posix()})';lines.append('|'+p.name+'|'+str(state).replace('|','\\|')[:160]+'|'+link+'|')
(O/'近期修改来源索引.md').write_text('\n'.join(lines),'utf8');m=json.loads((O/'manifest.json').read_text('utf8'));game=[x for x in m['bundles'] if x['mode']=='current-game'];ind=[x for x in m['bundles'] if x['mode']=='independent-main'];pairs=[];gi={x['bundle']:x for x in game}
for row in ind:
 g=gi.get(row['bundle']);pairs.append({'bundle':row['bundle'],'same_as_installed_game':g is not None and g['modified_sha256']==row['modified_sha256']})
(O/'independent-versus-game.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2),'utf8')
summary={'game_bundle_count':len(game),'changed_game_bundles':sum(x['status']!='unchanged' for x in game),'game_object_changes':dict(collections.Counter(o['status'] for x in game for o in x['objects'])),'independent_object_changes':dict(collections.Counter(o['status'] for x in ind for o in x['objects'])),'independent_different_bundles':[x['bundle'] for x in pairs if not x['same_as_installed_game']],'migration_tool_checks':['unchanged_native_baseline','detect_modified_input','changed_native_object_branch'],'errors':m['errors']};(O/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8');p=O/'修改总清单.md';p.write_text('> 当前游戏完整覆盖'+str(len(game))+'个bundle，其中'+str(summary['changed_game_bundles'])+'个变化。[近期功能来源](近期修改来源索引.md) · [统计](summary.json)\n\n'+p.read_text('utf8'),'utf8');print(json.dumps({'archive':str(O),**summary},ensure_ascii=False))
