import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
OUT=R/('概览单页原生模块菜单-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'backup').mkdir();(OUT/'modified').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();before={n:(GAME/n).read_bytes() for n in [W,L]}
for n,data in before.items():assert data==(SKIN/n).read_bytes();(OUT/'backup'/n).write_bytes(data)
envs={n:UnityPy.load(b) for n,b in before.items()};obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in obs.items()};changes={W:{},L:{}}
old=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':old(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return old(v,n,w,c)
TypeTreeHelper.write_value=write
co=next(o for o in obs[L].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerReportOverviewComposition-Large');d=co.read_typetree()
slot=next(c for c in d['m_gridComponents'] if c['m_elementID']=='PlayerAttributesBlock')
assert len(slot['m_gridElementConfigs'])==2
full=copy.deepcopy(slot['m_gridElementConfigs'][0]);full_id=full['Description']['m_PathID']
alternates=[copy.deepcopy(c) for c in slot['m_gridElementConfigs']]
# The configured list is the active carousel. A swap dropdown selects from the set instead.
slot['m_gridElementConfigs']=[full];slot['m_configDescriptions']=[copy.deepcopy(full['Description'])];slot['m_configDescriptionKeys']=[]
slot['m_isLocked']=0;slot['m_takesFocus']=0;slot['m_isDynamic']=0
changes[L][co.path_id]=d
ts=next(o.read_typetree() for o in obs[L].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerReportOverviewTileSet')
available={p['m_PathID'] for p in ts['m_gridElementDescriptions']}
assert all(c['Description']['m_PathID'] in available for c in alternates)
assert all(len(obs[L][c['Description']['m_PathID']].read_typetree()['<Configurations>k__BackingField'])==1 for c in alternates)
pageobj=obs[W][7857044477279960178];page=pageobj.read_typetree();matches=[]
for r in page['references']['RefIds']:
 a=r.get('data',{})
 if a.get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID')==1615455816372668659:
  a['IsCustomisable']=1;a['IsCustomisable_UxmlAttributeFlags']=1;matches.append(r['rid'])
assert len(matches)==1
changes[W][pageobj.path_id]=page
for n in [W,L]:
 for i,doc in changes[n].items():obs[n][i].save_typetree(doc)
 data=envs[n].file.save(packer='lz4');(OUT/'modified'/n).write_bytes(data)
 saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(obs[n])
 for i,o in saved.items():
  if i in changes[n]:assert o.read_typetree()==changes[n][i]
  else:assert sha(o.get_raw_data())==hashes[n][i]
for n,data in before.items():assert (GAME/n).read_bytes()==(SKIN/n).read_bytes()==data
try:
 for n in before:
  data=(OUT/'modified'/n).read_bytes()
  for p in [GAME,SKIN]:(p/n).write_bytes(data);assert (p/n).read_bytes()==data
except Exception:
 for n,data in before.items():
  for p in [GAME,SKIN]:(p/n).write_bytes(data)
 raise
report={'installed':True,'runtime_verified':False,'active_page_count':1,'native_swap_menu_enabled':True,'default_description':full_id,'available_variants':[c['Description']['m_PathID'] for c in alternates],'files':{n:{'before':sha(before[n]),'after':sha((GAME/n).read_bytes()),'changed':list(changes[n]),'unrelated_verified':len(obs[n])-len(changes[n])} for n in before}}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(str(OUT));print(json.dumps(report,indent=2))
