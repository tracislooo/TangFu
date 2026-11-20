"""Set the private Club Overview honours cards to three responsive columns."""
import ast,copy,datetime,hashlib,json,sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
for file,names in [('add-card-six-ratings.py',{'write','validate_ui'}),('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'}),('build-club-stadium-overlay-local.py',{'stage'})]:
 for n in ast.parse((R/file).read_text('utf8')).body:
  if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names:exec(compile(ast.Module([n],[]),file,'exec'),globals())
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
out=R/('club-trophies-three-columns-'+datetime.datetime.now(ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[];audits=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 path=folder/W;before=path.read_bytes();env=UnityPy.load(before);af=env.assets[0];objs={W:af.objects}
 row=Doc(W,pid=-991114000001000)
 baseline_tree=copy.deepcopy(row.d)
 row.st(1001,[(131105,row.pct(33.33333206176758)),(131095,row.pct(33.33333206176758)),(131097,row.px(0)),(131084,row.num(0)),(131085,row.num(0))])
 row.st(row.named('TFOverviewWon'),[(131105,row.pct(100)),(131097,row.px(0))])
 row.st(row.named('TFOverviewTrophyCard'),[(131105,row.pct(100)),(131097,row.px(0)),(131087,row.px(164))])
 imagebox=row.named('TFOverviewTrophyImages')
 row.st(imagebox,[(131105,row.pct(100)),(131097,row.px(0)),(131095,row.px(110)),(131087,row.px(110)),(131096,row.px(110)),(131094,row.px(110)),(131074,row.enum('center'))])
 for name in ['TFOverviewTrophySlot','TFOverviewTrophy','TFOverviewCompetitionLogo']:
  row.st(row.named(name),[(131105,row.pct(100)),(131097,row.px(0)),(131095,row.px(110)),(131087,row.px(110)),(131096,row.px(0)),(131085,row.num(1)),(262153,row.enum('scale-to-fit'))])
 row.st(row.named('TFOverviewCompetitionName'),[(65537,row.px(11)),(131087,row.px(32))])
 validate_ui(row.d,row.s)
 oldrefs={r['rid']:r for r in baseline_tree['references']['RefIds']}
 for rid,ref in oldrefs.items():
  actual=copy.deepcopy(row.r[rid])
  if 'm_RuleIndex' in ref.get('data',{}):actual['data']['m_RuleIndex']=ref['data']['m_RuleIndex']
  assert actual==ref
 # Reuse the complete current player honours branch on the AI club page.
 branch=next(n for n in ast.walk(ast.parse((R/'refine-club-footer-budgets-transfers.py').read_text('utf8'))) if isinstance(n,ast.FunctionDef) and n.name=='import_branch')
 exec(compile(ast.Module([branch],[]),'branch','exec'),globals())
 body=Doc(W,name='ClubSiteBlock')
 player=Doc(W,pid=-991100000000060)
 upper=body.add(body,1018,1018,'AIClubCompactTransferHistory')
 body.a(upper)['m_Classes']=[]
 for rid in [1033,1034]:body.move(rid,upper)
 def half(rid):
  body.st(rid,[(131083,body.enum('column')),(131105,body.pct(100)),(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(458768,body.enum('hidden'))])
 half(upper)
 mapping=import_branch(body,player,1052,1018)
 honours=mapping[1052]
 half(honours)
 body.st(honours,[(131098,body.px(8)),(131099,body.px(0))])
 body.st(1018,[(131083,body.enum('column'))])
 for rid in [1034,1061]:
  body.st(rid,[(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1))])
 body.st(1061,[(131083,body.enum('row'))])
 for rid in [1082,1083]:
  body.st(rid,[(131105,body.px(0)),(131097,body.px(0)),(131087,body.pct(100)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(131098,body.px(0))])
 body.st(1082,[(131090,body.px(6))])
 body.st(1083,[(131093,body.px(6))])
 for rid in [1108,1111]:
  body.st(rid,[(131087,body.px(0)),(131096,body.px(0)),(131084,body.num(1)),(131085,body.num(1))])
 # Preserve the native filter separator above both transfer lists.
 validate_ui(body.d,body.s)
 original_body=Doc(W,name='ClubSiteBlock')
 for rid,ref in original_body.r.items():
  if 'uxmlAssetId' in ref.get('data',{}):assert body.r[rid]==ref
 meta_obj=next(o for o in af.objects.values() if o.type.name=='AssetBundle')
 meta=meta_obj.read_typetree()
 donor_entry=next(e for k,e in meta['m_Container'] if e['asset']=={'m_FileID':0,'m_PathID':player.obj.path_id})
 donor_span=meta['m_PreloadTable'][donor_entry['preloadIndex']:donor_entry['preloadIndex']+donor_entry['preloadSize']]
 for key,entry in meta['m_Container']:
  if entry['asset']!={'m_FileID':0,'m_PathID':body.obj.path_id}:continue
  start=entry['preloadIndex'];span=list(meta['m_PreloadTable'][start:start+entry['preloadSize']])
  for pointer in donor_span:
   if pointer not in span:span.append(pointer)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span))
  meta['m_PreloadTable'].extend(span)
 hashes={pid:sha(o.get_raw_data()) for pid,o in af.objects.items()}
 changes={row.obj.path_id:row.d,row.sid:row.s,body.obj.path_id:body.d,body.sid:body.s,meta_obj.path_id:meta}
 for pid,data in changes.items():af.objects[pid].save_typetree(data)
 after=env.file.save(packer='lz4');check=UnityPy.load(after).assets[0].objects
 assert set(check)==set(hashes)
 for pid,obj in check.items():
  if pid in changes:assert obj.read_typetree()==changes[pid]
  else:assert sha(obj.get_raw_data())==hashes[pid]
 stage(tag,path,before,after)
 audits.append({'target':tag,'columns':3,'card_width_percent':33.3333,'image_max_width':110,'image_height':110,'ai_transfers':'upper half, in/out horizontal','ai_honours':'lower half, current player honours module','bindings_unchanged':True,'unrelated_objects_byte_identical':True})
for name,value in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},audit=audits))]:
 (out/(name+'.json')).write_text(json.dumps(value,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
