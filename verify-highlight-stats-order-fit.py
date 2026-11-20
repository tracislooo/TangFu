from pathlib import Path
import sys,json,hashlib,importlib.util,struct
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
P=R/'highlight-stats-order-fit-20261105-002439';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
tx=json.loads((P/'transaction.json').read_text('utf8'));checks=[]
for tag,pre in [('game',''),('skin','skin-')]:
 bundles={n:{o.path_id:o for o in UnityPy.load((P/(pre+n)).read_bytes()).objects} for n in [G,T,V]}
 def named(n,name):return next(o for o in bundles[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 def meta(n):return next(o.read_typetree() for o in bundles[n].values() if o.type.name=='AssetBundle')
 def guid(n,obj):return next(k for k,v in meta(n)['m_Container'] if v['asset']['m_PathID']==obj.path_id)
 stat=named(G,'HighlightUpperGoalsAssistsTallerRows');d=stat.read_typetree();view=named(V,'HighlightUpperGoalsAssistsView');vguid=guid(V,view);sguid=guid(G,stat);rs={r['rid']:r for r in d['references']['RefIds']}
 tables=[r['data'] for r in rs.values() if 'FixedElementSize' in r.get('data',{})];assert len(tables)==2 and all(s['FixedElementSize']==28 and vguid.encode() in bytes(s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']) for s in tables)
 expected=['picked-position','player','rating','goals','assists','run','pass%','keyPasses','keyTackles'];assert [c['m_columnID'] for c in view.read_typetree()['m_tableView']['m_tableConfig']]==expected
 for side in ['Home','Away']:
  d=named(G,'HighlightIntegrated'+side+'StatsAndFormation').read_typetree();assert next(u['path'] for u in d['m_Usings'] if u['alias']=='Highlight'+side+'Stats')==sguid
 old={o.path_id:o for o in UnityPy.load((P/('backup-'+tag)/G).read_bytes()).objects}
 for name in ['HighlightRestoredNativeEightStats','MatchStats_4x4','HighlightFiveAnalysisCenterWithoutMaps','SmallSubstituteCardLowerNoRating','HighlightPhaseSpecificFeetAndCondition']:
  obj=named(G,name);assert sha(obj.get_raw_data())==sha(old[obj.path_id].get_raw_data())
 oldt={o.path_id:o for o in UnityPy.load((P/('backup-'+tag)/T).read_bytes()).objects}
 count=0
 for obj in bundles[T].values():
  if obj.type.name=='MonoBehaviour' and obj.peek_name() in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:
   tr=obj.read_typetree();before=oldt[obj.path_id].read_typetree();assert [b['m_location'] for b in tr['m_gridComponents']]==[b['m_location'] for b in before['m_gridComponents']];count+=1
 assert count==4
 catpath=P/(tag+'-catalog.bin');cat=cm.Catalog(catpath.read_bytes());sourcecat=cm.Catalog((P/('backup-'+tag)/'catalog.bin').read_bytes());oldviewguid=guid(V,named(V,'HighlightEightFieldsView'))
 # Follow all existing preload labels used by the actual source view, if any.
 source_view_loc=sourcecat.locations('bea623364b065389ac4a9253f798b53b')[0];newloc=cat.locations(vguid)[0];updated=[]
 for i,(key,_) in enumerate(cat.keys()):
  if 'preload' not in str(key).lower():continue
  ko,ls=cat.key_records[i];values=[v[0] for v in cat.array(ls,'I')]
  if source_view_loc in values and newloc not in values:
   values.append(newloc);records=list(cat.key_records);records[i]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in values),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cat=cm.Catalog(bytes(cat.data));updated.append(key)
 raw=bytes(cat.data);catpath.write_bytes(raw);hashdata=hashlib.md5(raw).hexdigest().encode('ascii');(P/(tag+'-catalog.hash')).write_bytes(hashdata)
 for row in tx:
  if row['source']==str(catpath):row['after']=sha(raw)
  if row['source']==str(P/(tag+'-catalog.hash')):row['after']=sha(hashdata)
 for n,obj in [(G,stat),(G,named(G,'HighlightCompactMatchStatsThreeByThree')),(V,view)]:
  loc=cat.locations(guid(n,obj))[0];assert n in cat.location(cat.location(loc)['dependencies'][0])['internal']
 checks.append({'variant':tag,'upper_private_column_order':expected,'row_height':28,'layout_positions_unchanged':True,'shared_stats_original_comparisons_pitch_bench_byte_identical':True,'view_preload_labels_copied':updated,'catalog_owner_checked':True})
(P/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(P/'independent-check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),'utf8')
previous=json.loads((R/'current-highlight-layout.json').read_text('utf8'));(P/'previous-highlight-state.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');state=dict(previous);state.update(status='prepared',patch=str(P),source_script=str(R/'build-highlight-stats-order-fit.py'),restore=str(P/'restore.ps1'),verification=str(P/'independent-check.json'),runtime_verified=False,upper_stats_column_order=expected,upper_stats_row_height=28,lower_comparisons='private compact 9/10px fonts, five flex rows without old minimum heights',backup_directories=[str(P/('backup-'+t)) for t in ['game','skin','cache']]);(P/'highlight-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
installer=(P/'installer.py').read_text('utf8');installer+="\nstate=json.loads((out/('previous-highlight-state.json' if restore else 'highlight-state.json')).read_text('utf8'))\nif not restore:state.update(status='installed',installed_files=len(tx))\n(out.parent/'current-highlight-layout.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')\n";(P/'installer.py').write_text(installer,'utf8')
print(json.dumps(checks,ensure_ascii=False))
