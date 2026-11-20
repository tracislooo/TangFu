from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<bundle loader>','exec'))
LN='ui-tileslayouts_assets_all.bundle'
sp=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
saved_before=sp.read_bytes();layout=json.loads(saved_before.decode('utf-8-sig'));original_saved=copy.deepcopy(layout)
fullguids={'1f6ebbeeaeba50cbbb57ef2d123b47dc','76cd79feada45acebc482721c1b688da'}
topcount=0
for c in layout['m_gridComponents']:
 istop=any(cfg.get('AssetRef',{}).get('m_AssetGUID') in fullguids for cfg in c['m_gridElementConfigs'])
 h=8 if istop else 2;topcount+=int(istop)
 c['m_location']['y']=0 if istop else 8;c['m_location']['height']=h
 c['m_minSize']['y']=h;c['m_maxSize']['y']=h;c['m_expandToContent']=0
 for cfg in c['m_gridElementConfigs']:cfg['Size']['y']=h
assert topcount==1 and len(layout['m_gridComponents'])==7
# Keep user's chosen modules, widths, menu keys, GUIDs and player-specific configuration.
for c,old in zip(layout['m_gridComponents'],original_saved['m_gridComponents']):
 check=copy.deepcopy(c)
 for key in ['m_location','m_minSize','m_maxSize','m_expandToContent']:check[key]=old[key]
 for cfg,oldcfg in zip(check['m_gridElementConfigs'],old['m_gridElementConfigs']):cfg['Size']=oldcfg['Size']
 assert check==old
assert max(c['m_location']['y']+c['m_location']['height'] for c in layout['m_gridComponents'])==10
saved_output=json.dumps(layout,ensure_ascii=False,separators=(',',':')).encode('utf8')
lbefore={folder/LN:(folder/LN).read_bytes() for folder in [GAME,SKIN]};assert lbefore[GAME/LN]==lbefore[SKIN/LN]
le=UnityPy.load(lbefore[GAME/LN]);lo={o.path_id:o for o in le.objects};hashes={i:sha(o.get_raw_data()) for i,o in lo.items()}
changed={}
# Keep both native version-dropdown descriptions at the requested 8 rows as well.
for pid in [-930000000001004,-930000000001005]:
 d=lo[pid].read_typetree();old=copy.deepcopy(d)
 assert len(d['<Configurations>k__BackingField'])==1
 cfg=d['<Configurations>k__BackingField'][0];assert cfg['AssetRef']['m_AssetGUID'] in fullguids
 cfg['Size']['y']=8
 if d!=old:changed[pid]=d;lo[pid].save_typetree(d)
co=lo[3901662990989568885].read_typetree()
assert all(c['m_location']['height']==(8 if c['m_elementID']=='PlayerAttributesBlock' else 2) for c in co['m_gridComponents'])
assert max(c['m_location']['y']+c['m_location']['height'] for c in co['m_gridComponents'])==10
loutput=le.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(loutput).objects}
assert set(readback)==set(lo)
for i,h in hashes.items():
 if i in changed:assert readback[i].read_typetree()==changed[i]
 else:assert sha(readback[i].get_raw_data())==h,('Unrelated layout asset changed',i)
for p,d in lbefore.items():assert p.read_bytes()==d
assert sp.read_bytes()==saved_before
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('fix-actual-saved-overview-8plus2-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/LN).write_bytes(lbefore[folder/LN])
(out/'backup-custom-layout.json').write_bytes(saved_before);(out/'custom-layout-8plus2.json').write_bytes(saved_output);(out/LN).write_bytes(loutput)
report={'installed':False,'runtime_verified':False,'cause_confirmed':'Saved custom composition still had 7+1 and overrode bundle default 8+2','saved_layout_path':str(sp),'attribute_height':8,'bottom_height':2,'total_height':10,'bottom_modules':6,'user_tile_choices_widths_and_swap_keys_preserved':True,'private_dropdown_descriptions_updated':list(changed),'world_header_and_card_resources_unchanged':True,'before_sha256':{**{str(p):sha(d) for p,d in lbefore.items()},str(sp):sha(saved_before)},'after_sha256':{LN:sha(loutput),'saved_custom_layout':sha(saved_output)}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/LN).write_bytes(loutput);assert (folder/LN).read_bytes()==loutput
 sp.write_bytes(saved_output);assert sp.read_bytes()==saved_output
 for p,h in protected.items():
  if p not in lbefore:assert sha(p.read_bytes())==h
 for p,d in before.items():assert p.read_bytes()==d
except Exception:
 for p,d in lbefore.items():p.write_bytes(d)
 sp.write_bytes(saved_before)
 raise
installed=json.loads(sp.read_text(encoding='utf8'))
assert max(c['m_location']['y']+c['m_location']['height'] for c in installed['m_gridComponents'])==10
assert sum(c['m_location']['height']==8 for c in installed['m_gridComponents'])==1
assert sum(c['m_location']['height']==2 for c in installed['m_gridComponents'])==6
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'actual_custom_layout':[8,2,10],'private_descriptions_updated':list(changed),'saved_layout_sha256':sha(saved_output),'layout_bundle_sha256':sha(loutput)},ensure_ascii=False,indent=2))
