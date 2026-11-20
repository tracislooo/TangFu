from pathlib import Path
import ast,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
for fn,names in [('add-two-portrait-hidden-overviews.py',{'refs','data','named','owned_refs','rid_links'}),('split-season-radar-two-charts.py',{'graph'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),fn,'exec'))
OUT=Path(json.loads((R/'aligned-header-prepared.json').read_text())['output']);m=json.loads((OUT/'manifest.json').read_text('utf8'));tx=json.loads((OUT/'transaction.json').read_text('utf8'));live='--installed'in sys.argv;sha=lambda b:hashlib.sha256(b).hexdigest()
results=[]
for row,audit in zip(tx,m['audits']):
 src=Path(row['target']if live else row['source']);assert sha(src.read_bytes())==row['after']
 old={o.path_id:o for o in UnityPy.load(row['backup']).objects};new={o.path_id:o for o in UnityPy.load(str(src)).objects};assert old.keys()==new.keys()
 for pid in old:
  if pid not in audit['changes']:assert old[pid].get_raw_data()==new[pid].get_raw_data()
 doc=new[-941100000001020].read_typetree();rr=refs(doc);sheet=new[-941100000001021].read_typetree();graph(doc)
 def effective(i,key):
  ps=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'];p=next(p for p in reversed(ps)if p['m_Id']==key);h=p['m_Values'][0];pool={2:'floats',3:'dimensions',7:'strings'}.get(h['m_ValueType']);return sheet[pool][h['valueIndex']]if pool else h
 assert 1163 not in rr
 assert rr[1707]['data']['m_Parent']=={'rid':6738}
 assert effective(1707,131104)['value']==28 and effective(6724,131104)['value']==4
 assert effective(1199,131104)['value']==72
 assert effective(1184,131104)['value']==99
 assert effective(1295,131104)['value']==172
 assert effective(6304,131104)['value']==72
 assert effective(1349,131104)['value']==172
 assert effective(2242,131105)['value']==320 and effective(1026,131105)['value']==200
 olddoc=old[-941100000001020].read_typetree();oldrr=refs(olddoc)
 for i in [1719,1721,6729,1295,1297,2986,1203]:assert data(rr,i)==data(oldrr,i),('Native binding or event changed',i)
 for i in audit['hidden_rows']:
  ps=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']
  assert not any(p['m_Id']==458752 for p in ps)
  assert 'attributes-row-number-key-no-border'in rr[i]['data']['m_Classes']
  key=data(rr,i)['name'].removeprefix('RightHiddenRow_');badge=named(doc,'RightHiddenBadge_'+key);assert rr[badge]==oldrr[badge]
 for name in ['pros-list','const-list']:
  d=data(rr,named(doc,name));assert d['VerticalScrollerVisibility']==1 and d['ClampSizeToPage']==0
 outer,inner=audit['gates'];im={int(k):v for k,v in audit['selector_map'].items()};cm=[{int(k):v for k,v in c.items()}for c in audit['contract_maps']]
 assert rr[outer]['data']['m_Children']==[{'rid':cm[0][1001]},{'rid':inner}]
 assert rr[inner]['data']['m_Children']==[{'rid':cm[1][1001]},{'rid':im[2006]}]
 assert data(rr,outer)['Binding']['m_direct']['Path']['m_path']=='person.PositionalAbilitiesRolesVisible'
 assert data(rr,inner)['Binding']['m_visualFunction']['m_target']['m_guid']=='a4dffe7b331c90949b43d2d4e3155117'
 assert data(rr,im[1070])['Binding']['m_direct']['Path']['m_path']=='report.ScoutedSquadComparisonPlayers'
 for c in cm:
  assert data(rr,c[1008])['Binding']['m_direct']['Path']['m_path']=='contract.IsValid'
  assert data(rr,c[1039])['TextBinding']['m_direct']['Path']['m_path']=='contract.Wage.DisplayValue'
  assert data(rr,c[1036])['Binding']['m_direct']['Path']['m_path']=='contract.IsContractLengthApplicable'
 # Exercise the actual two-level branch topology for the meaningful states.
 for allowed,count,expected in [(False,0,cm[0][1001]),(False,3,cm[0][1001]),(True,0,cm[1][1001]),(True,3,im[2006])]:
  child=rr[outer]['data']['m_Children'][int(allowed)]['rid']
  if child==inner:child=rr[inner]['data']['m_Children'][int(count>0)]['rid']
  assert child==expected
 stats=new[-941100000001050].read_typetree();sr=refs(stats);ss=new[-941100000001051].read_typetree()
 for panel in ['SeasonStatsOutfielderPanel','SeasonStatsGoalkeeperPanel']:
  rows=sr[named(stats,panel)]['data']['m_Children'];assert len(rows)==4;heights=[]
  for c in rows:
   ps=ss['m_Rules'][sr[c['rid']]['data']['m_RuleIndex']]['m_Properties'];p=next(p for p in ps if p['m_Id']==131087);h=p['m_Values'][0];heights.append(ss['dimensions'][h['valueIndex']]['value'])
  assert heights==[27,24,24,24]
 results.append(dict(target=audit['target'],native_backgrounds_and_badges=True,header_anchors_aligned=True,comparison_contract_branches=4,native_contract_bindings=True,scrollbars_configured=True,other_objects_byte_identical=True))
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Protected resource',p)
report=dict(passed=True,installed=live,runtime_verified=False,results=results)
(OUT/('verification-installed.json'if live else'verification-prepared.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=False))
