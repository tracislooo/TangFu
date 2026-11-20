from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','rid_links'}),('split-season-radar-two-charts.py',{'graph','add_node'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
base=Path(json.loads((R/'full-season-header-prepared.json').read_text())['output']);m=json.loads((base/'manifest.json').read_text('utf8'));assert m['installed'];oldtx=json.loads((base/'transaction.json').read_text())
OUT=R/('test-full-season-scout-context-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[]
for j,row in enumerate(oldtx):
 tag=['game','skin'][j];path=Path(row['target']);before=path.read_bytes();assert sha(before)==row['after'];env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
 doc=obs[-941100000001020].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();st=Styles(sheet)
 p=(copy.deepcopy(rr[1116]),copy.deepcopy(rr[rr[1116]['data']['m_SerializedData']['rid']]))
 bridge=add_node(doc,p,6298,'ScoutHeaderPreservedContext');rr=refs(doc);rr[6298]['data']['m_Children'].remove({'rid':bridge});rr[6298]['data']['m_Children'].insert(0,{'rid':bridge});rr[6298]['data']['m_Children'].remove({'rid':1349});rr[bridge]['data']['m_Children'].append({'rid':1349});rr[1349]['data']['m_Parent']={'rid':bridge}
 st.edit(rr[bridge],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(131087,st.px(75)),st.p(131096,st.px(75)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131083,st.en('column'))],reset=True)
 assert data(rr,bridge)['Mappings']==data(rr,1116)['Mappings'];graph(doc)
 obs[-941100000001020].save_typetree(doc);obs[sid].save_typetree(sheet);output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check[-941100000001020].read_typetree()==doc;assert check[sid].read_typetree()==sheet
 for i,h in hashes.items():
  if i not in [-941100000001020,sid]:assert sha(check[i].get_raw_data())==h
 src,backup=OUT/tag/path.name,OUT/('backup-'+tag)/path.name;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(path),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=str(base/'manifest.json'),full_layout_patch=str(base),scout_context_preserved=True)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'full-season-scout-context-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
