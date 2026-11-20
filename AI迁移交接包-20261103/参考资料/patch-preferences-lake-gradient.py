from pathlib import Path
import ast,copy,json,datetime
R=Path(__file__).resolve().parent
src=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0].replace('F:/Steam/steamapps/common/Project Taco','F:/Steam/steamapps/common/Football Manager 27')
exec(compile(src,'<audit>','exec'))
source=ast.parse((R/'unify-lake-blue-controls.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['append_rule','color'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),'<style>','exec'))
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<styles>','exec'))
source=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
import struct
poolmap={2:"floats",3:"dimensions",4:"colors",5:"strings",6:"assets",7:"strings",8:"strings"}
W='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,S]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};expected={}
 proto=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='TextScalingPreferences');rr={r['rid']:r for r in proto['references']['RefIds']};pn=copy.deepcopy(rr[1025]);ps=copy.deepcopy(rr[pn['data']['m_SerializedData']['rid']])
 for ob in list(oo.values()):
  if ob.type.name!='MonoBehaviour':continue
  name=ob.peek_name() or ''
  if 'Preferences' not in name and name!='GridBreakpointPreference':continue
  d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']};grads=[r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient']
  if name=='PreferencesFMMenuCard' or name=='InterfaceColoursPreferencesCard':continue
  if not grads and name!='DetailedPreferencesTabButton':continue
  so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();st=Styles(sh)
  if name=='DetailedPreferencesTabButton':
   n=copy.deepcopy(pn);sd=copy.deepcopy(ps);rid=max(rr)+1;n['rid']=rid;sd['rid']=rid+1
   n['data'].update(m_Id=1995000001,m_Parent={'rid':1002},m_Children=[],m_Classes=['fm27-preference-category-gradient'],m_SerializedData={'rid':rid+1},m_RuleIndex=-1)
   sd['data'].update(uxmlAssetId=1995000001,name='LakeBluePreferenceSelection',pickingMode=1,pickingMode_UxmlAttributeFlags=1)
   d['references']['RefIds'] += [n,sd];rr[1002]['data']['m_Children'].insert(0,{'rid':rid});grads=[n]
   st.edit(n,[st.p(131102,st.h(7,'absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(0)),st.p(131105,st.h(3,{'unit':2,'value':100.})),st.p(131087,st.h(3,{'unit':2,'value':100.}))])
  for g in grads:
   # Preserve native geometry, bindings and selected-state visibility.
   st.edit(g,[st.p(-1,st.h(4,color('35C6E8'))),st.p(-1,st.h(4,color('078BC4')))])
   rule=sh['m_Rules'][g['data']['m_RuleIndex']]
   rule['m_Properties'][-2]['m_CustomName']='--start-colour';rule['m_Properties'][-1]['m_CustomName']='--end-colour'
  for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
  changes.append({'folder':str(folder),'template':name,'gradients':len(grads)})
 data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/W]).objects};assert set(check)==set(orig)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/W]=data
 e=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in e.objects};ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');sh=ob.read_typetree()
 append_rule(sh,['.fm27-preference-category-gradient'],[(458767,0.)])
 append_rule(sh,['.tabgroup__tab-settings--active .fm27-preference-category-gradient','.tabgroup__tab-settings--active.fm27-preference-category-gradient'],[(458767,1.)])
 ob.save_typetree(sh);data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/S]).objects}
 for pid,o in check.items():
  if pid==ob.path_id:assert o.read_typetree()==sh
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/S]=data
out=R/('preferences-lake-gradient-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
