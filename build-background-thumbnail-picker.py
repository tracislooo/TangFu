from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid
R=Path(__file__).resolve().parent
boot=(R/'repair-background-switch-local-assignment.py').read_text('utf8').split('for folder,tag in [(GAME,')[0]
boot=boot.replace('background-switch-local-assignment-','background-thumbnail-picker-')
exec(compile(boot,'setup','exec'))
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
STATE='TFBackgroundSelectedImageV3'
SCOPE='Int|0|(Session,Explicit,{TF27.BackgroundPicker},{selected-image-v3})'
ROW,STYLE=-941300000001000,-941300000001001
GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/background-thumbnail-row/v3').hex
CHOICES='5b2e64da94c8319418ea3db0fc8c92f2'
COMPARE='f6f314e9db56227459137669d87c44e9'
source=ast.parse((R/'hover-fc-portrait-selector-20261112-211124/add-hover-fc-portrait-selector.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['string','args','comparison','owned']],type_ignores=[]),'helpers','exec'))
def remove(d,i):
 ids=owned(d.r,i);parent=d.a(i)['m_Parent']['rid'];d.a(parent)['m_Children'].remove({'rid':i})
 d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in ids];d.r=refs(d.d)
def variable(name,value):return {'m_name':name,'m_scopeValue':{'m_serializedData':value}}
def fixedtext(d,i,t):
 s=d.data(i);s.update(text=t,text_UxmlAttributeFlags=1);s['TextBinding']['m_kind']=0;s['TextBinding_UxmlAttributeFlags']=1
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 before=(folder/W).read_bytes();env={W:UnityPy.load(before),G:UnityPy.load(str(folder/G))};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()};changes={W:{},G:{}}
 reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']};assert reserved.isdisjoint([ROW,STYLE]);assert ROW not in objs[W] and STYLE not in objs[W]
 nav=Doc(W,name='PrimaryNavigationBar');bg=Doc(W,name='GameWorldBackground');donor=Doc(G,name='HighlightHomeHorizontalFormation');rd=Doc(G,name='GenericDisplayValuePairDropdownRow')
 tree,sheet=copy.deepcopy(rd.d),copy.deepcopy(rd.s);tree['m_Name']='TFBackgroundThumbnailRow';tree['inlineSheet']['m_PathID']=STYLE;sheet['m_Name']='TFBackgroundThumbnailStyle'
 pointer_remap(tree,rd.af,nav.af);pointer_remap(sheet,rd.af,nav.af);import_types(rd.af,nav.af,tree['references']['RefIds'])
 for template,pid,data in [(nav.obj,ROW,tree),(objs[W][nav.sid],STYLE,sheet)]:
  ob=copy.copy(template);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[W][pid]=ob;ob.save_typetree(data)
 row=Doc(W,pid=ROW,tree=tree,style=sheet)
 for c in list(row.a(1002)['m_Children']):remove(row,c['rid'])
 row.a(1002)['m_Classes']=[];row.size(1002,224,150);row.st(1002,[(131083,row.enum('column'))])
 gate=row.add(bg,1002,1002,'ThumbnailChoice');row.data(gate).update(Binding=comparison('row.PropertyValue'),Binding_UxmlAttributeFlags=1);row.fill(gate)
 for index,(pid,title) in enumerate([(-910000000000149,'TF skin V1'),(-910000000000145,'昆山球场')]):
  card=row.add(rd,1002,gate,'BackgroundOption'+str(index));row.size(card,224,150);row.st(card,[(131083,row.enum('column'))])
  pic=row.add(bg,1004,card,'BackgroundThumbnail'+str(index));row.size(pic,224,126)
  prop=next(p for p in bg.s['m_Rules'][bg.a(1004+index)['m_RuleIndex']]['m_Properties'] if p['m_Id']==458753);ptr=copy.deepcopy(bg.s['assets'][prop['m_Values'][0]['valueIndex']]);pointer_remap(ptr,bg.af,row.af)
  row.st(pic,[(458753,row.val(6,ptr)),(262153,row.enum('scale-to-fit')),(196610,row.val(4,{'r':1.,'g':1.,'b':1.,'a':1.}))])
  label=row.add(rd,1008,card,'BackgroundTitle'+str(index));fixedtext(row,label,title);row.size(label,224,24);row.a(label)['m_Classes']=['body-md','global-text-primary']
 row.save()
 wrapper=nav.named('TFBackgroundButtonSharedSelection');old_label=copy.deepcopy(nav.r[nav.a(nav.named('TFBackgroundSwitchLabel'))['m_SerializedData']['rid']])
 for c in list(nav.a(wrapper)['m_Children']):remove(nav,c['rid'])
 nav.data(wrapper)['ValueVariables']=[variable(STATE,SCOPE),variable('TFBackgroundOption0','Int|0|'),variable('TFBackgroundOption1','Int|1|')]
 drop=nav.add(donor,1040,wrapper,'TFBackgroundThumbnailPicker');ds=nav.data(drop)
 ds.update(RowTemplate={'m_AssetGUID':GUID,'m_SubObjectName':'','m_SubObjectType':''},SelectionValueBinding={'m_path':STATE},UseRowTemplateToShowSelectedValue=0,HideOnSelectionChange=1,HideOnFocusLoss=1,Anchor=1,AlwaysUpdateInternalSelection=1,ForceRefreshOnNewChoices=1,ShowSelectedTick=1,pickingMode=0,enabledSelf=1)
 for k in ['RowTemplate','SelectionValueBinding','UseRowTemplateToShowSelectedValue','HideOnSelectionChange','HideOnFocusLoss','Anchor','AlwaysUpdateInternalSelection','ForceRefreshOnNewChoices','ShowSelectedTick','pickingMode','enabledSelf']:ds[k+'_UxmlAttributeFlags']=1
 ds['BindChoicesFunction']={'m_target':{'m_guid':CHOICES},'m_inputs':{'m_variable':{'m_argumentBytes':args([('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]',b'\x02\x01'+string('TFBackgroundOption0')+b'\x01'+string('TFBackgroundOption1'))])}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}};ds['BindChoicesFunction_UxmlAttributeFlags']=1
 nav.a(drop)['m_Classes']=['buttons-dropdown-base-regular','align-items-center'];nav.size(drop,88,28);nav.st(drop,[(131083,nav.enum('row'))])
 lab=nav.add(rd,1008,drop,'TFBackgroundPickerLabel');fixedtext(nav,lab,'切换背景');nav.a(lab)['m_Classes']=['body-sm','global-text-primary'];nav.data(lab)['pickingMode']=1
 arrow=nav.add(donor,1058,drop,'TFBackgroundPickerArrow');nav.a(arrow)['m_Classes']=copy.deepcopy(donor.a(1058)['m_Classes']);nav.size(arrow,12,12);nav.save()
 bg.data(bg.named('TFBackgroundSharedSelection'))['ValueVariables']=[variable(STATE,SCOPE)];bg.data(1002)['Binding']=comparison(STATE);bg.save()
 metaob=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=metaob.read_typetree()
 pointers=[{'m_FileID':0,'m_PathID':ROW},{'m_FileID':0,'m_PathID':STYLE}]+[p for p in row.s['assets'] if p['m_PathID'] in [-910000000000149,-910000000000145]]
 meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(pointers),'asset':pointers[0]}));meta['m_PreloadTable']+=pointers;meta['m_Container'].sort(key=lambda x:x[0]);metaob.save_typetree(meta);changes[W][metaob.path_id]=meta
 catroot=GAME.parent if tag=='game' else SKIN;oldcat=(catroot/'catalog.bin').read_bytes();cat=cm.Catalog(oldcat);base=next(q for q in cat.locations('148fecd3d1ac86a48aaa84bf7d95af06') if cat.location(q)['type'][1].endswith('VisualTreeAsset'));cat=cm.Catalog(cat.add_key_location(GUID,base,base))
 required=[]
 for key in [CHOICES,COMPARE,'550fc2c85c4c6af4c81e62ee766f64d5']:
  for q in cat.locations(key):
   for dep in cat.location(q)['dependencies']:
    if dep not in required:required.append(dep)
 for key in [GUID,'148fecd3d1ac86a48aaa84bf7d95af06','550fc2c85c4c6af4c81e62ee766f64d5']:
  for q in cat.locations(key):
   deps=cat.location(q)['dependencies'];deps += [i for i in required if i not in deps];raw=b''.join(struct.pack('<I',i) for i in deps);import zlib;struct.pack_into('<II',cat.data,q+12,cat.append(raw,True),zlib.crc32(raw))
 records=list(cat.key_records);idx=next(i for i,(k,l) in enumerate(records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');k,l=records[idx];items=[i[0] for i in cat.array(l,'I')]+cat.locations(GUID);records[idx]=(k,cat.append(b''.join(struct.pack('<I',i) for i in items),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*x) for x in records),True))
 output=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects};assert set(saved)==set(hashes)|{ROW,STYLE}
 for pid,h in hashes.items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 for target,data in [(folder/W,output),(catroot/'catalog.bin',bytes(cat.data)),(catroot/'catalog.hash',hashlib.md5(bytes(cat.data)).hexdigest().encode())]:
  old=target.read_bytes();backup=OUT/('backup-'+tag)/target.name;src=OUT/tag/target.name;backup.parent.mkdir(exist_ok=True);src.parent.mkdir(exist_ok=True);backup.write_bytes(old);src.write_bytes(data);protected.pop(str(target),None);transactions.append({'target':str(target),'backup':str(backup),'source':str(src),'before':sha(old),'after':sha(data)})
 reports.append({'target':tag,'row_guid':GUID,'dropdown':drop,'state':STATE,'scope':SCOPE,'changed_objects':list(changes[W]),'runtime_verified':False})
for x in transactions:assert sha(Path(x['target']).read_bytes())==x['before']
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'protected_sha256':protected,'reports':reports},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(transactions,ensure_ascii=False,indent=2),'utf8')
print(str(OUT))
