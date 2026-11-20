import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
OUT=R/('上方切换对齐原生下拉-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'backup').mkdir();(OUT/'modified').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
before={n:(GAME/n).read_bytes() for n in [W,L]}
for n,data in before.items():assert (SKIN/n).read_bytes()==data;(OUT/'backup'/n).write_bytes(data)
envs={n:UnityPy.load(data) for n,data in before.items()};obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in obs.items()};changes={W:{},L:{}}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
training=next(o.read_typetree() for o in obs[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='Overview1080_Compact_PlayerTrainingOverview')
working_frame=next(r['data'] for r in training['references']['RefIds'] if r.get('data',{}).get('m_TemplateAlias')=='tile-square-2x2')
working_using=next(u for u in training['m_Usings'] if u['alias']=='tile-square-2x2')
assert working_frame['m_Classes']==['height-100-percent','tile-content']
for obj in obs[W].values():
 if obj.type.name!='MonoBehaviour' or obj.peek_name() not in ['OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes']:continue
 d=obj.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
 frame=next(r['data'] for r in rr.values() if r.get('data',{}).get('m_TemplateAlias')=='OverviewVersionTileFrame')
 frame['m_Classes']=copy.deepcopy(working_frame['m_Classes'])
 u=next(u for u in d['m_Usings'] if u['alias']=='OverviewVersionTileFrame');u['path']=working_using['path'];u['asset']=copy.deepcopy(working_using['asset'])
 assert rr[frame['m_SerializedData']['rid']]['data']['templateId']=='OverviewVersionTileFrame'
 assert frame['m_Children']
 changes[W][obj.path_id]=d
assert len(changes[W])==2
co=next(o for o in obs[L].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerReportOverviewComposition-Large');comp=co.read_typetree()
slot=next(c for c in comp['m_gridComponents'] if c['m_elementID']=='PlayerAttributesBlock');native=next(c for c in comp['m_gridComponents'] if c['m_elementID']=='PlayerTrainingOverview')
for key in ['m_isLocked','m_isDynamic','m_features','m_takesFocus']:slot[key]=native[key]
slot['m_maxSize']={'x':20,'y':7}
assert len(slot['m_configDescriptions'])==len(slot['m_gridElementConfigs'])==2
assert all(c['Type']==0 for c in slot['m_gridElementConfigs'])
changes[L][co.path_id]=comp
report={'installed':False,'runtime_verified':False,'same_frame_as_lower_dropdown':working_using['path'],'tile_content_marker':True,'takes_focus':slot['m_takesFocus'],'files':{}}
for n in [W,L]:
 for i,d in changes[n].items():obs[n][i].save_typetree(d)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,o in saved.items():
  if i in changes[n]:assert o.read_typetree()==changes[n][i]
  else:assert sha(o.get_raw_data())==hashes[n][i]
 report['files'][n]={'before':sha(before[n]),'after':sha(data),'changed':list(changes[n]),'unrelated_verified':len(saved)-len(changes[n])}
for n in before:assert (GAME/n).read_bytes()==(SKIN/n).read_bytes()==before[n]
try:
 for n in before:
  data=(OUT/'modified'/n).read_bytes()
  for p in [GAME,SKIN]:(p/n).write_bytes(data);assert (p/n).read_bytes()==data
except Exception:
 for n,data in before.items():
  for p in [GAME,SKIN]:(p/n).write_bytes(data)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(OUT));print(json.dumps(report,indent=2))
