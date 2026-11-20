import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
P=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
data=(G/N).read_bytes();assert data==(P/N).read_bytes()
out=R/('概览标题显示校验-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();(out/'backup.bundle').write_bytes(data)
e=UnityPy.load(data);obs={o.path_id:o for o in e.objects};sha=lambda b:hashlib.sha256(b).hexdigest();before={i:sha(o.get_raw_data()) for i,o in obs.items()}
o=next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='Overview1080_AttributesTable_Style');d=o.read_typetree();count=0
for rule in d['m_Rules']:
 for prop in rule['m_Properties']:
  if prop['m_Id']==131080 and prop['m_Values'] and all(h['m_ValueType']==7 and d['strings'][h['valueIndex']]=='none' for h in prop['m_Values']):prop['m_Id']=131081;count+=1
assert count==6
o.save_typetree(d);new=e.file.save(packer='lz4');(out/N).write_bytes(new)
for obj in UnityPy.load(new).objects:
 if obj.path_id==o.path_id:assert obj.read_typetree()==d
 else:assert sha(obj.get_raw_data())==before[obj.path_id]
for p in [G,P]:assert (p/N).read_bytes()==data
for p in [G,P]:(p/N).write_bytes(new);assert sha((p/N).read_bytes())==sha(new)
(out/'manifest.json').write_text(json.dumps({'display_none_title_nodes':count,'after_sha256':sha(new),'runtime_verified':False},indent=2),encoding='utf-8')
print('Verified six title rules use the game version display:none property. Final SHA256:',sha(new))
