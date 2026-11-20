from pathlib import Path
import json,sys,os,shutil,hashlib,collections
R=Path.cwd();O=Path(sys.argv[1]);new=json.loads((O/'manifest.json').read_text('utf8'));P=Path(new['previous_ledger']);old=json.loads((P/'manifest.json').read_text('utf8'));prior={(r['mode'],r['bundle']):r for r in old['bundles']};rows=[];files=[]
for r in new['bundles']:
 prev=prior.get((r['mode'],r['bundle']))
 if prev and prev['modified_sha256']==r['modified_sha256']:continue
 files.append({'mode':r['mode'],'bundle':r['bundle'],'previous_sha256':prev.get('modified_sha256') if prev else None,'current_sha256':r['modified_sha256']})
 a={(o['cab'],o['path_id']):o for o in prev['objects']} if prev else {};b={(o['cab'],o['path_id']):o for o in r['objects']}
 for k in sorted(set(a)|set(b)):
  av=a.get(k);bv=b.get(k)
  if av and bv and av['after_raw_sha256']==bv['after_raw_sha256'] and av.get('texture_payload')==bv.get('texture_payload') and av.get('references')==bv.get('references') and av.get('modified_keys')==bv.get('modified_keys'):continue
  ob=bv or av;status='新增到差异清单' if av is None else '恢复至原版' if bv is None else '本次删除对象' if bv['status']=='deleted' else '本次修改对象'
  rows.append({'mode':r['mode'],'bundle':r['bundle'],'name':ob['name'],'path_id':ob['path_id'],'status':status,'previous_detail':os.path.relpath(P/av['detail'],O).replace('\\','/') if av else None,'current_detail':bv['detail'] if bv else None})
lines=['# 相对上一份记录的变化','','上一份：'+str(P),'','本页描述相邻两份修改记录的变化；恢复至原版表示不再出现在相对原版的差异清单中，不等于删除原生对象。原版完整清单见修改总清单.md。','','|版本|bundle|对象|Path ID|本次变化|当前记录|上次记录|','|---|---|---|---|---|---|---|']
for r in rows:
 vals=[r['mode'],r['bundle'],r['name'],r['path_id'],r['status'],f'[查看]({r["current_detail"]}/修改位置.md)' if r['current_detail'] else '已回到原版',f'[查看]({r["previous_detail"]}/修改位置.md)' if r['previous_detail'] else '无'];lines.append('|'+'|'.join(str(v).replace('|','\\|') for v in vals)+'|')
(O/'本次新增修改.md').write_text('\n'.join(lines),'utf8');(O/'changes-since-previous.json').write_text(json.dumps({'previous_ledger':str(P),'changed_bundle_pairs':files,'object_changes':rows},ensure_ascii=False,indent=2),'utf8')
aux=[]
for p in (O/'context').glob('current*.json'):
 try:j=json.loads(p.read_text('utf-8-sig'))
 except Exception:continue
 if not isinstance(j,dict):continue
 for key in ['uid_table','script','generator','verifier']:
  v=j.get(key)
  if not isinstance(v,str):continue
  q=Path(v)
  if q.exists() and q.is_file() and q.resolve().is_relative_to(R.resolve()) and q.suffix in ['.json','.py','.md']:
   dest=O/'context/auxiliary-sources'/(p.stem+'-'+key+'-'+q.name);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest);aux.append({'source':str(q),'saved':str(dest.relative_to(O)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(O/'context/auxiliary-sources.json').write_text(json.dumps(aux,ensure_ascii=False,indent=2),'utf8');p=O/'修改总清单.md';p.write_text('> [本次相对昨天的变化](本次新增修改.md)；未变化对象沿用上次已验证导出，旧记录需保留。\n\n'+p.read_text('utf8'),'utf8');shutil.copy2(R/'record-ledger-daily-delta.py',O/'record-ledger-daily-delta.py');print(json.dumps({'changed_bundle_pairs':len(files),'current_game_changed_bundles':[r['bundle'] for r in files if r['mode']=='current-game'],'object_changes_by_mode':dict(collections.Counter(r['mode'] for r in rows))},ensure_ascii=False))

