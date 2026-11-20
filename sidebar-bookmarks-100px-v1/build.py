"""Build an offline variant. All writes are confined to this directory."""
from pathlib import Path
import ast, copy, hashlib, json, struct, sys

OUT = Path(__file__).resolve().parent
R = OUT.parent
LOCATION = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME = Path(LOCATION['bundle_root'])
SKIN = Path(LOCATION['skin_packages'])
assert GAME == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
poolmap = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename, wanted in [('build-fc-player-hover-layout.py', {'write','Styles'}), ('add-card-six-ratings.py', {'validate_ui'})]:
    source = ast.parse((R / filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted], type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write
sha = lambda b: hashlib.sha256(b).hexdigest()
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
D = 'ui-styles_assets_default.bundle'
S = 'settings_assets_all.bundle'
FILES = [W,D,S]

def digest_dir(folder):
    return {str(p):sha(p.read_bytes()) for p in sorted(folder.iterdir()) if p.is_file()}

# Protect all installed Addressables bundles and both catalogs, plus the existing skin.
protected = digest_dir(GAME) | digest_dir(SKIN)
for p in [GAME.parent/'catalog.bin', GAME.parent/'catalog.hash', R/'current-custom-textures.json', R/'reserved-texture-ids.json', R/'current-game-location.json', R/'AGENTS.md']:
    protected[str(p)] = sha(p.read_bytes())
base = {n:(GAME/n).read_bytes() for n in FILES}
envs = {n:UnityPy.load(b) for n,b in base.items()}
objects = {n:{o.path_id:o for o in e.objects} for n,e in envs.items()}
hashes = {n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objects.items()}
expected = {n:{} for n in FILES}

def named(bundle, name):
    matches = [o for o in objects[bundle].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name]
    assert len(matches)==1, name
    return matches[0]

def save(bundle, obj, doc):
    obj.save_typetree(doc)
    expected[bundle][obj.path_id] = copy.deepcopy(doc)

def refs(d): return {r['rid']:r for r in d['references']['RefIds']}
def serial(rr,i): return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
def closure(rr, root):
    seen=set()
    def walk(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                i=v['rid']
                if i in rr and i not in seen:
                    seen.add(i);walk(rr[i]['data'])
            else:
                for k,x in v.items():
                    if k!='m_Parent':walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk({'rid':root})
    return seen

nav=named(W,'SecondaryNavigationBar'); nd=nav.read_typetree(); nr=refs(nd)
title=named(W,'OverviewTitleBar'); td=title.read_typetree(); tr=refs(td)
tsid=td['inlineSheet']['m_PathID']; ts=objects[W][tsid].read_typetree(); st=Styles(ts)
nsid=nd['inlineSheet']['m_PathID']; ns=objects[W][nsid].read_typetree()
assert serial(nr,1229)['name']=='BookmarksList'
assert nr[1046]['data']['m_Parent']['rid']==1016
assert nr[1046]['data']['m_RuleIndex']==-1

# Move the native bookmark block, including its keyboard focus and edit-popup events.
keep=closure(nr,1046)
ridmap={i:50000+k for k,i in enumerate(sorted(keep))}
usedids={r.get('data',{}).get('m_Id') for r in tr.values()}
eidmap={}
nextid=1910311000
for i in sorted(keep):
    if 'm_Id' in nr[i].get('data',{}):
        while nextid in usedids:nextid+=1
        eidmap[nr[i]['data']['m_Id']]=nextid;usedids.add(nextid);nextid+=1
def remap(v):
    if isinstance(v,dict):
        if set(v)=={'rid'}:return {'rid':ridmap.get(v['rid'],v['rid'])}
        return {k:(eidmap.get(x,x) if k in ['m_Id','uxmlAssetId','m_ParentId'] else remap(x)) for k,x in v.items()}
    if isinstance(v,list):return [remap(x) for x in v]
    return v
for i in sorted(keep):
    rec=remap(copy.deepcopy(nr[i]));rec['rid']=ridmap[i]
    # Original bookmark subtree has no inline rules. Check this before transferring.
    assert rec.get('data',{}).get('m_RuleIndex',-1)==-1
    td['references']['RefIds'].append(rec);tr[rec['rid']]=rec
nr[1016]['data']['m_Children']=[]
nd['references']['RefIds']=[r for r in nd['references']['RefIds'] if r['rid'] not in keep]
sidebar=ridmap[1046]
tr[sidebar]['data']['m_Parent']={'rid':1002}
tr[1002]['data']['m_Children'].append({'rid':sidebar})
for u in nd['m_Usings']:
    if u['alias'] not in {x['alias'] for x in td['m_Usings']}:td['m_Usings'].append(copy.deepcopy(u))

auto={'m_ValueType':1,'valueIndex':3}
def edit(i, props, clear_classes=False):
    st.edit(tr[i],props)
    if clear_classes:tr[i]['data']['m_Classes']=[]
def edgebox(i,left=0,top=0,right=0,bottom=0):
    edit(i,[st.p(131102,st.en('absolute')),st.p(131089,st.px(left)),st.p(131104,st.px(top)),st.p(131103,st.px(right)),st.p(131075,st.px(bottom)),st.p(131105,auto),st.p(131087,auto),st.p(131096,st.px(0)),st.p(131097,st.px(0))])
def ignore(i):
    s=serial(tr,i);s.update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)

# The title panel becomes a transparent, non-picking full-screen host.
for i in [1001,1002]:
    tr[i]['data']['m_Classes']=[];edgebox(i);ignore(i)
edit(1001,[st.p(458768,st.en('visible')),st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.}))])
# Only the actual header occupies the native header height, to the right of the sidebar.
tr[1004]['data']['m_Classes']=['main-navigation-overview-container','main-card-report-height']
edit(1004,[st.p(131102,st.en('absolute')),st.p(131089,st.px(100)),st.p(131103,st.px(0)),st.p(131104,st.px(0)),st.p(131105,auto),st.p(131084,st.num(0)),st.p(131096,st.px(0))]);ignore(1004)
edgebox(sidebar,right=0)
edit(sidebar,[st.p(131105,st.px(100)),st.p(131103,auto),st.p(131083,st.en('column')),st.p(131085,st.num(0)),st.p(131095,st.px(100)),st.p(131097,st.px(100)),st.p(131091,st.px(0)),st.p(131092,st.px(0)),st.p(458752,st.h(4,{'r':0.03125,'g':0.046875,'b':0.0625,'a':1.0}))],True)
serial(tr,sidebar).update(name='TFBookmarkSidebar100',name_UxmlAttributeFlags=1)
emptyfunc={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
for original in [1046,1178]:
    serial(tr,ridmap[original])['BindFunction']=copy.deepcopy(emptyfunc)
for original in [1071,1091,1129,1178]:
    i=ridmap[original];tr[i]['data']['m_Classes']=[];edgebox(i,bottom=36 if original==1071 else 0)
lst=ridmap[1229];ls=serial(tr,lst)
original_row=copy.deepcopy(ls['RowTemplate'])
ls['Binding']={'m_kind':1,'m_direct':{'Path':{'m_path':'gameworldsubtabsandbookmarks.CurrentSelectedBookmarksList'},'Nullable':0},'m_visualFunction':copy.deepcopy(ls['Binding']['m_visualFunction'])}
ls['Binding']['m_visualFunction']['m_target']['m_guid']=''
for key,value in {'Direction':0,'ScrollViewMode':0,'FixedElementSize':40.0,'DynamicElements':0,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':0}.items():
    ls[key]=value;ls[key+'_UxmlAttributeFlags']=1
edgebox(lst)
edit(lst,[st.p(131083,st.en('column')),st.p(458768,st.en('hidden'))])
edit(ridmap[1072],[st.p(131081,st.en('none'))])
popup=ridmap[1073];tr[popup]['data']['m_Classes']=['ui-concepts-chevron-down_small','popupwidget-hover','bookmarks-button']
edgebox(popup,top=0)
edit(popup,[st.p(131104,auto),st.p(131087,st.px(32)),st.p(131105,st.px(100)),st.p(131083,st.en('row')),st.p(131088,st.en('center'))])

# Constrain the existing native row template without changing click or selection events.
button=named(W,'BookmarkButton');bd=button.read_typetree();br=refs(bd)
bsid=bd['inlineSheet']['m_PathID'];bs=objects[W][bsid].read_typetree();bst=Styles(bs)
for i in [1001,1006,1009]:
    bst.edit(br[i],[bst.p(131105,bst.px(100)),bst.p(131097,bst.px(0)),bst.p(131095,bst.px(100)),bst.p(131085,bst.num(0)),bst.p(131087,bst.px(40)),bst.p(131091,bst.px(0)),bst.p(131092,bst.px(0))])
bst.edit(br[1009],[bst.p(131099,bst.px(4)),bst.p(131100,bst.px(4)),bst.p(131088,bst.en('flex-start'))])
bst.edit(br[1012],[bst.p(131105,bst.pct(100)),bst.p(131097,bst.px(0)),bst.p(458768,bst.en('hidden'))])
bst.edit(br[1022],[bst.p(65537,bst.px(11)),bst.p(196609,bst.en('ellipsis')),bst.p(65552,bst.en('nowrap')),bst.p(131097,bst.px(0))])
for doc,sheet in [(td,ts),(nd,ns),(bd,bs)]:validate_ui(doc,sheet)
for obj,doc in [(title,td),(objects[W][tsid],ts),(nav,nd),(button,bd),(objects[W][bsid],bs)]:save(W,obj,doc)

# Restrict the layout rules to management layers. Modal/card and match layers retain their geometry.
settings=named(S,'PanelLayerSettings');sd=settings.read_typetree()
layer=next(x for x in sd['m_layerSettings'] if x['Name']=='MenuTitle')
assert layer['Description']['Styles']==['main-card-report-height']
layer['Description']['Styles']=['tf-bookmark-sidebar-title-layer']
save(S,settings,sd)
styles=named(D,'AlwaysAppliedStyleSheet');dd=styles.read_typetree();ds=Styles(dd)
def rule(name,props):
    ri=len(dd['m_Rules'])
    dd['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':101,'m_Selectors':[{'m_Parts':[{'m_Value':name,'m_Type':6}],'m_PreviousRelationship':0}],'ruleIndex':ri}],'m_Properties':props,'line':-1})
rule('MenuTitle',[ds.p(131102,ds.en('absolute')),ds.p(131089,ds.px(0)),ds.p(131104,ds.px(0)),ds.p(131103,ds.px(0)),ds.p(131075,ds.px(0)),ds.p(131105,auto),ds.p(131087,auto)])
for name in ['MenuBody','ReportBody','Report']:
    rule(name,[ds.p(131089,ds.px(100)),ds.p(131103,ds.px(0)),ds.p(131105,auto),ds.p(131097,ds.px(0)),ds.p(131095,ds.pct(100))])
save(D,styles,dd)

packages=OUT/'packages';packages.mkdir(exist_ok=True)
baseline=OUT/'baseline';baseline.mkdir(exist_ok=True)
report=[]
for n,e in envs.items():
    raw=e.file.save(packer='lz4');loaded={o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(loaded)==set(objects[n]),n
    for pid,o in loaded.items():
        if pid in expected[n]:assert o.read_typetree()==expected[n][pid],(n,pid)
        else:assert sha(o.get_raw_data())==hashes[n][pid],('Unrelated object changed',n,pid)
    (packages/n).write_bytes(raw);(baseline/n).write_bytes(base[n])
    report.append({'bundle':n,'before_sha256':sha(base[n]),'after_sha256':sha(raw),'changed_objects':[{'path_id':i,'name':d.get('m_Name')} for i,d in expected[n].items()]})

# Complete independent package snapshot, taken from the current installed baseline.
for p in SKIN.iterdir():
    if not p.is_file() or p.name in FILES:continue
    source=GAME.parent/p.name if p.name.startswith('catalog.') else GAME/p.name
    assert source.exists(),source
    (packages/p.name).write_bytes(source.read_bytes())

for p,h in protected.items():assert sha(Path(p).read_bytes())==h,('Existing version changed',p)
manifest={'version':'TF27 Sidebar Bookmarks 100px V1','installed':False,'runtime_verified':False,'source_game':str(GAME),'source_skin_package_list':str(SKIN),'width_px':100,'direction':'vertical','scope':['ordinary management screens','management reports'],'special_screens_supported':False,'no_new_guids_or_path_ids':True,'native_bookmark_row_guid':original_row['m_AssetGUID'],'catalog_unchanged':True,'all_existing_game_bundles_and_skin_packages_unchanged':True,'changed_bundles':report,'protected_sha256':protected,'known_limitations':['Not loaded in game; runtime clipping, picking and report transitions remain to be checked.','Special title bars and match screens are outside this variant scope.']}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'README.md').write_text('# TF27 左侧书签栏 100px 独立试制版 V1\n\n普通管理页使用左侧100px竖向书签栏，保留原生书签跳转、选中及编辑入口。超出高度可竖向滚动。\n\npackages 为独立资源快照；baseline 为本次三个修改包的原始副本；build.py 为仅输出至本目录的构建脚本。未提供或执行游戏安装脚本。现有游戏、原皮肤包及目录文件均已做哈希不变检查。\n\n当前只完成离线结构与序列化验证，未启动游戏，未验证实际显示与点击。特殊全屏页及比赛页不在适配范围。不要把本目录直接导入原皮肤工程；后续调整应继续在此独立版本进行。\n','utf8')
print(json.dumps({'output':str(OUT),'modified_bundles':len(report),'installed':False,'runtime_verified':False,'existing_versions_unchanged':True},ensure_ascii=False))
