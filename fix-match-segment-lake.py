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

M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';C='ui-styles_assets_common.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [S,C,M]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
active=['.buttons-segmented-button-row-active-regular-placement-'+x for x in ['leading','middle','trailing']]+['.buttons-segmented-button-row-regular-selected','.segmented-button-group .unity-radio-button-group__child-active','.segmented-button-group-purple .unity-radio-button-group__child-active','.segmented-button-labels .unity-radio-button-group__child-active','.radio_group_button_purple .unity-radio-button-group__child-active','.tabgroup.SegmentedButtonRow .tabgroup__tab--active','.buttongroup.SegmentedButtonRow .buttongroup__button--active']
for folder in [GAME,SKIN]:
 for bn in [S,C]:
  e=UnityPy.load(before[folder/bn]);oo={o.path_id:o for o in e.objects};expected={}
  for ob in oo.values():
   if ob.type.name!='MonoBehaviour':continue
   sh=ob.read_typetree()
   if 'm_Rules' not in sh:continue
   edits=0
   for r in sh['m_Rules']:
    for p in r['m_Properties']:
     key=p.get('m_CustomName','')
     if key in ['--buttons-toggle-active-primary-surface','--buttons-toggle-active-primary-hover']:
      p['m_Values']=[Styles(sh).h(4,color('078BC4' if key.endswith('surface') else '119DD5'))];edits+=1
   if sh['m_Name']=='AlwaysAppliedStyleSheet':
    for a in active:
     append_rule(sh,[a,a+':hover'],[(458752,color('078BC4'))])
     append_rule(sh,[a+' .sigradient',a+' SIGradient'],[('--start-colour',color('35C6E8')),('--end-colour',color('078BC4')),(458767,1.)])
    append_rule(sh,['#playpause.simenubaritem','#playpause.simenubaritem:hover','#playpause.simenubaritem:active'],[(458752,color('078BC4'))])
    edits+=1
   if edits:ob.save_typetree(sh);expected[ob.path_id]=sh;changes.append({'folder':str(folder),'bundle':bn,'sheet':sh['m_Name'],'changes':edits})
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/bn]).objects};assert set(check)==set(orig)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert o.get_raw_data()==orig[pid].get_raw_data()
  payloads[folder/bn]=data
 e=UnityPy.load(before[folder/M]);oo={o.path_id:o for o in e.objects};expected={}
 ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='DefaultMatchUI');d=ob.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};nodes=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='playpause'];assert len(nodes)==1
 so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();Styles(sh).edit(nodes[0],[Styles(sh).p(458752,Styles(sh).h(4,color('078BC4')))])
 for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
 data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/M]).objects};assert set(check)==set(orig)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/M]=data
out=R/('match-segment-lake-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
