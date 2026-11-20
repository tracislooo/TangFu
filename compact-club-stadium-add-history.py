"""Compact live stadium details and append the native league history chart."""
import ast,copy,datetime,hashlib,json,sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
for file,names in [('add-card-six-ratings.py',{'write','validate_ui'}),('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'}),('build-club-stadium-overlay-local.py',{'stage'})]:
 for node in ast.parse((R/file).read_text('utf8')).body:
  if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
   exec(compile(ast.Module([node],[]),file,'exec'),globals())
node=next(n for n in ast.walk(ast.parse((R/'refine-club-footer-budgets-transfers.py').read_text('utf8'))) if isinstance(n,ast.FunctionDef) and n.name=='import_branch')
exec(compile(ast.Module([node],[]),'branch','exec'),globals())
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
out=R/('club-stadium-compact-history-'+datetime.datetime.now(ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[];audit=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 path=folder/W;before=path.read_bytes();env=UnityPy.load(before);af=env.assets[0];objs={W:af.objects}
 stadium=Doc(W,pid=-991100000000030);native=Doc(W,name='ClubSiteBlock')
 original=copy.deepcopy(stadium.d)
 right=stadium.named('TFClubLocationStadiumRight')
 stadium.st(1012,[(131087,stadium.px(156)),(131096,stadium.px(156)),(131094,stadium.px(156)),(131084,stadium.num(0)),(131085,stadium.num(0)),(131098,stadium.px(6))])
 stadium.st(1016,[(131087,stadium.pct(100)),(131096,stadium.px(0)),(131084,stadium.num(1)),(131085,stadium.num(1))])
 for rid in [1023,1025,1027,1028,1033,1034]:
  stadium.st(rid,[(131087,stadium.px(26)),(131096,stadium.px(26)),(131094,stadium.px(26)),(131084,stadium.num(0)),(131085,stadium.num(0))])
 mapping=import_branch(stadium,native,1051,right)
 history=mapping[1051]
 stadium.data(history).update(name='ClubStadiumNativeLeagueHistory',name_UxmlAttributeFlags=1)
 stadium.st(history,[(131105,stadium.pct(100)),(131087,stadium.px(0)),(131096,stadium.px(120)),(131084,stadium.num(1)),(131085,stadium.num(1)),(131098,stadium.px(8)),(458768,stadium.enum('hidden'))])
 for source_id in [1073,1094]:
  stadium.st(mapping[source_id],[(131087,stadium.px(0)),(131096,stadium.px(0)),(131105,stadium.pct(100)),(131084,stadium.num(1)),(131085,stadium.num(1))])
 stadium.st(mapping[1073],[(458752,stadium.val(4,dict(r=0.,g=0.,b=0.,a=0.))),(262151,stadium.px(0)),(262148,stadium.px(0))])
 stadium.st(mapping[1093],[(131087,stadium.px(22)),(131096,stadium.px(22)),(131084,stadium.num(0)),(131085,stadium.num(0))])
 stadium.st(mapping[1118],[(65537,stadium.px(12)),(131098,stadium.px(0)),(131099,stadium.px(0))])
 stadium.st(mapping[1120],[(131105,stadium.pct(100)),(131087,stadium.pct(100)),(131096,stadium.px(0)),(131084,stadium.num(1)),(131085,stadium.num(1))])
 assert stadium.a(right)['m_Children'][-1]=={'rid':history}
 for source_id,target_id in mapping.items():
  if 'uxmlAssetId' not in native.r[source_id].get('data',{}):continue
  expected=copy.deepcopy(native.r[source_id]['data']);actual=copy.deepcopy(stadium.r[target_id]['data'])
  actual['uxmlAssetId']=expected['uxmlAssetId']
  if source_id==native.a(1051)['m_SerializedData']['rid']:
   actual['name']=expected['name'];actual['name_UxmlAttributeFlags']=expected['name_UxmlAttributeFlags']
  assert actual==expected,source_id
 oldrefs={r['rid']:r for r in original['references']['RefIds']}
 for rid,ref in oldrefs.items():
  if 'uxmlAssetId' in ref.get('data',{}):assert stadium.r[rid]==ref
 validate_ui(stadium.d,stadium.s)
 meta_obj=next(o for o in af.objects.values() if o.type.name=='AssetBundle');meta=meta_obj.read_typetree()
 donor=next(e for k,e in meta['m_Container'] if e['asset']=={'m_FileID':0,'m_PathID':native.obj.path_id})
 donor_span=meta['m_PreloadTable'][donor['preloadIndex']:donor['preloadIndex']+donor['preloadSize']]
 for key,entry in meta['m_Container']:
  if entry['asset']!={'m_FileID':0,'m_PathID':stadium.obj.path_id}:continue
  start=entry['preloadIndex'];span=list(meta['m_PreloadTable'][start:start+entry['preloadSize']])
  for pointer in donor_span:
   if pointer not in span:span.append(pointer)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 changes={stadium.obj.path_id:stadium.d,stadium.sid:stadium.s,meta_obj.path_id:meta}
 baseline={pid:sha(o.get_raw_data()) for pid,o in af.objects.items()}
 for pid,data in changes.items():af.objects[pid].save_typetree(data)
 after=env.file.save(packer='lz4');check=UnityPy.load(after).assets[0].objects
 assert set(check)==set(baseline)
 for pid,obj in check.items():
  if pid in changes:assert obj.read_typetree()==changes[pid]
  else:assert sha(obj.get_raw_data())==baseline[pid]
 stage(tag,path,before,after)
 audit.append(dict(target=tag,rows=6,row_height=26,details_height=156,native_history_branch=1051,history_data='Club.LeagueHistory',original_stadium_bindings_unchanged=True,unrelated_objects_byte_identical=True))
for name,value in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},audit=audit))]:
 (out/(name+'.json')).write_text(json.dumps(value,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
