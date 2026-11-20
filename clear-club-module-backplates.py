"""Remove the two Club Overview module backplates on current independent bases."""
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, uuid
from pathlib import Path
from zoneinfo import ZoneInfo
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
for file, names in [
    ('add-card-six-ratings.py', {'write', 'validate_ui'}),
    ('build-match-ui-avatars-layout.py', {'refs','sd','find','pointer_remap','import_types','Doc'}),
    ('build-club-stadium-overlay-local.py', {'stage'}),
]:
    for node in ast.parse((R/file).read_text('utf8')).body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
            exec(compile(ast.Module([node],[]),file,'exec'),globals())
TypeTreeHelper.write_value = write
poolmap = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
spec = importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cfg = json.loads((R/'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
source_guid = 'f677caec43d6c1342b1bba39c5ae2c5f'
private_guid = uuid.uuid5(uuid.NAMESPACE_URL,'tf27/club/budget-transparent-backplate').hex
private_pid, style_pid = -991100000000100, -991100000000101
out = R/('club-module-backplates-clear-'+datetime.datetime.now(ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx, audits = [], []
sha = lambda raw:hashlib.sha256(raw).hexdigest()
def clear_surface(doc,rid):
    clear = doc.val(4,{'r':0.,'g':0.,'b':0.,'a':0.})
    doc.st(rid,[(458752,clear),(458753,doc.enum('none')),(262146,clear)])

for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
    originals = {name:(folder/name).read_bytes() for name in [G,W]}
    envs = {name:UnityPy.load(raw) for name,raw in originals.items()}
    objs = {name:env.assets[0].objects for name,env in envs.items()}
    changes = {G:{},W:{}}
    global_af = envs[G].assets[0]
    meta_obj = next(o for o in objs[G].values() if o.type.name=='AssetBundle')
    meta = meta_obj.read_typetree()
    entry = next(v for k,v in meta['m_Container'] if k==source_guid and 'inlineSheet' in objs[G][v['asset']['m_PathID']].read_typetree())
    source = Doc(G,pid=entry['asset']['m_PathID'])
    assert private_pid not in objs[G] and style_pid not in objs[G]
    # A private tile keeps the clear background specific to Club Overview.
    tree, sheet = copy.deepcopy(source.d),copy.deepcopy(source.s)
    tree['m_Name'] = 'ClubOverviewTransparentBudgetTile'
    tree['inlineSheet'] = {'m_FileID':0,'m_PathID':style_pid}
    sheet['m_Name'] = 'ClubOverviewTransparentBudgetTileStyle'
    for donor,pid,value in [(source.obj,private_pid,tree),(objs[G][source.sid],style_pid,sheet)]:
        clone = copy.copy(donor)
        clone.path_id=pid
        clone.data=clone._read_until=None
        objs[G][pid]=clone
    tile=Doc(G,pid=private_pid,tree=tree,style=sheet)
    for rid in (1002,1006,1008,1010):
        clear_surface(tile,rid)
    validate_ui(tile.d,tile.s)
    changes[G].update({private_pid:tile.d,style_pid:tile.s})
    preload = copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
    for pointer in preload:
        if pointer['m_FileID']==0:
            pointer['m_PathID']={source.obj.path_id:private_pid,source.sid:style_pid}.get(pointer['m_PathID'],pointer['m_PathID'])
    for pid in (private_pid,style_pid):
        pointer={'m_FileID':0,'m_PathID':pid}
        if pointer not in preload:preload.append(pointer)
    meta['m_Container'].append((private_guid,{'asset':{'m_FileID':0,'m_PathID':private_pid},'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(preload)}))
    meta['m_PreloadTable'].extend(preload)
    meta['m_Container'].sort(key=lambda row:row[0])
    changes[G][meta_obj.path_id]=meta

    finance=Doc(W,pid=-991100000000040)
    using=next(u for u in finance.d['m_Usings'] if u['alias']=='tile-wide-4x2')
    assert using['path']==source_guid
    using.update(path=private_guid,asset={'m_FileID':0,'m_PathID':0})
    changes[W][finance.obj.path_id]=finance.d
    stats=Doc(W,pid=-991100000000050)
    clear_surface(stats,1004)
    changes[W].update({stats.obj.path_id:stats.d,stats.sid:stats.s})
    validate_ui(finance.d,finance.s)
    validate_ui(stats.d,stats.s)

    catpath=(folder.parent if tag=='game' else folder)/'catalog.bin'
    catbefore=catpath.read_bytes()
    cat=cm.Catalog(catbefore)
    source_loc=next(l for l in cat.locations(source_guid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
    cat=cm.Catalog(cat.add_key_location(private_guid,source_loc,source_loc))
    label='GlobalVisualTreeAssetPreload'
    idx=next(i for i,(key,_) in enumerate(cat.keys()) if key==label)
    keyptr,locptr=cat.key_records[idx]
    locs=[x[0] for x in cat.array(locptr,'I')]+cat.locations(private_guid)
    records=list(cat.key_records)
    records[idx]=(keyptr,cat.append(b''.join(struct.pack('<I',x) for x in locs),True))
    struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*row) for row in records),True))
    cat=cm.Catalog(bytes(cat.data))
    assert cat.locations(private_guid)[0] in cat.locations(label)
    assert cat.location(cat.locations(private_guid)[0])['dependencies']==cat.location(source_loc)['dependencies']
    # All bindings and events in each original element are byte-for-byte retained.
    for rid,ref in source.r.items():
        actual=copy.deepcopy(tile.r[rid])
        if 'm_RuleIndex' in ref.get('data',{}):
            actual['data']['m_RuleIndex']=ref['data']['m_RuleIndex']
        assert actual==ref
    for name,env in envs.items():
        af=env.assets[0]
        baseline=UnityPy.load(originals[name]).assets[0].objects
        for pid,value in changes[name].items():af.objects[pid].save_typetree(value)
        after=env.file.save(packer='lz4')
        check=UnityPy.load(after).assets[0].objects
        assert set(check)==set(baseline)|set(changes[name])
        for pid,obj in check.items():
            if pid in changes[name]:assert obj.read_typetree()==changes[name][pid]
            else:assert obj.get_raw_data()==baseline[pid].get_raw_data()
        stage(tag,folder/name,originals[name],after)
    encoded=bytes(cat.data)
    stage(tag,catpath,catbefore,encoded)
    hp=catpath.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(encoded).hexdigest().encode('ascii'))
    audits.append({'target':tag,'modules':['ClubOverviewFinancesPanel','ClubOverviewTeamStatsPanel'],
                   'native_budget_bindings_preserved':True,'unrelated_objects_byte_identical':True,
                   'private_budget_tile_guid':private_guid})
for name,value in [('transaction',tx),('manifest',{'installed':False,'runtime_verified':False,'protected_sha256':{},'audit':audits})]:
    (out/(name+'.json')).write_text(json.dumps(value,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
