from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<bundle loader>','exec'))
HP=5775949770471550939
current=objects[HP].read_typetree();cr={r['rid']:r for r in current['references']['RefIds']}
report_source=json.loads((R/'touch-bar-three-native-status-icons-20261019-001825/manifest.json').read_text(encoding='utf8'))
assert sha(before[GAME/WN])==report_source['after_sha256']
icons={'Mindset':1141,'Hierarchy':1143,'OverallCondition':1145}
for label,i in icons.items():
 assert cr[i]['data']['m_FullTypeName']=='SI.Bindable.SIImage'
 sd=cr[cr[i]['data']['m_SerializedData']['rid']]['data'];assert sd['name']=='Header'+label+'Icon'
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('isolate-touch-bar-icons-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
log=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
if log.exists():(out/'Player-before-isolation.log').write_bytes(log.read_bytes())
variants={};data_by_variant={}
for keep in ['OverallCondition','Mindset','Hierarchy']:
 d=copy.deepcopy(current);rr={r['rid']:r for r in d['references']['RefIds']};removed=set()
 for label,i in icons.items():
  if label==keep:continue
  n=rr[i]['data'];rr[n['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i})
  removed.update([i,n['m_SerializedData']['rid']])
 d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in removed]
 validate_ui(d,objects[d['inlineSheet']['m_PathID']].read_typetree())
 objects[HP].save_typetree(d);data=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objects)
 for i,h in old_hashes.items():
  if i==HP:assert saved[i].read_typetree()==d
  else:assert sha(saved[i].get_raw_data())==h
 sd=saved[HP].read_typetree();sr={r['rid']:r for r in sd['references']['RefIds']}
 assert sum(i in sr for i in icons.values())==1
 for title in ['HeaderMindsetValue','HeaderHierarchyValue','HeaderOverallConditionValue']:
  assert any(r.get('data',{}).get('name')==title for r in sr.values())
 folder=out/('only-'+keep);folder.mkdir();(folder/WN).write_bytes(data)
 variants[keep]={'sha256':sha(data),'path':str(folder/WN),'removed_icon_nodes':sorted(removed),'three_status_texts_preserved':True};data_by_variant[keep]=data
for p,d in before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
installed='OverallCondition';data=data_by_variant[installed]
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(data);assert (folder/WN).read_bytes()==data
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,d in before.items():p.write_bytes(d)
 raise
manifest={'installed_variant':installed,'runtime_verified':False,'culprit_confirmed':False,'only_one_of_three_added_icons_enabled':True,'three_status_texts_preserved':True,'before_sha256':{str(p):sha(d) for p,d in before.items()},'variants':variants}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed_variant':installed,'sha256':sha(data),'prepared_variants':list(variants),'three_texts_preserved':True},ensure_ascii=False,indent=2))
