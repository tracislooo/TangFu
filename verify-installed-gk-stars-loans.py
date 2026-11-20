exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
out=R/'gk-no-title-left-stars-horizontal-loans-20261019-011613';rep=json.loads((out/'manifest.json').read_text(encoding='utf8'))
assert sha((GAME/WN).read_bytes())==sha((SKIN/WN).read_bytes())==rep['after_sha256'][WN]
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
assert sha((GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle').read_bytes())==sha((SKIN/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle').read_bytes())
gd=go[-930000000001003].read_typetree();gr={r['rid']:r for r in gd['references']['RefIds']};gs=go[gd['inlineSheet']['m_PathID']].read_typetree()
for i in rep['goalkeeping_titles_hidden']:
 p={p['m_Id']:p for p in gs['m_Rules'][gr[i]['data']['m_RuleIndex']]['m_Properties']}
 h=p[131081]['m_Values'][0];assert gs['strings'][h['valueIndex']]=='none'
 for pid in [131087,131096,131094]:
  h=p[pid]['m_Values'][0];assert gs['dimensions'][h['valueIndex']]['value']==0
refs={r['rid']:r for r in objects[FULL].read_typetree()['references']['RefIds']}
# Audit copied native bindings and event/function byte streams against their unchanged source assets.
verified=0
for imp in rep['inline_imports']:
 mp={int(k):v for k,v in imp['mapping'].items()};srcdoc=objects[imp['source']].read_typetree();sr={r['rid']:r for r in srcdoc['references']['RefIds']}
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:return {'rid':mp.get(v['rid'],v['rid'])}
   return {k:remap(a) for k,a in v.items() if k not in ['uxmlAssetId','templateId']}
  if isinstance(v,list):return [remap(a) for a in v]
  return v
 for old,new in mp.items():
  if old==1000:continue
  if 'UxmlSerializedData' in sr[old]['type']['class']:
   a=copy.deepcopy(refs[new]['data']);a.pop('uxmlAssetId',None);a.pop('templateId',None)
   assert a==remap(sr[old]['data']),('Native binding mismatch',imp['prefix'],old);verified+=1
left,right,club=[{int(k):v for k,v in x['mapping'].items()} for x in rep['inline_imports']]
assert refs[left[1008]]['data']['m_Children']==[]
assert refs[right[1009]]['data']['m_Children']==[]
assert refs[1297]['data']['m_Children'].index({'rid':rep['star_holder']})<refs[1297]['data']['m_Children'].index({'rid':1295})
assert property_value(refs[club[1007]],131083)=='row'
assert refs[club[1007]]['data']['m_Children']==[{'rid':club[1012]},{'rid':club[1013]}]
print(json.dumps({'goalkeeping_titles_hidden':len(rep['goalkeeping_titles_hidden']),'left_stars_above_country_club':True,'right_duplicate_stars_removed':True,'loan_clubs_horizontal':True,'native_serialized_bindings_and_event_payloads_verified':verified,'installed_game_skin_identical':True},indent=2))
