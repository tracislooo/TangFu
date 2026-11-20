"""Recolor the shared player hover backdrops and save two current-game variants."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,struct,sys,zipfile
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'serializer','exec'))
TypeTreeHelper.write_value=write
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(cfg['bundle_root']),Path(cfg['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
F='ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
NAMES=[W,F]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('hover-greyblue-both-versions-'+stamp)
OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
color={k:struct.unpack('<f',struct.pack('<f',v/255))[0] for k,v in zip(['r','g','b','a'],[38,52,69,255])}
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name not in NAMES}
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin',SKIN/'catalog.hash']:
    if p.exists():protected[str(p)]=sha(p.read_bytes())
transactions,reports=[],[]
game_outputs={}

for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
    edits=[]
    for bn in NAMES:
        target=folder/bn;before=target.read_bytes()
        env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
        hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
        expected={};rules_by_style={};owners={}
        for o in oo.values():
            if o.type.name!='MonoBehaviour' or b'RightPanelBackground' not in o.get_raw_data():continue
            doc=o.read_typetree();rr={r['rid']:r for r in doc.get('references',{}).get('RefIds',[])}
            nodes=[i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='RightPanelBackground']
            if not nodes:continue
            sid=doc['inlineSheet']['m_PathID'];assert doc['inlineSheet']['m_FileID']==0
            rules_by_style.setdefault(sid,set()).update(rr[i]['data']['m_RuleIndex'] for i in nodes)
            owners.setdefault(sid,[]).append({'template':doc['m_Name'],'pid':o.path_id,'background_nodes':nodes})
        assert rules_by_style,(tag,bn)
        for sid,indices in rules_by_style.items():
            sheet=oo[sid].read_typetree();original=copy.deepcopy(sheet)
            newindex=len(sheet['colors']);sheet['colors'].append(color)
            for ix in indices:
                props=[p for p in sheet['m_Rules'][ix]['m_Properties'] if p['m_Id']==458752]
                assert len(props)==1,(sid,ix)
                props[0]['m_Values']=[{'m_ValueType':4,'valueIndex':newindex}]
            # The change is limited to one background property per targeted rule.
            restored=copy.deepcopy(sheet);restored['colors']=original['colors']
            for ix in indices:
                old=next(p for p in original['m_Rules'][ix]['m_Properties'] if p['m_Id']==458752)
                for p in restored['m_Rules'][ix]['m_Properties']:
                    if p['m_Id']==458752:p['m_Values']=copy.deepcopy(old['m_Values'])
            assert restored==original,(tag,bn,sid)
            oo[sid].save_typetree(sheet);expected[sid]=sheet
            edits.append({'bundle':bn,'style':sid,'rules':sorted(indices),'owners':owners[sid]})
        raw=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
        assert set(saved)==set(oo)
        for pid,o in saved.items():
            if pid in expected:assert o.read_typetree()==expected[pid],(tag,bn,pid)
            else:assert sha(o.get_raw_data())==hashes[pid],(tag,bn,pid)
        backup=OUT/('backup-'+tag)/bn;source=OUT/tag/bn
        backup.parent.mkdir(exist_ok=True);source.parent.mkdir(exist_ok=True)
        backup.write_bytes(before);source.write_bytes(raw)
        transactions.append({'target':str(target),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(raw)})
        if tag=='game':game_outputs[bn]=raw
    reports.append({'target':tag,'color':'#263445','opacity':1,'changes':edits,'only_target_background_properties_changed':True})

# Build the FC choice from the same latest game baseline. Restore only its four
# original FC objects, leaving the new backdrop and every unrelated object intact.
trial=json.loads((R/'current-hover-large-portrait-trial.json').read_text('utf8'))
trialdir=Path(trial['patch'])
originals={o.path_id:o for o in UnityPy.load(str(trialdir/'backup-game'/W)).objects}
large={o.path_id:o for o in UnityPy.load(game_outputs[W]).objects}
fc_env=UnityPy.load(game_outputs[W]);fc={o.path_id:o for o in fc_env.objects}
cardids={-960000000003010,-960000000003011,-950000000000141,-950000000000140}
for pid in cardids:
    assert [e.name for e in fc[pid].assets_file.externals]==[e.name for e in originals[pid].assets_file.externals]
    fc[pid].set_raw_data(originals[pid].get_raw_data())
fcraw=fc_env.file.save(packer='lz4');fc_check={o.path_id:o for o in UnityPy.load(fcraw).objects}
assert set(fc_check)==set(large)
for pid,o in fc_check.items():assert o.get_raw_data()==(originals[pid] if pid in cardids else large[pid]).get_raw_data(),pid
variant_hashes={}
export=R/'exports'/('球员悬浮窗-大头像与FC-深灰蓝-'+stamp)
for title,worldraw in [('大头像版',game_outputs[W]),('FC卡面版',fcraw)]:
    dest=export/title/'aa'/'StandaloneWindows64';dest.mkdir(parents=True)
    (dest/W).write_bytes(worldraw);(dest/F).write_bytes(game_outputs[F])
    entries={W:sha(worldraw),F:sha(game_outputs[F])}
    variant_hashes[title]=entries
    (export/title/'文件校验.json').write_text(json.dumps(entries,indent=2),'utf8')
(export/'使用说明.txt').write_text('本包提供两种球员悬浮窗显示方式，均为深灰蓝 #263445、不透明背景。\n\n大头像版：左侧仅大头像，球场和属性保持。\nFC卡面版：左侧原FC卡面及六项评分，球场和属性保持。\n\n选择其中一版，将该版aa文件夹合并覆盖到 Football Manager 27/fm_Data/StreamingAssets/aa。先完全退出游戏；覆盖前保留现有同名文件。切换版本时覆盖另一版即可，不需要游戏内选择器。\n这些整包替换文件基于本次最新皮肤资源生成，供对应版本皮肤使用。\n\n当前游戏已安装大头像版。独立主皮肤保留FC卡面，并同步了底色。大头像布局已获用户确认；新底色尚待游戏内确认。\n','utf8')
zip_path=export.with_suffix('.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in export.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(export))
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    for title,hashes in variant_hashes.items():
        for bn,h in hashes.items():assert sha(z.read(title+'/aa/StandaloneWindows64/'+bn))==h
for t in transactions:assert sha(Path(t['target']).read_bytes())==t['before'],t['target']
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
manifest={'installed':False,'runtime_verified':False,'large_portrait_layout_user_approved':True,'new_background_runtime_verified':False,'color':'#263445','opacity':1,'protected_sha256':protected,'reports':reports,'export_directory':str(export),'export_zip':str(zip_path),'variant_hashes':variant_hashes,'fc_variant_only_four_card_objects_differ':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(transactions,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif($LASTEXITCODE -ne 0){throw 'Resource transaction failed.'}\n",'utf-8-sig')
shutil.copy2(Path(__file__),OUT/Path(__file__).name)
print(json.dumps({'prepared':True,'output':str(OUT),'export_zip':str(zip_path),'targets':len(transactions),'style_objects':[len(r['changes']) for r in reports]},ensure_ascii=True),flush=True)
