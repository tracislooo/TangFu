from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
C=json.loads((R/'current-game-location.json').read_text('utf8'))
O=R/'analysis/club-location-map';O.mkdir(exist_ok=True)
e=UnityPy.load(str(Path(C['bundle_root'])/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'))
obs={o.path_id:o for o in e.objects}
names=['ClubSiteBlock','ClubInfoReportBlock','ClubOverviewStadiumStack','ClubOverviewRecruitmentBudgetStack','ClubScreenOverviewBlock']
for ob in obs.values():
 if ob.type.name!='MonoBehaviour' or ob.peek_name() not in names:continue
 d=ob.read_typetree();name=d['m_Name'];s=obs[d['inlineSheet']['m_PathID']].read_typetree()
 (O/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8');(O/(name+'Style.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
 rs={r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
 print('\nDOC',name,ob.path_id,d['inlineSheet']['m_PathID'])
 def walk(i,depth=0):
  a=rs[i];sd=rs.get(a.get('m_SerializedData',{}).get('rid'),{});idx=a.get('m_RuleIndex',-1)
  props={p['m_Id']:[s[{2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(v['m_ValueType'],'strings')][v['valueIndex']] if v['m_ValueType'] in (2,3,4,5,6,7,8) else str(v) for v in p['m_Values']] for p in s['m_Rules'][idx]['m_Properties']} if idx>=0 else {}
  print(' '*depth,i,a.get('m_FullTypeName',a.get('m_TemplateAlias','')),sd.get('name'),sd.get('text',sd.get('DebugDisplay','')),props)
  for ch in a.get('m_Children',[]):walk(ch['rid'],depth+1)
 for i,a in rs.items():
  if 'm_Parent' in a and a['m_Parent']['rid'] not in rs:walk(i)
  elif 'm_Parent' in a and a['m_Parent']['rid']==1000:walk(i)
