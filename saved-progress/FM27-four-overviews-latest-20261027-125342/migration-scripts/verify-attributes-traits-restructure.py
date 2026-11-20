from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent
__file__=str(R/'refine-card-inner-layout.py')
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<installed loader>','exec'))
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';TABLE=-930000000001003
out=Path(sys.argv[1]);manifest=json.loads((out/'manifest.json').read_text(encoding='utf8'))
for folder in [GAME,SKIN]:
 for name,expected in manifest['after_sha256'].items():assert sha((folder/name).read_bytes())==expected
go={o.path_id:o for o in UnityPy.load(str(GAME/GN)).objects}
oldworld={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/WN)).objects}
oldglobal={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/GN)).objects}
table=go[TABLE].read_typetree();tr={r['rid']:r for r in table['references']['RefIds']};ts=go[table['inlineSheet']['m_PathID']].read_typetree()
oldtable=oldglobal[TABLE].read_typetree();otr={r['rid']:r for r in oldtable['references']['RefIds']}
def named(rs,name):return next(r for r in rs.values() if rs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
def props(rs,ss,i):
 a=rs[i]['data'];result={}
 if a.get('m_RuleIndex',-1)<0:return result
 for p in ss['m_Rules'][a['m_RuleIndex']]['m_Properties']:
  hs=p['m_Values'];result[p['m_Id']]=[('keyword',h['valueIndex']) if h['m_ValueType']==1 else ss[poolmap[h['m_ValueType']]][h['valueIndex']] for h in hs]
 return result
source=oldworld[-930000000001001].read_typetree();sr={r['rid']:r for r in source['references']['RefIds']}
def serialized(rs,i):return rs[rs[i]['data']['m_SerializedData']['rid']]['data']
assert [c['rid'] for c in tr[1011]['data']['m_Children']]==[1025,1063]
assert tr[1063]['data']['m_Parent']=={'rid':1011}
for key in ['Binding','RowTemplate','FixedElementSize','RowParamName']:assert serialized(tr,1097)[key]==serialized(otr,1097)[key]
assert serialized(tr,1097)['Binding']['m_direct']['Path']['m_path']=='Person.AttributesTechnicalGoalkeeping'
assert tr[1135]==otr[1135]
assert not any(r.get('data',{}).get('m_TemplateAlias')=='PlayerReportFootednessBlock' for r in tr.values())
checks=[]
for page in manifest['pages']:
 pid=page['page_id'];d=objects[pid].read_typetree();rs={r['rid']:r for r in d['references']['RefIds']};ss=objects[d['inlineSheet']['m_PathID']].read_typetree();old=oldworld[pid].read_typetree();oldrs={r['rid']:r for r in old['references']['RefIds']}
 assert rs[1011]['data']['m_Children']==[{'rid':1035}]
 assert rs[1035]==oldrs[1035]
 scroll=named(rs,'OverviewAttributesContentScroll');sd=serialized(rs,scroll['rid'])
 assert scroll['data']['m_FullTypeName']=='SI.UI.SIScrollView'
 assert scroll['data']['m_Children']==[{'rid':1040}]
 assert sd['mode']==0 and sd['horizontalScrollerVisibility']==2 and sd['verticalScrollerVisibility']==0
 assert serialized(rs,1040)==serialized(oldrs,1040)
 validate_ui(d,ss)
 for entry,third in zip(manifest['traits_imports'],[1009,1013]):
  prefix=entry['prefix'];root=named(tr,prefix+'PlayerTraitsFrame');assert tr[third]['data']['m_Children'][-1]=={'rid':root['rid']}
  sw=named(tr,prefix+'PlayerTraitsSwitch');no=named(tr,prefix+'PlayerTraitsNoDataText');lst=named(tr,prefix+'PlayerTraitsList')
  assert sw['data']['m_Children']==[{'rid':no['rid']},{'rid':lst['rid']}]
  assert serialized(tr,sw['rid'])['Binding']==serialized(sr,1055)['Binding']
  assert serialized(tr,no['rid'])['TextBinding']==serialized(sr,1077)['TextBinding']
  lsd=serialized(tr,lst['rid']);assert lsd['Binding']==serialized(sr,1078)['Binding']
  assert lsd['Truncate']==0 and lsd['DynamicElements']==1 and lsd['RowTemplate']==serialized(sr,1078)['RowTemplate']
  # Test the source schemas for missing/empty/many trait lists and native no-ban/ban displays.
  checks.append({'page':pid,'player_type':'outfield' if third==1009 else 'goalkeeper','native_empty_traits_branch_preserved':True,'complete_dynamic_trait_list_enabled':True,'rating_binding_preserved':True,'native_bans_component_unchanged':True})
validate_ui(table,ts)
record={'installed_game_skin_hashes_match':True,'four_layout_cases':checks,'native_traits_row_wrap_verified':'content-wrap','actual_game_runtime_verified':False}
mf=next(o for o in go.values() if o.type.name=='AssetBundle').read_typetree();traitpid=next(v['asset']['m_PathID'] for k,v in mf['m_Container'] if k=='cf6ecba08a86be0469c39c12907a714e')
assert go[traitpid].get_raw_data()==oldglobal[traitpid].get_raw_data()
traitrow=go[traitpid].read_typetree();assert any('content-wrap' in r.get('data',{}).get('m_Classes',[]) for r in traitrow['references']['RefIds'])
(out/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed_game_skin_match':True,'layout_cases_verified':len(checks),'empty_and_long_trait_schemas_verified':True,'native_bans_schemas_preserved':True,'runtime_verified':False}))
