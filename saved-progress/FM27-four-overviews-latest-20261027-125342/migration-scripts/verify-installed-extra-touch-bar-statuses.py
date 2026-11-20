exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
report=json.loads((R/'touch-bar-dynamics-happiness-condition-20261018-235513/manifest.json').read_text(encoding='utf8'))
assert report['after_sha256']==sha((GAME/WN).read_bytes())==sha((SKIN/WN).read_bytes())
d=objects[5775949770471550939].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
def name(i):return r.get(r[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
wrapper=next(i for i in r if name(i)=='HeaderFitnessSixMetrics');row=r[wrapper]['data']['m_Parent']['rid']
action=next(i for i in r if r[i].get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
assert r[row]['data']['m_Children']==[{'rid':wrapper},{'rid':action}]
names=[name(c['rid']) for c in r[wrapper]['data']['m_Children']]
assert names[-7::2]==['HeaderStatus_Mindset','HeaderStatus_Hierarchy','HeaderStatus_OverallHappiness','HeaderStatus_OverallCondition']
assert len(names)==19
cache={}
for c in report['copied_bindings']:
 pid=c['source_asset']
 if pid not in cache:
  if pid in objects:sd=objects[pid].read_typetree()
  else:
   ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));sd=next(o for o in ge.objects if o.path_id==pid).read_typetree()
  cache[pid]={x['rid']:x for x in sd['references']['RefIds']}
 a=copy.deepcopy(r[c['serialized']]['data']);b=copy.deepcopy(cache[pid][c['source_serialized']]['data'])
 for sd in [a,b]:
  for k in ['uxmlAssetId','name','name_UxmlAttributeFlags']:sd.pop(k,None)
 assert a==b
le=UnityPy.load(str(GAME/'ui-tileslayouts_assets_all.bundle'));grid=next(o for o in le.objects if o.path_id==3901662990989568885).read_typetree()
assert all(c['m_location']['height']==(8 if c['m_elementID']=='PlayerAttributesBlock' else 2) for c in grid['m_gridComponents'])
assert max(c['m_location']['y']+c['m_location']['height'] for c in grid['m_gridComponents'])==10
print(json.dumps({'installed_game_skin_identical':True,'four_new_modules_immediately_before_action':True,'total_modules':10,'original_native_bindings_verified':len(report['copied_bindings']),'native_condition_and_injury_branches_preserved':True,'grid_8_plus_2_preserved':True},indent=2))
