from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
out=next(p for p in sorted(Path.cwd().glob('pinned-1-11-update-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((out/'manifest.json').read_text('utf8'));count=0
for n in m['after_sha256']:
 if 'tileslayouts' in n:continue
 old={o.path_id:o for o in UnityPy.load(m['source_paths'][n]).objects};new={o.path_id:o for o in UnityPy.load(str(out/n)).objects}
 def compare(a,b,path=''):
  global count
  if isinstance(a,dict):
   if set(a)=={'m_FileID','m_PathID'}:return
   for k,v in a.items():
    if k=='m_Script':continue
    assert k in b,(path,k)
    compare(v,b[k],path+'.'+k)
  elif isinstance(a,list):
   assert len(a)==len(b),(path,len(a),len(b))
   for i,(v,w) in enumerate(zip(a,b)):compare(v,w,path+f'[{i}]')
  else:
   assert a==b,(path,a,b)
   count+=1
 for row in m['stage_assets']:
  if row['bundle']==n and not(n=='ui-styles_assets_default.bundle' and row['name']=='FigmaStyleVariables'):compare(old[row['source_id']].read_typetree(),new[row['id']].read_typetree(),row['name'] or '')

required={'PlayerReportPreviewTooltip','PlayerCellInMatch','MatchPlayerReport','MainMenu','IGEEditDetailsBlock','TacticsPositionDetailed','TacticsPositionCombined','NonPlayerReportHeader','NonPlayerAttributeCell','NonPlayerAttributeWithIconCell','PortalMessagesContentBlock','PortalScreen','PrimaryNavigationBar','Portal-Large','Portal-Large-FMC','Portal-Medium','Portal-Medium-FMC','Portal-Small','Portal-Small-FMC'}
verified=[]
for n in m['after_sha256']:
 old={o.path_id:o for o in UnityPy.load(m['source_paths'][n]).objects};new={o.path_id:o for o in UnityPy.load(str(out/n)).objects}
 for ob in old.values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name() not in required:continue
  candidates=[o for o in new.values() if o.type.name==ob.type.name and o.peek_name()==ob.peek_name()];assert len(candidates)==1
  a=ob.read_typetree();b=candidates[0].read_typetree();compare(a,b,ob.peek_name())
  if a.get('inlineSheet',{}).get('m_PathID'):
   compare(old[a['inlineSheet']['m_PathID']].read_typetree(),new[b['inlineSheet']['m_PathID']].read_typetree(),ob.peek_name()+'_Style')
  verified.append(ob.peek_name())
assert required<=set(verified),required-set(verified)
result={'final_source_values_preserved':count,'required_templates_and_inline_styles_verified':verified,'runtime_verified':False}
(out/'final-requirements-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print(json.dumps(result))
