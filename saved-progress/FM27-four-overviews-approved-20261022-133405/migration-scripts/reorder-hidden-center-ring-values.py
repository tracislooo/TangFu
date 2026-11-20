from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont

rows=[['adaptability','ambition','loyalty','pressure','professionalism','sportsmanship','temperament'],['versatility','dirtiness','consistency','important-matches','controversy','injury-proneness']]
labels=[['适应性','雄心','忠诚','抗压','职业','体育道德','情绪控制'],['多面性','肮脏动作','稳定','大赛发挥','争论','受伤倾向']]
def nst(name,ps):st(named(name)['rid'],ps)
# Move existing cells as complete units, preserving each attribute's native number/title bindings.
rowids=[named('OverviewHiddenAttributeRow'+str(i+1))['rid'] for i in range(2)]
dividers=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','').startswith('OverviewHiddenDivider_')]
assert len(dividers)==11
for d in dividers:
 parent=d['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':d['rid']})
di=0
for ix,keys in enumerate(rows):
 parent=rowids[ix];rr[parent]['data']['m_Children']=[{'rid':named('OverviewHiddenCell_'+key)['rid']} for key in keys]
 for j,key in enumerate(keys):
  cell=named('OverviewHiddenCell_'+key);cell['data']['m_Parent']={'rid':parent}
  st(cell['rid'],[(131089,px(j*30))])
  if j<len(keys)-1:
   divider=dividers[di];di+=1;divider['data']['m_Parent']={'rid':cell['rid']}
   rr[divider['data']['m_SerializedData']['rid']]['data']['name']='OverviewHiddenDivider_'+key
   cell['data']['m_Children'].append({'rid':divider['rid']})
assert di==11

inverted={}
for key in ['controversy','injury-proneness']:
 for tier in range(1,11):
  node=named(f'OverviewHiddenImage_{key}_{tier:02}')
  ptr={'m_FileID':fileid,'m_PathID':textures[f'HIDEstats{11-tier:02}']}
  sheet['assets'].append(ptr);st(node['rid'],[(458753,{'m_ValueType':6,'valueIndex':len(sheet['assets'])-1})])
 inverted[key]=[11-tier for tier in range(1,11)]

# Center numbers in the existing compact 26px rings; the 7px bold font fits four characters.
centernodes=[]
for r in list(rr.values()):
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if not name.startswith('OverviewFitness_'):continue
 if '_Number' in name or '_MissingNumber' in name or name=='OverviewFitness_Fatigue_RawValue':
  st(r['rid'],[(131104,px(0)),(131087,px(26)),(65537,px(7)),(65543,en('bold')),(65546,en('middle-center'))]);centernodes.append(r['rid'])
 elif name.endswith('_Title'):st(r['rid'],[(131104,px(28))])
 elif name in ['OverviewFitness_Condition','OverviewFitness_Sharpness','OverviewFitness_Fatigue']:st(r['rid'],[(131087,px(42))])
fatigue=named('OverviewFitness_Fatigue')['rid'];raw=named('OverviewFitness_Fatigue_RawValue')['rid']
children=rr[fatigue]['data']['m_Children'];rr[fatigue]['data']['m_Children']=[c for c in children if c['rid']!=raw]+[{'rid':raw}]
nst('OverviewFitnessPercentRow',[(131087,px(42))])
nst('OverviewHiddenAttributesPanel',[(131087,px(220)),(131096,px(220))])

# Verify the actual order, parents, reverse tiers, numeric content and unchanged bindings.
for ix,keys in enumerate(rows):
 assert rr[rowids[ix]]['data']['m_Children']==[{'rid':named('OverviewHiddenCell_'+k)['rid']} for k in keys]
 for j,key in enumerate(keys):
  c=named('OverviewHiddenCell_'+key);assert c['data']['m_Parent']=={'rid':rowids[ix]} and dimension(c,131089)==30*j
for key in ['controversy','injury-proneness']:
 for value in range(1,21):
  tier=(value+1)//2
  assert property_value(named(f'OverviewHiddenImage_{key}_{tier:02}'),458753)=={'m_FileID':fileid,'m_PathID':textures[f'HIDEstats{11-tier:02}']}
for i in centernodes:
 assert dimension(rr[i],131104)==0 and dimension(rr[i],131087)==26
 assert property_value(rr[i],65546)=='middle-center'
for key in ['Condition','Sharpness','Fatigue']:
 assert dimension(named('OverviewFitness_'+key+'_Title'),131104)==28
for i,r in old_refs.items():
 for k in ['TextBinding','Binding','BindFunction']:
  if k in r.get('data',{}):assert rr[i]['data'][k]==r['data'][k],('binding changed',i,k)
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
out=R/('reordered-attributes-centered-ring-values-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'rows':rows,'row_titles':labels,'inverted_images':inverted,'original_numeric_values_and_bindings_preserved':True,'ring_size':[26,26],'number_font_px':7,'numbers_in_ring_center':True,'title_top':28,'fatigue_zero_is_best_preserved':True,'direct_fatigue_number_preserved':True,'centered_number_node_count':len(centernodes),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')

# Render a diagram using the installed textures, dimensions, spacing, and requested order.
scale=4;preview=Image.new('RGB',(880,780),'#22262d');pd=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);nf=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',40);ringfont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
samples={'adaptability':15,'ambition':18,'loyalty':16,'pressure':14,'professionalism':17,'sportsmanship':15,'temperament':16,'versatility':17,'dirtiness':8,'consistency':16,'important-matches':14,'controversy':3,'injury-proneness':2}
for ix,keys in enumerate(rows):
 y=20+ix*280;offset=20+(60 if ix else 0)
 for j,key in enumerate(keys):
  x=offset+j*120+60;v=samples[key];tier=(v+1)//2
  if key in inverted:tier=11-tier
  pd.text((x,y+26),str(v),font=nf,fill='white',anchor='mm')
  im=names[f'HIDEstats{tier:02}'].read().image.convert('RGBA').resize((20,80),Image.Resampling.NEAREST);preview.paste(im,(x-10,y+56),im)
  label=labels[ix][j];pd.text((x,y+164),label[:3],font=small,fill='white',anchor='mm')
  if len(label)>3:pd.text((x,y+198),label[3:],font=small,fill='white',anchor='mm')
for j,(label,value,pct) in enumerate([('体能','92%',92),('比赛状态','78%',78),('疲劳','0',100)]):
 x=20+j*280+140;im=names[f'FitnessPercentRing{pct:03}'].read().image.convert('RGBA').resize((104,104),Image.Resampling.LANCZOS);preview.paste(im,(x-52,574),im)
 pd.text((x,626),value,font=ringfont,fill='white',anchor='mm');pd.text((x,714),label,font=font,fill='#a0a0a0',anchor='mm')
preview.save(out/'preview.png')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'inverted_attributes':list(inverted),'centered_numbers':len(centernodes)},ensure_ascii=True))
