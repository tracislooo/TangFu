"""Sidebar variant only: restore header x-position and place sidebar below both bars."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
location=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(location['bundle_root']);SKIN=Path(location['skin_packages'])
D='ui-styles_assets_default.bundle';path=GAME/D;before=path.read_bytes();env=UnityPy.load(before);objects=env.assets[0].objects
obj=next(o for o in objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');sheet=obj.read_typetree();original=copy.deepcopy(sheet)
def names(rule):return [[p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']] for sel in rule['m_ComplexSelectors']]
def rule(chain):
 matches=[r for r in sheet['m_Rules'] if names(r)==[chain]];assert len(matches)==1,(chain,len(matches));return matches[0]
def dim(r,prop,value):
 p=next(p for p in r['m_Properties'] if p['m_Id']==prop);sheet['dimensions'].append({'unit':1,'value':float(value)});p['m_Values']=[{'m_ValueType':3,'valueIndex':len(sheet['dimensions'])-1}]
side=rule(['tf-reference-sidebar-active','TFReferenceSidebar']);dim(side,131104,85);dim(side,131101,0)
dim(rule(['tf-reference-sidebar-active','tf-reference-header-controls']),131091,0)
dim(rule(['TitleBarBindingRoot','SecondaryNavigationBar']),131099,0)
changed=[i for i,(a,b) in enumerate(zip(original['m_Rules'],sheet['m_Rules'])) if a!=b];assert len(changed)==3
assert all(a==b for k,a in original.items() for b in [sheet[k]] if k not in ['m_Rules','dimensions'])
assert sheet['dimensions'][:len(original['dimensions'])]==original['dimensions']
hashes={pid:hashlib.sha256(o.get_raw_data()).hexdigest() for pid,o in objects.items()};obj.save_typetree(sheet);payload=env.file.save(packer='lz4');checked=UnityPy.load(payload).assets[0]
for pid,o in checked.objects.items():
 if pid==obj.path_id:assert o.read_typetree()==sheet
 else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[pid]
out=R/('sidebar-below-navigation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();src=out/'packages'/D;bak=out/'backup-game'/D;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(payload);bak.write_bytes(before)
sha=lambda b:hashlib.sha256(b).hexdigest();protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p!=path}
tx=[{'target':str(path),'source':str(src),'backup':str(bak),'before':sha(before),'after':sha(payload)}]
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'sidebar_top_px':85,'primary_nav_height':54,'divider_height':1,'secondary_nav_height':30,'header_offset_px':0,'body_and_match_rules_unchanged':True,'changed_rules':changed,'changed_objects':[obj.path_id],'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for name,flag in [('install',''),('restore-position',' --restore')]:
 (out/(name+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+'\n','utf-8-sig')
(out/'README.md').write_text('侧栏分支：顶部主导航和页签栏恢复原横向位置，侧栏位于54px主栏+1px分隔线+30px页签栏下方，top=85px，取消原10px顶部内边距。正文100px留位、比赛逆向补偿、14固定入口和书签保持原样。仅改当前游戏default styles一个文件，原皮肤工程未改。restore-position.ps1回退本次位置调整。实际游戏显示尚未验证。\n','utf8')
assert path.read_bytes()==before
print(str(out),flush=True)
