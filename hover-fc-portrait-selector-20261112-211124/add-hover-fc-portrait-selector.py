"""Prepare a native dropdown for both currently registered FC hover-card copies."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, uuid

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

def extract(file, names):
    tree = ast.parse((R / file).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names], type_ignores=[]), file, 'exec'), globals())

oldwrite = TypeTreeHelper.write_value
extract('build-fc-player-hover-layout.py', {'write'})
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
extract('add-card-six-ratings.py', {'validate_ui'})
extract('build-match-ui-avatars-layout.py', {'refs','sd','find','pointer_remap','import_types','Doc'})
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
CARD_GUID = '64033a72b9925c8dad3b08826077c328'
ROW, STYLE = -941200000001000, -941200000001001
ROW_GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27/hover-fc-portrait-selector-row/v1').hex
CHOICES = '5b2e64da94c8319418ea3db0fc8c92f2'
COMPARE = 'f6f314e9db56227459137669d87c44e9'
STATE = 'TFHoverCardPortraitMode'
FC_OPTION, PORTRAIT_OPTION = 'TFHoverFCOption', 'TFHoverPortraitOption'
OUT = R / ('hover-fc-portrait-selector-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
(OUT / 'templates').mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
reserved = {int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert reserved.isdisjoint([ROW, STYLE])
transactions, reports, documents = [], [], []
protected = {str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name != W}

def string(s):
    raw = s.encode('utf8')
    assert len(raw) < 128
    return bytes([len(raw)]) + raw

def args(items):
    encoded = [string(t)+v for t,v in items]
    return list(bytes([len(encoded)]) + b''.join(struct.pack('<I',len(v))+v for v in encoded))

def comparison(path):
    return {'m_kind':2, 'm_direct':{'Path':{'m_path':''}, 'Nullable':0}, 'm_visualFunction':{
        'm_target':{'m_guid':COMPARE}, 'm_inputs':{'m_variable':{'m_argumentBytes':args([
            ('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',4)),
            ('SI.VisualScripting.Int32VisualArg',struct.pack('<i',0)),
            ('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string(path))])}},
        'm_outputs':{'m_variable':{'m_argumentBytes':[]}}}}

def box(d,i,x,y,w,h):
    d.st(i,[(131102,d.enum('absolute')),(131089,d.px(x)),(131104,d.px(y)),
        (131105,d.px(w)),(131087,d.px(h)),(131097,d.px(0)),(131096,d.px(0)),
        (131095,{'m_ValueType':1,'valueIndex':3}),(131094,{'m_ValueType':1,'valueIndex':3}),
        (131084,d.num(0)),(131085,d.num(0)),(327681,[d.num(1),d.num(1)])])

def owned(rr, root):
    result = set()
    def visit(value):
        if isinstance(value,dict):
            if set(value)=={'rid'}:
                i=value['rid']
                if i == -2 or i in result:return
                assert i in rr,i
                result.add(i)
                for k,v in rr[i].get('data',{}).items():
                    if k!='m_Parent':visit(v)
            else:
                for v in value.values():visit(v)
        elif isinstance(value,list):
            for v in value:visit(v)
    visit({'rid':root})
    return result

def duplicate_subtree(d, root, parent):
    source=copy.deepcopy(d.r)
    ids=owned(source,root)
    mapping={i:d.nr+j for j,i in enumerate(sorted(ids))}
    d.nr += len(ids)
    nodeids=[i for i in sorted(ids) if 'm_Id' in source[i].get('data',{})]
    eid={source[i]['data']['m_Id']:d.nid+j for j,i in enumerate(nodeids)}
    d.nid += len(nodeids)
    assert d.nid < 2147483647
    def remap(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                if v['rid'] in mapping:v['rid']=mapping[v['rid']]
            else:
                for k,x in v.items():
                    if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in eid:v[k]=eid[x]
                    else:remap(x)
        elif isinstance(v,list):
            for x in v:remap(x)
    for i in sorted(ids):
        r=source[i];r['rid']=mapping[i];remap(r['data'])
        if i==root:r['data']['m_Parent']={'rid':parent}
        d.r[r['rid']]=r;d.d['references']['RefIds'].append(r)
    d.a(parent)['m_Children'].append({'rid':mapping[root]})
    return mapping

for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
    before=(folder/W).read_bytes()
    env={W:UnityPy.load(before),G:UnityPy.load(str(folder/G))}
    objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
    hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
    changes={W:{},G:{}}
    assert ROW not in objs[W] and STYLE not in objs[W]
    metadata=next(o for o in objs[W].values() if o.type.name=='AssetBundle')
    meta=metadata.read_typetree()
    card_ids=list(dict.fromkeys(v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==CARD_GUID and v['asset']['m_FileID']==0))
    assert set(card_ids)=={-960000000003010,-950000000000141},card_ids
    donor=Doc(G,name='HighlightHomeHorizontalFormation')
    originalrow=Doc(G,name='GenericDisplayValuePairDropdownRow')
    first=Doc(W,pid=card_ids[0])
    rd_tree,rd_sheet=copy.deepcopy(originalrow.d),copy.deepcopy(originalrow.s)
    rd_tree['m_Name']='TFHoverCardModeDropdownRow';rd_tree['inlineSheet']['m_PathID']=STYLE
    rd_sheet['m_Name']='TFHoverCardModeDropdownRowStyle'
    pointer_remap(rd_tree,originalrow.af,first.af)
    pointer_remap(rd_sheet,originalrow.af,first.af)
    import_types(originalrow.af,first.af,rd_tree['references']['RefIds'])
    for source,pid,data in [(originalrow.obj,ROW,rd_tree),(objs[G][originalrow.sid],STYLE,rd_sheet)]:
        # Clone an object header from the destination file to keep its script type local.
        template=first.obj if pid==ROW else objs[W][first.sid]
        ob=copy.copy(template);ob.path_id=pid;ob.data=None;ob._read_until=None
        ob.assets_file.objects[pid]=ob;objs[W][pid]=ob;ob.save_typetree(data)
    row=Doc(W,pid=ROW,tree=rd_tree,style=rd_sheet)
    textnode=next(i for i,r in row.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText')
    parent=row.a(textnode)['m_Parent']['rid'];index=row.a(parent)['m_Children'].index({'rid':textnode})
    switch_source=first.named('OverviewCardGoalkeeperSwitch')
    gate=row.add(first,switch_source,parent,'HoverModeTitleSwitch');row.move(gate,parent,index)
    row.data(gate).update(Binding=comparison('row.PropertyValue'),Binding_UxmlAttributeFlags=1,Preview={'Mask':3},Preview_UxmlAttributeFlags=1)
    row.st(gate,[(131084,row.num(1)),(131085,row.num(1))])
    other=row.add(row,textnode,gate,'HoverPortraitModeTitle')
    row.move(textnode,gate,0)
    for i,title in [(textnode,'FC卡面'),(other,'仅大头像')]:
        row.a(i)['m_Classes']=copy.deepcopy(originalrow.a(textnode)['m_Classes'])
        row.data(i).update(text=title,text_UxmlAttributeFlags=1,TextBinding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
        row.st(i,[(65537,row.px(12))])
    row.save()
    target_reports=[]
    for pid in card_ids:
        d=Doc(W,pid=pid)
        original=copy.deepcopy(d.d)
        stage=d.named('ReportPortraitLayerStage');portrait=d.named('PersonPictureFrame')
        parent=d.a(stage)['m_Parent']['rid'];index=d.a(parent)['m_Children'].index({'rid':stage})
        wrapper=d.add(d,stage,parent,'HoverCardModeHost');d.move(wrapper,parent,index)
        d.a(wrapper)['m_RuleIndex']=d.a(stage)['m_RuleIndex']
        selector=d.add(d,d.named('OverviewCardGoalkeeperSwitch'),wrapper,'HoverCardModeSwitch')
        d.data(selector).update(Binding=comparison(STATE),Binding_UxmlAttributeFlags=1,Preview={'Mask':3},Preview_UxmlAttributeFlags=1)
        d.fill(selector)
        d.move(stage,selector)
        large=d.add(d,stage,selector,'HoverLargePortraitOnly')
        d.fill(large)
        picmap=duplicate_subtree(d,portrait,large)
        d.data(picmap[portrait]).update(name='HoverLargePortraitFrame',name_UxmlAttributeFlags=1)
        box(d,picmap[portrait],15,48,310,460)
        drop=d.add(donor,1040,wrapper,'HoverCardModeSelector')
        d.a(drop)['m_Classes']=['buttons-dropdown-base-regular','align-items-center']
        ds=d.data(drop)
        ds.update(pickingMode=0,pickingMode_UxmlAttributeFlags=1,RowTemplate={'m_AssetGUID':ROW_GUID,'m_SubObjectName':'','m_SubObjectType':''},RowTemplate_UxmlAttributeFlags=1,
            SelectionValueBinding={'m_path':STATE},SelectionValueBinding_UxmlAttributeFlags=1,
            UseRowTemplateToShowSelectedValue=1,UseRowTemplateToShowSelectedValue_UxmlAttributeFlags=1,
            HideOnSelectionChange=1,HideOnSelectionChange_UxmlAttributeFlags=1,
            HideOnFocusLoss=1,HideOnFocusLoss_UxmlAttributeFlags=1,Anchor=1,Anchor_UxmlAttributeFlags=1,
            AlwaysUpdateInternalSelection=1,AlwaysUpdateInternalSelection_UxmlAttributeFlags=1,
            ForceRefreshOnNewChoices=1,ForceRefreshOnNewChoices_UxmlAttributeFlags=1)
        ds['BindChoicesFunction']={'m_target':{'m_guid':CHOICES},'m_inputs':{'m_variable':{'m_argumentBytes':args([
            ('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]',b'\x02\x01'+string(FC_OPTION)+b'\x01'+string(PORTRAIT_OPTION))])}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
        ds['BindChoicesFunction_UxmlAttributeFlags']=1
        box(d,drop,220,8,112,26)
        d.st(drop,[(65537,d.px(12))])
        arrow=d.add(donor,1058,drop,'HoverCardModeArrow')
        d.a(arrow)['m_Classes']=copy.deepcopy(donor.a(1058)['m_Classes'])
        box(d,arrow,92,6,14,14)
        variables=next(r['data'] for r in d.r.values() if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
        variables['ValueVariables'] += [
            {'m_name':STATE,'m_scopeValue':{'m_serializedData':'Int|0|(Session,Explicit,{},{TF27.HoverCard.Mode.v1})'}},
            {'m_name':FC_OPTION,'m_scopeValue':{'m_serializedData':'Int|0|'}},
            {'m_name':PORTRAIT_OPTION,'m_scopeValue':{'m_serializedData':'Int|1|'}}]
        variables['ValueVariables_UxmlAttributeFlags']=1
        old_ids={r['rid'] for r in original['references']['RefIds']}
        oldrefs=refs(original)
        touched=[i for i in old_ids if oldrefs[i]!=d.r[i]]
        assert set(touched)=={parent,stage,1015},touched
        assert d.a(selector)['m_Children']==[{'rid':stage},{'rid':large}]
        assert not any('OverviewCard' in d.data(i).get('name','') for i in picmap.values() if 'm_SerializedData' in d.a(i))
        d.save()
        target_reports.append({'path_id':pid,'switch':selector,'dropdown':drop,'large_portrait':picmap[portrait], 'original_refs_changed':touched,'fc_original_subtree_preserved':True})
    # Register the private row and its style in the destination AssetBundle.
    span=[{'m_FileID':0,'m_PathID':ROW},{'m_FileID':0,'m_PathID':STYLE}]
    meta['m_Container'].append((ROW_GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':span[0]}))
    meta['m_PreloadTable']+=span
    meta['m_Container'].sort(key=lambda v:v[0])
    metadata.save_typetree(meta);changes[W][metadata.path_id]=copy.deepcopy(meta)
    catpath=(GAME.parent if tag=='game' else SKIN)/'catalog.bin'
    catbefore=catpath.read_bytes();cat=cm.Catalog(catbefore)
    base=cat.locations(CARD_GUID)[0]
    cat=cm.Catalog(cat.add_key_location(ROW_GUID,base,base))
    required=[]
    for key in [CHOICES,COMPARE]:
        for dep in cat.location(cat.locations(key)[0])['dependencies']:
            if dep not in required:required.append(dep)
    for key in [CARD_GUID,ROW_GUID]:
        for offset in cat.locations(key):
            deps=cat.location(offset)['dependencies']
            deps += [i for i in required if i not in deps]
            struct.pack_into('<I',cat.data,offset+12,cat.append(b''.join(struct.pack('<I',i) for i in deps),True))
    records=list(cat.key_records)
    idx=next(i for i,(ko,_) in enumerate(records) if cat.object(ko)=='GameWorldVisualTreeAssetPreload')
    ko,ls=records[idx];items=[i[0] for i in cat.array(ls,'I')]+cat.locations(ROW_GUID)
    records[idx]=(ko,cat.append(b''.join(struct.pack('<I',i) for i in items),True))
    struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*i) for i in records),True))
    catraw=bytes(cat.data)
    output=env[W].file.save(packer='lz4')
    saved={o.path_id:o for o in UnityPy.load(output).objects}
    assert set(saved)==set(objs[W]) and reserved.isdisjoint(saved)
    for pid,h in hashes.items():
        if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h,(tag,pid)
    for pid,tree in changes[W].items():assert saved[pid].read_typetree()==tree,(tag,pid)
    finalcat=cm.Catalog(catraw)
    oldcat=cm.Catalog(catbefore)
    keys0=dict(oldcat.keys())
    keys1=dict(finalcat.keys())
    assert set(keys1)==set(keys0)|{ROW_GUID}
    for key in keys0:
        if key=='GameWorldVisualTreeAssetPreload':continue
        assert finalcat.array(keys1[key],'I')==oldcat.array(keys0[key],'I'),key
    assert finalcat.location(finalcat.locations(ROW_GUID)[0])['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
    assert finalcat.locations(ROW_GUID)[0] in [v[0] for v in finalcat.array(keys1['GameWorldVisualTreeAssetPreload'],'I')]
    for name,old,new in [(W,before,output),('catalog.bin',catbefore,catraw),('catalog.hash',None,hashlib.md5(catraw).hexdigest().encode())]:
        target=folder/name if name==W else catpath.parent/name
        if not target.exists():continue
        if old is None:old=target.read_bytes()
        backup=OUT/('backup-'+tag)/name;source=OUT/tag/name
        backup.parent.mkdir(exist_ok=True);source.parent.mkdir(exist_ok=True)
        backup.write_bytes(old);source.write_bytes(new)
        transactions.append({'target':str(target),'backup':str(backup),'source':str(source),'before':sha(old),'after':sha(new)})
    reports.append({'target':tag,'cards':target_reports,'unrelated_objects_unchanged':len(hashes)-len([i for i in hashes if i in changes[W]]),'new_row_guid':ROW_GUID,'default':'FC卡面','session_selection':True})

for tx in transactions:assert sha(Path(tx['target']).read_bytes())==tx['before'],tx['target']
for path,h in protected.items():assert sha(Path(path).read_bytes())==h,path
manifest={'installed':False,'runtime_verified':False,'protected_sha256':protected,'reports':reports}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(transactions,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif($LASTEXITCODE -ne 0){throw 'Resource transaction failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('球员悬浮FC卡右上角新增原生下拉选择器：FC卡面、仅大头像。默认FC，使用独立Session键共享本次游戏会话选择。大头像复用当前卡面完整原生照片/默认头像分支，310×460等比完整显示，不含FC背景、姓名附加资料或六项评分。球场、属性及其他悬浮区域沿用现有资源。游戏和独立主皮肤分别在当前资源上增量处理，同GUID两份FC模板同时维护。新增私有菜单行并登记目录、GameWorld预加载及原生函数依赖。文件验证不能代替游戏显示验证；未启动游戏或操作桌面。安装/回退使用同目录脚本，校验当前哈希，禁止旧整包覆盖后续修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'reports':reports},ensure_ascii=False),flush=True)
