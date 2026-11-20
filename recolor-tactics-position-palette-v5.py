"""Change six native tactics palette variables; preserve pooled colour aliases."""
from pathlib import Path
import sys, copy, datetime, hashlib, json, struct, subprocess
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
OUT=R/('tactics-position-six-colours-v5-'+stamp);OUT.mkdir()
names=['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']
palette={'striker':'E53935','attacking-midfield':'FB8C00','midfield':'FFD700','defensive-midfield':'2196F3','defender':'43A047','goalkeeper':'9C27B0'}
sha=lambda b:hashlib.sha256(b).hexdigest()
before={f/n:(f/n).read_bytes() if (f/n).exists() else None for f in [GAME,SKIN] for n in names}
protected_names=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-backgrounds_assets_common.bundle','ui-tablefactories_assets_all.bundle','ui-tableviews_assets_all.bundle']
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in [f/n for n in protected_names] if p.exists()}
for folder in [GAME.parent,SKIN]:
    for n in ['catalog.bin','catalog.hash']:
        if (folder/n).exists():protected[folder/n]=sha((folder/n).read_bytes())
outputs={};audit=[]
for path,raw in before.items():
    tag='game' if path.parent==GAME else 'skin'
    (OUT/('backup-'+tag)).mkdir(exist_ok=True);(OUT/('output-'+tag)).mkdir(exist_ok=True)
    if raw is not None:(OUT/('backup-'+tag)/path.name).write_bytes(raw)
    base=raw if raw is not None else before[GAME/path.name]
    env=UnityPy.load(base);objects={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in objects.items()};modified={};variables=[]
    for pid,o in objects.items():
        if o.type.name!='MonoBehaviour':continue
        d=o.read_typetree();old=copy.deepcopy(d);count=0
        for rule in d.get('m_Rules',[]):
            for p in rule['m_Properties']:
                match=next((key for key in palette if p.get('m_CustomName')=='--colours-tactics-'+key+'-foreground'),None)
                if match is None:continue
                assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4
                h=palette[match];rgba=dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',int(h[i:i+2],16)/255))[0] for i in [0,2,4]]+[1.0]))
                d['colors'].append(rgba);p['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}]
                variables.append({'name':p['m_CustomName'],'hex':'#'+h});count+=1
        if not count:continue
        assert count==6
        # Original pooled values stay intact, so unrelated users of those values
        # retain their colours. Exactly six variable handles change.
        assert d['colors'][:len(old['colors'])]==old['colors']
        props_delta=0
        for a,b in zip(old['m_Rules'],d['m_Rules']):
            for ap,bp in zip(a['m_Properties'],b['m_Properties']):
                if ap!=bp:
                    props_delta+=1;assert ap['m_CustomName']==bp['m_CustomName'] and bp['m_CustomName'].endswith('-foreground')
        assert props_delta==6
        o.save_typetree(d);modified[pid]=d
    assert len(modified)==1 and len(variables)==6
    output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objects)
    for pid,o in check.items():
        if pid in modified:assert o.read_typetree()==modified[pid]
        else:assert sha(o.get_raw_data())==hashes[pid],('Unrelated object changed',path,pid)
    outputs[path]=output;(OUT/('output-'+tag)/path.name).write_bytes(output)
    audit.append({'target':str(path),'existed_before':raw is not None,'changed_objects':[str(p) for p in modified],'six_variables':variables,'unrelated_objects_unchanged':len(objects)-1})

registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(x['path_id']) for x in reserved}
bg={o.path_id:o for o in UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle')).objects};assert banned.isdisjoint(bg)
meta=next(o.read_typetree() for o in bg.values() if o.type.name=='AssetBundle');assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable']);assert all(v['asset']['m_PathID'] not in banned for _,v in meta['m_Container'])
for row in registry['textures']:assert bg[int(row['path_id'])].peek_name()==row['name']
report={'installed':False,'runtime_verified':False,'palette':{k:'#'+v for k,v in palette.items()},'audit':audit,'only_six_variable_handles_per_stylesheet_changed':True,'original_colour_pools_preserved':True,'protected_files':{str(p):h for p,h in protected.items()},'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'before_sha256':{str(p):None if raw is None else sha(raw) for p,raw in before.items()},'reserved_70_absent':True,'active_custom_textures_verified':len(registry['textures'])}
def record():(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
record()
guards=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer=list(guards);restore=list(guards)
for p,raw in before.items():
    tag='game' if p.parent==GAME else 'skin'
    if raw is None:
        installer.append("if (Test-Path -LiteralPath '"+str(p)+"') { throw 'File appeared since preparation.' }")
        restore.append("if (Test-Path -LiteralPath '"+str(p)+"') { Remove-Item -LiteralPath '"+str(p)+"' -Force }")
    else:
        installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(raw)+"') { throw 'File changed since preparation.' }")
        restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-'+tag)/p.name)+"' -Destination '"+str(p)+"' -Force")
for p in outputs:
    tag='game' if p.parent==GAME else 'skin';installer.append("Copy-Item -LiteralPath '"+str(OUT/('output-'+tag)/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig');(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,raw in before.items():assert (p.read_bytes() if p.exists() else None)==raw
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,raw in outputs.items():p.write_bytes(raw)
    for p,raw in outputs.items():assert p.read_bytes()==raw
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,raw in before.items():
        if raw is None:
            if p.exists():p.unlink()
        else:p.write_bytes(raw)
    raise
report.update(installed=True,installed_verified=True);record()
print(json.dumps({'installed':True,'output':str(OUT),'palette':report['palette'],'card_and_other_resources_unchanged':True}))
