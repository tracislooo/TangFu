import copy, hashlib, json, sys, zipfile
from pathlib import Path
R=Path.cwd(); sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
TARGET=AA/'StandaloneWindows64'/N
OUT=R/'三行徽章间距进一步收紧-V44'
B=-4194025542157271532; S=8045407476604796436
sha=lambda b:hashlib.sha256(b).hexdigest()
source=TARGET.read_bytes()
assert sha(source)=='38e74187705e40e580e346df8ce3e3f6635faac27941d7dd30cfbb182ee53926'
e=UnityPy.load(str(TARGET)); obs={o.path_id:o for o in e.objects}
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
sheet=obs[S].read_typetree(); old=copy.deepcopy(sheet)
doc=obs[B].read_typetree(); refs={r['rid']:r for r in doc['references']['RefIds']}
def px(v):
    v={'unit':1,'value':float(v)}
    if v not in sheet['dimensions']:sheet['dimensions'].append(v)
    return {'m_ValueType':3,'valueIndex':sheet['dimensions'].index(v)}
def node(name):
    sd=next(r for r in refs.values() if r.get('data',{}).get('name')==name)
    return next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
changes={}
def patch(name,values):
    ri=node(name)['data']['m_RuleIndex']; ps=sheet['m_Rules'][ri]['m_Properties']
    for k,v in values.items():
        matches=[p for p in ps if p['m_Id']==k]
        assert len(matches)<=1
        if matches:matches[0]['m_Values']=[px(v)]
        else:ps.append({'m_Id':k,'m_CustomName':'','m_Line':-1,'m_Values':[px(v)]})
    changes.setdefault(ri,set()).update(values)
patch('ReportBadgeGrid4_3_4',{131082:176,131105:176,131097:176,131087:142,131092:4})
# Preserve the 50px canvases; reduce the spacing between their visible artwork.
patch('ReportATTBadge',{131091:-3,131092:-3})
patch('ReportAttributeBadgesFirstRow',{131090:-4})
for i,r in enumerate(old['m_Rules']):
    if i not in changes:assert sheet['m_Rules'][i]==r
    else:
        before=[p for p in r['m_Properties'] if p['m_Id'] not in changes[i]]
        after=[p for p in sheet['m_Rules'][i]['m_Properties'] if p['m_Id'] not in changes[i]]
        assert before==after
for k in old:
    if k not in ['m_Rules','dimensions']:assert sheet[k]==old[k]
assert sheet['dimensions'][:len(old['dimensions'])]==old['dimensions']
obs[S].save_typetree(sheet)
OUT.mkdir(exist_ok=True); dest=OUT/N; dest.write_bytes(e.file.save(packer='lz4'))
saved={o.path_id:o for o in UnityPy.load(str(dest)).objects}
assert saved.keys()==obs.keys()
assert saved[S].read_typetree()==sheet
for i,h in hashes.items():
    if i!=S:assert sha(saved[i].get_raw_data())==h,i
assert TARGET.read_bytes()==source
(OUT/'回退').mkdir(exist_ok=True); (OUT/'回退'/N).write_bytes(source)
m={'version':44,'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),
   'grid_width_px':176,'grid_height_px':142,'previous_grid_width_px':208,'previous_grid_height_px':150,
   'badge_size_px':50,'horizontal_center_spacing_px':44,'previous_horizontal_center_spacing_px':52,
   'vertical_center_spacing_px':46,'previous_vertical_center_spacing_px':50,
   'number_font_size_px':11,'number_center_y_px':21.6,
   'only_inline_style_changed':True,'unchanged_assets_verified':len(hashes)-1,
   'all_data_and_translation_bindings_unchanged':True,
   'changed_rule_properties':{str(i):sorted(v) for i,v in changes.items()},
   'installed':False,'game_runtime_verified':False}
(OUT/'修改记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'inlineStyle.json').write_text(json.dumps(sheet,ensure_ascii=False,indent=2),encoding='utf8')
for back in [False,True]:
    src='回退/'+N if back else N; expected=m['sha256'] if back else m['source_sha256']
    final=m['source_sha256'] if back else m['sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{TARGET}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V44：三行徽章区域208×150→176×142。横向中心间距52→44px，纵向中心间距50→46px。\n保持50px徽章画布，利用素材透明留白收紧排列；图标、字体、数字下移位置、原生翻译和数值绑定保持V43。\n只修改inlineStyle，其他4215个资源逐一核对哈希一致。\n退出游戏后运行安装.ps1；回退.ps1恢复V43。游戏内效果待实测。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
print(json.dumps(m,ensure_ascii=False))
