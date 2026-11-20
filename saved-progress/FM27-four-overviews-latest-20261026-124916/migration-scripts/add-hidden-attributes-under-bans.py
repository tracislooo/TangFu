from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))
from PIL import Image,ImageDraw,ImageFont
PAGES=[-930000000001001,-930000000001003]
keys=['adaptability','ambition','loyalty','pressure','professionalism','sportsmanship','temperament','versatility','dirtiness','consistency','important-matches','controversy','injury-proneness']
labels=['适应性','雄心','忠诚','抗压','职业','体育道德','情绪控制','多面性','肮脏动作','稳定','大赛发挥','争论','受伤倾向']
source_doc=copy.deepcopy(doc);source_refs=copy.deepcopy(rr);source_sheet=copy.deepcopy(sheet)
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
ge=UnityPy.load(str(GAME/GN));go={o.path_id:o for o in ge.objects}
globalmeta=next(o for o in go.values() if o.type.name=='AssetBundle').read_typetree()
rowpid=next(v['asset']['m_PathID'] for k,v in globalmeta['m_Container'] if k=='aa5993dcecf4529d9fa280f078b11b0c')
rowdoc=go[rowpid].read_typetree();rowrefs={r['rid']:r for r in rowdoc['references']['RefIds']}
worldbundle=next(o for o in objects.values() if o.type.name=='AssetBundle');metadata=worldbundle.read_typetree();metadata_before=copy.deepcopy(metadata)
hiddenpid=next(v['asset']['m_PathID'] for k,v in metadata['m_Container'] if k=='cd65232d2c8c59e4592f0bb85658abb4')
hiddendoc=objects[hiddenpid].read_typetree();hiddenrefs={r['rid']:r for r in hiddendoc['references']['RefIds']}
badgeguid='e61c9f83ee67aae4aadfec4ae509ae84';badgepid=next(v['asset']['m_PathID'] for k,v in globalmeta['m_Container'] if k==badgeguid)
globalaf=go[badgepid].assets_file
# Match the native hidden-value cell's GUID-based import; shared UI templates are already preloaded.
assert any(u['path']==badgeguid for u in hiddendoc['m_Usings'])
known_types={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
for t in globalaf.ref_types:
 k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if k not in known_types:af.ref_types.append(copy.copy(t));known_types.add(k)
native_label=copy.deepcopy(rowrefs[1017]);native_label_sd=copy.deepcopy(rowrefs[native_label['data']['m_SerializedData']['rid']])
native_mapper=copy.deepcopy(rowrefs[1021]);native_mapper_sd=copy.deepcopy(rowrefs[native_mapper['data']['m_SerializedData']['rid']])
native_badge=copy.deepcopy(hiddenrefs[1008]);native_badge_sd=copy.deepcopy(hiddenrefs[native_badge['data']['m_SerializedData']['rid']])
evidence=[]
for key,label in zip(keys,labels):
 source_number=next(r for r in source_refs.values() if source_refs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='OverviewHiddenNumber_'+key+'Value')
 title=next(r for r in source_refs.values() if source_refs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='OverviewHiddenTitle_'+key)
 path=source_refs[source_number['data']['m_SerializedData']['rid']]['data']['TextBinding']['m_direct']['Path']['m_path']
 assert path.endswith('.AttributeMinValue')
 evidence.append({'key':key,'label':label,'path':path,'label_binding':copy.deepcopy(source_refs[title['data']['m_SerializedData']['rid']]['data']['TextBinding'])})

def subtree(refs,i):
 nodes=[i]
 for c in refs[i]['data'].get('m_Children',[]):nodes.extend(subtree(refs,c['rid']))
 return nodes
def clone_source_subtree(source_root,parent,prefix):
 global next_rid,next_id
 nodes=subtree(source_refs,source_root);ids=nodes+[source_refs[i]['data']['m_SerializedData']['rid'] for i in nodes]
 start=max(rr)+1;mapping={i:start+j for j,i in enumerate(ids)}
 uid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 idmap={source_refs[i]['data']['m_Id']:uid+j for j,i in enumerate(nodes)}
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid'] in mapping:v['rid']=mapping[v['rid']]
   else:
    for k,x in list(v.items()):
     if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in idmap:v[k]=idmap[x]
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for i in ids:
  r=copy.deepcopy(source_refs[i]);r['rid']=mapping[i];remap(r['data'])
  if i in nodes:
   if i==source_root:r['data']['m_Parent']={'rid':parent}
   ix=r['data'].get('m_RuleIndex',-1)
   if ix>=0:
    nr=copy.deepcopy(source_sheet['m_Rules'][ix])
    for p in nr['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType']==1:continue
      pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(source_sheet[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    r['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(nr)
  elif 'name' in r['data']:r['data']['name']=prefix+r['data']['name']
  rr[r['rid']]=r;doc['references']['RefIds'].append(r)
 rr[parent]['data']['m_Children'].append({'rid':mapping[source_root]})
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 for i in ids:
  if i in nodes:continue
  expected=copy.deepcopy(source_refs[i]['data']);expected['uxmlAssetId']=idmap[expected['uxmlAssetId']]
  if 'name' in expected:expected['name']=prefix+expected['name']
  assert rr[mapping[i]]['data']==expected,('summary binding mismatch',i)
 return mapping[source_root],mapping

def replace_with_native(i,node_template,sd_template,name,classes=None):
 a=rr[i]['data'];sdid=a['m_SerializedData']['rid'];uid=a['m_Id']
 keep={k:copy.deepcopy(a[k]) for k in ['m_Id','m_Parent','m_Children','m_RuleIndex','m_SerializedData']}
 rr[i]['type']=copy.deepcopy(node_template['type']);rr[i]['data']=copy.deepcopy(node_template['data']);rr[i]['data'].update(keep)
 if classes is not None:rr[i]['data']['m_Classes']=classes
 rr[sdid]['type']=copy.deepcopy(sd_template['type']);rr[sdid]['data']=copy.deepcopy(sd_template['data'])
 rr[sdid]['data'].update(uxmlAssetId=uid,name=name,name_UxmlAttributeFlags=1)
 return rr[sdid]['data']

page_data={};audits=[]
for pagepid in PAGES:
 doc=objects[pagepid].read_typetree();sheetid=doc['inlineSheet']['m_PathID'];sheet=objects[sheetid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 zero=[prop(262150,px(0)),prop(262151,px(0)),prop(131084,num(0)),prop(131085,num(0))]
 new=[];next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 assert rr[1011]['data']['m_Children']==[{'rid':1035}]
 assert not any(u['alias']=='RightHiddenAttributeBadge' for u in doc['m_Usings'])
 doc['m_Usings'].append({'alias':'RightHiddenAttributeBadge','path':badgeguid,'asset':{'m_FileID':0,'m_PathID':0}})
 relative=zero+[prop(131102,en('relative')),prop(131105,auto()),prop(131097,px(0)),prop(131073,en('stretch'))]
 panel=make(1011,'RightHiddenAttributesPanel',relative+[prop(131093,px(12)),prop(131087,auto()),prop(131096,px(360))])
 summary=make(panel,'RightHiddenSummaryGraphic',relative+[prop(131105,px(210)),prop(131087,px(48)),prop(131096,px(48))])
 # Reserve newly created IDs in the document before cloning any source subtrees.
 doc['references']['RefIds'].extend(new);new=[]
 copies=[]
 for source_name in ['OverviewHiddenSummaryLine','OverviewHiddenBarLine']:
  src=next(r for r in source_refs.values() if source_refs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==source_name)
  root,mapping=clone_source_subtree(src['rid'],summary,'RightHidden_');copies.append({'source':src['rid'],'root':root,'mapping':mapping})
 listid=make(panel,'RightHiddenAttributesList',relative+[prop(131087,auto()),prop(131093,px(4))])
 row_records=[]
 for index,item in enumerate(evidence):
  key,path=item['key'],item['path']
  row=make(listid,'RightHiddenRow_'+key,relative+[prop(131083,en('row')),(prop(131073,en('center'))),prop(131088,en('space-between')),prop(131087,px(24)),prop(131096,px(24)),prop(131094,px(24)),prop(131093,px(0)),prop(131090,px(0))])
  rr[row]['data']['m_Classes']=copy.deepcopy(rowrefs[1008]['data']['m_Classes'])
  titleid=make(row,'RightHiddenLabel_'+key,zero+[prop(131102,en('relative')),prop(131084,num(1)),prop(131085,num(1)),prop(131097,px(0)),prop(131087,px(24)),prop(65546,en('middle-left'))])
  labeldata=replace_with_native(titleid,native_label,native_label_sd,'RightHiddenLabel_'+key)
  labeldata['TextBinding']=copy.deepcopy(item['label_binding']);labeldata['TextBinding_UxmlAttributeFlags']=1;labeldata['DebugDisplay']='';labeldata['text']='';labeldata['text_UxmlAttributeFlags']=0
  gate=make(row,'RightHiddenValueAvailable_'+key,zero+[prop(131102,en('relative')),prop(131105,px(40)),prop(131087,px(24)),prop(131074,en('center'))],True,0,path)
  missing=text(gate,'RightHiddenValueMissing_'+key,0,0,40,24,12,literal='--',center=True)
  rr[missing]['data']['m_Classes']=['content-no-wrap','body-md-strong']
  mapper=make(gate,'RightHiddenValueMapping_'+key,zero+[prop(131102,en('relative')),prop(131105,px(40)),prop(131087,px(24)),prop(131073,en('center')),prop(131088,en('center'))])
  ms=replace_with_native(mapper,native_mapper,native_mapper_sd,'RightHiddenValueMapping_'+key,[])
  ms['Mappings']=[{'m_serialisedType':0,'from':n,'to':{'m_path':path},'type':{'id':0}} for n in ['propertyValue','minValue']];ms['Mappings_UxmlAttributeFlags']=1
  badge=make(mapper,'RightHiddenBadge_'+key,zero+[prop(131102,en('relative')),prop(131087,px(24)),prop(131073,en('center')),prop(131088,en('center'))])
  bs=replace_with_native(badge,native_badge,native_badge_sd,'RightHiddenBadge_'+key,[])
  rr[badge]['data']['m_TemplateAlias']='RightHiddenAttributeBadge';bs['templateId']='RightHiddenAttributeBadge';bs['templateId_UxmlAttributeFlags']=1
  row_records.append({'key':key,'row':row,'label':titleid,'gate':gate,'missing':missing,'mapper':mapper,'badge':badge,'path':path})
 doc['references']['RefIds'].extend(new)
 assert rr[1011]['data']['m_Children']==[{'rid':1035},{'rid':panel}]
 assert [c['rid'] for c in rr[listid]['data']['m_Children']]==[x['row'] for x in row_records]
 assert len(row_records)==13
 for i,r in old.items():
  if i==1011:
   restored=copy.deepcopy(rr[i]);restored['data']['m_Children']=r['data']['m_Children'];assert restored==r
  else:assert rr[i]==r,('pre-existing content changed',pagepid,i)
 for item in row_records:
  assert dimension(rr[item['row']],131087)==24
  ms=rr[rr[item['mapper']]['data']['m_SerializedData']['rid']]['data']
  assert all(m['to']['m_path']==item['path'] for m in ms['Mappings'])
 validate_ui(doc,sheet)
 # Load the existing background images and shared AttributeBadge through this VTA's preload span.
 entry=next(v for k,v in metadata['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pagepid})
 span=copy.deepcopy(metadata['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in sheet['assets']:
  if ptr['m_PathID'] and ptr not in span:span.append(copy.deepcopy(ptr))
 entry.update(preloadIndex=len(metadata['m_PreloadTable']),preloadSize=len(span));metadata['m_PreloadTable'].extend(span)
 objects[pagepid].save_typetree(doc);objects[sheetid].save_typetree(sheet);page_data[pagepid]=doc;page_data[sheetid]=sheet
 audits.append({'page_id':pagepid,'panel':panel,'summary':summary,'summary_copies':copies,'list':listid,'rows':row_records})

worldbundle.save_typetree(metadata);output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
expected={**page_data,worldbundle.path_id:metadata}
assert set(saved)==set(objects)
for pid,h in old_hashes.items():
 if pid in expected:assert saved[pid].read_typetree()==expected[pid]
 else:assert sha(saved[pid].get_raw_data())==h,('unrelated asset changed',pid)
for pagepid in PAGES:
 d=saved[pagepid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
assert metadata['m_Dependencies']==metadata_before['m_Dependencies']
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('right-hidden-attributes-under-bans-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'output':str(out),'pages':audits,'attributes':[{k:v for k,v in e.items() if k!='label_binding'} for e in evidence],'row_height':24,'native_attribute_badge_guid':badgeguid,'native_badge_binding':'propertyValue and minValue both use existing AttributeMinValue','missing_value':'--','all_existing_top_content_preserved':True,'original_bans_preserved':True,'existing_right_scroll_preserved':True,'unchanged_objects':len(old_hashes)-len(expected),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
preview=Image.new('RGB',(624,830),'#22262d');pd=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27);nfont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
pd.text((24,20),'禁赛区域',font=font,fill='white');pd.line((24,66,600,66),fill='#555a61',width=1)
pd.text((24,96),'↗ 170     ↘ 170',font=nfont,fill='white');pd.text((390,104),'声望 8500',font=small,fill='#a0a0a0');pd.text((24,158),'隐藏',font=small,fill='#a0a0a0')
pd.rounded_rectangle((110,160,580,172),radius=6,fill='#44484e');pd.rounded_rectangle((110,160,500,172),radius=6,fill='#10c98f');pd.ellipse((494,156,510,176),fill='white')
vals=[15,18,16,14,17,15,16,17,8,16,14,3,2]
for i,(label,v) in enumerate(zip(labels,vals)):
 y=218+i*44;pd.text((30,y),label,font=font,fill='white');pd.text((574,y),str(v),font=nfont,fill=('#d4de53' if v>=15 else '#ffffff'),anchor='ra')
preview.save(out/'preview.png')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'pages':len(audits),'rows_per_page':13,'row_height':24,'native_badge':badgeguid,'original_top_content_unchanged':True},ensure_ascii=True))
