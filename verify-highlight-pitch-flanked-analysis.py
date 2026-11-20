from pathlib import Path
import sys,json,copy,hashlib,importlib.util,struct
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
P=R/'highlight-pitch-flanked-analysis-20261104-235348'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';T='ui-tileslayouts_assets_all.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
checks=[]
for tag,prefix in [('game',''),('skin','skin-')]:
 new={o.path_id:o for o in UnityPy.load((P/(prefix+G)).read_bytes()).objects};old={o.path_id:o for o in UnityPy.load((P/('backup-'+tag)/G).read_bytes()).objects}
 def named(name):return next(o for o in new.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
 def data(rs,i):return rs.get(rs[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 def val(sheet,h):return sheet[{2:'floats',3:'dimensions',7:'strings'}[h['m_ValueType']]][h['valueIndex']]
 for side in ['Home','Away']:
  o=named('HighlightIntegrated'+side+'StatsAndFormation');d=o.read_typetree();rs=refs(d);sheet=new[d['inlineSheet']['m_PathID']].read_typetree();row=next(i for i,r in rs.items() if 'm_Parent' in r.get('data',{}) and data(rs,i).get('name')=='IntegratedTeamStatsAndFormationRow');children=[c['rid'] for c in rs[row]['data']['m_Children']];weights=[]
  for i in children:
   rule=sheet['m_Rules'][rs[i]['data']['m_RuleIndex']];weights.append(val(sheet,next(p for p in rule['m_Properties'] if p['m_Id']==131084)['m_Values'][0]))
  assert weights==([3,3.5,3.5] if side=='Home' else [3.5,3.5,3])
  instance=children[1];alias=rs[instance]['data']['m_TemplateAlias'];assert data(rs,instance)['templateId']==alias
  oop=named('HighlightSixColumns'+side+'OutOfPossession');od=oop.read_typetree();ors=refs(od);variables=[v for r in ors.values() for v in r.get('data',{}).get('ValueVariables',[]) if v['m_name'].startswith('SelectedFormation')];assert len(variables)==4 and all(v['m_scopeValue']['m_serializedData'].startswith('Int|1|') for v in variables)
  assert next(u['path'] for u in d['m_Usings'] if u['alias']==alias)==next(k for k,v in next(o.read_typetree() for o in new.values() if o.type.name=='AssetBundle')['m_Container'] if v['asset']['m_PathID']==oop.path_id)
 for name in ['HighlightPhaseSpecificFeetAndCondition','SmallSubstituteCardLowerNoRating','HighlightLowerHomeSixPageCarousel','HighlightLowerAwaySixPageCarousel','MatchViewer_12x4']:
  obj=named(name);assert sha(obj.get_raw_data())==sha(old[obj.path_id].get_raw_data()),name
 layouts={o.path_id:o for o in UnityPy.load((P/(prefix+T)).read_bytes()).objects}
 count=0
 for obj in layouts.values():
  if obj.type.name!='MonoBehaviour' or obj.peek_name() not in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:continue
  tr=obj.read_typetree();bs=tr['m_gridComponents'];assert len(bs)==7 and [b['m_location']['width'] for b in bs]==[10,10,3,3,8,3,3];assert [b['m_elementID'] for b in bs[2:]]==['MatchMomentum','MatchStatsStandAlone','HighlightFiveAnalysisCenter','MatchEvents','xGStory']
  assert bs[-1]['m_gridElementConfigs'][0]['Type']==0
  count+=1
 assert count==4
 cat=cm.Catalog((P/('backup-'+tag)/'catalog.bin').read_bytes());idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');preload={v[0] for v in cat.array(cat.key_records[idx][1],'I')};meta=next(o.read_typetree() for o in new.values() if o.type.name=='AssetBundle')
 for side in ['Home','Away']:
  obj=named('HighlightSixColumns'+side+'OutOfPossession');guid=next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==obj.path_id);loc=cat.locations(guid)[0];assert loc in preload and cat.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset';assert G in cat.location(cat.location(loc)['dependencies'][0])['internal']
 checks.append({'variant':tag,'top_weights_exact':True,'oop_default_second_page':True,'native_bottom_picker':True,'grid_variants':count,'upper_feet_bench_carousels_shared_viewer_byte_unchanged':True,'catalog_type_owner_preload':True})
(P/'independent-check.json').write_text(json.dumps(checks,indent=2),'utf8')
print('Independent verification passed: both variants, unchanged top, native events then xG, bottom 3/3/8/3/3.')
state=json.loads((R/'current-highlight-layout.json').read_text('utf8'));(P/'previous-highlight-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
state.update(status='prepared',patch=str(P),source_script=str(R/'build-highlight-pitch-flanked-analysis.py'),restore=str(P/'restore.ps1'),bottom_columns=[3,3,8,3,3],lower_middle_defaults=['MatchMomentum','MatchStatsStandAlone','home maps / live pitch / away maps','MatchEvents','xGStory'],center='lower central 8x3, home maps left/live pitch center/away maps right, internal widths 1:2:1',verification=str(P/'independent-check.json'),runtime_verified=False,backup_directories=[str(P/('backup-'+t)) for t in ['game','skin','cache']])
(P/'highlight-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
installer=(P/'installer.py').read_text('utf8')
installer+="\nstate=json.loads((out/('previous-highlight-state.json' if restore else 'highlight-state.json')).read_text('utf8'))\nif not restore:state.update(status='installed',installed_files=len(tx))\n(out.parent/'current-highlight-layout.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')\n"
(P/'installer.py').write_text(installer,'utf8')

