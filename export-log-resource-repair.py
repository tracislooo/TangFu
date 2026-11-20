from pathlib import Path
import sys,json,hashlib,importlib.util,zipfile,copy
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
AA=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');B=AA/'StandaloneWindows64'
OUT=R/'exports/FM27-log-repair-20261111';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda x:hashlib.sha256(x).hexdigest()
report={'installed':False,'source':str(AA),'files':[],'changes':[]};protected={}
def emit(p,data):
 original=p.read_bytes();protected[p]=sha(original);rel=p.relative_to(AA)
 dest=OUT/'aa'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 report['files'].append({'path':str(rel),'before':sha(original),'after':sha(data)})
for p in sorted(B.glob('*.bundle')):
 if not any(s in p.name for s in ['ui-visualtreeassets','ui-styles','gamemodules_assets_gameworld']):continue
 raw=p.read_bytes();e=UnityPy.load(raw);expected={};original={o.path_id:sha(o.get_raw_data()) for o in e.objects}
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  edits=[]
  for i,r in enumerate(d['m_Rules']):
   for prop in r['m_Properties']:
    if prop['m_Id']!=458753:continue
    for h in prop['m_Values']:
     if h['m_ValueType']==7 and d['strings'][h['valueIndex']]=='none':
      h.update(m_ValueType=1,valueIndex=6);edits.append(i)
  if edits:
   o.save_typetree(d);expected[o.path_id]=d;report['changes'].append({'bundle':p.name,'object':o.path_id,'rules':edits,'fix':'background-image Enum none -> Keyword None'})
 if expected:
  data=e.file.save(packer='lz4');objs={o.path_id:o for o in UnityPy.load(data).objects};assert objs.keys()==original.keys()
  for pid,o in objs.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert sha(o.get_raw_data())==original[pid]
  emit(p,data);print(p.name,len(expected),flush=True)
report['unresolved_function']='c0b4248e39d6df84d978dd6f8a209dcf: absent from current native function bundle; requires matching source resources'
assert all(sha(p.read_bytes())==h for p,h in protected.items())
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'说明.txt').write_text('仅导出，未安装。基于本机2026-11-11当前资源制作，不能保证与对方皮肤版本一致。\n修复背景图片none的序列化类型。playbacktime视觉函数对象缺失，本包未修复。其他对象逐项字节验证未改。\n使用前备份对应原文件；aa目录对应游戏fm_Data/StreamingAssets/aa。本包不包含目录文件。\n长文件名异常：对方需将中场体能列表的自定义视图改成短名，例如中场1；本包不修改个人视图。\n13条压缩纹理回退警告本包未处理，需对方原始背景包才能保证版本一致。\n未进行游戏运行验证，不能据此保证闪退已解决。\n','utf-8-sig')
z=OUT.with_suffix('.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in OUT.rglob('*'):
  if p.is_file():f.write(p,p.relative_to(OUT))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
print(json.dumps({'zip':str(z),'files':len(report['files']),'style_objects':len(report['changes'])}))
