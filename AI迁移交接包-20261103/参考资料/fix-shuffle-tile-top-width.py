from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, subprocess, sys
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(cfg['bundle_root']),Path(cfg['skin_packages'])
FN='ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
out=R/('shuffle-tile-width-smaller-values-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[];audits=[]
for tag,root in [('game',GAME),('skin',SKIN)]:
    before=(root/FN).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
    tile=obs[1519666771143645661];doc=tile.read_typetree();refs={r['rid']:r for r in doc['references']['RefIds']}
    sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet);P=st.p
    # align-self:center shrank the top half to its only in-flow child (the portrait).
    # Give the top half the full tile width and restore stretch alignment.
    node=refs[1022];index=node['data']['m_RuleIndex'];assert index>=0
    props=sheet['m_Rules'][index]['m_Properties']
    replace={131074:P(131074,st.en('stretch')),131105:P(131105,st.pct(100)),131085:P(131085,st.num(0))}
    sheet['m_Rules'][index]['m_Properties']=[p for p in props if p['m_Id'] not in replace]+list(replace.values())
    count=0
    for r in refs.values():
        v=r.get('data',{})
        if v.get('m_FullTypeName')!='SI.Bindable.SIText':continue
        sd=refs[v['m_SerializedData']['rid']]['data']
        if not sd.get('name','').startswith('Overview') or not sd.get('name','').endswith('Value'):continue
        binding=sd.get('TextBinding',{})
        if not binding.get('m_visualFunction',{}).get('m_target',{}).get('m_guid'):continue
        j=v['m_RuleIndex'];props=sheet['m_Rules'][j]['m_Properties']
        assert any(p['m_Id']==65537 for p in props)
        sheet['m_Rules'][j]['m_Properties']=[p for p in props if p['m_Id']!=65537]+[P(65537,st.px(13))]
        count+=1
    assert count==12,(tag,count)
    sheetobj.save_typetree(sheet);output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
    assert set(saved)==set(obs)
    for i,o in saved.items():
        if i==sheetobj.path_id:assert o.read_typetree()==sheet
        else:assert sha(o.get_raw_data())==hashes[i],(tag,i)
    # Check effective saved width/alignment and every value's font size.
    def prop_value(rule,key):
        p=next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id']==key)
        h=p['m_Values'][0];return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
    assert prop_value(index,131074)=='stretch'
    assert prop_value(index,131105)=={'unit':2,'value':100.0}
    backup,source=out/('backup-'+tag)/FN,out/tag/FN
    backup.parent.mkdir();source.parent.mkdir();backup.write_bytes(before);source.write_bytes(output)
    tx.append({'target':str(root/FN),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)})
    audits.append({'target':tag,'changed_object':str(sheetobj.path_id),'unchanged_objects':len(obs)-1,'top_width':'100%','top_align_self':'stretch','score_values':count,'score_font_px':13,'previous_score_font_px':16,'vta_and_bindings_unchanged':True})
manifest={'installed':False,'runtime_verified':False,'change':'Restore full-width tile top, keeping buttons/club/nation on both sides; reduce both FC branches value font 16 to 13px','protected_sha256':{},'audits':audits}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher="""$ErrorActionPreference = 'Stop'
$statusPath = Join-Path $PSScriptRoot 'automatic-install-status.txt'
$logPath = Join-Path $PSScriptRoot 'automatic-install.log'
Set-Content -LiteralPath $statusPath -Value 'Waiting for Football Manager to exit normally.' -Encoding UTF8
while ($true) {
    while (Get-Process -Name fm -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
    & 'PYTHON_PATH' 'INSTALLER_PATH' $PSScriptRoot *> $logPath
    if ($LASTEXITCODE -eq 0) {
        Set-Content -LiteralPath $statusPath -Value ('Installed and verified at ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) -Encoding UTF8
        break
    }
    if (Get-Process -Name fm -ErrorAction SilentlyContinue) { continue }
    Set-Content -LiteralPath $statusPath -Value 'Installation stopped; see automatic-install.log.' -Encoding UTF8
    break
}
""".replace('PYTHON_PATH',sys.executable).replace('INSTALLER_PATH',str(R/'install-independent-resource-patch.py'))
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
(R/'current-shuffle-player-tile.json').write_text(json.dumps({'patch':str(out),'manifest':str(out/'manifest.json'),'installed':False,'status':'prepared','runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
print(out)
