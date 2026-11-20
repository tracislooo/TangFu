"""Verify installed V64 package bytes, PPtrs, layering and native data retention."""
from pathlib import Path
import sys,json,hashlib,importlib.util,struct
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
O=R/'tactics-tf-pitch-card-background-v64-20261028-041800'
report=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in report['after_sha256'].items():assert sha(Path(p).read_bytes())==h,p
for p,h in report['protected_files'].items():assert sha(Path(p).read_bytes())==h,p
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';B='ui-backgrounds_assets_common.bundle'
world=UnityPy.load(str(G/W));wo={o.path_id:o for o in world.objects};old={o.path_id:o for o in UnityPy.load(str(O/'backup-game'/W)).objects}
changed={int(x) for x in report['changed_world_objects']};assert wo.keys()==old.keys()
for pid,obj in old.items():
    if pid not in changed:assert obj.get_raw_data()==wo[pid].get_raw_data(),pid
bg=UnityPy.load(str(G/B));bo=bg.assets[0].objects;oldbg=UnityPy.load(str(O/'backup-game'/B)).assets[0].objects;bm=next(o for o in bo.values() if o.type.name=='AssetBundle')
assert set(bo)==set(oldbg)|{-910000000000148}
for pid,obj in oldbg.items():
    if pid!=bm.path_id:assert obj.get_raw_data()==bo[pid].get_raw_data(),pid
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert len(registry['textures'])==registry['active_custom_texture_count']==179
for row in registry['textures']:assert bo[int(row['path_id'])].peek_name()==row['name']
loaded=UnityPy.load(str(G/W),str(G/B));wa=next(a for a in loaded.assets if a.name!=bg.assets[0].name)
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def refs(d):return {a['rid']:a.get('data',{}) for a in d['references']['RefIds']}
def sd(r,i):return r[r[i]['m_SerializedData']['rid']]
def named(r,n):return next(i for i,a in r.items() if r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('name')==n)
def prop(r,s,i,key):
    rule=s['m_Rules'][r[i]['m_RuleIndex']];h=next(p for p in rule['m_Properties'] if p['m_Id']==key)['m_Values'][0];return s[pool[h['m_ValueType']]][h['valueIndex']]
layers=[]
for pid in [-8273082868742719783,3127595210179668386]:
    d=wo[pid].read_typetree();r=refs(d);s=wo[d['inlineSheet']['m_PathID']].read_typetree();frame=named(r,'TacticsPlayerPortraitFrame');im=named(r,'TacticsPlayerCardBackgroundImage');portrait=named(r,'TacticsPlayerPortraitBinding');surface=named(r,'DetailedCardInnerSurface' if pid<0 else 'CombinedCardInnerSurface')
    children=[a['rid'] for a in r[frame]['m_Children']];assert children.index(surface)<children.index(im)<children.index(portrait)
    assert prop(r,s,frame,131105)['value']==prop(r,s,frame,131087)['value']==75
    assert prop(r,s,im,131105)['value']==prop(r,s,im,131087)['value']==67
    assert prop(r,s,im,131089)['value']==prop(r,s,im,131104)['value']==4 and sd(r,im)['pickingMode']==1
    p=prop(r,s,im,458753);assert p['m_PathID']==-910000000000147
    assert PPtr(m_FileID=p['m_FileID'],m_PathID=p['m_PathID'],assetsfile=wa).deref().get_raw_data()==bo[p['m_PathID']].get_raw_data()
    layers.append(d['m_Name'])
renderers=0
for audit in report['native_pitch_renderers']:
    pid=next(pid for pid,o in wo.items() if pid in changed and o.type.name=='MonoBehaviour' and o.peek_name()==audit['name'])
    d=wo[pid].read_typetree();r=refs(d);s=wo[d['inlineSheet']['m_PathID']].read_typetree();original=refs(old[pid].read_typetree())
    for row in audit['renderers']:
        i=row['rid'];assert sd(r,i)==sd(original,i)
        p=prop(r,s,i,458753);assert p['m_PathID']==-910000000000148
        assert PPtr(m_FileID=p['m_FileID'],m_PathID=p['m_PathID'],assetsfile=wa).deref().peek_name()=='TF patch aligned'
        assert sd(r,i)['UsePerspectiveDrawing']==0 and sd(r,i)['FillAllAvailableSpace']==1
        assert prop(r,s,i,262153)=='stretch-to-fill';renderers+=1
assert renderers==6
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
wm=next(o.read_typetree() for o in wo.values() if o.type.name=='AssetBundle')
for f in [G.parent,S]:
    raw=(f/'catalog.bin').read_bytes();assert (f/'catalog.hash').read_bytes()==hashlib.md5(raw).hexdigest().encode();c=cm.Catalog(raw)
    for pid in [-8273082868742719783,3127595210179668386,-4411574370150944845,3412805035020634299]:
        guid=next(k for k,v in wm['m_Container'] if v['asset']['m_PathID']==pid)
        loc=next(i for i in c.locations(guid) if c.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');deps=c.location(loc)['dependencies'];assert c.location(deps[0])['internal'].endswith('\\'+W)
        assert any(c.location(dep)['internal'].endswith('\\'+B) for dep in deps)
params=json.loads((O/'alignment.json').read_text('utf8'));assert params['corner_error_pixels']<.001
report.update(independent_installed_verification=True,verified_card_layers=layers,verified_native_pitch_renderers=renderers,original_178_texture_bytes_verified=True,runtime_verified=False)
(O/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed_verified':True,'native_pitch_renderers':renderers,'card_layers':layers,'native_coordinates_unchanged':True,'active_custom_textures':179,'runtime_verified':False},ensure_ascii=False))
