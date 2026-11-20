from pathlib import Path
import copy,json,datetime
R=Path.cwd();src=(R/'patch-preferences-lake-gradient.py').read_text('utf8');exec(compile(src[:src.index("W='ui-visualtree")],'<audit-helpers>','exec'))
before={f/S:(f/S).read_bytes() for f in [GAME,SKIN]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
for p,raw in before.items():
 e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};original={i:o.get_raw_data() for i,o in oo.items()};ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');s=ob.read_typetree();fixed=0
 for rule in reversed(s['m_Rules']):
  sels=rule.get('m_ComplexSelectors',[])
  if not sels or not all('buttons-dropdown-icon-base-responsibilities-primary' in json.dumps(x) and 'si-dropdown__selection-field' in json.dumps(x) for x in sels):continue
  ps=[q for q in rule['m_Properties'] if q['m_Id']==458752]
  if not ps:continue
  ps[0]['m_Values']=[Styles(s).h(4,color('315461'))];fixed+=1;break
 assert fixed==1
 ob.save_typetree(s);data=e.file.save(packer='lz4')
 for o in UnityPy.load(data).objects:
  if o.path_id==ob.path_id:assert o.read_typetree()==s
  else:assert o.get_raw_data()==original[o.path_id]
 payloads[p]=data;changes.append({'target':str(p),'employee_dropdown':'#315461'})
out=R/('employee-muted-lake-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8');print(out)
