"""Move the existing editor widget before the bookmark list; change no other geometry."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<writer>','exec'));TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';path=GAME/W;before=path.read_bytes();env=UnityPy.load(before);a=env.assets[0];obj=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='TFReferenceBookmarkSidebar');d=obj.read_typetree();original=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']}
assert rr[1046]['data']['m_Children']==[{'rid':1071},{'rid':1072},{'rid':1073}]
rr[1046]['data']['m_Children']=[{'rid':1073},{'rid':1071},{'rid':1072}]
assert rr[1073]==next(r for r in original['references']['RefIds'] if r['rid']==1073)
sha=lambda b:hashlib.sha256(b).hexdigest();hashes={i:sha(o.get_raw_data()) for i,o in a.objects.items()};obj.save_typetree(d);payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
assert set(check.objects)==set(a.objects)
for i,o in check.objects.items():
 if i==obj.path_id:assert o.read_typetree()==d
 else:assert sha(o.get_raw_data())==hashes[i]
out=R/('sidebar-bookmark-editor-top-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();src=out/'packages'/W;bak=out/'backup-game'/W;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(payload);bak.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p!=path}
tx=[{'target':str(path),'source':str(src),'backup':str(bak),'before':sha(before),'after':sha(payload)}]
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'editor_position':'immediately before native bookmark list','only_change':'Bookmarks child ordering','widget_height_px':20,'icon_px':16,'native_popup_bindings_and_events_unchanged':True,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for action,flag in [('install',''),('restore-position',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+'\n','utf-8-sig')
assert path.read_bytes()==before
print(str(out),flush=True)
