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
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-930000000001003
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-nonhidden-four-rows-lines-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 def delete(node):
  rr=refs(doc);parent=rr[node]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':node});gone=owned_refs(rr,node);doc['references']['RefIds']=[x for x in doc['references']['RefIds']if x['rid']not in gone]
 panel=named(doc,'SeasonStatsGoalkeeperPanel');rows=[c['rid']for c in rr[panel]['data']['m_Children']]
 removed=['GamesWonAndPlayed','PlayerOfTheMatchAwards','MinutesPerGoalConceded','PassCompletedPer90']
 for field in removed:delete(named(doc,'GoalkeeperStatCell_'+field))
 rr=refs(doc);cells=[c['rid']for row in rows for c in rr[row]['data']['m_Children']];assert len(cells)==8
 saved={i:copy.deepcopy(rr[i])for cell in cells for i in owned_refs(rr,cell)}
 for cell in cells:rr[rr[cell]['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':cell})
 for row in rows[4:]:delete(row)
 rr=refs(doc);rows=rows[:4]
 for j,cell in enumerate(cells):
  rr[cell]['data']['m_Parent']={'rid':rows[j//2]};rr[rows[j//2]]['data']['m_Children'].append({'rid':cell})
 for row in rows:st.edit(rr[row],[st.p(131087,st.pct(25)),st.p(131102,st.en('relative'))])
 for i,v in saved.items():
  actual=copy.deepcopy(rr[i]);old=copy.deepcopy(v)
  if i in cells:actual['data'].pop('m_Parent');old['data'].pop('m_Parent')
  assert actual==old,('Retained cell binding changed',i)
 # Reuse the exact color of the header's horizontal separators.
 div=named(doc,'OverviewPersonalRowsDivider1');rule=sheet['m_Rules'][rr[div]['data']['m_RuleIndex']]
 color=copy.deepcopy(next(p for p in rule['m_Properties']if p['m_Id']==458752)['m_Values'][0])
 proto=(copy.deepcopy(rr[rows[0]]),copy.deepcopy(rr[rr[rows[0]]['data']['m_SerializedData']['rid']]))
 def line(parent,name,vertical=False,middle=False):
  node=add_node(doc,proto,parent,name);rr=refs(doc)
  props=[st.p(131102,st.en('absolute')),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(458752,copy.deepcopy(color))]
  if vertical:props +=[st.p(131103,st.px(0)),st.p(131104,st.px(0)),st.p(131080,st.px(0)),st.p(131105,st.px(1)),st.p(131097,st.px(1))]
  else:
   props +=[st.p(131089,st.px(0)),st.p(131103,st.px(0)),st.p(131087,st.px(1)),st.p(131096,st.px(1))]
   props.append(st.p(131104,st.pct(50))if middle else st.p(131080,st.px(0)))
  st.edit(rr[node],props,reset=True);data(rr,node).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
  return node
 for j,row in enumerate(rows):line(row,'NonHiddenGoalkeeperRowSeparator'+str(j+1))
 other=named(doc,'SeasonStatsOutfielderPanel')
 for j,c in enumerate(list(refs(doc)[other]['data']['m_Children'])):line(c['rid'],'NonHiddenOutfielderRowSeparator'+str(j+1))
 block=named(doc,'MiddleNonHiddenSeasonRadarAndTwelveStats')
 line(block,'NonHiddenRadarDataHorizontalDivider',middle=True)
 line(block,'NonHiddenStatsProsConsVerticalDivider',vertical=True)
 # Widen the displayed portrait frame symmetrically around its existing centre.
 rr=refs(doc);portrait=[]
 for i in rr:
  if data(rr,i).get('name')=='PersonPictureFrame' if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 else False:
   rule=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]
   widths=[sheet['dimensions'][v['valueIndex']]['value']for p in rule['m_Properties']if p['m_Id']==131105 for v in p['m_Values']if v['m_ValueType']==3]
   if widths==[226.0]:st.edit(rr[i],[st.p(131105,st.px(236))]);portrait.append(i)
 assert len(portrait)==1
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,goalkeeper_fields_removed=removed,goalkeeper_columns=2,goalkeeper_rows=4,retained_cell_bindings_exact=True,row_separators=True,radar_data_separator=True,pros_cons_vertical_separator=True,separator_color_matches_header=True,portrait_width_before=226,portrait_width_after=236,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-four-rows-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
