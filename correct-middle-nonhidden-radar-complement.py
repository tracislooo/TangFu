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
OUT=R/('middle-nonhidden-radar-complement-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 def delete(node):
  rr=refs(doc);parent=rr[node]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':node});gone=owned_refs(rr,node);doc['references']['RefIds']=[x for x in doc['references']['RefIds']if x['rid']not in gone]
 # Start from the original twelve native statistics for each position group.
 native=oo[-950000000000164].read_typetree();ns=oo[native['inlineSheet']['m_PathID']].read_typetree();nst=Styles(ns)
 div=named(doc,'OverviewPersonalRowsDivider1');rule=sheet['m_Rules'][rr[div]['data']['m_RuleIndex']]
 colorvalue=copy.deepcopy(sheet['colors'][next(p for p in rule['m_Properties']if p['m_Id']==458752)['m_Values'][0]['valueIndex']])
 groups=[('SeasonStatsGoalkeeperPanel','GoalkeeperStatCell_', ['ExpectedGoalsPreventedPer90','TotalSavesPer90','ConcededPer90','PossessionWonPer90','PossessionLostPer90','PassCompletedPer90']),('SeasonStatsOutfielderPanel','SeasonStatCell_', ['ExpectedGoalsPer90','ShotsOnTargetPer90','ExpectedAssistsPer90','PassCompletedPer90','TacklesCompletedPer90','KeyHeadersPer90'])]
 details=[]
 for panelname,prefix,radarfields in groups:
  donor=copy.deepcopy(native);ds=copy.deepcopy(ns);dst=Styles(ds);dr=refs(donor);panel=named(donor,panelname)
  rows=[c['rid']for c in dr[panel]['data']['m_Children']]
  cells=[c['rid']for row in rows for c in dr[row]['data']['m_Children']if data(dr,c['rid']).get('name','').startswith(prefix)]
  assert len(cells)==12
  remaining=[c for c in cells if data(dr,c)['name'][len(prefix):]not in radarfields];assert len(remaining)==6
  keptfields=[data(dr,c)['name'][len(prefix):]for c in remaining]
  def drop(i):
   xr=refs(donor);p=xr[i]['data']['m_Parent']['rid'];xr[p]['data']['m_Children'].remove({'rid':i});gone=owned_refs(xr,i);donor['references']['RefIds']=[x for x in donor['references']['RefIds']if x['rid']not in gone]
  for cell in remaining:
   dr[dr[cell]['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':cell})
  for row in rows:
   for ch in list(refs(donor)[row]['data']['m_Children']):drop(ch['rid'])
  drop(rows[3]);rows=rows[:3];dr=refs(donor)
  saved={i:copy.deepcopy(dr[i])for cell in remaining for i in owned_refs(dr,cell)}
  for j,cell in enumerate(remaining):
   dr[cell]['data']['m_Parent']={'rid':rows[j//2]};dr[rows[j//2]]['data']['m_Children'].append({'rid':cell})
   dst.edit(dr[cell],[dst.p(131105,dst.pct(50)),dst.p(131087,dst.pct(100)),dst.p(131097,dst.px(0)),dst.p(131084,dst.num(0)),dst.p(131085,dst.num(1)),dst.p(131088,dst.en('center'))])
   for i in owned_refs(dr,cell):
    if dr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':dst.edit(dr[i],[dst.p(65537,dst.px(10 if 'Title_'in data(dr,i).get('name','')else 16))])
  proto=(copy.deepcopy(dr[rows[0]]),copy.deepcopy(dr[dr[rows[0]]['data']['m_SerializedData']['rid']]))
  for j,row in enumerate(rows):
   dst.edit(dr[row],[dst.p(131087,dst.pct(struct.unpack('<f',struct.pack('<f',100/3))[0])),dst.p(131102,dst.en('relative')),dst.p(131085,dst.num(1)),dst.p(131096,dst.px(0))])
   line=add_node(donor,proto,row,panelname+'ComplementRowSeparator'+str(j+1));dr=refs(donor)
   dst.edit(dr[line],[dst.p(131102,dst.en('absolute')),dst.p(131089,dst.px(0)),dst.p(131103,dst.px(0)),dst.p(131080,dst.px(0)),dst.p(131087,dst.px(1)),dst.p(131096,dst.px(1)),dst.p(131084,dst.num(0)),dst.p(131085,dst.num(0)),dst.p(458752,dst.h(4,copy.deepcopy(colorvalue)))],reset=True)
   data(dr,line).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
  for i,v in saved.items():
   actual=copy.deepcopy(dr[i]);old=copy.deepcopy(v)
   for q in [actual,old]:q['data'].pop('m_RuleIndex',None)
   if i in remaining:
    actual['data'].pop('m_Parent');old['data'].pop('m_Parent')
   assert actual==old,('Native binding changed',i)
  dst.edit(dr[panel],[dst.p(131087,dst.pct(100)),dst.p(131096,dst.px(0)),dst.p(131105,dst.pct(100))])
  graft(doc,sheet,donor,ds,named(doc,panelname),panel)
  details.append(dict(panel=panelname,radar_fields=radarfields,table_fields=keptfields,columns=2,rows=3))
 rr=refs(doc)
 assert named(doc,'NonHiddenRadarDataHorizontalDivider') and named(doc,'NonHiddenStatsProsConsVerticalDivider')
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,groups=details,native_cells_restored=True,retained_cell_bindings_exact=True,horizontal_and_vertical_lines_preserved=True,portrait_unchanged=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-radar-complement-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
