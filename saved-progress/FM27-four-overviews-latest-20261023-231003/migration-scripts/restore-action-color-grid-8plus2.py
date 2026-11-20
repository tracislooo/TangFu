from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939;LN='ui-tileslayouts_assets_all.bundle';CP=3901662990989568885
layout_before={folder/LN:(folder/LN).read_bytes() for folder in [GAME,SKIN]}
assert layout_before[GAME/LN]==layout_before[SKIN/LN]
le=UnityPy.load(layout_before[GAME/LN]);lo={o.path_id:o for o in le.objects};lh={i:sha(o.get_raw_data()) for i,o in lo.items()}
comp=lo[CP].read_typetree();oldcomp=copy.deepcopy(comp)
assert comp['m_Name']=='PlayerReportOverviewComposition-Large'
for c in comp['m_gridComponents']:
 attr=c['m_elementID']=='PlayerAttributesBlock';height=8 if attr else 2
 c['m_location']['y']=0 if attr else 8;c['m_location']['height']=height
 c['m_minSize']['y']=height;c['m_maxSize']['y']=height;c['m_expandToContent']=0
 for cfg in c['m_gridElementConfigs']:cfg['Size']['y']=height
assert len(comp['m_gridComponents'])==7
for c in comp['m_gridComponents']:
 h=8 if c['m_elementID']=='PlayerAttributesBlock' else 2
 assert c['m_location']['height']==c['m_minSize']['y']==c['m_maxSize']['y']==h
 assert all(cfg['Size']['y']==h for cfg in c['m_gridElementConfigs'])
assert max(c['m_location']['y']+c['m_location']['height'] for c in comp['m_gridComponents'])==10
# Only heights/y positions and expansion constraints are allowed to change in the composition.
for new,old in zip(comp['m_gridComponents'],oldcomp['m_gridComponents']):
 check=copy.deepcopy(new)
 for key in ['m_location','m_minSize','m_maxSize','m_expandToContent']:check[key]=old[key]
 for cfg,orig in zip(check['m_gridElementConfigs'],old['m_gridElementConfigs']):cfg['Size']=orig['Size']
 assert check==old
lo[CP].save_typetree(comp);layout_output=le.file.save(packer='lz4')
lsaved={o.path_id:o for o in UnityPy.load(layout_output).objects}
assert set(lsaved)==set(lo)
for i,h in lh.items():
 if i==CP:assert lsaved[i].read_typetree()==comp
 else:assert sha(lsaved[i].get_raw_data())==h
# Restore Action colors from the actual pre-Touch-Bar backup, retaining compact geometry.
doc=objects[HP].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(rr)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
pre=R/'header-touch-bar-style-20261018-152216/backup-game'/WN
pe=UnityPy.load(str(pre));po={o.path_id:o for o in pe.objects};pd=po[HP].read_typetree();pr={r['rid']:r for r in pd['references']['RefIds']};ps=po[pd['inlineSheet']['m_PathID']].read_typetree()
action=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
grad=next(c['rid'] for c in rr[action]['data']['m_Children'] if rr[c['rid']]['data']['m_FullTypeName']=='SI.Bindable.SIGradient')
for i in [action,grad]:
 ix=pr[i]['data']['m_RuleIndex']
 if ix<0:rr[i]['data']['m_RuleIndex']=-1;continue
 rulecopy=copy.deepcopy(ps['m_Rules'][ix])
 for p in rulecopy['m_Properties']:
  for h in p['m_Values']:
   if h['m_ValueType']==1:continue
   pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ps[pool][h['valueIndex']]))
   h['valueIndex']=len(sheet[pool])-1
 rr[i]['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rulecopy)
override(rr[action]['data'],[prop(131087,px(26)),prop(131096,px(26)),prop(131094,px(26)),prop(131074,en('center')),prop(262147,px(6)),prop(131099,px(10)),prop(131100,px(10))])
# No inline gray fill/border and the native gradient is visible again.
action_props=sheet['m_Rules'][rr[action]['data']['m_RuleIndex']]['m_Properties']
assert not any(p['m_Id'] in [458752,262146] for p in action_props)
if rr[grad]['data']['m_RuleIndex']>=0:
 assert not any(p['m_Id']==131081 and any(h['m_ValueType']!=1 and sheet[poolmap[h['m_ValueType']]][h['valueIndex']]=='none' for h in p['m_Values']) for p in sheet['m_Rules'][rr[grad]['data']['m_RuleIndex']]['m_Properties'])
assert {i for i in oldrefs if rr[i]!=oldrefs[i]}=={action,grad}
for i in [action,grad]:
 r=copy.deepcopy(rr[i]);r['data']['m_RuleIndex']=oldrefs[i]['data']['m_RuleIndex'];assert r==oldrefs[i]
validate_ui(doc,sheet)
objects[HP].save_typetree(doc);objects[sid].save_typetree(sheet)
world_output=env.file.save(packer='lz4');wsaved={o.path_id:o for o in UnityPy.load(world_output).objects}
assert set(wsaved)==set(objects)
for i,h in old_hashes.items():
 if i in [HP,sid]:assert wsaved[i].read_typetree()=={HP:doc,sid:sheet}[i]
 else:assert sha(wsaved[i].get_raw_data())==h
validate_ui(wsaved[HP].read_typetree(),wsaved[sid].read_typetree())
all_before={**before,**layout_before}
for p,d in all_before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('native-action-color-overview-8plus2-'+stamp);out.mkdir()
outputs={WN:world_output,LN:layout_output}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for name in outputs:(backup/name).write_bytes(all_before[folder/name])
for name,data in outputs.items():(out/name).write_bytes(data)
report={'installed':False,'runtime_verified':False,'action_color':'Native primary button classes and native gradient restored from pre-Touch-Bar backup','color_reference':str(pre),'grid_composition':CP,'grid_height':10,'attribute_height':8,'bottom_row_y':8,'bottom_height':2,'bottom_card_count':6,'all_configuration_sizes_updated':True,'other_breakpoints_preserved':True,'changed_assets':{WN:[HP,sid],LN:[CP]},'before_sha256':{str(p):sha(d) for p,d in all_before.items()},'after_sha256':{name:sha(d) for name,d in outputs.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:
   for name,data in outputs.items():(folder/name).write_bytes(data);assert (folder/name).read_bytes()==data
  for p,h in protected.items():
   if p not in layout_before:assert sha(p.read_bytes())==h
 except Exception:
  for p,d in all_before.items():p.write_bytes(d)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'after_sha256':report['after_sha256'],'grid':[8,2,10]},ensure_ascii=False,indent=2))
