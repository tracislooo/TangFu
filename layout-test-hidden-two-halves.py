from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('add-left-test-overview.py',{'prune'}),('split-season-radar-two-charts.py',{'graph'})]:
 t=ast.parse((R/filename).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),filename,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
OUT=R/('test-hidden-two-halves-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'))
manifest=json.loads(Path(previous['manifest']).read_text('utf8'));tx=[];checks=[]
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 go={o.path_id:o for o in UnityPy.load(str(root/G)).objects}
 doc=obs[-941100000001020].read_typetree();original=copy.deepcopy(doc);sheet=obs[doc['inlineSheet']['m_PathID']].read_typetree();st=Styles(sheet);rr=refs(doc)
 def edit(i,**kw):
  ids={'width':131105,'height':131087,'minheight':131096,'maxheight':131094,'grow':131084,'shrink':131085,'basis':131082,'direction':131083,'bottom':131090,'left':131091,'right':131092,'padleft':131099,'padright':131100,'minwidth':131097,'maxwidth':131095}
  props=[]
  for k,v in kw.items():
   val=st.en(v)if isinstance(v,str)and v!='auto'else ({'m_ValueType':1,'valueIndex':2}if v=='auto'else st.num(v)if k in ['grow','shrink']else st.pct(float(v[:-1]))if isinstance(v,str)and v.endswith('%')else st.px(v))
   if isinstance(v,str)and v.endswith('%'):val=st.pct(float(v[:-1]))
   props.append(st.p(ids[k],val))
  st.edit(rr[i],props)
 # Reflow only the seventh page's lower right information block.
 edit(1011,direction='row',grow=1,minheight=0)
 edit(5852,width='50%',minwidth=0,maxwidth='50%',height='100%',grow=0,shrink=0,basis='auto',padright=8)
 edit(6298,width='50%',minwidth=0,maxwidth='50%',height='100%',minheight=0,maxheight='auto',grow=0,shrink=0,basis='auto',direction='column',padleft=8)
 edit(5854,width='100%',height=58,minheight=58,maxheight=58,grow=0,shrink=0)
 edit(6064,direction='column',width='100%',height='auto',grow=1,basis=0,minheight=0)
 rows=[]
 for col in [6222,6224,6226]:
  children=list(rr[col]['data']['m_Children'])
  for c in children:
   rr[col]['data']['m_Children'].remove(c);rr[c['rid']]['data']['m_Parent']={'rid':6064};rows.append(c)
  prune(doc,col);rr=refs(doc)
 rr[6064]['data']['m_Children']=rows
 assert len(rows)==13
 for c in rows:edit(c['rid'],width='100%',minwidth=0,maxwidth='100%',height=22,minheight=22,maxheight=22,grow=0,shrink=0,bottom=0)
 for i in [6264,6266]:edit(i,height=0,minheight=0,maxheight=0,bottom=0,grow=0,shrink=0)
 for i in [6310,6312,6306,6308]:edit(i,width='100%',height='100%',minheight=0,maxheight='auto',grow=1,shrink=1,basis=0,direction='column')
 for i in [6314,6316]:edit(i,width='100%',minwidth=0,maxwidth='100%',height=0,minheight=0,maxheight='auto',grow=1,shrink=1,basis=0,left=0,right=0)
 edit(6318,width='100%',height=1,minheight=1,maxheight=1,grow=0,shrink=0)
 # Embed a private copy of the existing native-bound pros/cons template.
 native=copy.deepcopy(go[-940000000015000].read_typetree());ns=go[native['inlineSheet']['m_PathID']].read_typetree()
 assert not native['m_Usings']
 nr=refs(native);rootrid=native['m_VisualTree']['rid'];kids=nr[rootrid]['data']['m_Children'];assert len(kids)==1
 offset=max(rr)+100;idbase=max(r.get('data',{}).get('m_Id',0)for r in rr.values())+100
 offsets={k:len(sheet[k])for k in set(poolmap.values())}
 idmap={r['data']['m_Id']:idbase+j for j,r in enumerate(native['references']['RefIds'])if 'm_Id'in r.get('data',{})}
 for k in offsets:sheet[k].extend(copy.deepcopy(ns[k]))
 rulebase=len(sheet['m_Rules'])
 for rule in copy.deepcopy(ns['m_Rules']):
  for selector in rule['m_ComplexSelectors']:selector['ruleIndex']+=rulebase
  for p in rule['m_Properties']:
   for h in p['m_Values']:
    if h['m_ValueType']in poolmap:h['valueIndex']+=offsets[poolmap[h['m_ValueType']]]
  sheet['m_Rules'].append(rule)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid']in nr:v['rid']+=offset
   else:
    for k,x in v.items():
     if k=='rid'and isinstance(x,int):v[k]=x+offset
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for r in native['references']['RefIds']:
  if r['rid']==rootrid:continue
  v=r.get('data',{})
  if v.get('m_RuleIndex',-1)>=0:v['m_RuleIndex']+=rulebase
  if 'm_Id'in v:v['m_Id']=idmap[v['m_Id']]
  if 'uxmlAssetId'in v:v['uxmlAssetId']=idmap[v['uxmlAssetId']]
  remap(r);doc['references']['RefIds'].append(r)
 parent=rr[6308]['data']['m_Parent']['rid'];prune(doc,6308);rr=refs(doc)
 embedded=kids[0]['rid']+offset;rr[embedded]['data']['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':embedded})
 for i in [1001,1002]:edit(i+offset,direction='column',width='100%',height='100%',minheight=0,maxheight='auto',grow=1,shrink=1,basis=0)
 for i in [1004,1005]:edit(i+offset,width='100%',minwidth=0,maxwidth='100%',height=0,minheight=0,maxheight='auto',grow=1,shrink=1,basis=0,direction='column',bottom=4)
 for i in [1008,1011]:edit(i+offset,width='100%',height=0,minheight=0,maxheight='auto',grow=1,shrink=1,basis=0)
 # Every imported binding is unchanged, including native list rows and headings.
 for r in native['references']['RefIds']:
  v=r.get('data',{})
  if 'm_SerializedData'in v:continue
  if r['rid']in rr:assert rr[r['rid']]==r
 graph(doc)
 sid=doc['inlineSheet']['m_PathID'];obs[-941100000001020].save_typetree(doc);obs[sid].save_typetree(sheet)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
 assert check[-941100000001020].read_typetree()==doc;assert check[sid].read_typetree()==sheet
 for i,h in baseline.items():
  if i not in [-941100000001020,sid]:assert sha(check[i].get_raw_data())==h
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,hidden_rows=13,private_pros_cons_copy=True,unrelated_objects_unchanged=True));print('Verified '+tag,flush=True)
manifest.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Test overview: hidden attributes left; stacked pros/cons or transfer/favoured right',checks=checks)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'hidden-two-halves-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
