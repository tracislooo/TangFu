"""Independently verify prepared or installed database-view resources."""
from pathlib import Path
import sys,json,hashlib,copy,importlib.util,struct
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]).resolve();installed='--installed' in sys.argv
m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';V='ui-tableviews_assets_all.bundle'
VP,RP,SP=-991112000001000,-991112000001010,-991112000001011
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
results=[]
for p,s in tx['sources'].items():
 assert sha(Path(s).read_bytes())==m['after_sha256'][p],('Damaged output',s)
 assert sha(Path(tx['before'][p]).read_bytes())==m['before_sha256'][p],('Damaged backup',p)
 if installed:assert sha(Path(p).read_bytes())==m['after_sha256'][p],('Installed mismatch',p)
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 report=next(x for x in m['reports'] if x['folder']==tag)
 def path(n):
  if installed:return folder.parent/n if tag=='game' and n.startswith('catalog.') else folder/n
  return out/tag/n
 allobjs={};backupobjs={}
 for n in [G,W,V]:
  oo={o.path_id:o for o in UnityPy.load(str(path(n))).objects}
  old={o.path_id:o for o in UnityPy.load(str(out/('backup-'+tag)/n)).objects}
  changed=set(report['changed_objects'][n]);assert set(old)<=set(oo)
  for pid,o in old.items():
   if pid not in changed:assert o.get_raw_data()==oo[pid].get_raw_data(),('Unexpected object modification',tag,n,pid)
  allobjs[n]=oo;backupobjs[n]=old
 def named(n,name,old=False):return next(o for o in (backupobjs if old else allobjs)[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name).read_typetree()
 a=named(V,'SearchResultsTableOverview');old=named(V,'SearchResultsTableOverview',True);b=allobjs[V][VP].read_typetree()
 cc=a['m_tableView']['m_tableConfig'];bc=b['m_tableView']['m_tableConfig']
 k=next(i for i,c in enumerate(cc) if c['m_columnID']=='knowledge');assert cc[k+1]['m_columnID']=='average-rating'
 assert len(cc)==len(old['m_tableView']['m_tableConfig'])+1
 rating=next(c for c in named(V,'SearchResultsTableStatsClub')['m_tableView']['m_tableConfig'] if c['m_columnID']=='average-rating');assert cc[k+1]==rating
 copya=copy.deepcopy(a);copya['m_tableView']['m_tableConfig'].pop(k+1)
 for c,orig in zip(copya['m_tableView']['m_tableConfig'],old['m_tableView']['m_tableConfig']):
  if c['m_columnID'] in ['knowledge','club-player-search','tactical-effectiveness-gauge-no-sort']:
   c['m_columnMetadata']['m_widthOverride']=orig['m_columnMetadata']['m_widthOverride']
   c['m_columnMetadata']['m_minWidthOverride']=orig['m_columnMetadata']['m_minWidthOverride']
 assert copya==old,'Overview changes exceed rating and width adjustments'
 replacements={'current-ability-stars':'hidden-current-ability','potential-ability-stars':'hidden-potential-ability'}
 assert len(cc)==len(bc)
 for x,y in zip(cc,bc):
  expected=copy.deepcopy(x)
  if x['m_columnID'] in replacements:
   expected['m_columnID']=replacements[x['m_columnID']];expected['m_columnMetadata'].update(m_widthOverride=64.,m_minWidthOverride=64.)
  assert y==expected
 cd=named(V,'PlayerSearchResultsViewCollection');oldcd=named(V,'PlayerSearchResultsViewCollection',True)
 entry=cd['m_tableViewSettings'].pop(1);assert entry['PropertyValue']=={'m_FileID':0,'m_PathID':VP};assert cd==oldcd
 row=allobjs[G][RP].read_typetree();rr={r['rid']:r for r in row['references']['RefIds']}
 def sd(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
 gate=next(i for i,r in rr.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and sd(i).get('name')=='DatabaseOverviewHiddenTitleSelector')
 false,true=[x['rid'] for x in rr[gate]['data']['m_Children']]
 assert sd(false)['TextBinding']['m_direct']['Path']['m_path']=='row.DisplayValue'
 assert sd(true)['text']=='总览+隐藏' and sd(true)['TextBinding']['m_kind']==0
 raw=bytes(sd(gate)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);pos=1;args=[]
 for i in range(raw[0]):
  length=struct.unpack_from('<I',raw,pos)[0];pos+=4;args.append(raw[pos:pos+length]);pos+=length
 assert pos==len(raw) and struct.unpack('<i',args[0][-4:])[0]==2 and struct.unpack('<i',args[1][-4:])[0]==1 and args[2].endswith(b'row.PropertyValue')
 for dropdown in report['dropdowns']:
  d=allobjs[dropdown['bundle']][dropdown['pid']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
  for rid in dropdown['overrides']:
   z=r[rid]['data'];assert z['RowTemplate']['m_AssetGUID']==m['new_row_guid'] and z['UseRowTemplateToShowSelectedValue']==1
 catalog=cm.Catalog(path('catalog.bin').read_bytes());original=cm.Catalog((out/('backup-'+tag)/'catalog.bin').read_bytes());keys=dict(catalog.keys());oldkeys=dict(original.keys())
 assert set(keys)-set(oldkeys)=={m['new_view_guid'],m['new_row_guid']}
 label='GlobalVisualTreeAssetPreload'
 for key,ptr in oldkeys.items():
  oldloc=[x[0] for x in original.array(ptr,'I')];newloc=[x[0] for x in catalog.array(keys[key],'I')]
  assert newloc[:len(oldloc)]==oldloc
  if key!=label:assert newloc==oldloc
  for loc in oldloc:assert catalog.location(loc)==original.location(loc),('Existing catalog location changed',key)
 for guid,n,pid,kind in [(m['new_view_guid'],V,VP,'SI.Bindable.StreamedTableViewSettings'),(m['new_row_guid'],G,RP,'UnityEngine.UIElements.VisualTreeAsset')]:
  ls=[x[0] for x in catalog.array(keys[guid],'I')];assert len(ls)==1
  loc=catalog.location(ls[0]);assert loc['type'][1]==kind,(guid,loc['type'])
  assert catalog.location(loc['dependencies'][0])['internal'].replace('\\','/').endswith('/'+n)
  meta=next(o.read_typetree() for o in allobjs[n].values() if o.type.name=='AssetBundle')
  entry=next(v for k,v in meta['m_Container'] if k==guid);assert entry['asset']=={'m_FileID':0,'m_PathID':pid}
  span=meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]
  assert {'m_FileID':0,'m_PathID':pid} in span
  if n==G:assert {'m_FileID':0,'m_PathID':SP} in span and ls[0] in [x[0] for x in catalog.array(keys[label],'I')]
 if path('catalog.hash').exists():assert path('catalog.hash').read_text().strip()==hashlib.md5(path('catalog.bin').read_bytes()).hexdigest()
 results.append({'target':tag,'overview_and_hidden_columns_verified':True,'menu_order_and_title_verified':True,'catalog_and_preload_verified':True,'unrelated_objects_preserved':True})
result={'installed':installed,'runtime_verified':False,'results':results}
(out/('verification-installed.json' if installed else 'verification-prepared.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
