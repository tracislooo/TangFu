from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
out=Path('highlight-top-bottom-redesign-20261104-020344');results=[]
for tag,prefix in [('game',''),('skin','skin-')]:
 bn='ui-tileslayouts_assets_all.bundle';e=UnityPy.load(str(out/(prefix+bn)));os={o.path_id:o for o in e.objects}
 for name in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:
  t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);blocks=t['m_gridComponents'];assert len(blocks)==9
  assert [(b['m_location']['x'],b['m_location']['y'],b['m_location']['width'],b['m_location']['height']) for b in blocks]==[(0,0,4,6),(4,0,4,6),(8,0,8,6),(16,0,4,6),(20,0,4,6),(0,6,6,4),(6,6,6,4),(12,6,6,4),(18,6,6,4)]
  reg=os[t['m_gridElementSet']['m_PathID']].read_typetree();ids={p['m_PathID'] for p in reg['m_gridElementDescriptions']}
  for b in blocks:
   cfg=b['m_gridElementConfigs'][0];dp=cfg['Description']['m_PathID'];assert dp in ids;desc=os[dp].read_typetree();assert b['m_elementID']==desc['<ID>k__BackingField'];assert cfg['Size']=={'x':b['m_location']['width'],'y':b['m_location']['height']};assert cfg in desc['<Configurations>k__BackingField']
  for group in reg['m_tileGroups']:
   for p in group['m_tiles']:assert p['m_PathID'] in ids
  for p in reg['m_gridElementDescriptions']:
   d=os[p['m_PathID']].read_typetree()
   if d['<ID>k__BackingField'].startswith('HighlightRedesign'):continue
   assert any(c['Size']=={'x':6,'y':4} for c in d['<Configurations>k__BackingField']),d['m_Name']
  results.append({'variant':tag,'layout':name,'9_slots':True,'all_default_configs_resolve':True,'full_native_menu_loadable_at_6x4':True})
 bn='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';e=UnityPy.load(str(out/(prefix+bn)));os={o.path_id:o for o in e.objects}
 for name in ['HighlightRedesignHomeOOPVertical','HighlightRedesignAwayOOPVertical']:
  t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']}
  panels=[r[a['m_SerializedData']['rid']] for a in r.values() if a.get('m_FullTypeName')=='FM.UI.FMTacticsPanel'];assert len(panels)==2 and all(s['Orientation']==0 and s['FlipPositions']==0 for s in panels)
 t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='HighlightRedesignPitchAndTwoCharts');r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};assert [x['rid'] for x in r[1008]['m_Children']]==[1022,3121];assert [x['rid'] for x in r[3121]['m_Children']]==[3123,3261]
 for gone in [2147,2149,2151,2153,2429,3169]:assert gone not in r
(out/'independent-layout-check.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'verified_layouts':len(results),'slots_per_layout':9,'all_default_configs_resolve':True,'full_native_menu_loadable':True,'vertical_oop_both_sides':True,'center_contains_only_pitch_momentum_xg':True},ensure_ascii=False))
