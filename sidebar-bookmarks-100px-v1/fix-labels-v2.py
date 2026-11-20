from pathlib import Path
import ast,copy,hashlib,json,sys
R=Path(__file__).resolve().parent.parent;V=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 source=ast.parse((R/filename).read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),filename,'exec'))
TypeTreeHelper.write_value=write
import struct
sha=lambda b:hashlib.sha256(b).hexdigest()
G=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
v1=json.loads((V/'manifest.json').read_text('utf8'))
before=(G/W).read_bytes();assert sha(before)==next(x['after_sha256'] for x in v1['changed_bundles'] if x['bundle']==W)
env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
obj=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='BookmarkButton');doc=obj.read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
serial=lambda i:rr[rr[i]['data']['m_SerializedData']['rid']]['data']
sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
assert serial(1016)['Binding']['m_direct']['Path']['m_path']=='gameworldsubtabsandbookmarks.AreBookmarkLabelsVisible'
serial(1016)['Binding']['m_direct']['Path']['m_path']='const.true'
serial(1016).update(InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1)
st.edit(rr[1016],[st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131097,st.px(0)),st.p(131095,st.px(68)),st.p(458768,st.en('hidden'))])
st.edit(rr[1022],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(196609,st.en('ellipsis')),st.p(65552,st.en('nowrap'))])
validate_ui(doc,sheet);obj.save_typetree(doc);oo[sid].save_typetree(sheet)
raw=env.file.save(packer='lz4');loaded={o.path_id:o for o in UnityPy.load(raw).objects};assert set(loaded)==set(oo)
for i,o in loaded.items():
 if i in [obj.path_id,sid]:assert o.read_typetree()=={obj.path_id:doc,sid:sheet}[i]
 else:assert sha(o.get_raw_data())==hashes[i],i
out=V/'labels-v2';out.mkdir(exist_ok=False);(out/'backup-game').mkdir();(out/W).write_bytes(raw);(out/'backup-game'/W).write_bytes(before)
tx=[{'target':str(G/W),'source':str(out/W),'backup':str(out/'backup-game'/W),'before':sha(before),'after':sha(raw)}]
protected={p:sha(Path(p).read_bytes()) for p in v1['protected_sha256'] if Path(p)!=G/W}
record={'version':'Sidebar 100px V2 labels always visible','installed':False,'runtime_verified':False,'cause':'Native AreBookmarkLabelsVisible hides labels according to horizontal bookmark bar policy','label_binding':'row.DisplayValue','visibility_binding':'const.true','protected_sha256':protected}
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
import shutil
shutil.copyfile(R/'install-independent-resource-patch.py',out/'installer.py')
for name,flag in [('install',''),('restore-v1',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
# A complete rollback restores the three original files from the first trial install.
full=out/'full-rollback';full.mkdir();original=json.loads((V/'trial-install-001/transaction.json').read_text('utf8'))
for row in original:
 if Path(row['target']).name==W:row.update(source=str(out/W),after=sha(raw))
(full/'transaction.json').write_text(json.dumps(original,ensure_ascii=False,indent=2),'utf8')
targets={Path(x['target']) for x in original};fullprotected={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fullprotected,'purpose':'Restore original pre-sidebar game files'},ensure_ascii=False,indent=2),'utf8')
shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':str(out),'changed_objects':[obj.path_id,sid],'width_px':100,'labels_always_visible':True,'original_text_binding_preserved':True},ensure_ascii=False))
