from pathlib import Path
import math
R=Path(__file__).parent
# Load existing codecs and factories only, without running their installers.
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split("bar=named(")[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont
from UnityPy.export.Texture2DConverter import image_to_texture2d
from UnityPy.classes import PPtr

stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('fitness-percent-rings-'+stamp);out.mkdir();pngdir=out/'textures';pngdir.mkdir()
BN='ui-backgrounds_assets_common.bundle'
before.update({folder/BN:(folder/BN).read_bytes() for folder in [GAME,SKIN]})
assert before[GAME/BN]==before[SKIN/BN]
protected.pop(GAME/BN)
original_bg_hashes={o.path_id:sha(o.get_raw_data()) for o in be.objects}
bgobjects={o.path_id:o for o in be.objects}
bgtemplate=bgobjects[-910000000000001];bgtd=bgtemplate.read_typetree()
bgbundle=next(o for o in bgobjects.values() if o.type.name=='AssetBundle')
bgmeta=bgbundle.read_typetree();oldbgmeta=copy.deepcopy(bgmeta)
nextpid=min(bgobjects)-1;images={};addedtextures={}

# Validate numeric scales against the installed native collections.
collections={}
for o in UnityPy.load(str(GAME/'ui-datacollections_assets_all.bundle')).objects:
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['RawConditionDataCollection','SharpnessDataCollection','FatigueDataCollection']:
  d=o.read_typetree();rs={r['rid']:r for r in d['references']['RefIds']}
  collections[d['m_Name']]=rs[d['m_keyColumn']['rid']]['data']['m_rows']
assert max(collections['RawConditionDataCollection'])==100
assert max(collections['SharpnessDataCollection'])==100
assert max(collections['FatigueDataCollection'])==1000

def ring(percent):
 scale=8;size=34*scale;width=2.5*scale
 im=Image.new('RGBA',(size,size));draw=ImageDraw.Draw(im)
 inset=3.0*scale;bounds=(inset,inset,size-inset,size-inset)
 draw.ellipse(bounds,outline='#41464e',width=round(width))
 if percent==100:draw.ellipse(bounds,outline='#d4de53',width=round(width))
 elif percent>0:
  end=-90+360*percent/100
  draw.arc(bounds,-90,end,fill='#d4de53',width=round(width))
  radius=(size-2*inset)/2-width/2;center=size/2;cap=width/2
  for angle in [-90,end]:
   x=center+radius*math.cos(math.radians(angle));y=center+radius*math.sin(math.radians(angle))
   draw.ellipse((x-cap,y-cap,x+cap,y+cap),fill='#d4de53')
 return im.resize((68,68),Image.Resampling.LANCZOS)

for percent in range(101):
 name=f'FitnessPercentRing{percent:03}';assert name not in names
 im=ring(percent);im.save(pngdir/(name+'.png'));pid=nextpid;nextpid-=1
 pixels,fmt=image_to_texture2d(im,4,bgtemplate.platform,bgtd['m_PlatformBlob'])
 td=copy.deepcopy(bgtd);td.update(m_Name=name,m_Width=68,m_Height=68,m_TextureFormat=4,m_MipCount=1,m_CompleteImageSize=len(pixels),m_IsAlphaChannelOptional=False)
 td['image data']=pixels;td['m_StreamData']={'offset':0,'size':0,'path':''}
 obj=copy.copy(bgtemplate);obj.path_id=pid;obj.data=None;obj._read_until=None
 obj.save_typetree(td);bgaf.objects[pid]=obj
 ptr={'m_FileID':0,'m_PathID':pid}
 bgmeta['m_Container'].append((name.lower(),{'preloadIndex':len(bgmeta['m_PreloadTable']),'preloadSize':1,'asset':copy.deepcopy(ptr)}));bgmeta['m_PreloadTable'].append(ptr)
 textures[name]=pid;images[pid]=im;addedtextures[pid]=td
bgmeta['m_Container'].sort(key=lambda kv:kv[0]);bgbundle.save_typetree(bgmeta)
bgoutput=be.file.save(packer='lz4')
bgcheck={o.path_id:o for o in UnityPy.load(bgoutput).objects}
assert set(bgcheck)==set(bgobjects)|set(addedtextures)
for pid,h in original_bg_hashes.items():
 if pid!=bgbundle.path_id:assert sha(bgcheck[pid].get_raw_data())==h,pid
for pid,im in images.items():assert bgcheck[pid].read().image.convert('RGBA').tobytes()==im.tobytes()
assert bgcheck[bgbundle.path_id].read_typetree()==bgmeta
assert bgmeta['m_PreloadTable'][:len(oldbgmeta['m_PreloadTable'])]==oldbgmeta['m_PreloadTable']

panel=named('OverviewHiddenAttributesPanel')['rid']
assert dimension(rr[panel],131105)==210
assert dimension(named('OverviewHiddenAttributeRow2'),131104)+dimension(named('OverviewHiddenAttributeRow2'),131087)==168
st(panel,[(131087,px(238)),(131096,px(238))])
row=make(panel,'OverviewFitnessPercentRow',box(0,170,210,66))
gray=property_value(named('OverviewCurrentReputationTitle'),65536)
assert all(abs(gray[c]-160/255)<1e-6 for c in ['r','g','b']) and gray['a']==1
grayhandle=val(4,copy.deepcopy(gray))
def ringimage(parent,name,percent):
 sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[f'FitnessPercentRing{percent:03}']})
 return make(parent,name,box(18,0,34,34)+[prop(458753,{'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}),prop(262153,en('scale-to-fit'))])
def leaf(parent,key,percent):
 group=make(parent,f'OverviewFitness_{key}_Percent{percent:03}',box(0,0,70,52))
 ringimage(group,f'OverviewFitness_{key}_Ring{percent:03}',percent)
 text(group,f'OverviewFitness_{key}_Number{percent:03}',0,36,70,16,12,literal=str(percent)+'%',center=True)
 return group
def decision(parent,key,path,lo,hi,scale):
 if lo==hi:return leaf(parent,key,lo)
 mid=(lo+hi)//2
 limit=mid if scale==1 else (mid+1)*scale-scale//2-1
 switch=make(parent,f'OverviewFitness_{key}_Above{limit}',box(0,0,70,52),True,limit,path)
 decision(switch,key,path,lo,mid,scale);decision(switch,key,path,mid+1,hi,scale)
 return switch
metrics=[('Condition','体能','person.Condition',1,-1),('Sharpness','比赛状态','person.Sharpness',1,-1),('Fatigue','疲劳','person.Fatigue',10,-2147483648)]
roots={}
for index,(key,title,path,scale,minimum) in enumerate(metrics):
 cell=make(row,'OverviewFitness_'+key,box(index*70,0,70,66))
 titleid=text(cell,'OverviewFitness_'+key+'_Title',0,52,70,14,9,literal=title,center=True)
 st(titleid,[(65536,grayhandle)])
 gate=make(cell,'OverviewFitness_'+key+'_Available',box(0,0,70,52),True,minimum,path);roots[key]=gate
 missing=make(gate,'OverviewFitness_'+key+'_Missing',box(0,0,70,52))
 ringimage(missing,'OverviewFitness_'+key+'_MissingRing',0)
 text(missing,'OverviewFitness_'+key+'_MissingNumber',0,36,70,16,12,literal='--',center=True)
 decision(gate,key,path,0,100,scale)
doc['references']['RefIds'].extend(new)

# Check actual serialized switches and leaf contents for every source value.
def selected(i,value):
 a=rr[i]['data'];s=rr[a['m_SerializedData']['rid']]['data']
 if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack('<i',args[1][1])[0]
  return selected(a['m_Children'][int(value is not None and value>limit)]['rid'],value)
 return i
verified=0
for key,title,path,scale,minimum in metrics:
 for raw in [None,-2147483648]+list(range(-500,1202)):
  i=selected(roots[key],raw);a=rr[i]['data'];s=rr[a['m_SerializedData']['rid']]['data']
  expected=None if raw is None or raw<=minimum else min(100,max(0,(raw+(5 if scale==10 else 0))//scale))
  assert s['name']==f'OverviewFitness_{key}_'+('Missing' if expected is None else f'Percent{expected:03}'),(key,raw,s['name'],expected)
  img,txt=[rr[c['rid']] for c in a['m_Children']]
  assert rr[txt['data']['m_SerializedData']['rid']]['data']['text']==('--' if expected is None else str(expected)+'%')
  assert property_value(img,458753)=={'m_FileID':fileid,'m_PathID':textures[f'FitnessPercentRing{expected or 0:03}']}
  verified+=1
assert {i for i in old_refs if rr[i]!=old_refs[i]}=={panel}
validate_ui(doc,sheet)
entry=next(v for k,v in meta['m_Container'] if k==fullguid)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for pid in images:
 ptr={'m_FileID':fileid,'m_PathID':pid}
 if ptr not in span:span.append(ptr)
entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet);bundle.save_typetree(meta)
uioutput=env.file.save(packer='lz4');uicheck={o.path_id:o for o in UnityPy.load(uioutput).objects}
for pid,h in old_hashes.items():
 if pid in [FULL,sid,bundle.path_id]:assert uicheck[pid].read_typetree()=={FULL:doc,sid:sheet,bundle.path_id:meta}[pid]
 else:assert sha(uicheck[pid].get_raw_data())==h,pid
validate_ui(uicheck[FULL].read_typetree(),uicheck[sid].read_typetree())
resolved=UnityPy.load(uioutput,bgoutput);wf=next(a for a in resolved.assets if a.name==af.name)
for ptr in sheet['assets']:
 if ptr['m_PathID'] in images:assert PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=wf).deref().read().image.size==(68,68)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for n in [WN,BN]:(backup/n).write_bytes(before[folder/n])
(out/WN).write_bytes(uioutput);(out/BN).write_bytes(bgoutput)
report={'installed':False,'runtime_verified':False,'output':str(out),'panel_size':[210,238],'row_box':[0,170,210,66],'ring_size':[34,34],'title_color':'#A0A0A0','number_color':'#FFFFFF','metrics':[{'key':k,'title':t,'binding':p,'raw_scale':s,'minimum_exclusive':m} for k,t,p,s,m in metrics],'fatigue_percent':'clamp(floor((raw+5)/10),0,100)','native_scale_evidence':collections,'added_texture_count':101,'source_values_verified':verified,'unchanged_ui_objects':len(old_hashes)-3,'unchanged_background_objects':len(original_bg_hashes)-1,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{WN:sha(uioutput),BN:sha(bgoutput)}}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
# Generate a visual proof from decoded delivered textures at the actual layout coordinates.
preview=Image.new('RGB',(630,260),'#22262d');pd=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27);numfont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
for j,(key,title,path,scale,minimum) in enumerate(metrics):
 percent=[92,78,24][j];im=bgcheck[textures[f'FitnessPercentRing{percent:03}']].read().image.convert('RGBA').resize((102,102),Image.Resampling.LANCZOS)
 preview.paste(im,(j*210+54,18),im);pd.text((j*210+105,150),str(percent)+'%',font=numfont,fill='white',anchor='mm');pd.text((j*210+105,203),title,font=font,fill='#a0a0a0',anchor='mm')
preview.save(out/'preview.png')
try:
 for folder in [GAME,SKIN]:
  for n,data in [(BN,bgoutput),(WN,uioutput)]:(folder/n).write_bytes(data);assert (folder/n).read_bytes()==data
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
