"""Give spare identity width to career stats, then sync the FC page's full layout."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'}),('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
# Reuse the tested subtree remapper, retaining the current FC outer styles too.
t=ast.parse((R/'add-approved-left-fc-hidden-overview.py').read_text('utf8'));fn=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='graft_fc')
fn.name='graft_fc_exact'
fn.body=[n for n in fn.body if not(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=='edit'and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=='st')]
exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact-fc-remapper','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PORTRAIT,PSTYLE=-941100000001020,-941100000001021
FC,FSTYLE=-941100000001060,-941100000001061
EXTRA=36
OUT=R/('approved-career-wider-fc-layout-synced-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
previous=json.loads((R/'current-player-overview-test-variant.json').read_text('utf8'))
reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
tx=[];checks=[]
def add_tx(tag,target,output,before):
 src,backup=OUT/tag/target.name,OUT/('backup-'+tag)/target.name;src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True);src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 portrait=oo[PORTRAIT].read_typetree();ps=oo[PSTYLE].read_typetree();oldps=copy.deepcopy(ps);pr=refs(portrait);pst=Styles(ps)
 def dim(node,key):
  prop=next(p for p in ps['m_Rules'][pr[node]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==key);h=prop['m_Values'][0];assert h['m_ValueType']==3
  value=ps['dimensions'][h['valueIndex']];assert value['unit']==1;return value['value']
 assert dim(1173,131105)==610 and dim(2242,131105)==300
 old_native_left=dim(1026,131089);old_divider_left=dim(6288,131089)
 old_native_width=dim(1026,131105);assert old_native_width==300
 changed_rules=set()
 for node,values in [
  (1173,[(131105,646),(131082,646)]),
  (2242,[(131105,336),(131095,336)]),
  (1026,[(131089,old_native_left+EXTRA)]),
  (6288,[(131089,old_divider_left+EXTRA)]),
 ]:
  rule=pr[node]['data']['m_RuleIndex'];assert [i for i,r in pr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
  keys={k for k,v in values};props=ps['m_Rules'][rule]['m_Properties'];ps['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+[pst.p(k,pst.px(v))for k,v in values];changed_rules.add(rule)
 assert dim(2242,131082)==249 # retain concrete host height and the old clipping fix
 assert dim(1173,131105)-dim(1026,131089)==610-old_native_left
 assert dim(1173,131105)-dim(6288,131089)==610-old_divider_left
 for i,rule in enumerate(oldps['m_Rules']):
  if i not in changed_rules:assert ps['m_Rules'][i]==rule
 fc_old=oo[FC].read_typetree();fc_old_style=oo[FSTYLE].read_typetree()
 fc=copy.deepcopy(portrait);fs=copy.deepcopy(ps)
 detail=graft_fc_exact(fc,fs,fc_old,fc_old_style)
 fc.update(m_Name=fc_old['m_Name'],inlineSheet={'m_FileID':0,'m_PathID':FSTYLE},m_ContentHash=fc_old['m_ContentHash']);fs['m_Name']=fc_old_style['m_Name']
 assert canonical(fc,fs,skip_portrait=True)==canonical(portrait,ps,skip_portrait=True)
 assert canonical(fc,fs,portrait_only=True)==canonical(fc_old,fc_old_style,portrait_only=True)
 fr=refs(fc);stage=named(fc,'ReportPortraitLayerStage')
 scaleprop=next(p for p in fs['m_Rules'][fr[stage]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==327681)
 assert [fs['floats'][h['valueIndex']]for h in scaleprop['m_Values']]==[1.0,1.0]
 graph(fc);validate_ui(fc,fs);validate_ui(portrait,ps)
 ab=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=ab.read_typetree();oldmeta=copy.deepcopy(meta)
 def entry_for(pid):return next((k,e)for k,e in meta['m_Container']if e['asset']=={'m_FileID':0,'m_PathID':pid})
 portrait_key,portrait_entry=entry_for(PORTRAIT);fc_key,fc_entry=entry_for(FC)
 span=copy.deepcopy(meta['m_PreloadTable'][fc_entry['preloadIndex']:fc_entry['preloadIndex']+fc_entry['preloadSize']])
 additions=meta['m_PreloadTable'][portrait_entry['preloadIndex']:portrait_entry['preloadIndex']+portrait_entry['preloadSize']]
 for original in additions:
  ptr=copy.deepcopy(original)
  if ptr['m_FileID']==0:ptr['m_PathID']={PORTRAIT:FC,PSTYLE:FSTYLE}.get(ptr['m_PathID'],ptr['m_PathID'])
  if ptr not in span:span.append(ptr)
 assert not any(ptr['m_PathID']in reserved for ptr in span)
 fc_entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 catpath=(root.parent if tag=='game'else root)/'catalog.bin';hashpath=catpath.with_name('catalog.hash');catbefore=catpath.read_bytes();hashbefore=hashpath.read_bytes();cat=cm.Catalog(catbefore)
 fc_loc=next(i for i in cat.locations(fc_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 portrait_loc=next(i for i in cat.locations(portrait_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 olddeps=cat.location(fc_loc)['dependencies'];deps=list(dict.fromkeys(olddeps+cat.location(portrait_loc)['dependencies']))
 assert cat.location(deps[0])['internal'].endswith(W)
 if deps!=olddeps:
  raw=b''.join(struct.pack('<I',i)for i in deps);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,fc_loc+12,offset,zlib.crc32(raw));cat=cm.Catalog(bytes(cat.data))
 assert cat.location(fc_loc)['dependencies']==deps
 assert fc_loc in cat.locations('GameWorldVisualTreeAssetPreload')
 changes={PSTYLE:ps,FC:fc,FSTYLE:fs,ab.path_id:meta}
 for i,value in changes.items():oo[i].save_typetree(value)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==oo.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,value in changes.items():assert check[i].read_typetree()==value
 # Recompare actual serialized output, including both layouts and FC scale.
 assert canonical(check[FC].read_typetree(),check[FSTYLE].read_typetree(),skip_portrait=True)==canonical(check[PORTRAIT].read_typetree(),check[PSTYLE].read_typetree(),skip_portrait=True)
 assert canonical(check[FC].read_typetree(),check[FSTYLE].read_typetree(),portrait_only=True)==canonical(fc_old,fc_old_style,portrait_only=True)
 add_tx(tag,root/W,output,before)
 catout=bytes(cat.data)
 if catout!=catbefore:
  add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashbefore)
 else:protected[str(catpath)]=sha(catbefore);protected[str(hashpath)]=sha(hashbefore)
 checks.append(dict(target=tag,career_width_before=300,career_width_after=336,width_reallocated_from_identity=EXTRA,
  overall_header_right_width=646,original_ability_radar_screen_position_and_width_preserved=True,
  portrait_page_data_and_bindings_byte_identical=True,
  fc_non_portrait_layout_canonical_equal_to_latest_portrait=True,
  fc_card_canonical_equal_to_previous_fc=True,fc_card_scale=1,
  fc_career_and_lower_radar_preload_and_dependency_closure_verified=True,
  selector_titles_saved_selection_and_old_variants_unchanged=True,unrelated_objects_byte_identical=True))
 print('Verified '+tag+': career 336px; FC layout synchronized with exact existing card',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],checks=checks,protected_sha256=protected,change='Allocate 36px identity spare width to career statistics and synchronize FC layout with latest portrait, retaining the exact current FC card',fc_layout_synced_to_latest_portrait=True)
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'career-wider-fc-synced-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
