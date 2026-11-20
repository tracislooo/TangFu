import hashlib,importlib.util,json,struct,sys
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
A=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
D=R/'五张CA最新卡面backgrounds包-V50'
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
world=(A/WN).read_bytes();catalog=(A.parent/'catalog.bin').read_bytes();background=(D/BN).read_bytes()
assert sha(world)=='6cfc78ae4b251ad20ef2e7334ad0acfe28be5d1a30b33af8adda3e0632c3c519'
assert sha(catalog)=='c99d840aa8bea9731327e510034202fa944679c1a872698a49d8b45bffaaa7f8'
e=UnityPy.load(world,background)
wf=next(f for f in e.assets if f.name=='CAB-1ab8e16d7264cd64aba00192bdf91ea2')
bf=next(f for f in e.assets if f.name=='CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8')
ids=set(range(-910000000000007,-910000000000002));assert not(ids&set(wf.objects))
names={-910000000000003-i:n for i,n in enumerate(['CA000','CA120','CA140','CA160','CA180'])}
records=[];styles=[]
for o in wf.objects.values():
    if o.type.name!='MonoBehaviour':continue
    if not any(struct.pack('<q',pid) in o.get_raw_data() for pid in ids):continue
    t=o.read_typetree()
    if 'assets' not in t:continue
    refs=[p for p in t['assets'] if p.get('m_PathID') in ids]
    if not refs:continue
    assert len(refs)==5
    for p in refs:
        assert p['m_FileID']==7
        texture=PPtr(m_FileID=p['m_FileID'],m_PathID=p['m_PathID'],assetsfile=wf).deref()
        assert texture.assets_file is bf
        assert texture.get_raw_data()==bf.objects[p['m_PathID']].get_raw_data()
        assert texture.peek_name()==names[p['m_PathID']]
    styles.append(o.path_id)
assert len(styles)==8
for pid,name in names.items():
    obj=bf.objects[pid];t=obj.read_typetree();image=obj.read().image
    records.append({'name':name,'file_id':7,'path_id':pid,'resolved_source':BN,'resolved_cab':bf.name,
                    'texture_sha256':sha(obj.get_raw_data()),'size':list(image.size)})
meta=next(o for o in wf.objects.values() if o.type.name=='AssetBundle').read_typetree()
assert bf.name.lower() in meta['m_Dependencies']
preload_count=0
for _,v in meta['m_Container']:
    span=meta['m_PreloadTable'][v['preloadIndex']:v['preloadIndex']+v['preloadSize']]
    if v['asset']['m_PathID'] in styles or any(p['m_FileID']==0 and p['m_PathID'] in styles for p in span):
        assert all({'m_FileID':7,'m_PathID':pid} in span for pid in ids);preload_count+=1
assert preload_count==13
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
c=cm.Catalog(catalog);locations={loc for _,p in c.keys() for (loc,) in c.array(p,'I')}
bundles={}
for loc in locations:
    v=c.location(loc)
    if v['provider'].endswith('.AssetBundleProvider'):
        for n in [BN,WN]:
            if v['internal'].endswith('\\'+n):bundles[n]=loc
assert set(bundles)=={BN,WN}
dependent=0
for loc in locations:
    deps=[p[0] for p in c.array(c.unpack(loc,'7I')[3],'I')]
    if bundles[WN] in deps:
        assert bundles[BN] in deps;dependent+=1
assert dependent==19764
m={'background_sha256':sha(background),'world_sha256_unchanged':sha(world),'catalog_sha256_unchanged':sha(catalog),
   'all_five_resolved_to_new_backgrounds':True,'gameworld_CA_copies_absent':True,'verified_style_count':8,
   'verified_style_image_references':40,'verified_preload_entries':preload_count,'verified_catalog_dependencies':dependent,
   'resolved_textures':records,'game_runtime_verified':False}
(D/'游戏引用与依赖校验.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'cross_bundle_resolution':'PASS','style_references':40,'preload_entries':13,'catalog_dependencies':dependent},ensure_ascii=False))
