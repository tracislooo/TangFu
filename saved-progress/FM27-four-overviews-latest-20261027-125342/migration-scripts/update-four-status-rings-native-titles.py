from pathlib import Path
import ast,copy,json,math,struct,re,colorsys
boot=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','four-status-rings-native-translations-')
exec(compile(boot,'backup-and-helpers','exec'))
from PIL import Image,ImageDraw,ImageFont
from UnityPy.export.Texture2DConverter import image_to_texture2d
B='ui-backgrounds_assets_common.bundle'
for folder in [GAME,SKIN]:
 p=folder/B;before[p]=p.read_bytes();protected.pop(p,None);(OUT/('backup-game' if folder==GAME else 'backup-skin')/B).write_bytes(before[p])
assert before[GAME/B]==before[SKIN/B]
env[B]=UnityPy.load(before[GAME/B]);objs[B]={o.path_id:o for o in env[B].objects};hashes[B]={i:sha(o.get_raw_data()) for i,o in objs[B].items()};changed[B]={}
# Use native data-collection/column declarations as scale and localization evidence.
collections={};titles={}
for o in UnityPy.load(str(GAME/'ui-datacollections_assets_all.bundle')).objects:
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['RawConditionDataCollection','SharpnessDataCollection','FatigueDataCollection']:
  d=o.read_typetree();r=refs(d);collections[d['m_Name']]=r[d['m_keyColumn']['rid']]['data']['m_rows']
for o in UnityPy.load(str(GAME/'ui-tablefactories_assets_all.bundle')).objects:
 if o.type.name!='MonoBehaviour' or o.peek_name()!='PlayerTableFactory':continue
 def walk(v):
  if isinstance(v,dict):
   if v.get('m_id') in ['condition-icon','match-sharpness','fatigue-icon']:titles[v['m_id']]=v['m_translationID']['GameID']
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(o.read_typetree())
assert titles=={'condition-icon':3250,'fatigue-icon':3251,'match-sharpness':3252}
# Rasterize mathematical UI rings; existing background images are never edited.
textures={};images={};af=env[B].assets[0];template=next(o for o in objs[B].values() if o.type.name=='Texture2D' and o.peek_name()=='FitnessPercentRing100');td=template.read_typetree();metaobj=next(o for o in objs[B].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();(OUT/'textures').mkdir()
def ring(pct,direction,missing=False):
 scale=10;size=26*scale;c=size/2;r=(13-1-3.5/2)*scale;width=3.5*scale
 im=Image.new('RGBA',(size,size));draw=ImageDraw.Draw(im)
 color=tuple(round(v*255) for v in colorsys.hsv_to_rgb(pct/300,.75,.88))
 track=(65,70,78,255)
 def arc(fraction,fill,sign):
  if fraction<=0:return
  steps=max(2,round(720*fraction));points=[(c+r*math.cos(math.radians(-90+sign*360*fraction*j/steps)),c+r*math.sin(math.radians(-90+sign*360*fraction*j/steps))) for j in range(steps+1)]
  draw.line(points,fill=fill,width=round(width),joint='curve')
  for x,y in [points[0],points[-1]]:draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=fill)
 arc(1,track,1)
 if not missing:
  if pct==0:
   # Empty progress remains empty; a red start marker makes the zero state explicit.
   draw.ellipse((c-width*.22,c-r-width*.22,c+width*.22,c-r+width*.22),fill=color+(255,))
  else:arc(pct/100,color+(255,),1 if direction=='CW' else -1)
 return im.resize((68,68),Image.Resampling.LANCZOS)
nextpid=-940000000017000
for direction,pct in [(a,b) for a in ['CW','CCW'] for b in range(101)]+[('Missing',0)]:
 name=f'FM27StatusRing{direction}{pct:03}';im=ring(pct,direction,direction=='Missing');pid=nextpid;nextpid-=1;assert pid not in objs[B]
 data=copy.deepcopy(td);pixels,fmt=image_to_texture2d(im,4,template.platform,data['m_PlatformBlob']);data.update(m_Name=name,m_Width=68,m_Height=68,m_TextureFormat=4,m_MipCount=1,m_CompleteImageSize=len(pixels),m_IsAlphaChannelOptional=False);data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
 obj=copy.copy(template);obj.path_id=pid;af.objects[pid]=obj;objs[B][pid]=obj;obj.save_typetree(data);changed[B][pid]=data;textures[(direction,pct)]=pid;images[(direction,pct)]=im
 ptr={'m_FileID':0,'m_PathID':pid};meta['m_Container'].append((name.lower(),{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':1,'asset':ptr}));meta['m_PreloadTable'].append(ptr);im.save(OUT/'textures'/(name+'.png'))
meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed[B][metaobj.path_id]=meta
bio=objs[W][-2572099601129076466].read_typetree();br=refs(bio)
serial=lambda r,i:r[r[i]['data']['m_SerializedData']['rid']]
translation=copy.deepcopy(serial(br,1078)['data']['TextBinding'])
def native_title(data,tid):
 b=copy.deepcopy(translation);raw=bytearray(b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);pos=raw.index(ord(']'))+1;struct.pack_into('<i',raw,pos,tid);b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw);data.update(TextBinding=b,TextBinding_UxmlAttributeFlags=1,text='',text_UxmlAttributeFlags=0,tooltip='',tooltip_UxmlAttributeFlags=0,DebugDisplay='')
def args_decode(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):
  size=struct.unpack_from('<I',b,p)[0];p+=4;out.append(bytearray(b[p:p+size]));p+=size
 assert p==len(b);return out
def encode_args(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(v))+v for v in args))
def threshold_data(data,limit):
 b=data['Binding']['m_visualFunction']['m_inputs']['m_variable'];a=args_decode(b['m_argumentBytes']);struct.pack_into('<i',a[1],len(a[1])-4,limit);b['m_argumentBytes']=encode_args(a)
def threshold(data):
 a=args_decode(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);return struct.unpack_from('<i',a[1],len(a[1])-4)[0]
def image_style(i,key):
 if key not in handles:
  sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[key]});handles[key]={'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}
 override(rr[i]['data'],[prop(458753,handles[key])])
pagechecks=[]
for pid,sid in [(-930000000001001,-930000000001000),(-930000000001003,-930000000001002),(-940000000010000,-940000000010001),(-940000000012000,-940000000012001)]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;handles={}
 fileid=next(i+1 for i,e in enumerate(objs[W][pid].assets_file.externals) if e.name.lower()==af.name.lower())
 assert serial(rr,1097)['data']['TextBinding']['m_direct']['Path']['m_path']=='Person.BiographyMilestonesString'
 assert serial(rr,6280)['data']['TextBinding']['m_direct']['Path']['m_path']=='Person.BiographyCareerStatsString'
 native_title(sd(1096),4549);native_title(sd(6296),4548)
 for key,tid in [('Condition',3250),('Sharpness',3252),('Fatigue',3251)]:native_title(sd(named('OverviewFitness_'+key+'_Title')),tid)
 for i,r in list(rr.items()):
  a=r.get('data',{});d=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=d.get('name','')
  if name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')):
   if '_MissingRing' in name:image_style(i,('Missing',0))
   else:
    m=re.search(r'_Ring(\d{3})$',name)
    if m:image_style(i,('CW',max(0,min(100,(int(m[1])-50)*2))))
    m=re.search(r'_Number(\d{3})$',name)
    if m:d['text']=str(max(0,min(100,(int(m[1])-50)*2)))+'%'
  if name.startswith('OverviewFitness_Fatigue_HealthRing'):
   if name.endswith('Missing'):image_style(i,('Missing',0))
   else:
    m=re.search(r'Ring(\d{3})$',name)
    if m:image_style(i,('CCW',int(m[1])))
 # Add a negative-fatigue branch before the old positive tree, keeping the raw number unchanged.
 gate=named('OverviewFitness_Fatigue_HealthRingAvailable');missing=rr[gate]['data']['m_Children'][0]['rid'];positive=rr[gate]['data']['m_Children'][1]['rid'];prototype=copy.deepcopy(old[positive]);prototype_sd=copy.deepcopy(serial(old,positive));leaf=named('OverviewFitness_Fatigue_HealthRing100');leaf_node=copy.deepcopy(old[leaf]);leaf_sd=copy.deepcopy(serial(old,leaf))
 sign=add_pair(prototype,prototype_sd,gate,'OverviewFitness_Fatigue_DirectionBySign');rr[sign]['data']['m_RuleIndex']=old[positive]['data']['m_RuleIndex'];threshold_data(sd(sign),-1)
 negative_leaves={}
 def build(parent,lo,hi):
  if lo==hi:
   i=add_pair(leaf_node,leaf_sd,parent,f'OverviewFitness_Fatigue_NegativeHealthRing{lo:03}');rr[i]['data']['m_RuleIndex']=old[leaf]['data']['m_RuleIndex'];image_style(i,('CW',lo));negative_leaves[i]=lo;return i
  mid=(lo+hi)//2;i=add_pair(prototype,prototype_sd,parent,f'OverviewFitness_Fatigue_NegativeAbove{-498+5*mid}');rr[i]['data']['m_RuleIndex']=old[positive]['data']['m_RuleIndex'];threshold_data(sd(i),-498+5*mid);build(i,lo,mid);build(i,mid+1,hi);return i
 negative=build(sign,0,100);rr[positive]['data']['m_Parent']={'rid':sign};rr[sign]['data']['m_Children'].append({'rid':positive});rr[gate]['data']['m_Children']=[{'rid':missing},{'rid':sign}]
 # The third version alone changes its bans/radar width ratio.
 if pid==-940000000010000:
  for i,grow in [(6228,2),(1026,3)]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(grow)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0))])
 def select(i,value):
  a=rr[i]['data'];data=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':return select(a['m_Children'][int(value is not None and value>threshold(data))]['rid'],value)
  return i
 count=0
 for raw in [None,-2147483648]+list(range(-650,1201)):
  selected=select(gate,raw)
  if raw in [None,-2147483648]:assert selected==missing
  elif raw<0:assert negative_leaves[selected]==max(0,min(100,(raw+502)//5)),raw
  else:assert sd(selected)['name']==f'OverviewFitness_Fatigue_HealthRing{100-max(0,min(100,(raw+5)//10)):03}',raw
  count+=1
 for metric in ['Condition','Sharpness']:
  root=named('OverviewFitness_'+metric+'_Available')
  for raw in [None,-1]+list(range(0,121)):
   chosen=select(root,raw)
   if raw is None or raw<0:continue
   texts=[sd(c['rid']).get('text') for c in rr[chosen]['data']['m_Children']]
   expected=max(0,min(100,(raw-50)*2));assert str(expected)+'%' in texts,(metric,raw,texts)
 assert serial(rr,named('OverviewFitness_Fatigue_RawValue'))==serial(old,named('OverviewFitness_Fatigue_RawValue'))
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet
 pagechecks.append({'page':pid,'fatigue_cases':count,'normalized_condition_range':[50,100],'display_range':[0,100],'native_translation_ids':[4548,4549,3250,3252,3251]})
# Keep a readable visual check using the exact generated assets.
preview=Image.new('RGB',(760,230),'#171b23');draw=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for j,(title,pct,direction) in enumerate([('0%',0,'CW'),('50%',50,'CW'),('100%',100,'CW'),('Fatigue +500',50,'CCW'),('Fatigue -250',50,'CW')]):
 im=images[(direction,pct)].resize((104,104),Image.Resampling.LANCZOS);x=24+j*148;preview.paste(im,(x,40),im);draw.text((x+52,166),title,font=font,fill='white',anchor='mm')
preview.save(OUT/'ring-preview.png')
outputs={n:env[n].file.save(packer='lz4') for n in [W,B]}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
# Verify selected decoded texture colors, transparency, and arc orientation survive bundling.
bgcheck={o.path_id:o for o in UnityPy.load(outputs[B]).objects}
for key in [('CW',0),('CW',1),('CW',50),('CW',99),('CW',100),('CCW',50),('Missing',0)]:assert bgcheck[textures[key]].read().image.convert('RGBA').tobytes()==images[key].tobytes()
report={'installed':False,'runtime_verified':False,'versions':4,'pages':pagechecks,'native_title_evidence':titles,'native_scale_evidence':collections,
 'condition_sharpness':'5000->0%,10000->100%; current UI-normalized fields 50->0%,100->100%',
 'fatigue':'raw number preserved; at 0 ring=100%; positive depletes clockwise to 0 at1000; negative depletes counterclockwise to0 at-500',
 'circle_colours':'red at0%, yellow at50%, green at100%; no data gray',
 'third_bans_radar_ratio':[2,3],'added_ring_textures':203,'existing_background_images_preserved':True,
 'catalog_global_and_tilelayouts_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'versions':4,'fatigue_cases':sum(x['fatigue_cases'] for x in pagechecks),'native_titles':titles,'ring_textures':203}))
