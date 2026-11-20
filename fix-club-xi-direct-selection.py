"""Use the native PlayerFromTeamSelectionIndex accessor, in eleven isolated scopes."""
import ast, copy, datetime, hashlib, json, struct, sys, importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
def defs(file,names):
    for n in ast.parse((R/file).read_text('utf8')).body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names:
            exec(compile(ast.Module([n],[]),file,'exec'),globals())
defs('add-card-six-ratings.py',{'write','validate_ui'})
defs('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
defs('build-club-stadium-overlay-local.py',{'stage'})
defs('build-club-starting-xi-scores.py',{'visual_arg','path_arg','function_ref'})
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
out=R/('club-xi-direct-selection-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[];audit=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
    path=folder/G;before=path.read_bytes();env=UnityPy.load(before);af=env.assets[0]
    world=UnityPy.load(str(folder/W));objs={G:af.objects,W:world.assets[0].objects}
    top=Doc(G,pid=-991100000000000)
    donor=Doc(W,name='PortalNewsTimedTile_6x4')
    box=top.named('ClubOverviewStartingXIScores')
    columns=[x['rid'] for x in top.a(box)['m_Children']]
    assert len(columns)==2
    parent=box
    for index in range(11):
        if index:parent=top.add(donor,1002,parent,'XISelectionScope'+str(index))
        data=top.data(parent)
        data.update(ValueVariables=[{'m_name':'teamselectionindex','m_scopeValue':{'m_serializedData':f'Int|{index}|'}}],
            ValueVariables_UxmlAttributeFlags=1,
            ReferenceVariables=[{'m_type':{'id':1886157170},'m_initToNull':1,'m_name':f'xiplayer{index+1}'}],
            ReferenceVariables_UxmlAttributeFlags=1,
            BindFunction=[function_ref('8ca91f1cfa07a3447ad7c8381cadfef5',[
                path_arg('tactic.PlayerFromTeamSelectionIndex'),path_arg(f'xiplayer{index+1}'),
                visual_arg(b'SI.VisualScripting.BooleanVisualArg',b'\1')])],BindFunction_UxmlAttributeFlags=1)
        if index:top.st(parent,[(131083,top.enum('row')),(131105,top.pct(100)),(131085,top.num(0))])
    for col in columns:top.move(col,parent)
    for name in ['AttackScoreValue','DefenceScoreValue']:
        data=top.data(top.named(name));var=data['TextBinding']['m_visualFunction']['m_inputs']['m_variable']
        raw=bytes(var['m_argumentBytes']);offset=1;parts=[]
        assert raw[0]==110
        for index in range(110):
            size=struct.unpack_from('<I',raw,offset)[0];part=raw[offset+4:offset+4+size];offset+=4+size
            text=part[part[0]+3:].decode('ascii')
            expected=f'xiSlot{index//10+1}.player.'
            assert text.startswith(expected),text
            parts.append(path_arg(f'xiplayer{index//10+1}.'+text[len(expected):]))
        assert offset==len(raw)
        var['m_argumentBytes']=list(bytes([110])+b''.join(struct.pack('<I',len(p))+p for p in parts))
    validate_ui(top.d,top.s)
    # Verify the live native accessor and its required index scope, not merely a guessed property name.
    native=Doc(W,name='PitchPositionValueDropdownRow')
    assert 'Tactic.PlayerFromTeamSelectionIndex.Name' in json.dumps(native.d)
    assert 'teamselectionindex' in json.dumps(native.d)
    cat=cm.Catalog(((folder.parent if tag=='game' else folder)/'catalog.bin').read_bytes())
    assert cat.location(cat.locations('8ca91f1cfa07a3447ad7c8381cadfef5')[0])['type'][1]=='SI.VisualScripting.VisualFunction'
    hashes={pid:sha(o.get_raw_data()) for pid,o in af.objects.items()}
    changes={top.obj.path_id:top.d,top.sid:top.s}
    for pid,t in changes.items():af.objects[pid].save_typetree(t)
    after=env.file.save(packer='lz4');check=UnityPy.load(after).assets[0].objects
    assert set(check)==set(hashes)
    for pid,o in check.items():
        if pid in changes:assert o.read_typetree()==changes[pid]
        else:assert sha(o.get_raw_data())==hashes[pid]
    stage(tag,path,before,after)
    audit.append({'target':tag,'native_player_accessor':'tactic.PlayerFromTeamSelectionIndex',
        'selection_indices':list(range(11)),'independent_scopes':11,'attribute_paths':220,
        'formula_objects_unchanged':True,'unrelated_objects_byte_identical':True})
for n,d in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},audit=audit))]:
    (out/(n+'.json')).write_text(json.dumps(d,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
