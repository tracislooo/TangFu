"""Restore the prior competition appearances and native ability radar beneath the updated hidden module."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'}),('fix-old-left-fc-binding-route.py',{'remove','graft'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-950000000000162;KEY='e898cf8de19d543984f58379abb35340'
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
previous=json.loads((R/'current-old-left-fc-hidden-overview.json').read_text('utf8'));sourceout=Path(previous['manifest']).parent
assert 'binding-route-fix' in sourceout.name
OUT=R/('old-left-fc-competition-radar-divider-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 print('Preparing '+tag,flush=True);before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();old=copy.deepcopy(doc);sheet=oo[doc['inlineSheet']['m_PathID']].read_typetree();oldsheet=copy.deepcopy(sheet)
 backup=sourceout/('backup-'+tag)/W;donors={o.path_id:o for o in UnityPy.load(str(backup)).objects};source=donors[PAGE].read_typetree();ss=donors[source['inlineSheet']['m_PathID']].read_typetree()
 # Historical source is restricted to the requested appearances/radar subtree.
 rr=refs(doc);career=named(doc,'ApprovedHeaderCareerPlayerContext');parent=rr[career]['data']['m_Parent']['rid'];assert parent==6322
 removed=remove(doc,career);mapping=graft(doc,sheet,source,ss,6298,parent);rr=refs(doc);st=Styles(sheet);row=mapping[6298]
 data(rr,row).update(name='OldLeftFCCompetitionAppearancesAndAbilityRadar',name_UxmlAttributeFlags=1)
 st.edit(rr[row],[st.p(131087,st.px(0)),st.p(131096,st.px(200)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1))])
 prototype=(rr[6330],rr[rr[6330]['data']['m_SerializedData']['rid']]);sep=add_node(doc,prototype,row,'OldLeftFCCompetitionRadarVerticalDivider');rr=refs(doc)
 rr[row]['data']['m_Children']=[{'rid':mapping[6228]},{'rid':sep},{'rid':mapping[1026]}]
 props=copy.deepcopy(sheet['m_Rules'][rr[6330]['data']['m_RuleIndex']]['m_Properties']);st.edit(rr[sep],props,reset=True)
 # Imported chart and competition template bindings are exact copies of the prior display.
 sr=refs(source)
 for i in [1035,1043]:assert data(rr,mapping[i])==dict(data(sr,i),uxmlAssetId=rr[mapping[i]]['data']['m_Id'])
 oldrr=refs(old)
 for i,r in oldrr.items():
  if i not in removed and i!=parent:assert rr[i]==r,('Retained upper layout or identity changed',i)
 assert sheet['m_Rules'][:len(oldsheet['m_Rules'])]==oldsheet['m_Rules']
 doc['m_ContentHash']=zlib.crc32(json.dumps(doc,ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
 graph(doc);validate_ui(doc,sheet)
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');entries=[v for k,v in meta['m_Container']if k==KEY];assert len(entries)==1 and entries[0]['asset']=={'m_FileID':0,'m_PathID':PAGE}
 changes={PAGE:doc,doc['inlineSheet']['m_PathID']:sheet}
 for i,d in changes.items():oo[i].save_typetree(d)
 output=env.file.save(packer='lz4');back={o.path_id:o for o in UnityPy.load(output).objects};assert back.keys()==oo.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(back[i].get_raw_data())==h,('Unrelated object changed',tag,i)
 for i,d in changes.items():assert back[i].read_typetree()==d
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,page=PAGE,unique_guid=KEY,appearances_template_guid=next(u['path']for u in doc['m_Usings']if u['alias']=='PlayerReportBansBlock'),native_radar_binding_unchanged=True,vertical_divider_between_competition_and_radar=sep,upper_module_and_id_and_identity_divider_unchanged=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,previous_manifest=previous['manifest'],change='Replace career table with prior competition appearances and eight-axis ability radar, with a vertical separator',protected_sha256=protected,checks=checks)
for n,v in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'old-left-fc-competition-radar-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
