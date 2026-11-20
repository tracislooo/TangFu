from pathlib import Path
import importlib.util,json,hashlib,gzip
R=Path.cwd();O=sorted((R/'saved-progress').glob('FM27-original-diff-*'))[-1];snap=Path(json.loads((R/'current-main-sidebar-snapshot.json').read_text('utf8'))['archive']);G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa')
s=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
def load(p):
 c=mod.Catalog(p.read_bytes());cache={};out={}
 def loc(off):
  if off not in cache:
   d=c.location(off);cache[off]={'primary':d['primary'],'internal':d['internal'],'provider':d['provider'],'type':list(d['type']),'dependencies':[c.location(x)['primary'] for x in d['dependencies']]}
  return cache[off]
 for k,l in c.keys():out[str(k)]=[loc(x[0]) for x in c.array(l,'I')]
 return out
before=load(G/'catalog.bin')
for mode in ['main','sidebar']:
 after=load(snap/mode/'aa/catalog.bin');changes=[]
 for k in sorted(set(before)|set(after)):
  if before.get(k)!=after.get(k):changes.append({'key':k,'status':'added' if k not in before else 'deleted' if k not in after else 'modified','before':before.get(k),'after':after.get(k)})
 p=O/mode/'catalog-changes.json.gz';p.parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(p,'wt',encoding='utf8') as f:json.dump(changes,f,ensure_ascii=False,indent=2)
 (O/mode/'catalog-说明.md').write_text(f'# Addressables目录变更\n\n共{len(changes)}条键对应的位置、资源类型或依赖发生变化。详见catalog-changes.json.gz；已排除纯二进制偏移变化。\n\n原版和修改版完整catalog均已保存。extraData和内部哈希等二进制元信息不包含在本语义摘要中，迁移必须根据新版目录结构重新生成和验证，不能直接覆盖旧catalog。\n','utf8')
 print(mode,'catalog changes',len(changes),flush=True)
