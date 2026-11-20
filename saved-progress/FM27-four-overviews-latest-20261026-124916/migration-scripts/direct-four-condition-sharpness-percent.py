from pathlib import Path
import re,struct
boot=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','direct-four-condition-sharpness-percent-')
exec(compile(boot,'backup-and-helpers','exec'))
B='ui-backgrounds_assets_common.bundle'
bg=UnityPy.load(str(GAME/B));cab=bg.assets[0].name
textures={o.peek_name():o.path_id for o in bg.objects if o.type.name=='Texture2D' and o.peek_name().startswith('FM27StatusRingCW')}
assert len(textures)==101
def threshold(data):
 b=bytes(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);p=1;args=[]
 for _ in range(b[0]):
  size=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+size]);p+=size
 return struct.unpack_from('<i',args[1],len(args[1])-4)[0]
audits=[]
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree()
 fid=next(i+1 for i,e in enumerate(objs[W][pid].assets_file.externals) if e.name.lower()==cab.lower());changed_records=set();rings=0;numbers=0
 for i,r in rr.items():
  d=sd(i);name=d.get('name','')
  if not name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')):continue
  m=re.search(r'_Ring(\d{3})$',name)
  if m:
   pct=int(m[1]);ptr={'m_FileID':fid,'m_PathID':textures[f'FM27StatusRingCW{pct:03}']}
   if ptr not in sheet['assets']:sheet['assets'].append(ptr)
   override(r['data'],[prop(458753,{'m_ValueType':6,'valueIndex':sheet['assets'].index(ptr)})]);changed_records.add(i);rings+=1
  m=re.search(r'_Number(\d{3})$',name)
  if m:d['text']=str(int(m[1]))+'%';changed_records.add(r['data']['m_SerializedData']['rid']);numbers+=1
 assert rings==202 and numbers==202,(rings,numbers)
 for i,r in old.items():
  if i not in changed_records:assert rr[i]==r,('unrelated UI record changed',pid,i)
 def select(i,value):
  a=rr[i]['data']
  if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':return select(a['m_Children'][int(value is not None and value>threshold(sd(i)))]['rid'],value)
  return i
 for metric in ['Condition','Sharpness']:
  root=named('OverviewFitness_'+metric+'_Available')
  for raw in range(101):
   leaf=select(root,raw);children=rr[leaf]['data']['m_Children'];ring=next(c['rid'] for c in children if re.search(r'_Ring\d{3}$',sd(c['rid']).get('name','')));number=next(c['rid'] for c in children if re.search(r'_Number\d{3}$',sd(c['rid']).get('name','')))
   assert sd(number)['text']==f'{raw}%'
   prop0=next(p for p in sheet['m_Rules'][rr[ring]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458753)
   assert sheet['assets'][prop0['m_Values'][0]['valueIndex']]=={'m_FileID':fid,'m_PathID':textures[f'FM27StatusRingCW{raw:03}']}
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet
 audits.append({'page':str(pid),'inlineStyle':str(sid),'checked_values_per_metric':101,'rings':rings,'numbers':numbers})
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'mapping':'UI value 0..100 -> same percentage; 1=1%,100=100%','pages':audits,'fatigue_and_missing_bindings_unchanged':True,'backgrounds_global_layout_catalog_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
(OUT/'restore.ps1').write_text('\n'.join(['$ErrorActionPreference = "Stop"']+["Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force" for p in before]),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'versions':4,'checks':808}))
