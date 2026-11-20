"""Set the scoped primary-menu font to 70% of its original 16px size."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
setup=(R/'change-staff-shortcut-to-recruitment-database.py').read_text('utf8').split('nav=UnityPy.load')[0]
exec(compile(setup,'resource-initialization-only','exec'))
S='ui-styles_assets_default.bundle'
before={f/S:(f/S).read_bytes() for f in [GAME,SKIN]}
for p in before:protected.pop(p,None)
for f in [GAME,SKIN]:protected[f/W]=sha((f/W).read_bytes())
new_size=struct.unpack('<f',struct.pack('<f',16*.7))[0]
outputs={};reports=[]
for folder in [GAME,SKIN]:
 env=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 obj=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');doc=obj.read_typetree();old=copy.deepcopy(doc)
 matches=[]
 for index,rule in enumerate(doc['m_Rules']):
  for sel in rule['m_ComplexSelectors']:
   parts=[[(p['m_Value'],p['m_Type']) for p in s['m_Parts']] for s in sel['m_Selectors']]
   if parts==[[('MainNav',6)],[('MenuBar',6)],[('portal-text',3)]]:matches.append(index)
 assert len(matches)==1,matches
 index=matches[0];prop=next(p for p in doc['m_Rules'][index]['m_Properties'] if p['m_Id']==65537)
 assert len(prop['m_Values'])==1 and prop['m_Values'][0]['m_ValueType']==3
 old_size=doc['dimensions'][prop['m_Values'][0]['valueIndex']]['value']
 doc['dimensions'].append({'unit':1,'value':new_size});prop['m_Values']=[{'m_ValueType':3,'valueIndex':len(doc['dimensions'])-1}]
 expected=copy.deepcopy(old);expected['dimensions']=doc['dimensions'];expected['m_Rules'][index]=doc['m_Rules'][index];assert doc==expected
 obj.save_typetree(doc);raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==obj.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i]
 outputs[folder/S]=raw;reports.append({'target':str(folder/S),'previous_px':old_size,'new_px':new_size,'original_px':16,'ratio':.7,'scope':'#MainNav #MenuBar .portal-text','other_styles_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-font70-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/S;bak=out/('backup-'+tag)/S;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(raw);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'changes':reports}))
