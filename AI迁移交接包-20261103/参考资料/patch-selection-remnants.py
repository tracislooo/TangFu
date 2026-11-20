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

W='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';V='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,V,S]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
for folder in [GAME,SKIN]:
 for bn in [W,V]:
  e=UnityPy.load(before[folder/bn]);oo={o.path_id:o for o in e.objects};expected={}
  protoenv=UnityPy.load(before[folder/W]);proto=next(o.read_typetree() for o in protoenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='TextScalingPreferences');rr={r['rid']:r for r in proto['references']['RefIds']};pn=copy.deepcopy(rr[1025]);ps=copy.deepcopy(rr[pn['data']['m_SerializedData']['rid']])
  meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');highlightids={a['asset']['m_PathID'] for guid,a in meta['m_Container'] if guid=='c7137eb48e725d74a91323863dae1393'}
  for ob in list(oo.values()):
   if ob.type.name!='MonoBehaviour':continue
   name=ob.peek_name() or '';d=ob.read_typetree()
   if 'inlineSheet' not in d:continue
   rr={r['rid']:r for r in d['references']['RefIds']};isregion=any(k in name for k in ['Preferences','GridBreakpointPreference','Responsibilit']) or ob.path_id in highlightids
   if not isregion:continue
   so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();st=Styles(sh)
   roots=[r for r in rr.values() if r.get('data',{}).get('m_Parent',{}).get('rid')==1000 and 'm_Classes' in r['data']]
   for r in roots:
    if 'fm27-lake-select-region' not in r['data']['m_Classes']:r['data']['m_Classes'].append('fm27-lake-select-region')
   targets=[r for r in rr.values() if 'navigation-tab-settings' in r.get('data',{}).get('m_Classes',[]) and not any(rr.get(c['rid'],{}).get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient' for c in r['data'].get('m_Children',[]))]
   if ob.path_id in highlightids:targets=roots[:1]
   nr=max(rr)+1
   for par in targets:
    n=copy.deepcopy(pn);sd=copy.deepcopy(ps);n['rid']=nr;sd['rid']=nr+1;nr+=2
    n['data'].update(m_Id=1996000000+nr,m_Parent={'rid':par['rid']},m_Children=[],m_Classes=['fm27-remnant-gradient'],m_SerializedData={'rid':sd['rid']},m_RuleIndex=-1)
    sd['data'].update(uxmlAssetId=n['data']['m_Id'],name='LakeSelectionGradient',pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    st.edit(n,[st.p(131102,st.h(7,'absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(0)),st.p(131105,st.h(3,{'unit':2,'value':100.})),st.p(131087,st.h(3,{'unit':2,'value':100.}))])
    par['data']['m_Children'].insert(0,{'rid':n['rid']});d['references']['RefIds'] += [n,sd]
   for r in d['references']['RefIds']:
    a=r.get('data',{})
    if a.get('m_FullTypeName')=='SI.Bindable.SIGradient' and 'fm27-lake-action-gradient' not in a.get('m_Classes',[]):
     a['m_Classes'].append('fm27-selection-native-gradient')
   for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
   changes.append({'folder':str(folder),'bundle':bn,'template':name,'added_gradients':len(targets)})
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/bn]).objects};assert set(check)==set(orig)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert o.get_raw_data()==orig[pid].get_raw_data()
  payloads[folder/bn]=data
 e=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in e.objects};ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');sh=ob.read_typetree()
 active=['.buttons-segmented-button-row-active-regular-placement-'+p for p in ['leading','middle','trailing']]+['.unity-radio-button-group__child-active','.tabgroup__tab-settings--active','.buttons-segmented-button-row-regular-selected']
 for a in active:
  q='.fm27-lake-select-region '+a
  append_rule(sh,[q,q+':hover'],[(458752,color('078BC4'))])
  append_rule(sh,[q+' .fm27-selection-native-gradient',q+'.fm27-lake-select-region .fm27-selection-native-gradient'],[('--start-colour',color('35C6E8')),('--end-colour',color('078BC4')),(458767,1.)])
 append_rule(sh,['.fm27-remnant-gradient'],[(458767,0.),('--start-colour',color('35C6E8')),('--end-colour',color('078BC4'))])
 append_rule(sh,['.unity-radio-button-group__child-active .fm27-remnant-gradient','.tabgroup__tab-settings--active .fm27-remnant-gradient'],[(458767,1.)])
 append_rule(sh,['.fm27-lake-select-region .unity-base-slider__dragger','.fm27-lake-select-region .unity-slider__dragger','.fm27-lake-select-region .sislider--dragger'],[(458752,color('35C6E8')),(262146,color('35C6E8'))])
 append_rule(sh,['.buttons-dropdown-icon-base-responsibilities-primary .si-dropdown__selection-field'],[(458752,color('078BC4'))])
 for r in sh['m_Rules']:
  txt=json.dumps(r.get('m_ComplexSelectors',[]))
  if 'responsib' in txt.lower() and not any(k in txt for k in ['fm27','dropdown']):
   for p in r['m_Properties']:
    if p['m_Id']==458752:
     hs=p['m_Values'];purple=any(h['m_ValueType']==8 and any(k in sh['strings'][h['valueIndex']] for k in ['toggle-active-primary','purple','twilight']) for h in hs)
     if purple:p['m_Values']=[Styles(sh).h(4,color('078BC4'))]
 ob.save_typetree(sh);data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/S]).objects}
 for pid,o in check.items():
  if pid==ob.path_id:assert o.read_typetree()==sh
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/S]=data
out=R/('selection-remnants-lake-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)

