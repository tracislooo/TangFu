from pathlib import Path
import sys,json,hashlib,datetime,shutil,gzip,html,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('G:\\Doc\\ChatGPT\\New project\\saved-progress\\FM27-original-diff-20261111-191041\\original\\aa');snap=Path('G:\\Doc\\ChatGPT\\New project\\saved-progress\\FM27-warning-fix-snapshot-20261111-220801')
O=R/'saved-progress'/('FM27-warning-updated-diff-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));O.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def norm(v):
 if isinstance(v,(bytes,bytearray)):return {'binary_bytes':len(v),'sha256':sha(v)}
 if isinstance(v,dict):return {str(k):norm(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [norm(x) for x in v]
 return v
MISSING=object()
def delta(a,b,path=''):
 if a==b:return
 if isinstance(a,dict) and isinstance(b,dict):
  for k in sorted(set(a)|set(b)):
   p=path+'/'+k.replace('~','~0').replace('/','~1')
   if k not in a:yield {'path':p,'op':'add','after':b[k]}
   elif k not in b:yield {'path':p,'op':'remove','before':a[k]}
   else:yield from delta(a[k],b[k],p)
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
  for i,(x,y) in enumerate(zip(a,b)):yield from delta(x,y,path+'/'+str(i))
 else:yield {'path':path,'op':'replace','before':a,'after':b}
def env(p):
 e=UnityPy.load(str(p));d={}
 for o in e.objects:
  k=(o.assets_file.name.lower(),o.path_id)
  if k in d:raise ValueError('duplicate object identity')
  d[k]=o
 return e,d
def tree(o):return norm(o.read_typetree())
def export_uxml(t,p):
 if 'm_VisualTree' not in t:return
 refs={r['rid']:r for r in t.get('references',{}).get('RefIds',[])}
 root=ET.Element('UXML-inspection',{'name':t.get('m_Name',''),'note':'Inspection reconstruction; authoritative serialized data is in adjacent JSON. Not directly importable.'})
 for u in t.get('m_Usings',[]):ET.SubElement(root,'Template',{'alias':str(u.get('alias','')),'path':str(u.get('path',''))})
 def visit(rid,parent,seen):
  if rid in seen:return
  seen=seen|{rid};r=refs.get(rid,{});d=r.get('data',{});tag=d.get('m_FullTypeName') or 'TemplateInstance'
  node=ET.SubElement(parent,tag,{'rid':str(rid),'element-id':str(d.get('m_Id','')),'class':' '.join(d.get('m_Classes',[])),'rule-index':str(d.get('m_RuleIndex',-1))})
  if d.get('m_TemplateAlias'):node.set('template',d['m_TemplateAlias'])
  sd=refs.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  for key in ['name','text','bindingPath','templateId']:
   if isinstance(sd.get(key),(str,int,float)):node.set(key,str(sd[key]))
  data=ET.SubElement(node,'SerializedData');data.text=json.dumps(sd,ensure_ascii=False)
  if d.get('m_SerializedDataOverride'):ET.SubElement(node,'SerializedOverrides').text=json.dumps(d['m_SerializedDataOverride'],ensure_ascii=False)
  for c in d.get('m_Children',[]):visit(c['rid'],node,seen)
 visit(t['m_VisualTree']['rid'],root,set());ET.indent(root);ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
def save_obj(o,base):
 base.parent.mkdir(parents=True,exist_ok=True);raw=o.get_raw_data();base.with_suffix('.bin').write_bytes(raw)
 try:
  t=tree(o);dump(base.with_suffix('.json'),t);export_uxml(t,base.with_suffix('.uxml'));return t,None
 except Exception as ex:return None,str(ex)
manifest={'original_source':str(G),'user_confirmed_original':True,'snapshot':str(snap),'output':str(O),'created':datetime.datetime.now().isoformat(),'bundles':[],'errors':[]}
allnames=sorted({p.name for p in (G/'StandaloneWindows64').glob('*.bundle')}|{p.name for mode in ['main','independent-main'] for p in (snap/mode/'aa/StandaloneWindows64').glob('*.bundle')})
original_hashes=[]
for n in allnames:
 p=G/'StandaloneWindows64'/n
 original_hashes.append({'name':n,'sha256':sha(p.read_bytes()) if p.exists() else None,'size':p.stat().st_size if p.exists() else None})
dump(O/'original-all-bundle-hashes.json',original_hashes)
for mode in ['main','independent-main']:
 for p in sorted((snap/mode/'aa/StandaloneWindows64').glob('*.bundle')):
  n=p.name;q=G/'StandaloneWindows64'/n;rel=Path('StandaloneWindows64')/n;bk=O/'original/aa'/rel;bk.parent.mkdir(parents=True,exist_ok=True)
  if q.exists() and not bk.exists():shutil.copy2(q,bk);assert sha(bk.read_bytes())==sha(q.read_bytes())
  row={'mode':mode,'bundle':n,'original_sha256':sha(q.read_bytes()) if q.exists() else None,'modified_sha256':sha(p.read_bytes()),'objects':[]}
  manifest['bundles'].append(row)
  if row['original_sha256']==row['modified_sha256']:row['status']='identical';continue
  print(mode,n,flush=True)
  try:
   ne,no=env(p);oe,oo=env(q) if q.exists() else (None,{})
   folder=O/mode/n
   for key in sorted(set(oo)|set(no)):
    a=oo.get(key);b=no.get(key)
    if a and b and a.get_raw_data()==b.get_raw_data():continue
    obj=b or a;pid=str(obj.path_id);cab=key[0];identity=cab+'/'+pid
    try:name=obj.peek_name() or obj.type.name
    except:name=obj.type.name
    rec={'cab':cab,'path_id':pid,'name':name,'type':obj.type.name,'status':'added' if not a else 'deleted' if not b else 'modified','before_raw_sha256':sha(a.get_raw_data()) if a else None,'after_raw_sha256':sha(b.get_raw_data()) if b else None}
    row['objects'].append(rec);base=folder/cab/pid
    at,ae=save_obj(a,base/'original') if a else (None,None);bt,be=save_obj(b,base/'modified') if b else (None,None)
    if ae or be:rec['decode_errors']={'original':ae,'modified':be};manifest['errors'].append({'identity':identity,'bundle':n,'mode':mode,'error':rec['decode_errors']})
    changes=list(delta(at,bt)) if at is not None and bt is not None else []
    dump(base/'changes.json',changes);rec['field_changes']=len(changes);rec['detail']=str(base.relative_to(O));rec['semantic_equal']=at==bt if at is not None and bt is not None else None
    text=['# '+str(name),'',f'状态：{rec["status"]}；类型：{rec["type"]}；Path ID：{pid}','','字段路径使用 JSON Pointer；数组长度改变时完整记录该数组前后值。完整数据见 original.json / modified.json；二进制见 .bin。','']
    for c in changes:
     text.extend(['## '+c['path'],'','```json',json.dumps(c,ensure_ascii=False,indent=2),'```',''])
    (base/'修改位置.md').write_text('\n'.join(text),'utf8')
   row['status']='objects_changed' if row['objects'] else 'packaging_only'
   row['original_externals']={a.name:[x.path for x in a.externals] for a in oe.assets} if oe else {};row['modified_externals']={a.name:[x.path for x in a.externals] for a in ne.assets}
  except Exception as ex:row['status']='error';row['error']=str(ex);manifest['errors'].append({'mode':mode,'bundle':n,'error':str(ex)})
  dump(O/'manifest.partial.json',manifest)
# catalog and settings are saved separately; binary catalog must be semantically merged after updates.
for p in G.glob('*'):
 if p.is_file():
  dst=O/'original/aa'/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
for p in list(R.glob('current-*.json'))+[R/'reserved-texture-ids.json',R/'AGENTS.md']:
 if p.exists():shutil.copy2(p,O/p.name)
lines=['# 当前修改版与游戏原版逐对象对比','','原版来源：'+str(G),'','修改版来源：'+str(snap),'','主皮肤与侧边栏分别对比。仅封装不同、对象内容相同的包单独标注。新增和删除对象同样完整导出。','', '|版本|bundle|状态|差异对象数|','|---|---|---|---|']
for r in manifest['bundles']:lines.append(f'|{r["mode"]}|{r["bundle"]}|{r["status"]}|{len(r["objects"])}|')
lines+=['','## 全部差异对象','','|版本|包|对象名|类型|Path ID|状态|字段数|详细记录|','|---|---|---|---|---|---|---|---|']
for r in manifest['bundles']:
 for o in r['objects']:lines.append('|'+ '|'.join(str(x).replace('|','\\|') for x in [r['mode'],r['bundle'],o['name'],o['type'],o['path_id'],o['status'],o['field_changes'],f'[查看]({o["detail"]}/修改位置.md)'])+'|')
(O/'修改总清单.md').write_text('\n'.join(lines),'utf8')
manifest['completed']=True;dump(O/'manifest.json',manifest)
dump(R/'current-warning-bundle-diff.json',{'archive':str(O),'manifest':str(O/'manifest.json'),'snapshot':str(snap),'errors':len(manifest['errors'])})
print(json.dumps({'output':str(O),'bundles':len(manifest['bundles']),'objects':sum(len(r['objects']) for r in manifest['bundles']),'errors':len(manifest['errors'])},ensure_ascii=False),flush=True)
