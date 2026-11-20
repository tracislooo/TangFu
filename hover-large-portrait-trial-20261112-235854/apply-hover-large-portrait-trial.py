"""Replace only the FC hover-card region with a large portrait in the game."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
    tree=ast.parse((R/file).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(cfg['bundle_root']),Path(cfg['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
CARD='64033a72b9925c8dad3b08826077c328'
sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('hover-large-portrait-trial-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir()
target=GAME/W;before=target.read_bytes()
protected={str(p):sha(p.read_bytes()) for p in GAME.glob('*.bundle') if p.name!=W}
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/W,SKIN/'catalog.bin']:
    if p.exists():protected[str(p)]=sha(p.read_bytes())
env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
ids=list(dict.fromkeys(v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==CARD and v['asset']['m_FileID']==0))
assert set(ids)=={-960000000003010,-950000000000141}
expected={};reports=[]

def reachable(rr,root):
    result=set()
    def walk(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                i=v['rid']
                if i==-2 or i in result:return
                assert i in rr,i
                result.add(i)
                for k,x in rr[i].get('data',{}).items():
                    if k!='m_Parent':walk(x)
            else:
                for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk({'rid':root})
    return result

for pid in ids:
    doc=oo[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
    assert not any('HoverCardMode' in r.get('data',{}).get('name','') for r in rr.values())
    sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
    def named(name):
        return next(i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
    stage,frame=named('ReportPortraitLayerStage'),named('PersonPictureFrame')
    portrait_before={i:copy.deepcopy(rr[i]) for i in reachable(rr,frame)}
    rr[stage]['data']['m_Children']=[{'rid':frame}]
    st.box(rr[frame],10,10,320,500)
    keep=reachable(rr,doc['m_VisualTree']['rid'])
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in keep]
    assert all(rr[i]==v for i,v in portrait_before.items() if i!=frame)
    aliases={r.get('data',{}).get('m_TemplateAlias') for r in doc['references']['RefIds']}-{None,''}
    doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias'] in aliases]
    # Remove inactive FC rules and texture handles from this private stylesheet.
    active=sorted({r['data']['m_RuleIndex'] for r in doc['references']['RefIds'] if r.get('data',{}).get('m_RuleIndex',-1)>=0})
    rules={old:new for new,old in enumerate(active)}
    for r in doc['references']['RefIds']:
        a=r.get('data',{})
        if a.get('m_RuleIndex',-1)>=0:a['m_RuleIndex']=rules[a['m_RuleIndex']]
    sheet['m_Rules']=[sheet['m_Rules'][i] for i in active]
    for pool in set(poolmap.values()):
        used=sorted({h['valueIndex'] for rule in sheet['m_Rules'] for p in rule['m_Properties'] for h in p['m_Values'] if poolmap.get(h['m_ValueType'])==pool})
        remap={old:new for new,old in enumerate(used)}
        sheet[pool]=[sheet[pool][i] for i in used]
        for rule in sheet['m_Rules']:
            for p in rule['m_Properties']:
                for h in p['m_Values']:
                    if poolmap.get(h['m_ValueType'])==pool:h['valueIndex']=remap[h['valueIndex']]
    validate_ui(doc,sheet)
    assert not any('OverviewCard' in r.get('data',{}).get('name','') or 'ReportCACard' in r.get('data',{}).get('name','') or 'TooltipCard' in r.get('data',{}).get('name','') for r in doc['references']['RefIds'])
    for ident,data in [(pid,doc),(sid,sheet)]:oo[ident].save_typetree(data);expected[ident]=copy.deepcopy(data)
    (OUT/'templates'/(str(pid)+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
    reports.append({'path_id':pid,'style_id':sid,'photo_frame':[10,10,320,500],'original_photo_branches_preserved':True,'remaining_managed_refs':len(keep),'removed_managed_refs':len(rr)-len(keep)})

cat=cm.Catalog((GAME.parent/'catalog.bin').read_bytes());keys=dict(cat.keys())
locations=[cat.location(i) for i in cat.locations(CARD)]
assert all(l['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and cat.location(l['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W) for l in locations)
preloads=[x[0] for x in cat.array(keys['GameWorldVisualTreeAssetPreload'],'I')]
assert set(cat.locations(CARD))<=set(preloads)
output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(oo)
for pid,o in saved.items():
    if pid in expected:assert o.read_typetree()==expected[pid],pid
    else:assert sha(o.get_raw_data())==hashes[pid],pid
reserved={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert reserved.isdisjoint(saved)
backup,source=OUT/'backup-game'/W,OUT/'game'/W
backup.parent.mkdir();source.parent.mkdir();backup.write_bytes(before);source.write_bytes(output)
assert target.read_bytes()==before
for path,h in protected.items():assert sha(Path(path).read_bytes())==h,path
manifest={'installed':False,'runtime_verified':False,'game_only_trial':True,'standalone_skin_changed':False,'user_approved_for_export':False,'protected_sha256':protected,'reports':reports,'unrelated_objects_unchanged':len(oo)-len(expected),'catalog_unchanged':True,'no_selector':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps([{'target':str(target),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)}],indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif($LASTEXITCODE -ne 0){throw 'Resource transaction failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('本次仅供游戏内查看：将球员悬浮窗FC卡面区域直接换成320×500等比大头像，保留原生照片/默认头像分支，移除FC背景、六项评分及卡面附加资料。右侧球场、属性、其余悬浮入口和独立主皮肤保持不变。没有选择器。只改游戏gameworld包内两份当前同GUID卡模板及其私有样式；目录、纹理和其他对象不变。备份与哈希保护回退已保存。尚待用户确认效果，未制作使用者选择用的独立分发文件。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'modified_objects':list(expected),'game_only':True}),flush=True)
