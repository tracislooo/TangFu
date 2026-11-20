"""Set the scoped primary-menu font to 85% of its original 16px size."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,sys
R=Path(__file__).resolve().parent
setup=(R/'change-staff-shortcut-to-recruitment-database.py').read_text('utf8').split('nav=UnityPy.load')[0]
exec(compile(setup,'resource-initialization-only','exec'))
S='ui-styles_assets_default.bundle'
before={f/S:(f/S).read_bytes() for f in [GAME,SKIN]}
for p in before:protected.pop(p,None)
for f in [GAME,SKIN]:protected[f/W]=sha((f/W).read_bytes())
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,names in [('build-fc-player-hover-layout.py',{'Styles'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'})]:
 tree=ast.parse((R/filename).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names],type_ignores=[]),filename+':definitions-only','exec'))
outputs={};reports=[]
for folder in [GAME,SKIN]:
 env=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 obj=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');doc=obj.read_typetree();old=copy.deepcopy(doc);st=Styles(doc)
 # Reuse exactly the divider selectors to preserve first-title and locale behavior.
 divider_rules=[rule for rule in doc['m_Rules'] if any(any(p['m_Value']=='PrimaryNavMessagesFrame' for sel in c['m_Selectors'] for p in sel['m_Parts']) for c in rule['m_ComplexSelectors']) and any(p['m_Id']==131077 for p in rule['m_Properties'])]
 assert len(divider_rules)==1
 dividers=copy.deepcopy(divider_rules[0]['m_ComplexSelectors']);idx=len(doc['m_Rules'])
 for c in dividers:c['ruleIndex']=idx
 doc['m_Rules'].append({'m_ComplexSelectors':dividers,'m_Properties':[st.p(131099,st.px(4))],'line':-1})
 def rule(selectors,props):
  idx=len(doc['m_Rules']);doc['m_Rules'].append({'m_ComplexSelectors':[selector(t,idx) for t in selectors],'m_Properties':props,'line':-1})
 root='#MainNav #MenuBar '
 custom=['Messages','Competitions','FixtureSchedule','DataHub','MedicalCentre','Youth','Staff']
 rule([root+'#MainFrame']+[root+'#PrimaryNav'+n+'Frame' for n in custom],[st.p(131100,st.px(6))])
 rule([root+'.portal-text'],[st.p(131092,st.px(2))])
 rule([root+'.navigation-tab-no-dropdown-padding-element'],[st.p(131105,st.px(2))])
 rule([root+'#NavTabDropdown'],[st.p(131105,st.px(10)),st.p(131097,st.px(10)),st.p(131085,st.num(0)),st.p(262151,st.px(0))])
 rule([root+'#NavTabDropdownIndicator'],[st.p(131105,st.px(8)),st.p(131087,st.px(8)),st.p(131097,st.px(8)),st.p(131096,st.px(8)),st.p(131085,st.num(0)),st.p(262150,st.px(0))])
 assert doc['m_Rules'][:len(old['m_Rules'])]==old['m_Rules']
 for ruledata in doc['m_Rules'][len(old['m_Rules']):]:
  assert all(h['m_ValueType'] not in [8,10] for p in ruledata['m_Properties'] for h in p['m_Values'])
 expected=copy.deepcopy(old)
 for key in ['dimensions','floats','m_Rules']:expected[key]=doc[key]
 assert doc==expected
 obj.save_typetree(doc);raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==obj.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i]
 outputs[folder/S]=raw;reports.append({'target':str(folder/S),'title_padding_right_px':6,'divider_padding_left_px':4,'label_margin_right_px':2,'dropdown_previous_effective_width':20,'dropdown_width_px':10,'dropdown_ratio':.5,'indicator_size_px':8,'no_dropdown_spacer_px':2,'font_and_dividers_unchanged':True,'sidebar_and_other_styles_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-tight-spacing-half-dropdown-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/S;bak=out/('backup-'+tag)/S;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(raw);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'changes':reports}))
