from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont

changed=[];numbers=[];titles=[];ringnodes=[]
for r in list(rr.values()):
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if not name.startswith('OverviewFitness_'):continue
 if '_Number' in name or '_MissingNumber' in name or name=='OverviewFitness_Fatigue_RawValue':
  st(r['rid'],[(131089,px(30)),(131104,px(4)),(131105,px(40)),(131087,px(16)),(65537,px(12)),(65536,color(255,255,255)),(65543,en('bold')),(65546,en('middle-left')),(65552,en('nowrap'))])
  numbers.append(r['rid']);changed.append(r['rid'])
 elif name.endswith('_Title'):
  gray=property_value(named('OverviewCurrentReputationTitle'),65536)
  st(r['rid'],[(131089,px(30)),(131104,px(22)),(131105,px(40)),(131087,px(14)),(65537,px(9)),(65536,val(4,copy.deepcopy(gray))),(65546,en('middle-left')),(65552,en('nowrap'))])
  titles.append(r['rid']);changed.append(r['rid'])
 elif name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')) and ('_Ring' in name or '_MissingRing' in name):
  st(r['rid'],[(131089,px(0)),(131104,px(7)),(131105,px(26)),(131087,px(26))])
  ringnodes.append(r['rid']);changed.append(r['rid'])
fatigategate=named('OverviewFitness_Fatigue_HealthRingAvailable')['rid']
st(fatigategate,[(131089,px(0)),(131104,px(7)),(131105,px(26)),(131087,px(26))]);changed.append(fatigategate)

# Inspect every leaf (including unavailable displays), every title and all three cells.
assert len(numbers)==205 and len(titles)==3 and len(ringnodes)==204
for i in numbers:
 n=rr[i];assert [dimension(n,p) for p in [131089,131104,131105,131087,65537]]==[30,4,40,16,12]
 assert property_value(n,65546)=='middle-left'
 assert property_value(n,65536)=={'r':1.,'g':1.,'b':1.,'a':1.}
for i in titles:
 n=rr[i];assert [dimension(n,p) for p in [131089,131104,131105,131087,65537]]==[30,22,40,14,9]
 assert property_value(n,65536)==property_value(named('OverviewCurrentReputationTitle'),65536)
for i in ringnodes+[fatigategate]:
 n=rr[i];assert [dimension(n,p) for p in [131089,131104,131105,131087]]==[0,7,26,26]
for ix,key in enumerate(['Condition','Sharpness','Fatigue']):
 n=named('OverviewFitness_'+key);assert dimension(n,131089)==ix*70 and dimension(n,131105)==70
 assert 30+40<=dimension(n,131105) and 22+14<=dimension(n,131087)
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('binding or text changed',i)
assert {i for i in rr if rr[i]!=old_refs[i]}==set(changed)
assert set(rr)==set(old_refs)
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in [FULL,sid]:assert saved[pid].read_typetree()=={FULL:doc,sid:sheet}[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('fitness-left-rings-right-text-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)

# Native-scale text width checks plus a diagram using the exact delivered textures.
fontcheck=[]
for face in ['C:/Windows/Fonts/msyh.ttc','C:/Windows/Fonts/arialbd.ttf']:
 f=ImageFont.truetype(face,12)
 for value in ['100%','1000']:
  width=f.getlength(value);assert width<=40,(face,value,width)
  fontcheck.append({'font':face,'text':value,'width':width,'available_width':40})
assert ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',9).getlength('比赛状态')<=40
preview=Image.new('RGB',(880,210),'#22262d');pd=ImageDraw.Draw(preview)
nf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',48);tf=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',36)
for j,(label,value,pct) in enumerate([('体能','92%',92),('比赛状态','78%',78),('疲劳','0',100)]):
 x=20+j*280;im=names[f'FitnessPercentRing{pct:03}'].read().image.convert('RGBA').resize((104,104),Image.Resampling.LANCZOS)
 preview.paste(im,(x,48),im);pd.text((x+120,68),value,font=nf,fill='white',anchor='lm');pd.text((x+120,132),label,font=tf,fill='#a0a0a0',anchor='lm')
preview.save(out/'preview.png')
report={'installed':False,'runtime_verified':False,'layout':'left ring, right value above title','cell_width':70,'ring_box':[0,7,26,26],'value_box':[30,4,40,16],'title_box':[30,22,40,14],'number_font':12,'title_font':9,'gap':4,'numbers_verified':len(numbers),'titles_verified':len(titles),'font_width_checks':fontcheck,'all_serialized_bindings_preserved':True,'fatigue_zero_is_best_preserved':True,'rotated_attribute_images_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'verified_number_nodes':len(numbers),'value_font_px':12,'ring_px':26,'long_text_checks_passed':True},ensure_ascii=True))
