from pathlib import Path
import copy,json,datetime,struct
R=Path(__file__).resolve().parent
src=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8')
exec(compile(src.split('payloads={};changes={}')[0],'<current-resource-audit>','exec'))
C='ui-styles_assets_common.bundle';names={S,C}
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in names}
protected={p:h for p,h in protected.items() if Path(p) not in before}
payloads={};changes=[]
def target(sel):
 parts={p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']}
 if 'sub-dropdown-content-container' in parts and 'hover' in parts:return '067BAE'
 if 'navigation-dropdown-menu_item_base-default' in parts:
  if 'hover' in parts or 'active' in parts:return '078BC4'
 if 'buttons-dropdown-icon-base-responsibilities-primary' in parts and 'si-dropdown__selection-field' in parts:return '35C6E8'
 if 'si-dropdown' in parts or 'cascading-menu__folder__entry' in parts or 'routine-dropdown-item__selected' in parts:
  if 'hover' in parts or 'visual-highlighted' in parts:return '35C6E8'
  if 'active' in parts or 'routine-dropdown-item__selected' in parts:return '078BC4'
 return None
for path,raw in before.items():
 e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};count=0
 for ob in oo.values():
  if ob.type.name!='MonoBehaviour':continue
  d=ob.read_typetree()
  if 'm_Rules' not in d:continue
  original=copy.deepcopy(d);newrules=[]
  for idx,r in enumerate(d['m_Rules']):
   groups={}
   for sel in r.get('m_ComplexSelectors',[]):
    code=target(sel)
    if code:groups.setdefault(code,[]).append(sel)
   if not groups:continue
   ps=[p for p in r['m_Properties'] if p['m_Id']==458752]
   if not ps:continue
   assert len(ps)==1
   selected=[s for g in groups.values() for s in g]
   r['m_ComplexSelectors']=[s for s in r['m_ComplexSelectors'] if s not in selected]
   for code,sels in groups.items():
    nr=copy.deepcopy(original['m_Rules'][idx]);nr['m_ComplexSelectors']=copy.deepcopy(sels)
    col=dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',int(code[i:i+2],16)/255))[0] for i in [0,2,4]]+[1.]))
    d['colors'].append(col)
    for p in nr['m_Properties']:
     if p['m_Id']==458752:p['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}]
    newrules.append(nr);changes.append({'target':str(path),'sheet':d['m_Name'],'original_rule':idx,'color':'#'+code,'selectors':sels});count+=1
  if newrules:
   for nr in newrules:
    for sel in nr['m_ComplexSelectors']:sel['ruleIndex']=len(d['m_Rules'])
    d['m_Rules'].append(nr)
   # Existing property values and all non-target selectors remain unchanged.
   assert d['colors'][:len(original['colors'])]==original['colors']
   for idx,r in enumerate(original['m_Rules']):assert d['m_Rules'][idx]['m_Properties']==r['m_Properties']
   ob.save_typetree(d);changed[ob.path_id]=d
 assert count>=(3 if path.name==C else 9),(path,count)
 data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};assert set(check)==set(oo)
 for pid,o in check.items():
  if pid in changed:assert o.read_typetree()==changed[pid]
  else:assert sha(o.get_raw_data())==hashes[pid]
 payloads[path]=data
out=R/('dropdown-lake-blue-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,data in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dest=out/tag/p.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
 backup=out/('backup-'+tag)/p.name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(before[p]);tx['sources'][str(p)]=str(dest);tx['before'][str(p)]=str(backup)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits,'active_textures_verified':len(registry['textures']),'unrelated_objects_unchanged':True}
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
for n,flag in [('install',''),('restore',' --restore')]:
 (out/(n+'.ps1')).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"'"+flag+'\n', 'utf8')
for p,b in before.items():assert p.read_bytes()==b,p
print(json.dumps({'output':str(out),'changed_rules':len(changes),'audits':audits},ensure_ascii=False))

