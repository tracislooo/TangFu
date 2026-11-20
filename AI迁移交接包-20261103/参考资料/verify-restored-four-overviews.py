from pathlib import Path
import sys,json,hashlib,ast,importlib.util,collections
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
OUT=next(p for p in sorted(R.glob('restore-approved-four-overviews-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((OUT/'manifest.json').read_text('utf8'));GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SNAP=Path(m['approved_snapshot'])/'skin-tf27-01'/'packages'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle';B='ui-backgrounds_assets_common.bundle'
env={n:UnityPy.load(str(OUT/n)) for n in m['after_sha256']};env[B]=UnityPy.load(str(GAME/B));afs={a.name.lower():a for e in env.values() for a in e.assets};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog((OUT/'catalog.bin').read_bytes());oldcat=cm.Catalog((OUT/'backup-game/catalog.bin').read_bytes());keys=set(dict(cat.keys()));assert set(dict(oldcat.keys()))<=keys
assert hashlib.md5((OUT/'catalog.bin').read_bytes()).hexdigest()==(OUT/'catalog.hash').read_text('ascii')
def guids(v):
 if isinstance(v,dict):
  if v.get('m_AssetGUID'):yield v['m_AssetGUID']
  if v.get('m_target',{}).get('m_guid'):yield v['m_target']['m_guid']
  for u in v.get('m_Usings',[]):
   if u.get('path'):yield u['path']
  for x in v.values():yield from guids(x)
 elif isinstance(v,list):
  for x in v:yield from guids(x)
pointercount=0;validtrees=[];guidcount=0
for item in m['stage_assets']:
 obj=objs[item['bundle']][item['id']];d=obj.read_typetree()
 def walk(v):
  global pointercount
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
    cab=(obj.assets_file.name if not v['m_FileID'] else obj.assets_file.externals[v['m_FileID']-1].name).lower()
    if cab in afs:assert v['m_PathID'] in afs[cab].objects,('broken object reference',d.get('m_Name'),cab,v)
    pointercount+=1
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(d)
 for guid in guids(d):assert guid in keys,('missing guid',d.get('m_Name'),guid);guidcount+=1
 if 'm_VisualTree' in d:
  ptr=d['inlineSheet'];af=obj.assets_file if not ptr['m_FileID'] else afs[obj.assets_file.externals[ptr['m_FileID']-1].name.lower()]
  validate_ui(d,af.objects[ptr['m_PathID']].read_typetree());validtrees.append(d['m_Name'])
for n in [W,G,L]:
 before=UnityPy.load(str(OUT/'backup-game'/n));bm=next(o.read_typetree() for o in before.objects if o.type.name=='AssetBundle');am=next(o.read_typetree() for o in objs[n].values() if o.type.name=='AssetBundle')
 pairs=lambda meta:collections.Counter((k,v['asset']['m_FileID'],v['asset']['m_PathID']) for k,v in meta['m_Container'])
 assert not (pairs(bm)-pairs(am)),('native container entries lost',n)
locations={}
for k,ls in cat.keys():
 for (loc,) in cat.array(ls,'I'):locations[loc]=cat.location(loc)
seen=set();active=set()
def visit(loc):
 if loc in seen:return
 assert loc not in active,('dependency cycle',cat.location(loc)['internal'])
 active.add(loc)
 for dep in cat.location(loc)['dependencies']:visit(dep)
 active.remove(loc);seen.add(loc)
for loc in locations:visit(loc)
for guid in m['registered_custom_guids']:
 locs=cat.locations(guid);assert len(locs)==1
 loc=cat.location(locs[0]);assert loc['dependencies'];assert cat.location(loc['dependencies'][0])['type'][1].endswith('IAssetBundleResource')
# Native page additions and the four private descriptions are complete.
host=objs[W][7857044477279960178].read_typetree();hr={r['rid']:r for r in host['references']['RefIds']};v=next(r['data'] for r in hr.values() if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
titles=[x for x in v['ValueVariables'] if x['m_name'].endswith('VariantTitle')];assert len(titles)==4
identities=['PlayerOverviewFull','PlayerOverviewSimple','PlayerOverviewLeftFC','PlayerOverviewLeftPortrait']
grid=next(r['data']['Bindings'] for r in hr.values() if 'm_gridElementBindingData' in r.get('data',{}).get('Bindings',{}))
for ident in identities:assert any(x['DescriptionAndMapping']['DescriptionName']==ident for x in grid['m_gridElementBindingData'])
tile=objs[L][1332213496068314481].read_typetree()
for pid in [-930000000001004,-930000000001005,-940000000010030,-940000000012030]:
 assert {'m_FileID':0,'m_PathID':pid} in tile['m_gridElementDescriptions']
 desc=objs[L][pid].read_typetree()
 for cfg in desc['<Configurations>k__BackingField']:assert cfg['AssetRef']['m_AssetGUID'] in keys
for pid,hidden in [(-930000000001001,True),(-930000000001003,False),(-940000000010000,True),(-940000000012000,False)]:
 d=objs[W][pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};names=[r.get(x.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name') for x in r.values()]
 assert ('RightHiddenAttributesPanel' in names)==hidden
# Compare native SeasonStats bindings and card arithmetic with the approved snapshot.
oldG={o.path_id:o for o in UnityPy.load(str(SNAP/G)).objects};oldW={o.path_id:o for o in UnityPy.load(str(SNAP/W)).objects}
for pid in [-940000000007000,-940000000007002,-940000000008100,-940000000010010]:
 d=objs[W][pid].read_typetree();base=oldW[pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
 for x in base['references']['RefIds']:
  if 'UxmlSerializedData' in x.get('type',{}).get('class',''):
   # Pointers may remap; season stats' named paths and serialized numeric formatters stay unchanged.
   def paths(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if k=='m_path':yield x
      else:yield from paths(x)
    elif isinstance(v,list):
     for x in v:yield from paths(x)
   assert list(paths(x))==list(paths(r[x['rid']])),('stats paths changed',pid,x['rid'])
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['gid','check_graph','graph_runner']],type_ignores=[]),'graph validator','exec'))
for pid in list(range(-940000000000105,-940000000000099))+list(range(-940000000000204,-940000000000199)):
 if pid not in objs[G]:continue
 d=objs[G][pid].read_typetree();check_graph(d);run=graph_runner(d);oldrun=graph_runner(oldG[pid].read_typetree());count=len(d['m_inputs'])-2
 for value in [1,10,20,None]:assert run([value]*count)==oldrun([value]*count)
assert hashlib.sha256((GAME/B).read_bytes()).hexdigest()==m['background_bundle_unchanged_sha256']
audit={'verified':True,'versions':4,'validated_trees':len(validtrees),'checked_object_pointers':pointercount,'checked_guids':guidcount,'catalog_cycles':False,'native_container_entries_preserved':True,'stats_paths_and_card_calculations_preserved':True,'background_unchanged':True,'runtime_verified':False}
(OUT/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'output':str(OUT),**audit}))
