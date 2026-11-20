from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont

def nst(name,ps):st(named(name)['rid'],ps)
rows=[['adaptability','ambition','controversy','loyalty','pressure','professionalism','sportsmanship'],['temperament','versatility','consistency','dirtiness','important-matches','injury-proneness']]
for index,keys in enumerate(rows):
 nst('OverviewHiddenAttributeRow'+str(index+1),[(131104,px(48 if index==0 else 118)),(131087,px(56))])
 for j,key in enumerate(keys):
  nst('OverviewHiddenCell_'+key,[(131087,px(56))])
  nst('OverviewHiddenImagePositive_'+key,[(131104,px(14))])
  nst('OverviewHiddenTitle_'+key,[(131104,px(34))])
  if j<len(keys)-1:nst('OverviewHiddenDivider_'+key,[(131087,px(48))])

# Tighten the circle/value/title stack while preserving a readable 14px line box.
for r in list(rr.values()):
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if not name.startswith('OverviewFitness_'):continue
 if name.endswith('_Title'):st(r['rid'],[(131104,px(40))])
 elif '_Number' in name or '_MissingNumber' in name or name=='OverviewFitness_Fatigue_RawValue':
  st(r['rid'],[(131104,px(26)),(131087,px(14)),(65537,px(12))])
 elif name in ['OverviewFitness_Condition','OverviewFitness_Sharpness','OverviewFitness_Fatigue']:st(r['rid'],[(131087,px(54))])
 elif name.startswith(('OverviewFitness_Condition','OverviewFitness_Sharpness')) and '_Ring' not in name and '_MissingRing' not in name:
  st(r['rid'],[(131087,px(40))])
nst('OverviewFitnessPercentRow',[(131104,px(176)),(131087,px(54))])
nst('OverviewHiddenAttributesPanel',[(131087,px(232)),(131096,px(232))])

for p in range(101):textures[f'FitnessPercentRing{p:03}']=names[f'FitnessPercentRing{p:03}'].path_id
fatigue=named('OverviewFitness_Fatigue')['rid'];path='person.Fatigue'
gate=make(fatigue,'OverviewFitness_Fatigue_HealthRingAvailable',box(22,0,26,26),True,-2147483648,path)
leaf_levels={}
def ring(parent,name,percent):
 sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[f'FitnessPercentRing{percent:03}']})
 return make(parent,name,box(0,0,26,26)+[prop(458753,{'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}),prop(262153,en('scale-to-fit'))])
missing=ring(gate,'OverviewFitness_Fatigue_HealthRingMissing',0)
def build(parent,lo,hi):
 if lo==hi:
  i=ring(parent,f'OverviewFitness_Fatigue_HealthRing{100-lo:03}',100-lo);leaf_levels[i]=100-lo;return i
 mid=(lo+hi)//2;limit=(mid+1)*10-6
 i=make(parent,f'OverviewFitness_Fatigue_HealthAbove{limit}',box(0,0,26,26),True,limit,path)
 build(i,lo,mid);build(i,mid+1,hi);return i
build(gate,0,100)
doc['references']['RefIds'].extend(new)

def select(i,raw):
 a=rr[i]['data'];sd=rr[a['m_SerializedData']['rid']]['data']
 if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  args=decode(sd['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack('<i',args[1][1])[0]
  return select(a['m_Children'][int(raw is not None and raw>limit)]['rid'],raw)
 return i
checked=0
for raw in [None,-2147483648]+list(range(-1000,1501)):
 i=select(gate,raw)
 if raw in [None,-2147483648]:assert i==missing
 else:assert leaf_levels[i]==100-min(100,max(0,(raw+5)//10)),raw
 checked+=1
assert leaf_levels[select(gate,0)]==100 and leaf_levels[select(gate,1000)]==0
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('existing binding changed',i)
assert rr[named('OverviewFitness_Fatigue_RawValue')['data']['m_SerializedData']['rid']]['data']['TextBinding']['m_direct']['Path']['m_path']=='person.Fatigue'
assert dimension(named('OverviewHiddenAttributeRow2'),131104)-(dimension(named('OverviewHiddenAttributeRow1'),131104)+dimension(named('OverviewHiddenAttributeRow1'),131087))==14
for keys in rows:
 for key in keys:
  assert dimension(named('OverviewHiddenImagePositive_'+key),131104)==14
  assert dimension(named('OverviewHiddenTitle_'+key),131104)==34
assert dimension(named('OverviewFitnessPercentRow'),131104)+dimension(named('OverviewFitnessPercentRow'),131087)<=dimension(named('OverviewHiddenAttributesPanel'),131087)
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
out=R/('fatigue-health-ring-spaced-rows-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'fatigue_ring':'100-clamp(round_half_up(raw/10),0,100)','fatigue_zero_is_best':True,'fatigue_number':'unchanged direct binding person.Fatigue; no percent sign','ring_size':[26,26],'third_row_y':48,'fourth_row_y':118,'row_height':56,'between_rows_gap':14,'attribute_stack_y':{'number':0,'image':14,'title':34},'fitness_stack_y':{'image':0,'number':26,'title':40},'fatigue_source_cases_verified':checked,'all_existing_serialized_bindings_preserved':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
preview=Image.new('RGB',(660,620),'#22262d');pd=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);nf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
labels=[['适应性','雄心','争论','忠诚','抗压','职业','体育道德'],['情绪控制','多面性','稳定','肮脏动作','大赛发挥','受伤倾向']]
for j,keys in enumerate(rows):
 y=18+(0 if j==0 else 210);offset=15 if j==0 else 60
 for k,key in enumerate(keys):
  x=offset+k*90+45;pd.text((x,y+20),str([15,18,8,16,14,17,15][k]),font=nf,fill='white',anchor='mm')
  im=names['HIDEstats08'].read().image.convert('RGBA').resize((15,60),Image.Resampling.NEAREST);preview.paste(im,(x-7,y+42),im)
  label=labels[j][k]
  pd.text((x,y+122),label[:3],font=small,fill='white',anchor='mm')
  if len(label)>3:pd.text((x,y+145),label[3:],font=small,fill='white',anchor='mm')
for j,(label,value,ringpct) in enumerate([('体能','92%',92),('比赛状态','78%',78),('疲劳','0',100)]):
 x=15+j*210+105;im=names[f'FitnessPercentRing{ringpct:03}'].read().image.convert('RGBA').resize((78,78),Image.Resampling.LANCZOS);preview.paste(im,(x-39,418),im)
 pd.text((x,518),value,font=nf,fill='white',anchor='mm');pd.text((x,559),label,font=font,fill='#a0a0a0',anchor='mm')
preview.save(out/'preview.png')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'cases_verified':checked,'fatigue_zero_ring':leaf_levels[select(gate,0)]},ensure_ascii=True))
