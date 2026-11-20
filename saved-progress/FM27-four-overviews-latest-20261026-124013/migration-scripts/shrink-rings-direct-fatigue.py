from pathlib import Path
import math
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont
from UnityPy.export.Texture2DConverter import image_to_texture2d

BN='ui-backgrounds_assets_common.bundle'
before.update({p/BN:(p/BN).read_bytes() for p in [GAME,SKIN]})
assert before[GAME/BN]==before[SKIN/BN]
protected.pop(GAME/BN)
bgobjects={o.path_id:o for o in be.objects}
bghashes={pid:sha(o.get_raw_data()) for pid,o in bgobjects.items()}
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('compact-rings-direct-fatigue-'+stamp);out.mkdir();(out/'textures').mkdir()
changedtextures={};images={}
for percent in range(101):
 name=f'FitnessPercentRing{percent:03}';obj=names[name];td=obj.read_typetree()
 scale=12;size=26*scale;width=3.5*scale;center=size/2;radius=(26/2-1.0-3.5/2)*scale
 im=Image.new('RGBA',(size,size));draw=ImageDraw.Draw(im)
 for fraction,fill in [(1.,'#41464e'),(percent/100,'#d4de53')]:
  if fraction==0:continue
  points=[]
  for i in range(max(2,round(720*fraction))+1):
   a=math.radians(-90+360*fraction*i/max(2,round(720*fraction)))
   points.append((center+radius*math.cos(a),center+radius*math.sin(a)))
  draw.line(points,fill=fill,width=round(width),joint='curve')
  for x,y in [points[0],points[-1]]:draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=fill)
 im=im.resize((68,68),Image.Resampling.LANCZOS);im.save(out/'textures'/(name+'.png'))
 pixels,fmt=image_to_texture2d(im,4,obj.platform,td['m_PlatformBlob']);assert int(fmt)==4
 td.update(m_TextureFormat=4,m_MipCount=1,m_CompleteImageSize=len(pixels));td['image data']=pixels;td['m_StreamData']={'offset':0,'size':0,'path':''}
 obj.save_typetree(td);changedtextures[obj.path_id]=td;images[percent]=im
bgoutput=be.file.save(packer='lz4');savedbg={o.path_id:o for o in UnityPy.load(bgoutput).objects}
for pid,h in bghashes.items():
 if pid in changedtextures:assert savedbg[pid].read_typetree()==changedtextures[pid]
 else:assert sha(savedbg[pid].get_raw_data())==h,pid
for percent,im in images.items():assert savedbg[names[f'FitnessPercentRing{percent:03}'].path_id].read().image.convert('RGBA').tobytes()==im.tobytes()

# Remove the fatigue conversion tree entirely. The number now reads the native value directly.
fatigue=named('OverviewFitness_Fatigue')['rid'];title=named('OverviewFitness_Fatigue_Title')['rid']
removed=set()
def collect(i):
 a=rr[i]['data'];removed.add(i);removed.add(a['m_SerializedData']['rid'])
 for c in a.get('m_Children',[]):collect(c['rid'])
for c in rr[fatigue]['data']['m_Children']:
 if c['rid']!=title:collect(c['rid'])
rr[fatigue]['data']['m_Children']=[{'rid':title}]
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed:del rr[i]
direct=text(fatigue,'OverviewFitness_Fatigue_RawValue',0,10,70,28,14,path='person.Fatigue',center=True)
assert rr[rr[direct]['data']['m_SerializedData']['rid']]['data']['TextBinding']['m_kind']==1
doc['references']['RefIds'].extend(new)

# Keep the existing first two metric bindings; adjust only their geometry.
for r in list(rr.values()):
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if not name.startswith('OverviewFitness_'):continue
 if ('_Ring' in name or '_MissingRing' in name) and name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')):
  st(r['rid'],[(131089,px(22)),(131105,px(26)),(131087,px(26))])
 elif ('_Number' in name or '_MissingNumber' in name) and name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')):
  st(r['rid'],[(131104,px(28))])
 elif name.endswith('_Title'):st(r['rid'],[(131104,px(44))])
 elif name in ['OverviewFitness_Condition','OverviewFitness_Sharpness','OverviewFitness_Fatigue']:st(r['rid'],[(131087,px(58))])
 elif name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')):
  st(r['rid'],[(131087,px(44))])
st(named('OverviewFitnessPercentRow')['rid'],[(131087,px(58))])
st(named('OverviewHiddenAttributesPanel')['rid'],[(131087,px(230)),(131096,px(230))])

# No remaining fatigue switches, percentages, or ring nodes may be reachable.
allnames=[r.get('data',{}).get('name','') for r in rr.values()]
assert not any(n.startswith('OverviewFitness_Fatigue_') and any(t in n for t in ['Percent','Above','Ring','Number']) for n in allnames)
rawsd=rr[rr[direct]['data']['m_SerializedData']['rid']]['data']
assert rawsd['TextBinding']['m_direct']=={'Path':{'m_path':'person.Fatigue'},'Nullable':1}
assert rawsd['text']=='' and rawsd['text_UxmlAttributeFlags']==0
for key in ['Condition','Sharpness']:
 for p in [0,1,50,99,100]:
  ringnode=named(f'OverviewFitness_{key}_Ring{p:03}')
  assert dimension(ringnode,131105)==dimension(ringnode,131087)==26
  num=named(f'OverviewFitness_{key}_Number{p:03}')
  assert rr[num['data']['m_SerializedData']['rid']]['data']['text']==str(p)+'%'
  assert dimension(num,131104)==28
for i in old_refs:
 if i in removed:continue
 if 'UxmlSerializedData' in old_refs[i].get('type',{}).get('class',''):assert rr[i]==old_refs[i],i
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
uioutput=env.file.save(packer='lz4');savedui={o.path_id:o for o in UnityPy.load(uioutput).objects}
for pid,h in old_hashes.items():
 if pid in [FULL,sid]:assert savedui[pid].read_typetree()=={FULL:doc,sid:sheet}[pid]
 else:assert sha(savedui[pid].get_raw_data())==h,pid
validate_ui(savedui[FULL].read_typetree(),savedui[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for n in [WN,BN]:(backup/n).write_bytes(before[folder/n])
(out/WN).write_bytes(uioutput);(out/BN).write_bytes(bgoutput)
preview=Image.new('RGB',(630,210),'#22262d');pd=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27);nf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
for j,(label,value) in enumerate([('体能',92),('比赛状态',78),('疲劳',240)]):
 if j<2:
  im=images[value].resize((78,78),Image.Resampling.LANCZOS);preview.paste(im,(j*210+66,9),im)
 pd.text((j*210+105,118 if j<2 else 76),str(value)+('%' if j<2 else ''),font=nf,fill='white',anchor='mm')
 pd.text((j*210+105,165),label,font=font,fill='#a0a0a0',anchor='mm')
preview.save(out/'preview.png')
report={'installed':False,'runtime_verified':False,'ring_size':[26,26],'ring_stroke_px':3.5,'previous_ring_size':[34,34],'previous_stroke_px':2.5,'fatigue_display':'raw number, no percent sign or ring','fatigue_binding':'person.Fatigue','removed_fatigue_records':len(removed),'first_two_metrics_bindings_unchanged':True,'title_color':'#A0A0A0','before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{WN:sha(uioutput),BN:sha(bgoutput)}}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  for n,b in [(BN,bgoutput),(WN,uioutput)]:(folder/n).write_bytes(b);assert sha((folder/n).read_bytes())==sha(b)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'ring_size':[26,26],'stroke':3.5,'fatigue_binding':rawsd['TextBinding']['m_direct']},ensure_ascii=True))
