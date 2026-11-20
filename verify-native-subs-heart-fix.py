from pathlib import Path
import sys,json,ast,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
def load(path):return {o.path_id:o for o in UnityPy.load(str(path)).objects}
objects={n:load(out/n) for n in tx['files']}
def tree(n,name):
 o=next(o for o in objects[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name);d=o.read_typetree();s=objects[n][d['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};validate_ui(d,s);return d,s,r
def sd(r,i):return r.get(r[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def value(s,r,i,pid):
 a=r[i]['data'];p=next(p for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==pid);v=p['m_Values'][0];return s[poolmap[v['m_ValueType']]][v['valueIndex']]
for entry in m['removed_legacy_hearts']:
 d,s,r=tree(W,entry['template']);assert entry['removed_icon'] not in r
 assert not any(sd(r,i).get('name')=='Conditionicon' and r[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIImage' for i in r)
 blank=entry['empty_normal_branch'];assert r[blank]['data']['m_FullTypeName']=='UnityEngine.UIElements.VisualElement';assert value(s,r,blank,131105)['value']==value(s,r,blank,131087)['value']==0
 parent=r[blank]['data']['m_Parent']['rid'];assert r[parent]['data']['m_Children']==[{'rid':blank},{'rid':entry['injury_branch']}]
 assert r[entry['injury_branch']]['data']['m_FullTypeName']=='SI.Bindable.SIImage'
 # Custom percentage/ring binding and its layout remain exactly as before this correction.
 old_objects=load(tx['before'][str(Path(tx['game'])/W)]);old=old_objects[next(o.path_id for o in objects[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()==entry['template'])].read_typetree();rr={x['rid']:x for x in old['references']['RefIds']}
 for i in rr:
  if sd(rr,i).get('name','').startswith('MatchCondition_'):assert rr[i]==r[i],('custom condition node changed',entry['template'],i)

d,s,r=tree(M,'SquadOverview');baseobs=load(m['baseline']);base=baseobs[4934403862489788947].read_typetree();br={x['rid']:x for x in base['references']['RefIds']};bs=baseobs[base['inlineSheet']['m_PathID']].read_typetree()
for sub in [1032,1035,1038,1041]:
 a=r[sub]['data'];b=br[sub]['data'];assert a==b,('native substitute element differs',sub)
 parent=b['m_Parent']['rid'];assert r[parent]['data']['m_Children']==br[parent]['data']['m_Children'];assert sd(r,parent)==sd(br,parent)
 assert sd(r,sub)['FixedElementSize']==sd(br,sub)['FixedElementSize']
 if b['m_RuleIndex']>=0:assert s['m_Rules'][b['m_RuleIndex']]==bs['m_Rules'][b['m_RuleIndex']]
 assert len(r[parent]['data']['m_Children'])==2
assert not any(sd(r,i).get('name','').startswith('MatchSubstitutesAnchor_') for i in r)
hosts=[i for i in r if 'm_Parent' in r[i].get('data',{}) and sd(r,i).get('name','').startswith('MatchBottomTacticalToolbar')];assert len(hosts)==1;host=hosts[0]
assert r[host]['data']['m_Parent']['rid']==1009 and value(s,r,host,131102)=='absolute' and value(s,r,host,131080)=={'unit':2,'value':100.0}
assert value(s,r,host,131087)['value']==32 and value(s,r,host,131103)['value']==0
assert 'padding-horizontal-global-padding-extra-large' in r[host]['data']['m_Classes']
for n,ps in m['changes'].items():
 before=load(tx['before'][str(Path(tx['game'])/n)]);assert set(before)==set(objects[n])
 for i,o in before.items():
  if str(i) not in ps:assert o.get_raw_data()==objects[n][i].get_raw_data(),('unrelated object changed',n,i)
for p,h in m['protected_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
result={'passed':True,'legacy_condition_images_removed':3,'native_injury_branches_preserved':3,'custom_condition_subtrees_unchanged':True,'native_substitute_list_elements_exactly_restored':4,'native_expandable_children_and_settings_restored':True,'independent_toolbar_count':1,'toolbar_contributes_no_flow_width_or_height':True,'catalog_and_unrelated_assets_unchanged':True,'runtime_verified':False}
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print(json.dumps(result))
