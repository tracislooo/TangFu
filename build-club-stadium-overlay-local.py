"""Overlay club details on a local stadium photograph. Run on the by-club baseline."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
sys.path.insert(0,str(root/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
def helpers(file,names):
    tree = ast.parse((root/file).read_text('utf8'))
    exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],[]),file,'exec'),globals())
helpers('redesign-card-top-info-foot.py',{'write'})
helpers('build-match-ui-avatars-layout.py',{'import_types'})
helpers('add-card-six-ratings.py',{'validate_ui'})
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',root/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cfg=json.loads((root/'current-game-location.json').read_text('utf8'))
game=Path(cfg['bundle_root'])
pack=Path(sys.argv[1]).resolve()
provider='SI.Core.LocalAssetProvider'
prefix='tf27/stadium/club/'
photos={}
for row in ET.parse(pack/'config.xml').findall('.//record[@to]'):
    match=re.fullmatch(r'graphics/pictures/club/(\d+)/background',row.get('to'),re.I)
    if not match: continue
    src=(pack/row.attrib['from']).resolve()
    assert src.is_relative_to(pack)
    path=next((f for f in (src,src.with_suffix('.jpg'),src.with_suffix('.png')) if f.suffix.lower() in ('.jpg','.png') and f.is_file()),None)
    if path:
        key=prefix+match[1]+'/background'
        assert key not in photos or photos[key]==path
        photos[key]=path
assert photos
out=root/('club-stadium-overlay-local-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
tx=[]
def stage(tag,p,b,a):
    dst=out/tag/p.name
    bak=out/('backup-'+tag)/p.name
    for path,raw in [(dst,a),(bak,b)]:
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
    tx.append(dict(target=str(p),source=str(dst),backup=str(bak),before=sha(b),after=sha(a)))
def bundle(tag,path,edit):
    before=path.read_bytes()
    env=UnityPy.load(before)
    af=env.assets[0]
    hashes={i:sha(o.get_raw_data()) for i,o in af.objects.items()}
    changes=edit(af)
    for i,t in changes.items():af.objects[i].save_typetree(t)
    result=env.file.save(packer='lz4')
    check=UnityPy.load(result).assets[0].objects
    assert set(check)==set(hashes)
    for i,h in hashes.items():
        if i in changes:assert check[i].read_typetree()==changes[i]
        else:assert sha(check[i].get_raw_data())==h
    stage(tag,path,before,result)

def overlay(af):
    pid=-991100000000030
    tree=af.objects[pid].read_typetree()
    sid=tree['inlineSheet']['m_PathID']
    sheet=af.objects[sid].read_typetree()
    refs={r['rid']:r.get('data',{}) for r in tree['references']['RefIds']}
    photo=next(i for i,r in refs.items() if 'm_SerializedData' in r and refs[r['m_SerializedData']['rid']].get('name')=='ClubOverviewStadiumPackPhoto')
    parent=refs[photo]['m_Parent']['rid']
    assert refs[parent]['m_Children']==[{'rid':1012},{'rid':photo}]
    refs[parent]['m_Children'].reverse()
    def styles(i,values):
        el=refs[i]
        idx=el['m_RuleIndex']
        rule=copy.deepcopy(sheet['m_Rules'][idx]) if idx>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
        props=[p for p in rule['m_Properties'] if p['m_Id'] not in values]
        for prop,(kind,val) in values.items():
            pool=sheet[poolmap[kind]]
            props.append({'m_Id':prop,'m_Line':-1,'m_CustomName':'','m_Values':[{'m_ValueType':kind,'valueIndex':len(pool)}]})
            pool.append(val)
        rule['m_Properties']=props
        el['m_RuleIndex']=len(sheet['m_Rules'])
        sheet['m_Rules'].append(rule)
    zero=(3,{'unit':1,'value':0.0})
    full=(3,{'unit':2,'value':100.0})
    styles(parent,{131102:(7,'relative'),458768:(7,'hidden')})
    styles(photo,{131102:(7,'absolute'),131089:zero,131104:zero,131105:full,131087:full,131098:zero,262153:(7,'scale-and-crop')})
    image=refs[refs[photo]['m_SerializedData']['rid']]
    image.update(ScaleMode=1,scaleMode=1,scaleMode_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    def shade(alpha):return (4,dict(r=0.03125,g=0.078125,b=0.125,a=alpha))
    styles(1012,{458752:shade(.53125)})
    for i in (1016,1023,1025,1027,1028,1033,1034):
        styles(i,{458752:shade(0)})
    validate_ui(tree,sheet)
    return {pid:tree,sid:sheet}

functions=UnityPy.load(str(game/'ui-visualfunctions_assets_all.bundle')).assets[0]
def donor(name,kind):
    obj=next(o for o in functions.objects.values() if o.peek_name()==name)
    return next(r for r in obj.read_typetree()['references']['RefIds'] if r['type']['class']==kind)
def binding(af):
    pid=-991100000000070
    tree=af.objects[pid].read_typetree()
    records=tree['references']['RefIds']
    def node(kind):return next(r['data'] for r in records if r['type']['class']==kind)
    cats=[r['data'] for r in records if r['type']['class']=='TextFunctions_Concat']
    assert cats[0]['m_dataInText']['m_defaultSocketValue']['m_value']=='graphics/pictures/club/'
    cats[0]['m_dataInText']['m_defaultSocketValue']['m_value']=prefix
    exists=donor('TryConvertObjectIDToAddressableID','GeneralVisualFunction_ResourceExists')
    branch=donor('BindToDatabaseObjectImage','GeneralVisualFunction_Branch')
    hide=donor('BindToDatabaseObjectImage','VisualElementFunctionLibrary_HideElement')
    negate=donor('BindToDatabaseObjectImage','GeneralVisualFunction_Not_bool_bool')
    import_types(functions,af,[exists,branch,hide,negate])
    for r in (exists,branch,hide,negate):
        assert all(old['rid']!=r['rid'] for old in records)
        r['data']['m_parentID']=tree['m_id']
        records.append(r)
        tree['m_nodes'].append({'rid':r['rid']})
    ex,br,vis,inv=[r['data'] for r in (exists,branch,hide,negate)]
    def link(a,b):a['m_destinationID']=b['m_id']
    def wire(a,b):a['m_sourceID']=b['m_id']
    show=node('SIImage_SetImage')
    link(cats[1]['m_execOutExecOutput'],ex['m_execInExecInput'])
    wire(ex['m_dataInResourceName'],cats[1]['m_dataOutString'])
    link(ex['m_execOutExecOutput'],vis['m_execInExecInput'])
    wire(inv['m_dataInB'],ex['m_dataOutBoolean'])
    wire(vis['m_dataInShouldHide'],inv['m_dataOutBoolean'])
    wire(vis['m_dataInVisualElement'],node('VisualDataGetterNode')['m_dataSocket'])
    link(vis['m_execOutExecOutput'],br['m_execInExecInput'])
    wire(br['m_dataInCondition'],ex['m_dataOutBoolean'])
    link(br['m_execOutTrue'],show['m_execInExecInput'])
    br['m_execOutFalse']['m_destinationID']={'m_idBytes':[0]*16}
    return {pid:tree}

def locations(raw):
    cat=cm.Catalog(raw)
    keys=dict(cat.keys())
    assert not photos.keys() & keys.keys()
    records=list(cat.key_records)
    st=next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str))
    it=next(cat.location(i[0])['raw'][6] for k,v in keys.items() if isinstance(k,str) for i in cat.array(v,'I')[:1] if cat.location(i[0])['type'][1]=='UnityEngine.Texture2D')
    prov=cat.add_string(provider)
    def string(s):
        if s.isascii():return cat.add_string(s)
        return cat.append(s.encode('utf-16le'),True)|0x80000000
    for k,p in sorted(photos.items()):
        key=string(k)
        loc=cat.append(struct.pack('<7I',key,string(p.as_posix()),prov,cm.NULL,0,cm.NULL,it))
        obj=cat.append(struct.pack('<IHH',key,0,0))
        records.append((cat.append(struct.pack('<II',st,obj)),cat.append(struct.pack('<I',loc),True)))
    struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*r) for r in records),True))
    check=cm.Catalog(bytes(cat.data))
    mapping=dict(check.keys())
    assert len(mapping)==len(keys)+len(photos) and check.key_records[:len(cat.key_records)]==cat.key_records
    for key,p in photos.items():
        loc=check.location(check.array(mapping[key],'I')[0][0])
        assert (loc['internal'],loc['provider'],loc['type'][1])==(p.as_posix(),provider,'UnityEngine.Texture2D')
    return bytes(cat.data)

for tag,folder in [('game',game),('skin',Path(cfg['skin_packages']))]:
    bundle(tag,folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',overlay)
    bundle(tag,folder/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',binding)
    p=(folder.parent if tag=='game' else folder)/'catalog.bin'
    raw=p.read_bytes()
    cat=locations(raw)
    stage(tag,p,raw,cat)
    p=p.with_suffix('.hash')
    stage(tag,p,p.read_bytes(),hashlib.md5(cat).hexdigest().encode('ascii'))
for n,data in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},provider=provider,pack=str(pack),unique_photo_keys=len(photos),missing_photo='hide photo only',layout='absolute photo behind translucent stadium details'))]:
    (out/(n+'.json')).write_text(json.dumps(data,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(root/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out)

