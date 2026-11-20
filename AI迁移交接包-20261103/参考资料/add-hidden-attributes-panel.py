from pathlib import Path
R=Path(__file__).parent
# Reuse the established native comparison codec/node factory and external-texture validation.
exec(compile((R/'add-capa-layered-bar.py').read_text(encoding='utf8').split('# Expand only')[0],'<existing native layer helpers>','exec'))
hidden_names=[f'HIDEstats{i:02}' for i in range(1,11)]
for n in hidden_names:
 assert n in names and names[n].read().image.size==(5,20)
 textures[n]=names[n].path_id
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def box(x,y,w,h):return zero+[prop(131102,en('absolute')),prop(131089,px(x)),prop(131104,px(y)),prop(131105,px(w)),prop(131087,px(h))]
textnode=copy.deepcopy(named('CardCurrentAbilityValue'))
textsd=copy.deepcopy(rr[textnode['data']['m_SerializedData']['rid']])
titlenode=copy.deepcopy(rr[1096]);titlesd=copy.deepcopy(rr[titlenode['data']['m_SerializedData']['rid']])
titleargs=decode(titlesd['data']['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
assert len(titleargs)==1
def text(parent,name,x,y,w,h,size=10,path=None,translation=None,literal=None,center=False):
 i=make(parent,name,box(x,y,w,h)+[prop(65537,px(size)),prop(65536,color(255,255,255)),prop(65546,en('middle-center' if center else 'middle-left')),prop(65552,en('nowrap'))])
 a=rr[i]['data'];sdid=a['m_SerializedData']['rid'];uid=a['m_Id']
 a['m_FullTypeName']=textnode['data']['m_FullTypeName']
 s=rr[sdid];template=titlesd if translation is not None else textsd
 s['type']=copy.deepcopy(template['type']);s['data']=copy.deepcopy(template['data'])
 d=s['data'];d.update(uxmlAssetId=uid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,DebugDisplay='',text='',text_UxmlAttributeFlags=0)
 if translation is not None:
  args=copy.deepcopy(titleargs);args[0]=(args[0][0],struct.pack('<i',translation)+args[0][1][4:])
  d['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
 elif path:
  d['TextBinding']['m_kind']=1;d['TextBinding']['m_direct']={'Path':{'m_path':path},'Nullable':1}
 else:
  d['TextBinding']['m_kind']=0;d['text']=literal;d['text_UxmlAttributeFlags']=1
 d['TextBinding_UxmlAttributeFlags']=1
 return i
def number(parent,name,path,x,y,w,h,size=12):
 gate=make(parent,name+'Available',box(x,y,w,h),True,0,path)
 text(gate,name+'Missing',0,0,w,h,size,literal='--',center=True)
 text(gate,name+'Value',0,0,w,h,size,path=path,center=True)
 return gate
bar=named('OverviewCAPALayeredBar')['rid']
assert rr[bar]['data']['m_Parent']=={'rid':1026}
st(1026,[(131105,px(546)),(131095,px(546)),(131097,px(0))])
panel=make(1026,'OverviewHiddenAttributesPanel',zero+[prop(131102,en('relative')),prop(131105,px(294)),prop(131097,px(294)),prop(131087,px(160)),prop(131096,px(160)),prop(131091,px(12)),prop(131074,en('center'))])
line1=make(panel,'OverviewHiddenSummaryLine',box(0,0,294,24))
for prefix,x,path,tid in [('CA',0,'person.PlayerCurrentAbility',15234),('PA',94,'person.PlayerPotentialAbility',15235)]:
 make(line1,'Overview'+prefix+'WhiteDot',box(x,8,8,8)+[prop(458752,color(255,255,255)),prop(262147,px(4))])
 text(line1,'Overview'+prefix+'NativeTitle',x+12,0,48,24,10,translation=tid)
 number(line1,'Overview'+prefix+'NativeNumber',path,x+60,0,26,24)
text(line1,'OverviewCurrentReputationTitle',184,0,60,24,10,translation=15236)
number(line1,'OverviewCurrentReputation','person.PlayerCurrentReputation',244,0,50,24)
line2=make(panel,'OverviewHiddenBarLine',box(0,24,294,24))
text(line2,'OverviewHiddenNativeTitle',0,0,38,24,11,translation=32477)
rr[1026]['data']['m_Children'].remove({'rid':bar});rr[bar]['data']['m_Parent']={'rid':line2};rr[line2]['data']['m_Children'].append({'rid':bar})
st(bar,[(131102,en('absolute')),(131089,px(42)),(131104,px(2)),(131091,px(0)),(131092,px(0)),(131093,px(0)),(131090,px(0))])
definitions=[
 [('adaptability','适应性'),('ambition','雄心'),('controversy','争论'),('loyalty','忠诚'),('pressure','抗压'),('professionalism','职业'),('sportsmanship','体育道德')],
 [('temperament','情绪控制'),('versatility','多面性'),('consistency','稳定'),('dirtiness','肮脏动作'),('important-matches','大赛发挥'),('injury-proneness','受伤倾向')]]
# Use the game's own table-column binding paths and translation IDs as the source of truth.
factoryjson=json.loads((R/'FMskin/ui-tablefactories_assets_all/PlayerTableFactory.json').read_text(encoding='utf8'))
fe=UnityPy.load(str(GAME/'ui-tablefactories_assets_all.bundle'))
factory=next(o for o in fe.objects if o.path_id==factoryjson['path_id']).read_typetree()
columns={}
def walk(v):
 if isinstance(v,dict):
  if isinstance(v.get('m_id'),str) and v['m_id'].startswith('hidden-'):columns[v['m_id']]=v
  for a in v.values():walk(a)
 elif isinstance(v,list):
  for a in v:walk(a)
walk(factory)
roots={};evidence=[]
for rowindex,items in enumerate(definitions):
 row=make(panel,f'OverviewHiddenAttributeRow{rowindex+1}',box(21 if rowindex else 0,48+54*rowindex,len(items)*42,54))
 for index,(key,label) in enumerate(items):
  column=columns['hidden-'+key];path=column['m_sortBinding']['m_path'];assert path.startswith('binding.')
  path='person.'+path[len('binding.'):];tid=column['m_translationID']['GameID']
  cell=make(row,'OverviewHiddenCell_'+key,box(index*42,0,42,54))
  number(cell,'OverviewHiddenNumber_'+key,path,0,0,42,14)
  text(cell,'OverviewHiddenTitle_'+key,0,38,42,14,10,translation=tid,center=True)
  imagebox=box(18,16,5,20)
  gate=make(cell,'OverviewHiddenImagePositive_'+key,imagebox,True,0,path);roots[key]=gate
  make(gate,'OverviewHiddenImageUnavailable_'+key,box(0,0,5,20))
  parent=gate
  for tier in range(1,11):
   if tier<10:
    switch=make(parent,f'OverviewHidden_{key}_Above{tier*2}',box(0,0,5,20),True,tier*2,path);parent=switch
   name=f'HIDEstats{tier:02}';sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[name]})
   handle={'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}
   make(parent,f'OverviewHiddenImage_{key}_{tier:02}',box(0,0,5,20)+[prop(458753,handle),prop(262153,en('scale-to-fit'))])
  if index<len(items)-1:make(cell,'OverviewHiddenDivider_'+key,box(41,4,1,46)+[prop(458752,color(150,150,150,90))])
  evidence.append({'attribute':key,'requested_label':label,'path':path,'translation_id':tid})
doc['references']['RefIds'].extend(new)
# Native switch evaluation checks the generated tree for all values around every boundary.
def select(i,value):
 d=rr[i]['data'];s=rr[d['m_SerializedData']['rid']]['data']
 if d.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack('<i',args[1][1])[0]
  return select(d['m_Children'][int(value is not None and value>limit)]['rid'],value)
 return s['name']
for key,root in roots.items():
 for value in [None]+list(range(-5,26)):
  expected='OverviewHiddenImageUnavailable_'+key if value is None or value<=0 else f'OverviewHiddenImage_{key}_{min(10,(value+1)//2):02}'
  assert select(root,value)==expected,(key,value,select(root,value),expected)
allowed={1026,bar}
assert {i for i in old_refs if rr[i]!=old_refs[i]}==allowed
assert rr[bar]['data']['m_Children']==old_refs[bar]['data']['m_Children']
assert len(evidence)==13 and len({e['path'] for e in evidence})==13
assert sum('OverviewHiddenDivider_' in r.get('data',{}).get('name','') for r in new)==11
validate_ui(doc,sheet)
# Extend only this VTA's preload list with the ten native background images.
entry=next(v for k,v in meta['m_Container'] if k==fullguid)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for n in hidden_names:
 ptr={'m_FileID':fileid,'m_PathID':textures[n]}
 if ptr not in span:span.append(ptr)
entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet);bundle.save_typetree(meta)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid,bundle.path_id]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet,bundle.path_id:meta}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
from UnityPy.classes import PPtr
resolved=UnityPy.load(output,bgbytes);wf=next(a for a in resolved.assets if a.name==af.name)
for ptr in sheet['assets'][-130:]:assert PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=wf).deref().read().image.size==(5,20)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('hidden-attributes-four-row-panel-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid,bundle.path_id],'panel_size':[294,160],'row_columns':[7,6],'second_row_offset':21,'divider_count':11,'attributes':evidence,'hidden_translation_id':32477,'all_13_tiers_tested':True,'existing_capa_switches_unchanged':True,'existing_scout_stars_card_second_version_unchanged':True,'catalog_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-3}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output),'attributes':evidence},ensure_ascii=False))
