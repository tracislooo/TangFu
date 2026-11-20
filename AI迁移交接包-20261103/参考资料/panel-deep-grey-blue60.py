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

C='ui-styles_assets_common.bundle';before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [S,C]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
roles={'--layout-ui-tiles-dark-background','--layout-modules-tiles-background','--layout-ui-cards-light-background','--layout-ui-cards-dark-background','--cards-background','--layout-ui-tiles-light-background','--layout-modules-block-surface','--layout-surfaces-cards-surface','--layout-modules-tiles-interaction-surface-default','--layout-modules-tiles-interaction-surface-hover','--layout-modules-tiles-interaction-surface-pressed'}
for folder in [GAME,SKIN]:
 envs={bn:UnityPy.load(before[folder/bn]) for bn in [S,C]};defs={}
 for bn,e in envs.items():
  for ob in e.objects:
   if ob.type.name!='MonoBehaviour':continue
   sh=ob.read_typetree()
   for r in sh.get('m_Rules',[]):
    for p in r['m_Properties']:
     if p.get('m_CustomName'):defs[p['m_CustomName']]=(sh,p)
 def resolve(sh,p,seen=()):
  hs=p['m_Values']
  if len(hs)==1 and hs[0]['m_ValueType']==4:return copy.deepcopy(sh['colors'][hs[0]['valueIndex']])
  for h in hs:
   if h['m_ValueType']==8:
    k=sh['strings'][h['valueIndex']]
    if k in defs and k not in seen:return resolve(*defs[k],seen+(k,))
  return None
 for bn,e in envs.items():
  oo={o.path_id:o for o in e.objects};expected={}
  for ob in oo.values():
   if ob.type.name!='MonoBehaviour':continue
   sh=ob.read_typetree()
   if 'm_Rules' not in sh:continue
   old=copy.deepcopy(sh)
   for i,r in enumerate(sh['m_Rules']):
    for p in r['m_Properties']:
     if p.get('m_CustomName') not in roles:continue
     c=resolve(old,p)
     if c and c['a']>.6001 and max(c['r'],c['g'],c['b'])<.25:
      previous=copy.deepcopy(c);c.update(color('263445'));c['a']=struct.unpack('<f',struct.pack('<f',.6))[0];p['m_Values']=[Styles(sh).h(4,c)];changes.append({'target':str(folder/bn),'sheet':sh['m_Name'],'role':p['m_CustomName'],'before':previous,'after':c})
   if sh!=old:ob.save_typetree(sh);expected[ob.path_id]=sh
  if not expected:continue
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/bn]).objects};assert set(check)==set(orig)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert o.get_raw_data()==orig[pid].get_raw_data()
  payloads[folder/bn]=data
out=R/('panel-deep-grey-blue60-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
