"""Prepare compact trophy display for the existing overview honours panel; no background art."""
from pathlib import Path
import sys,ast,json,copy,hashlib,datetime,struct,uuid,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
extract('build-club-overview-eight-panels.py',set())
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
SRC=Path(r'K:\桌面\FM27 Comeback Skin v1.8.3\Skin files')
ROOT=R/('club-overview-trophies-no-background-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));ROOT.mkdir()
PID=-991114000001000;SID=PID-1;GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/club-overview/compact-trophy-row/v1').hex
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
donore=UnityPy.load(str(SRC/W));donoro={o.path_id:o for o in donore.objects}
class Donor:
 def __init__(self,pid):
  self.obj=donoro[pid];self.af=self.obj.assets_file;self.d=self.obj.read_typetree();self.r=refs(self.d)
 def a(self,i):return self.r[i]['data']
dr=Donor(-5495443699739417454);db=Donor(-8436403980044243281)
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def args(items):
 a=[string(t)+v for t,v in items];return list(bytes([len(a)])+b''.join(struct.pack('<I',len(v))+v for v in a))
def listargs(path):return args([('SI.Bindable.BindingKeyVisualArg',b'\0'),('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\1'+string(path))])
def remove(d,i):
 d.a(d.a(i)['m_Parent']['rid'])['m_Children'].remove({'rid':i});drop=set()
 def visit(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    j=v['rid']
    if j!=-2 and j not in drop:drop.add(j);visit(d.r[j].get('data',{}))
   else:
    for k,x in v.items():
     if k!='m_Parent':visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
 visit({'rid':i});d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in drop];d.r=refs(d.d)
def flex(d,i):d.st(i,[(131105,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
tx=[];audits=[];protected={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 OUT=ROOT/tag;OUT.mkdir();(OUT/'templates').mkdir();backup=ROOT/('backup-'+tag);backup.mkdir()
 original=(folder/W).read_bytes();env={W:UnityPy.load(original)};objs={W:{o.path_id:o for o in env[W].objects}};changes={W:{}};documents=[]
 hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 rowold=Doc(W,name='ClubHistoryHonourCardRow');tr=copy.deepcopy(rowold.d);st=copy.deepcopy(rowold.s)
 tr['m_Name']='TFClubOverviewTrophyRow';tr['inlineSheet']['m_PathID']=SID;st['m_Name']='TFClubOverviewTrophyRowStyle'
 banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
 assert not {PID,SID}&(set(objs[W])|banned)
 for so,pid,tree in [(rowold.obj,PID,tr),(objs[W][rowold.sid],SID,st)]:
  ob=copy.copy(so);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[W][pid]=ob;ob.save_typetree(tree)
 row=Doc(W,pid=PID)
 for c in list(row.a(1001)['m_Children']):remove(row,c['rid'])
 row.nr=max(row.r)+1
 row.st(1001,[(131105,{'m_ValueType':1,'valueIndex':2}),(131097,row.px(0)),(131095,row.px(150)),(131085,row.num(0)),(131084,row.num(0))])
 won=row.add(dr,1063,1001,'TFOverviewWon');card=row.add(dr,1065,won,'TFOverviewTrophyCard')
 row.st(card,[(131105,row.px(150)),(131087,row.px(192)),(131085,row.num(0)),(131073,row.enum('center')),(131083,row.enum('column')),(131099,row.px(5)),(131100,row.px(5))])
 box=row.add(dr,1071,card,'TFOverviewTrophyImages');row.size(box,132,130);row.st(box,[(131083,row.enum('row')),(458768,row.enum('hidden'))])
 slot=row.add(dr,1073,box,'TFOverviewTrophySlot');row.st(slot,[(131083,row.enum('row')),(131087,row.px(130)),(131085,row.num(0))])
 for src,parent,name in [(1075,slot,'TFOverviewTrophy'),(1077,box,'TFOverviewCompetitionLogo')]:
  i=row.add(dr,src,parent,name);row.st(i,[(131087,row.px(130)),(131095,row.px(132)),(131085,row.num(0)),(262153,row.enum('scale-to-fit'))])
  if src==1077:row.st(i,[(131105,row.px(132))])
 name=row.add(dr,1083,card,'TFOverviewCompetitionName');row.a(name)['m_Classes']=['primary-text-colour'];row.st(name,[(131105,row.pct(100)),(131087,row.px(32)),(65537,row.px(12)),(65546,row.enum('middle-center')),(65552,row.enum('normal')),(131085,row.num(0))])
 counts=row.add(dr,1081,card,'TFOverviewWinCountLine');row.st(counts,[(131083,row.enum('row')),(131088,row.enum('center')),(131087,row.px(22)),(131085,row.num(0))])
 for src in [1089,1091]:
  i=row.add(dr,src,counts,'TFOverviewWinCount'+str(src));row.a(i)['m_Classes']=['primary-text-colour'];row.st(i,[(65537,row.px(13)),(65543,row.enum('bold')),(131085,row.num(0))])
 row.save()
 body=Doc(W,name='ClubOverviewEightPanelBody');assert body.data(1099)['Binding']['m_direct']['Path']['m_path']=='club.HistoryHonours.HistoryHonoursList'
 remove(body,1099)
 scroll=body.add(db,1007,1076,'TFOverviewTrophyScroll');flex(body,scroll);body.st(scroll,[(131087,body.px(0)),(458768,body.enum('hidden'))])
 lst=body.add(db,1015,scroll,'TFOverviewTrophies');body.data(lst)['ItemTemplate']['m_AssetGUID']=GUID;body.data(lst)['VisualFuncBinding']['m_inputs']['m_variable']['m_argumentBytes']=listargs('club.HistoryHonours.HistoryHonoursList')
 body.data(lst).update(ItemUssClassName='',NumPreviewElements=6)
 body.st(lst,[(131105,body.pct(100)),(131083,body.enum('row')),(131086,body.enum('wrap')),(131088,body.enum('center')),(131073,body.enum('flex-start')),(131085,body.num(0))]);body.save()
 # Register private row in bundle container and Addressables preload list.
 mo=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();sourceguid=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':rowold.obj.path_id})
 span=[]
 def pointers(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'}:
    if v['m_PathID'] and v not in span:span.append(copy.deepcopy(v))
   else:
    for x in v.values():pointers(x)
  elif isinstance(v,list):
   for x in v:pointers(x)
 pointers(row.d);pointers(row.s)
 for pid in [PID,SID]:
  if {'m_FileID':0,'m_PathID':pid} not in span:span.append({'m_FileID':0,'m_PathID':pid})
 meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda kv:kv[0]);mo.save_typetree(meta);changes[W][mo.path_id]=meta
 cp=(folder.parent if tag=='game' else folder)/'catalog.bin';hp=cp.with_suffix('.hash');cb=cp.read_bytes();hb=hp.read_bytes();cat=cm.Catalog(cb)
 sl=next(l for l in cat.locations(sourceguid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');cat=cm.Catalog(cat.add_key_location(GUID,sl,sl))
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+cat.locations(GUID);records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cat=cm.Catalog(bytes(cat.data))
 # Verify functions, templates, own bundle dependency, and actual preloading.
 function_ids=['7a35874b5cb0acb4d846df3f46c3a872','d52cf0b2ba55c764b9ecda52092aa257','36a81e80154fa1d4e9a3b0cdea217c5b']
 fe=UnityPy.load(str((folder if (folder/'ui-visualfunctions_assets_all.bundle').exists() else GAME)/'ui-visualfunctions_assets_all.bundle'));fo={o.path_id:o for o in fe.objects};fm=next(o.read_typetree() for o in fo.values() if o.type.name=='AssetBundle')
 for guid in function_ids:
  fl=next(cat.location(l) for l in cat.locations(guid) if cat.location(l)['type'][1]=='SI.VisualScripting.VisualFunction')
  fp=next(v['asset']['m_PathID'] for k,v in fm['m_Container'] if k==guid);assert fp in fo and fo[fp].type.name=='MonoBehaviour'
  assert fl['dependencies'] and 'ui-visualfunctions' in cat.location(fl['dependencies'][0])['internal']
 entry=cat.location(cat.locations(GUID)[0]);assert entry['type'][1]=='UnityEngine.UIElements.VisualTreeAsset';assert entry['dependencies']==cat.location(sl)['dependencies'];assert cat.locations(GUID)[0] in cat.locations('GameWorldVisualTreeAssetPreload')
 result=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(result).objects};assert set(check)==set(hashes)|{PID,SID}
 for i,h in hashes.items():
  if i not in changes[W]:assert sha(check[i].get_raw_data())==h,(tag,i)
 for i,tree in changes[W].items():assert check[i].read_typetree()==tree,(tag,i)
 for doc in [row,body]:validate_ui(check[doc.obj.path_id].read_typetree(),check[doc.sid].read_typetree())
 for target,data,old in [(folder/W,result,original),(cp,bytes(cat.data),cb),(hp,hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii'),hb)]:
  source=OUT/target.name;bp=backup/target.name;source.write_bytes(data);bp.write_bytes(old);tx.append({'target':str(target),'source':str(source),'backup':str(bp),'before':sha(old),'after':sha(data)})
 for p in folder.glob('*.bundle'):
  if p.name!=W:protected[str(p)]=sha(p.read_bytes())
 audits.append({'target':tag,'runtime_verified':False,'unrelated_objects_byte_identical':True,'no_texture_or_background_changes':True,'private_row':{'pid':PID,'style':SID,'guid':GUID},'card_size':[150,192],'function_guids':function_ids})
 print(json.dumps({'prepared':tag,'output':str(ROOT)}),flush=True)
for p in [R/'reserved-texture-ids.json',R/'current-custom-textures.json']:protected[str(p)]=sha(p.read_bytes())
manifest={'installed':False,'runtime_verified':False,'request':'Compact trophies in screenshot Club Overview honours panel, existing background retained.','audits':audits,'protected_sha256':protected}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(ROOT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (ROOT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(R/'current-club-overview-trophies.json').write_text(json.dumps({'patch':str(ROOT),'installed':False,'runtime_verified':False,'background_images':False},ensure_ascii=False,indent=2),'utf8')

