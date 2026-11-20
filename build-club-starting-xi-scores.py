"""Add first-XI attacking and defensive scores beside the club kits."""
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import uuid
from pathlib import Path

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite=TypeTreeHelper.write_value
def load_definitions(file,names,rewrites=()):
    code=ast.parse((R/file).read_text('utf8'))
    for node in code.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
            source=ast.unparse(node)
            for before,after in rewrites:
                source=source.replace(before,after)
            exec(compile(source,file,'exec'),globals())

load_definitions('add-card-six-ratings.py',{'write','guid','gid','link','socket_source','constant','check_graph','validate_ui'})
load_definitions('add-card-six-ratings.py',{'make_function','graph_runner'},(
    ("'OverviewCard'","'ClubOverviewStartingXI'"),
    ('4 * mid + 1','22 * mid + 10'),
    ('range(300)','range(1000)'),
))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
load_definitions('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
load_definitions('build-club-stadium-overlay-local.py',{'stage'})

cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(cfg['bundle_root'])
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FN='ui-visualfunctions_assets_all.bundle'
head_pid=-991100000000000
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
sha=lambda b:hashlib.sha256(b).hexdigest()
out=R/('club-starting-xi-scores-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx=[]

def objects(file):
    return UnityPy.load(str(file)).assets[0].objects
vf=objects(GAME/FN)
functions={o.peek_name():o for o in vf.values() if o.type.name=='MonoBehaviour'}
templates=json.loads((R/'movement-sum-node-templates-v37.json').read_text('utf8'))
for o in functions.values():
    for ref in o.read_typetree().get('references',{}).get('RefIds',[]):
        if ref['type']['class']:
            templates.setdefault(ref['type']['class'],ref)
native_text=functions['BindIntAddOrSubstractToSIText'].read_typetree()
native_sum=functions['BindMultipleIntArgsAsSumToDestination'].read_typetree()
views=objects(GAME/'ui-tableviews_assets_all.bundle')
tables={o.peek_name():o for o in views.values() if o.type.name=='MonoBehaviour'}
factory=next(o for o in objects(GAME/'ui-tablefactories_assets_all.bundle').values() if o.peek_name()=='TacticTeamSelectionTableFactory')
def cols(value):
    if isinstance(value,dict):
        if isinstance(value.get('m_id'),str) and 'm_sortBinding' in value:
            yield value['m_id'],value['m_sortBinding']['m_path'].lower()
        for v in value.values():yield from cols(v)
    elif isinstance(value,list):
        for v in value:yield from cols(v)
column_paths=dict(cols(factory.read_typetree()))
profiles=[]
for i,(code,title,view) in enumerate((('Attack','进攻','FirstTeamTableAttributesAttacking'),('Defence','防守','FirstTeamTableAttributesDefensive'))):
    fields=[v['m_columnID'] for v in tables[view].read_typetree()['m_tableView']['m_tableConfig'] if v['m_columnID'].startswith('attribute-')]
    assert len(fields)==10
    paths=[column_paths[f].removeprefix('binding.') for f in fields]
    assert all(p.startswith('player.attribute') and p.endswith('.attributeminvalue') for p in paths),paths
    paths=[f'xiSlot{j+1}.{p}' for j in range(11) for p in paths]
    profiles.append((code,title,-991100000000080-i,uuid.uuid5(uuid.NAMESPACE_URL,'tf27/club/starting-xi/'+code).hex,paths))
def visual_arg(kind,payload):
    return bytes([len(kind)])+kind+payload
def path_arg(path):
    text=path.encode('ascii')
    return visual_arg(b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',bytes([1,len(text)])+text)
def function_ref(guid,args):
    return {'m_target':{'m_guid':guid},'m_inputs':{'m_variable':{'m_argumentBytes':list(bytes([len(args)])+b''.join(struct.pack('<I',len(x))+x for x in args))}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
def select_slot(index):
    idx=visual_arg(b'SI.VisualScripting.Int32VisualArg',struct.pack('<i',index))
    no=visual_arg(b'SI.VisualScripting.BooleanVisualArg',b'\0')
    yes=visual_arg(b'SI.VisualScripting.BooleanVisualArg',b'\1')
    return function_ref('21ee6b430323a494099e32901c5497cb',[path_arg('club.MainTeam.Tactic.TacticalPositions'),path_arg(f'xiSlot{index+1}'),idx,no,yes])

audit=[]
for tag,folder in [('game',GAME),('skin',Path(cfg['skin_packages']))]:
    bp=folder/G
    before=bp.read_bytes()
    env=UnityPy.load(before)
    a=env.assets[0]
    objs={G:a.objects,W:objects(folder/W)}
    hashes={i:sha(o.get_raw_data()) for i,o in objs[G].items()}
    top=Doc(G,pid=head_pid)
    assert top.a(1006)['m_Children'][-1]=={'rid':1011}
    donor=Doc(W,name='PortalNewsTimedTile_6x4')
    scorebox=top.add(donor,1002,1006,'ClubOverviewStartingXIScores')
    setter=top.data(scorebox)
    assert 'BindFunction' in setter and 'ReferenceVariables' in setter
    setter.update(ValueVariables=[],ValueVariables_UxmlAttributeFlags=0,
                  ReferenceVariables=[{'m_type':{'id':910512747},'m_initToNull':1,'m_name':f'xiSlot{j+1}'} for j in range(11)],
                  ReferenceVariables_UxmlAttributeFlags=1,BindFunction=[select_slot(i) for i in range(11)],
                  BindFunction_UxmlAttributeFlags=1)
    top.st(scorebox,[(131083,top.enum('row')),(131091,top.px(8)),(131085,top.num(0)),(131105,top.px(112)),(131074,top.enum('center'))])
    style=Doc(G,name='ClubSiteHeaderTemplate')
    def label(parent,name,text,points,bind=None):
        i=top.add(style,1060,parent,name)
        sd=top.data(i)
        sd.update(text=text,text_UxmlAttributeFlags=1)
        top.a(i)['m_Classes']=['body-md-regular','global-text-primary']
        top.st(i,[(65537,top.px(points)),(65546,top.enum('middle-center')),(131105,top.pct(100))])
        if bind:
            sd['TextBinding']={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':bind}
            sd['TextBinding_UxmlAttributeFlags']=1
        else:
            sd['TextBinding']['m_kind']=0
            sd['TextBinding_UxmlAttributeFlags']=0
    SUM=-940000000000100
    go=a.objects
    fn_donor=go[SUM]
    metaobj=next(o for o in a.objects.values() if o.type.name=='AssetBundle')
    meta=metaobj.read_typetree()
    key=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':SUM})
    catpath=(folder.parent if tag=='game' else folder)/'catalog.bin'
    cat_before=catpath.read_bytes()
    cat=cm.Catalog(cat_before)
    assert cat.locations('21ee6b430323a494099e32901c5497cb')
    loc=cat.locations(key)[0]
    assert cat.location(loc)['type'][1]=='SI.VisualScripting.VisualFunction'
    changed={}
    for code,title,pid,fg,paths in profiles:
        col=top.add(style,1006,scorebox,code+'ScoreColumn')
        top.st(col,[(131083,top.enum('column')),(131105,top.px(56)),(131085,top.num(0))])
        label(col,code+'ScoreLabel',title,13)
        label(col,code+'ScoreValue','--',21,function_ref(fg,[path_arg(p) for p in paths]))
        fn=make_function(code,[(path,5) for path in paths])
        fn['m_description']='Starting XI: sum of 110 visible attributes, divided by 22 and rounded half-up. Missing values display --.'
        check_graph(fn)
        run=graph_runner(fn)
        for value in (1,10,20):
            assert run([value]*110)==str((110*value+11)//22)
        for total in range(11,2201,22):
            assert run([10]*110,total-1)==str((total+10)//22)
            assert run([10]*110,total)==str((total+11)//22)
        for value in (None,0,21):
            assert run([10]*109+[value])=='--'
        import_types(next(iter(vf.values())).assets_file,a,fn['references']['RefIds'])
        assert pid not in a.objects
        asset=copy.copy(fn_donor)
        asset.path_id=pid
        asset.data=asset._read_until=None
        a.objects[pid]=asset
        changed[pid]=fn
        pointer={'m_FileID':0,'m_PathID':pid}
        start=len(meta['m_PreloadTable'])
        meta['m_PreloadTable'].extend([fn['m_Script'],pointer])
        meta['m_Container'].append((fg,{'asset':pointer,'preloadIndex':start,'preloadSize':2}))
        cat=cm.Catalog(cat.add_key_location(fg,loc,loc))
        added=cat.location(cat.locations(fg)[0])
        assert added['dependencies']==cat.location(loc)['dependencies']
    meta['m_Container'].sort(key=lambda row:row[0])
    validate_ui(top.d,top.s)
    changed.update({head_pid:top.d,top.sid:top.s,metaobj.path_id:meta})
    for i,t in changed.items():a.objects[i].save_typetree(t)
    result=env.file.save(packer='lz4')
    check=UnityPy.load(result).assets[0].objects
    assert set(check)==set(hashes)|set(changed)
    for i,t in changed.items():assert check[i].read_typetree()==t,(tag,i)
    for i,h in hashes.items():
        if i not in changed:assert sha(check[i].get_raw_data())==h,(tag,i)
    stage(tag,bp,before,result)
    encoded=bytes(cat.data)
    stage(tag,catpath,cat_before,encoded)
    hp=catpath.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(encoded).hexdigest().encode('ascii'))
    audit.append({'target':tag,'score_functions':2,'starting_slots':11,'formula':'(sum + 11) // 22','rounding_thresholds_verified':200})
manifest={'installed':False,'runtime_verified':False,'protected_sha256':{},'audit':audit}
for n,data in [('transaction',tx),('manifest',manifest)]:
    (out/(n+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)

