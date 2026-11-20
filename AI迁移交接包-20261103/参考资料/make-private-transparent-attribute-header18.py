from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<current bundle loader>','exec'))
import importlib.util,uuid
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FULL=-930000000001001;SIMPLE=-930000000001003;FRAME=-930000000001007
NEW_FRAME=-940000000002000;NEW_STYLE=-940000000002001
OLD_GUID='57111d625e8d5c47b1a855bfe718e042'
NEW_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm-player-attributes/private-transparent-tile-header-18px/v1').hex
extra_before={folder/GN:(folder/GN).read_bytes() for folder in [GAME,SKIN]}
assert extra_before[GAME/GN]==extra_before[SKIN/GN]
catpath=GAME.parent/'catalog.bin';skincat=SKIN/'catalog.bin'
cat_before=catpath.read_bytes();skin_cat_before=skincat.read_bytes() if skincat.exists() else None
hashpath=catpath.with_suffix('.hash');hash_before=hashpath.read_bytes()
cachepath=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
cache_before=cachepath.read_bytes() if cachepath.exists() else None
ge=UnityPy.load(extra_before[GAME/GN]);go={o.path_id:o for o in ge.objects};gh={i:sha(o.get_raw_data()) for i,o in go.items()}
assert NEW_FRAME not in go and NEW_STYLE not in go
source_frame=go[FRAME].read_typetree();source_sheet=go[source_frame['inlineSheet']['m_PathID']].read_typetree()
doc=copy.deepcopy(source_frame);sheet=copy.deepcopy(source_sheet)
doc['m_Name']='PlayerAttributes_TransparentHeader18_TileFrame';sheet['m_Name']='PlayerAttributes_TransparentHeader18_TileFrame_Style'
doc['inlineSheet']={'m_FileID':0,'m_PathID':NEW_STYLE}
rr={r['rid']:r for r in doc['references']['RefIds']};frame_refs=copy.deepcopy(rr)
# Transparent background fill only: do not change overall opacity, borders or pointer handling.
for i in [1001,1002,1004,1006,1008,1010,1011,1015,1016]:
 override(rr[i]['data'],[prop(458752,color(0,0,0,0)),prop(458753,{'m_ValueType':1,'valueIndex':3})])
for i in [1002,1004,1006,1008]:
 override(rr[i]['data'],[prop(131101,px(0)),prop(131098,px(0)),prop(131093,px(0)),prop(131090,px(0))])
override(rr[1011]['data'],[prop(131087,px(18)),prop(131096,px(18)),prop(131094,px(18)),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('center')),prop(131101,px(0)),prop(131098,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(458768,en('visible'))])
# The arrow is inserted by the native grid into the title controls; allow its original hit box to overflow.
for i in [1015,1016]:
 override(rr[i]['data'],[prop(131087,px(18)),prop(131096,px(0)),prop(131094,px(18)),prop(131074,en('center')),prop(131101,px(0)),prop(131098,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(458768,en('visible'))])
override(rr[1020]['data'],[prop(131087,px(18)),prop(131096,px(0)),prop(131094,px(18)),prop(131074,en('center')),prop(131101,px(0)),prop(131098,px(0)),prop(131093,px(0)),prop(131090,px(0))])
override(rr[1012]['data'],[prop(131101,px(0))])
for i,r in frame_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('Native control or binding changed',i)
assert rr[1010]['data']['m_Classes']==frame_refs[1010]['data']['m_Classes']
assert dimension(rr[1011],131087)==dimension(rr[1011],131096)==dimension(rr[1011],131094)==18
validate_ui(doc,sheet)
# Add an isolated tree and sheet to the same native global bundle.
def addobject(source_obj,pid,data):
 obj=copy.copy(source_obj);obj.path_id=pid;obj.assets_file=source_obj.assets_file
 obj.assets_file.objects[pid]=obj;go[pid]=obj;obj.save_typetree(data);return obj
addobject(go[source_frame['inlineSheet']['m_PathID']],NEW_STYLE,sheet)
addobject(go[FRAME],NEW_FRAME,doc)
ab=next(o for o in go.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();oldmeta=copy.deepcopy(meta)
assert not any(k==NEW_GUID for k,v in meta['m_Container'])
start=len(meta['m_PreloadTable'])
meta['m_PreloadTable'].extend([copy.deepcopy(doc['m_Script']),{'m_FileID':0,'m_PathID':NEW_STYLE},{'m_FileID':0,'m_PathID':NEW_FRAME}])
meta['m_Container'].append((NEW_GUID,{'preloadIndex':start,'preloadSize':3,'asset':{'m_FileID':0,'m_PathID':NEW_FRAME}}));meta['m_Container'].sort(key=lambda kv:kv[0]);ab.save_typetree(meta)
# Both attribute versions use the private frame. No content/style/layout nodes change.
world_changes={}
for pid in [FULL,SIMPLE]:
 d=objects[pid].read_typetree();old=copy.deepcopy(d)
 u=next(u for u in d['m_Usings'] if u['alias']=='OverviewVersionTileFrame')
 assert u['path']==OLD_GUID and u['asset']=={'m_FileID':0,'m_PathID':0}
 u['path']=NEW_GUID
 check=copy.deepcopy(d);next(u for u in check['m_Usings'] if u['alias']=='OverviewVersionTileFrame')['path']=OLD_GUID
 assert check==old
 objects[pid].save_typetree(d);world_changes[pid]=d
# Register the GUID and add it to the actual global preload label, preserving all existing keys.
spec=importlib.util.spec_from_file_location('catalog18',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog(cat_before);oldkeys=dict(cat.keys())
source_location=next(l for l in cat.locations(OLD_GUID) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
cat=cm.Catalog(cat.add_key_location(NEW_GUID,source_location,source_location));new_location=cat.locations(NEW_GUID)[0]
label='GlobalVisualTreeAssetPreload';idx=next(i for i,(k,locs) in enumerate(cat.key_records) if cat.object(k)==label)
key_obj,oldset=cat.key_records[idx];oldlocs=[x[0] for x in cat.array(oldset,'I')]
newset=cat.append(b''.join(struct.pack('<I',p) for p in oldlocs+[new_location]),True)
records=list(cat.key_records);records[idx]=(key_obj,newset)
newtable=cat.append(b''.join(struct.pack('<2I',*r) for r in records),True);struct.pack_into('<I',cat.data,8,newtable)
cat_output=bytes(cat.data);cc=cm.Catalog(cat_output);newkeys=dict(cc.keys())
assert set(newkeys)==set(oldkeys)|{NEW_GUID}
assert all(newkeys[k]==locs for k,locs in oldkeys.items() if k!=label)
assert [x[0] for x in cc.array(newkeys[label],'I')]==oldlocs+[new_location]
assert cc.location(cc.locations(NEW_GUID)[0])['internal']==NEW_GUID
# Binary reload audits: all lower-card templates and all unrelated assets must be byte-identical.
global_output=ge.file.save(packer='lz4');world_output=env.file.save(packer='lz4')
gsaved={o.path_id:o for o in UnityPy.load(global_output).objects};wsaved={o.path_id:o for o in UnityPy.load(world_output).objects}
assert set(gsaved)==set(gh)|{NEW_FRAME,NEW_STYLE};assert set(wsaved)==set(old_hashes)
for i,h in gh.items():
 if i==ab.path_id:assert gsaved[i].read_typetree()==meta
 else:assert sha(gsaved[i].get_raw_data())==h,('Original global asset changed',i)
assert gsaved[NEW_FRAME].read_typetree()==doc;assert gsaved[NEW_STYLE].read_typetree()==sheet
validate_ui(gsaved[NEW_FRAME].read_typetree(),gsaved[NEW_STYLE].read_typetree())
for i,h in old_hashes.items():
 if i in world_changes:assert wsaved[i].read_typetree()==world_changes[i]
 else:assert sha(wsaved[i].get_raw_data())==h,('Unrelated world asset changed',i)
for pid in [FULL,SIMPLE]:
 d=wsaved[pid].read_typetree();validate_ui(d,wsaved[d['inlineSheet']['m_PathID']].read_typetree())
assert all(k in gsaved for k in [FRAME,source_frame['inlineSheet']['m_PathID']])
for p,data in {**before,**extra_before}.items():assert p.read_bytes()==data
assert catpath.read_bytes()==cat_before
assert (skincat.read_bytes() if skincat.exists() else None)==skin_cat_before
for p,h in protected.items():assert sha(p.read_bytes())==h
assert hashpath.read_bytes()==hash_before
assert (cachepath.read_bytes() if cachepath.exists() else None)==cache_before
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('attributes-private-transparent-header18-'+stamp);out.mkdir()
outputs={WN:world_output,GN:global_output}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for name in outputs:(backup/name).write_bytes(({**before,**extra_before})[folder/name])
 if tag=='game':(backup/'catalog.bin').write_bytes(cat_before);(backup/'catalog.hash').write_bytes(hash_before)
 elif skin_cat_before is not None:(backup/'catalog.bin').write_bytes(skin_cat_before)
for name,data in outputs.items():(out/name).write_bytes(data)
(out/'catalog.bin').write_bytes(cat_output)
report={'installed':False,'runtime_verified':False,'private_frame_guid':NEW_GUID,'private_frame_pid':NEW_FRAME,'private_style_pid':NEW_STYLE,'source_frame_guid':OLD_GUID,'source_frame_preserved':True,'title_height':18,'title_min_max_height':[18,18],'background_transparent':True,'whole_element_opacity_unchanged':True,'native_binding_event_and_dropdown_serialized_data_preserved':True,'border_preserved':True,'both_attribute_versions_updated':[FULL,SIMPLE],'lower_cards_and_player_content_unchanged':True,'catalog_global_preload_label_registered':True,'catalog_hash_file_preserved':True,'skin_catalog_previously_existed':skin_cat_before is not None,'before_sha256':{**{str(p):sha(data) for p,data in {**before,**extra_before}.items()},str(catpath):sha(cat_before),str(skincat):sha(skin_cat_before) if skin_cat_before is not None else None},'after_sha256':{**{name:sha(data) for name,data in outputs.items()},'catalog.bin':sha(cat_output)},'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  for name,data in outputs.items():(folder/name).write_bytes(data);assert (folder/name).read_bytes()==data
 catpath.write_bytes(cat_output);skincat.write_bytes(cat_output)
 assert catpath.read_bytes()==skincat.read_bytes()==cat_output
 for p,h in protected.items():
  if p not in [GAME/GN,SKIN/GN,catpath]:assert sha(p.read_bytes())==h
 assert hashpath.read_bytes()==hash_before
 assert (cachepath.read_bytes() if cachepath.exists() else None)==cache_before
except Exception:
 for p,data in {**before,**extra_before}.items():p.write_bytes(data)
 catpath.write_bytes(cat_before)
 if skin_cat_before is None:
  if skincat.exists():skincat.unlink()
 else:skincat.write_bytes(skin_cat_before)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'new_guid':NEW_GUID,'header_height':18,'source_shared_frame_unchanged':True,'both_versions_updated':True,'after_sha256':report['after_sha256']},ensure_ascii=False,indent=2))
