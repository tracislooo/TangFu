from pathlib import Path
import sys,json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('# 1. Prematch')[0]
boot=boot.replace('match-ui-avatars-layout-','epl-goal-popup-portrait-').replace('NAMES=[W,G,M,F]','NAMES=[W,M]')
exec(compile(boot,'backup-current-bundles-and-load-ui-helpers','exec'))

d=Doc(M,name='GoalScoredPopup_EPL');original=copy.deepcopy(d.d);old_refs=refs(original);old_sheet=copy.deepcopy(d.s)
assert d.obj.path_id==-3806672750247675237
assert d.a(1004)['m_Children']==[{'rid':1006},{'rid':1007}]
assert not any(d.data(i).get('name')=='GoalScorerPortraitHeader' for i,x in d.r.items() if 'm_Parent' in x.get('data',{}))

# Preserve the original 40x72 club strip and 260x72 event-details panel.
details=ve(d,1004,'GoalEventOriginalInfoArea',300,72)
d.st(details,[(131083,d.enum('row')),(131073,d.enum('stretch'))])
d.move(1006,details);d.move(1007,details)
header=ve(d,1004,'GoalScorerPortraitHeader',300,80);d.move(header,1004,0)
d.st(header,[(131083,d.enum('column')),(131073,d.enum('center')),(131088,d.enum('flex-start'))])
mapping,photo=picture(d,header,'person1',72,'GoalScorerPortrait')
d.st(photo,[(131084,d.num(1)),(131085,d.num(0))])
d.size(1004,300,152);d.st(1004,[(131083,d.enum('column'))])

def centre_names(parent,nodes,texts,height,name):
 group=ve(d,parent,name)
 d.st(parent,[(131102,d.enum('relative'))])
 # Equal side slots keep the names centered independently of jersey numbers and event icons.
 d.st(group,[(131102,d.enum('absolute')),(131089,d.px(44)),(131103,d.px(44)),(131104,d.px(0)),(131080,d.px(0)),(131083,d.enum('row')),(131073,d.enum('center')),(131088,d.enum('center')),(131084,d.num(0)),(131085,d.num(0)),(131097,d.px(0)),(458768,d.enum('hidden'))])
 for i in nodes:
  d.move(i,group);d.a(i)['m_Classes']=[c for c in d.a(i).get('m_Classes',[]) if c!='flex-grow-class']
  d.st(i,[(131084,d.num(0)),(131085,d.num(1)),(131097,d.px(0))])
 for i in texts:
  d.a(i)['m_Classes']=[c for c in d.a(i).get('m_Classes',[]) if c!='flex-grow-class']
  d.st(i,[(131084,d.num(0)),(131085,d.num(1)),(131097,d.px(0)),(65546,d.enum('middle-center')),(65552,d.enum('nowrap'))])
 return group
scorer_names=centre_names(1013,[1035,1036],[1048,1036],40,'GoalScorerCenteredNames')
assist_names=centre_names(1052,[1068,1069],[1076,1069],32,'GoalAssistCenteredNames')
no_assist=centre_names(1054,[1072],[1072],32,'GoalNoAssistCenteredLabel')
d.save()

def styled_value(i,pid):
 p=next(p for p in d.s['m_Rules'][d.a(i)['m_RuleIndex']]['m_Properties'] if p['m_Id']==pid);v=p['m_Values'][0];return d.s[poolmap[v['m_ValueType']]][v['valueIndex']]
# Check the geometric contract and preserve every existing binding/translation/condition/event.
assert d.a(1004)['m_Children']==[{'rid':header},{'rid':details}]
assert d.a(details)['m_Children']==[{'rid':1006},{'rid':1007}]
assert styled_value(1004,131087)['value']==styled_value(header,131087)['value']+styled_value(details,131087)['value']==152
assert styled_value(mapping,131105)['value']==styled_value(mapping,131087)['value']==72
assert d.data(mapping)['Mappings'][0]['to']['m_path']=='person1'
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert d.r[i]==r,('original serialized binding altered',i)
for i in [1006,1007,1016,1017,1020,1021,1023,1034,1038,1045,1060,1061,1067]:
 assert d.a(i)['m_RuleIndex']==old_refs[i]['data']['m_RuleIndex'],('original panel/number/icon style altered',i)
for i in [scorer_names,assist_names,no_assist]:assert styled_value(i,131089)==styled_value(i,131103)=={'unit':1,'value':44.0}
for i in [1006,1007]:
 ri=old_refs[i]['data']['m_RuleIndex'];assert d.s['m_Rules'][ri]==old_sheet['m_Rules'][ri]

# Existing PersonPicture is addressed by its native GUID; no new catalog keys or image files.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
picture_guid=next(u['path'] for u in d.d['m_Usings'] if u['alias']=='PersonPicture');assert cm.Catalog(before[GAME.parent/'catalog.bin']).locations(picture_guid)
output=env[M].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[M])
for pid,h in hashes[M].items():
 if pid not in changes[M]:assert sha(check[pid].get_raw_data())==h,('unrelated asset altered',pid)
for pid,expected in changes[M].items():assert check[pid].read_typetree()==expected,('roundtrip mismatch',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/M).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.') or p.name==W:protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'template':'GoalScoredPopup_EPL','path_id':d.obj.path_id,'inline_style':d.sid,'popup_size':[300,152],'original_info_area':[300,72],'club_strip':[40,72],'info_block':[260,72],'portrait_size':[72,72],'portrait_binding':'person1 -> player1.Person -> match.MatchLowerThirdPlayer1.Person','scorer_and_assist_names_centered':True,'all_original_bindings_unchanged':True,'original_number_and_event_icon_styles_unchanged':True,'normal_no_assist_own_goal_switches_unchanged':True,'changes':{M:{str(pid):v.get('m_Name','') for pid,v in changes[M].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{M:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps({'passed':True,'serialization_roundtrip':True,'all_original_binding_records_unchanged':True,'original_info_dimensions_preserved':True,'jersey_number_and_event_icon_styles_unchanged':True,'normal_no_assist_own_goal_logic_unchanged':True,'portrait_uses_current_goal_scorer':True,'equal_side_insets_for_name_centering':True,'unrelated_objects_unchanged':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[M],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'template':d.d['m_Name'],'popup_size':[300,152],'original_info_area_unchanged':[300,72],'portrait_size':[72,72]},ensure_ascii=False))
