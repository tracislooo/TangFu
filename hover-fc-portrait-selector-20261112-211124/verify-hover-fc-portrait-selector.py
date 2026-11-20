"""Audit prepared or installed hover selector resources without running the game."""
from pathlib import Path
import ast, hashlib, importlib.util, json, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
out=Path(sys.argv[1]);installed='--installed' in sys.argv
tx=json.loads((out/'transaction.json').read_text('utf8'))
manifest=json.loads((out/'manifest.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
reserved={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
CARD='64033a72b9925c8dad3b08826077c328';ROW='c0d7ea1aa9d052b6aeaee5add8f5c6fd'
def guids(v):
    found=set()
    if isinstance(v,dict):
        for k,x in v.items():
            if k in ['m_guid','m_AssetGUID','path'] and isinstance(x,str) and len(x)==32 and all(c in '0123456789abcdef' for c in x):found.add(x)
            else:found.update(guids(x))
    elif isinstance(v,(tuple,list)):
        for x in v:found.update(guids(x))
    return found
reports=[]
for root,tag in [(Path(cfg['bundle_root']),'game'),(Path(cfg['skin_packages']),'skin')]:
    candidate=out/tag
    catpath=(root.parent if tag=='game' else root)/'catalog.bin' if installed else candidate/'catalog.bin'
    cat=cm.Catalog(catpath.read_bytes());keys=dict(cat.keys())
    oldcat=cm.Catalog((out/('backup-'+tag)/'catalog.bin').read_bytes())
    assert set(keys)==set(dict(oldcat.keys()))|{ROW}
    allowed_locations=set(oldcat.locations(CARD))
    for key,oldpointer in oldcat.keys():
        original=[x[0] for x in oldcat.array(oldpointer,'I')]
        actual=[x[0] for x in cat.array(keys[key],'I')]
        assert actual==original+(cat.locations(ROW) if key=='GameWorldVisualTreeAssetPreload' else []),key
        for offset in original:
            previous,current=oldcat.location(offset),cat.location(offset)
            if offset in allowed_locations:
                assert current['dependencies'][:len(previous['dependencies'])]==previous['dependencies']
                previous={k:v for k,v in previous.items() if k not in ['dependencies','raw']}
                current={k:v for k,v in current.items() if k not in ['dependencies','raw']}
            assert current==previous,key
    loaded={};seen=set();audits=[]
    def load(bundle):
        if bundle not in loaded:
            path=root/bundle if installed or not (candidate/bundle).exists() else candidate/bundle
            if not path.exists():path=Path(cfg['bundle_root'])/bundle
            oo={o.path_id:o for o in UnityPy.load(str(path)).objects}
            meta=next((o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle'),None)
            assert meta is not None,('Missing AssetBundle metadata',bundle,str(path))
            loaded[bundle]=(oo,meta)
        return loaded[bundle]
    def audit(guid):
        if guid in seen:return
        seen.add(guid);assert guid in keys,('missing GUID',guid)
        locs=[cat.location(v[0]) for v in cat.array(keys[guid],'I')]
        locs=[l for l in locs if l['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','SI.VisualScripting.VisualFunction']]
        if not locs:return
        for l in locs:
            assert l['dependencies']
            bundle=cat.location(l['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
            oo,meta=load(bundle)
            field='m_VisualTree' if l['type'][1].endswith('VisualTreeAsset') else 'm_nodes'
            trees=[]
            for key,v in meta['m_Container']:
                if key!=guid or v['asset']['m_FileID']!=0:continue
                ob=oo[v['asset']['m_PathID']]
                if ob.type.name!='MonoBehaviour':continue
                tree=ob.read_typetree()
                if field in tree:trees.append((ob,tree))
            assert trees,(guid,bundle,l['type'])
            for ob,tree in trees:
                if field=='m_VisualTree':
                    sheet=oo[tree['inlineSheet']['m_PathID']].read_typetree()
                    validate_ui(tree,sheet)
                audits.append({'guid':guid,'bundle':bundle,'pid':ob.path_id,'name':tree['m_Name'],'type':l['type'][1]})
                for child in guids(tree):audit(child)
    for guid in [CARD,ROW]:audit(guid)
    oo,meta=load(W)
    before={o.path_id:o for o in UnityPy.load(str(out/('backup-'+tag)/W)).objects}
    expected={int(c['path_id']) for c in next(r for r in manifest['reports'] if r['target']==tag)['cards']}
    assert reserved.isdisjoint(oo)
    for pid in expected:
        d=oo[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
        def sd(i):return rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        def named(name):return next(i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and sd(i).get('name')==name)
        drop=sd(named('HoverCardModeSelector'))
        assert drop['pickingMode']==0 and drop['RowTemplate']['m_AssetGUID']==ROW
        assert drop['SelectionValueBinding']['m_path']=='TFHoverCardPortraitMode'
        assert drop['UseRowTemplateToShowSelectedValue']==1 and drop['HideOnSelectionChange']==1
        b=bytes(drop['BindChoicesFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert b'TFHoverFCOption' in b and b'TFHoverPortraitOption' in b
        switch=named('HoverCardModeSwitch');assert len(rr[switch]['data']['m_Children'])==2
        assert rr[switch]['data']['m_Children'][0]['rid']==named('ReportPortraitLayerStage')
        assert rr[switch]['data']['m_Children'][1]['rid']==named('HoverLargePortraitOnly')
        variables=next(r['data'] for r in rr.values() if r['type']['class']=='BindingVariablesComponent/UxmlSerializedData')
        values={v['m_name']:v['m_scopeValue']['m_serializedData'] for v in variables['ValueVariables']}
        assert values['TFHoverCardPortraitMode']=='Int|0|(Session,Explicit,{},{TF27.HoverCard.Mode.v1})'
        assert values['TFHoverFCOption']=='Int|0|' and values['TFHoverPortraitOption']=='Int|1|'
        original=before[pid].read_typetree()
        oldrefs={r['rid']:r for r in original['references']['RefIds']}
        assert {i for i in oldrefs if rr[i]!=oldrefs[i]}=={1001,1015,1299}
    changed=set(expected)|{oo[pid].read_typetree()['inlineSheet']['m_PathID'] for pid in expected}
    changed.add(next(o.path_id for o in oo.values() if o.type.name=='AssetBundle'))
    for pid,o in before.items():
        if pid not in changed:assert sha(o.get_raw_data())==sha(oo[pid].get_raw_data()),(tag,pid)
    labels=[x[0] for x in cat.array(keys['GameWorldVisualTreeAssetPreload'],'I')]
    assert set(cat.locations(ROW))<=set(labels)
    card_deps=cat.location(cat.locations(CARD)[0])['dependencies']
    for guid in [ROW,'5b2e64da94c8319418ea3db0fc8c92f2','f6f314e9db56227459137669d87c44e9']:
        deps=cat.location(cat.locations(guid)[0])['dependencies']
        assert set(deps)<=set(card_deps),(tag,guid)
    reports.append({'target':tag,'typed_resources':audits,'cards_verified':sorted(expected),'original_noncard_objects_unchanged':True,'catalog_preload_dependencies_verified':True})
for t in tx:
    path=Path(t['target'] if installed else t['source'])
    assert sha(path.read_bytes())==t['after'],path
for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h,path
result={'installed':installed,'runtime_verified':False,'reports':reports,'resource_files_verified':len(tx),'protected_files_verified':len(manifest['protected_sha256'])}
(out/('verification-installed.json' if installed else 'verification-prepared.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'verified':True,'installed':installed,'resource_files':len(tx),'typed_resources':[len(r['typed_resources']) for r in reports]},ensure_ascii=False))
