from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
out=next(p for p in sorted(Path.cwd().glob('pinned-1-14-update-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((out/'manifest.json').read_text('utf8'));count=0
for n in m['after_sha256']:
 if 'tileslayouts' in n or 'backgrounds_assets' in n:continue
 old={o.path_id:o for o in UnityPy.load(m['source_paths'][n]).objects};new={o.path_id:o for o in UnityPy.load(str(out/n)).objects}
 def compare(a,b,path=''):
  global count
  if isinstance(a,dict):
   if set(a)=={'m_FileID','m_PathID'}:return
   for k,v in a.items():
    if k=='m_Script':continue
    if k not in b:
     assert k in {x[1] for x in m.get('schema_fields_removed',[])},(path,k)
     continue
    compare(v,b[k],path+'.'+k)
  elif isinstance(a,list):
   assert len(a)==len(b),(path,len(a),len(b))
   for i,(v,w) in enumerate(zip(a,b)):compare(v,w,path+f'[{i}]')
  else:
   assert a==b,(path,a,b)
   count+=1
 for row in m['stage_assets']:
  if row['bundle']==n :compare(old[row['source_id']].read_typetree(),new[row['id']].read_typetree(),row['name'] or '')

required={'PlayerReportPreviewTooltip','PlayerCellInMatch','MatchPlayerReport','MainMenu','IGEEditDetailsBlock','TacticsPositionDetailed','TacticsPositionCombined','NonPlayerReportHeader','NonPlayerAttributeCell','NonPlayerAttributeWithIconCell','PortalMessagesContentBlock','PortalScreen','PrimaryNavigationBar','Portal-Large','Portal-Large-FMC','Portal-Medium','Portal-Medium-FMC','Portal-Small','Portal-Small-FMC','ClubScreenOverviewBlock','MarketingBannerTile_8x2'}
verified=[]
for n in m['after_sha256']:
 if 'backgrounds_assets' in n:continue
 old={o.path_id:o for o in UnityPy.load(m['source_paths'][n]).objects};new={o.path_id:o for o in UnityPy.load(str(out/n)).objects}
 for ob in old.values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name() not in required:continue
  candidates=[o for o in new.values() if o.type.name==ob.type.name and o.peek_name()==ob.peek_name()];assert len(candidates)==1
  a=ob.read_typetree();b=candidates[0].read_typetree();compare(a,b,ob.peek_name())
  if a.get('inlineSheet',{}).get('m_PathID'):
   compare(old[a['inlineSheet']['m_PathID']].read_typetree(),new[b['inlineSheet']['m_PathID']].read_typetree(),ob.peek_name()+'_Style')
  verified.append(ob.peek_name())
assert required<=set(verified),required-set(verified)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';obs={o.path_id:o for o in UnityPy.load(str(out/W)).objects};d=next(o for o in obs.values() if o.peek_name()=='PrimaryNavigationBar').read_typetree();rr={v['rid']:v for v in d['references']['RefIds']};sheet=obs[d['inlineSheet']['m_PathID']].read_typetree()
root=next(i for i,r in rr.items() if 'fm27-header-holiday-shortcut' in r.get('data',{}).get('m_Classes',[]));todo=[root];visited=set()
while todo:
 i=todo.pop()
 if i in visited:continue
 visited.add(i);v=rr[i]['data'];ri=v.get('m_RuleIndex',-1)
 if ri>=0:assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][ri]['m_Properties'] for h in p['m_Values']),i
 todo.extend(c['rid'] for c in v.get('m_Children',[]))
result={'holiday_inline_variables_absent':True,'holiday_subtree_nodes_checked':len(visited),'final_source_values_preserved' :count,'required_templates_and_inline_styles_verified':verified,'runtime_verified':False}
(out/'final-requirements-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print(json.dumps(result))
