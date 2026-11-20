"""Read-only validation of the independent variant."""
from pathlib import Path
import hashlib, importlib.util, json, sys
OUT=Path(__file__).resolve().parent;R=OUT.parent
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=cm.Catalog((OUT/'packages/catalog.bin').read_bytes())
m=json.loads((OUT/'manifest.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,p
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
env=UnityPy.load(str(OUT/'packages'/W));oo={o.path_id:o for o in env.objects}
def named(name):return next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
title=named('OverviewTitleBar').read_typetree();rr={r['rid']:r for r in title['references']['RefIds']}
sheet=oo[title['inlineSheet']['m_PathID']].read_typetree()
def serial(i):return rr.get(rr[i]['data']['m_SerializedData']['rid'],{}).get('data',{})
sidebar=next(i for i,r in rr.items() if 'm_SerializedData' in r.get('data',{}) and serial(i).get('name')=='TFBookmarkSidebar100')
lst=next(i for i,r in rr.items() if 'm_SerializedData' in r.get('data',{}) and serial(i).get('name')=='BookmarksList')
props={p['m_Id']:p['m_Values'] for p in sheet['m_Rules'][rr[sidebar]['data']['m_RuleIndex']]['m_Properties']}
for k in [131105,131095,131097]:
    h=props[k][0];assert h['m_ValueType']==3 and sheet['dimensions'][h['valueIndex']]=={'unit':1,'value':100.0}
assert 131094 not in props # No fixed max-height can collapse the full-height sidebar.
assert serial(lst)['Direction']==0 and serial(lst)['ScrollViewMode']==0
assert serial(lst)['Binding']['m_direct']['Path']['m_path']=='gameworldsubtabsandbookmarks.CurrentSelectedBookmarksList'
assert serial(lst)['RowTemplate']['m_AssetGUID']=='55c5e407237e29e43a7ee0feb446fea9'
nav=named('SecondaryNavigationBar').read_typetree()
assert not any(r.get('data',{}).get('name')=='BookmarksList' for r in nav['references']['RefIds'])
checks=[]
for guid in ['1bd5258a7812f2640b961d9d11250367','55c5e407237e29e43a7ee0feb446fea9','b1ff27b6c6d03754fa21a04e116fe813']:
    locs=[l for l in catalog.locations(guid) if catalog.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert len(locs)==1
    loc=catalog.location(locs[0]);assert 'VisualTreeAsset' in str(loc['type'])
    assert loc['dependencies']
    dep=catalog.location(loc['dependencies'][0]);assert W in dep['internal']
    checks.append({'guid':guid,'type':loc['type'],'first_dependency':dep['internal']})
retired=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in retired}|{-910000000000001,-910000000000002,-910000000000146}
for name in ['ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle']:
    e=UnityPy.load(str(OUT/'packages'/name));objects={o.path_id:o for o in e.objects}
    assert not (set(objects)&banned),(name,'retired object')
    for o in objects.values():
        if o.type.name=='AssetBundle':
            d=o.read_typetree()
            assert all(x['m_PathID'] not in banned for x in d['m_PreloadTable'])
            assert all(v['asset']['m_PathID'] not in banned for _,v in d['m_Container'])
result={'offline_validation_passed':True,'width_px':100,'vertical_list':True,'original_tab_bookmarks_removed':True,'catalog_templates':checks,'retired_texture_ids_absent':True,'existing_game_and_skin_unchanged':True,'runtime_verified':False}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
