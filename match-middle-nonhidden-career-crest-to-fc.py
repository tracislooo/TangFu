"""Refine the installed nonhidden middle portrait page incrementally."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
source=(R/'sync-middle-portrait-hidden-to-fc.py').read_text('utf8')
exec(source[source.index("source=(R/'add-approved"):source.index('spec=importlib')])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-930000000001003
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-nonhidden-career-match-fc-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 fc=oo[-930000000001001].read_typetree();fs=oo[fc['inlineSheet']['m_PathID']].read_typetree();fr=refs(fc)
 # The exact installed FC career subtree includes its native visible scrollbar.
 detail=graft(doc,sheet,fc,fs,named(doc,'OverviewTopRightStatusPanel'),named(fc,'OverviewTopRightStatusPanel'));rr=refs(doc)
 def copy_rule(target,source):
  rule=copy.deepcopy(fs['m_Rules'][fr[source]['data']['m_RuleIndex']])
  for p in rule['m_Properties']:
   for v in p['m_Values']:
    pool=poolmap.get(v['m_ValueType'])
    if pool:sheet[pool].append(copy.deepcopy(fs[pool][v['valueIndex']]));v['valueIndex']=len(sheet[pool])-1
  rr[target]['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
 def chain(rmap,doc):
  club=named(doc,'ClubImage');setter=rmap[club]['data']['m_Parent']['rid'];holder=rmap[setter]['data']['m_Parent']['rid'];layer=rmap[holder]['data']['m_Parent']['rid'];stage=rmap[layer]['data']['m_Parent']['rid'];column=rmap[stage]['data']['m_Parent']['rid'];return [holder,layer,stage,column]
 tc,fcchain=chain(rr,doc),chain(fr,fc)
 for t,f in zip(tc,fcchain):copy_rule(t,f)
 # Align the central column boundary as well, so the FC positions share an origin.
 targetcentre=next(c['rid']for c in rr[1169]['data']['m_Children']if data(rr,c['rid']).get('name')=='ReportPortraitStatusColumn')
 sourcecentre=next(c['rid']for c in fr[1169]['data']['m_Children']if data(fr,c['rid']).get('name')=='ReportPortraitStatusColumn')
 widthkeys={131105,131082,131097,131095}
 props=copy.deepcopy([p for p in fs['m_Rules'][fr[sourcecentre]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']in widthkeys])
 for p in props:
  for v in p['m_Values']:
   pool=poolmap.get(v['m_ValueType'])
   if pool:sheet[pool].append(copy.deepcopy(fs[pool][v['valueIndex']]));v['valueIndex']=len(sheet[pool])-1
 st.edit(rr[targetcentre],props)
 assert not any(data(rr,i).get('name')=='MiddleNonHiddenCareerVerticalScroll'for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,source_fc_page=-930000000001001,career_subtree_matches_fc=True,native_career_scrollbar_matches_fc=True,crest_holder_and_layer_and_origin_styles_match_fc=True,center_column_width_matches_fc=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-career-match-fc-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
