from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};counts=[]
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]:
  d=oo[pid].read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();root=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='PopupFourRowsSeasonStats');todo=[root['rid']];count=0
  while todo:
   r=rr[todo.pop()];a=r['data'];todo.extend(c['rid'] for c in a.get('m_Children',[]));ix=a.get('m_RuleIndex',-1)
   if a.get('m_FullTypeName')!='SI.Bindable.SIText' or ix<0:continue
   rule=s['m_Rules'][ix];font=next((p for p in rule['m_Properties'] if p['m_Id']==65537),None)
   if not font:continue
   h=font['m_Values'][0];assert h['m_ValueType']==3;old=s['dimensions'][h['valueIndex']]['value'];assert old in [9,12],old
   new=12 if old==9 else 18
   s['dimensions'].append({'unit':1,'value':float(new)});font['m_Values']=[{'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}]
   # Keep the larger title and value inside each 50px row.
   for key,value in [(131087,20 if old==9 else 26),(131096,20 if old==9 else 26)]:
    prop=next((p for p in rule['m_Properties'] if p['m_Id']==key),None)
    if prop is not None:
     s['dimensions'].append({'unit':1,'value':float(value)});prop['m_Values']=[{'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}]
   count+=1
  assert count>=24,count;so.save_typetree(s);changed[so.path_id]=s;counts.append({'name':d['m_Name'],'enlarged_texts':count})
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True)
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'routes':counts})
out=R/('popup-season-stats-larger-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'title_design_font':12,'value_design_font':18,'title_display_font':10.2,'value_display_font':15.3,'four_rows_three_columns_preserved':True,'audits':audits};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
