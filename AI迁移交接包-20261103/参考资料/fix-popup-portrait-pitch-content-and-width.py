from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';S='ui-styles_assets_default.bundle'
ROW,STYLE=-960000000003040,-960000000003041
ROWGUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/TooltipPortraitFourteenPositionZones/v1').hex
PORTRAIT_GUID='98e3c5afceff4db439eb6ddd69e3e387'
sha=lambda b:hashlib.sha256(b).hexdigest()
before={p/n:(p/n).read_bytes() for p in [GAME,SKIN] for n in [W,G,S]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n],n
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:before[p]=p.read_bytes()
assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};obs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in obs.items()};expected={W:{},G:{}}
oldwrite=TypeTreeHelper.write_value
helpers=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def serial(rs,i):return rs[rs[i]['data']['m_SerializedData']['rid']]['data']
def named(bundle,name):
 a=[o for o in obs[bundle].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name];assert len(a)==1,name
 return a[0]
def save(bundle,o,d):o.save_typetree(d);expected[bundle][o.path_id]=copy.deepcopy(d)
def clone(bundle,source,pid,d):
 assert pid not in obs[bundle]
 o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;save(bundle,o,d)
def value(s,n,key):
 p=next((p for p in s['m_Rules'][n['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==key),None)
 if p is None:return None
 h=p['m_Values'][0]
 return s['dimensions'][h['valueIndex']]['value'] if h['m_ValueType']==3 else None
def node(rs,name):
 a=[r for r in rs.values() if rs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name];assert len(a)==1,name
 return a[0]
f32=lambda v:struct.unpack('<f',struct.pack('<f',float(v)))[0]

# Private row: rotate the actual fourteen horizontal zones into three columns/six bands.
row_source=named(G,'OverviewFourteenPositionRectangleRow');row=row_source.read_typetree();rs=refs(row)
style_source=obs[G][row['inlineSheet']['m_PathID']];style=style_source.read_typetree();st=Styles(style)
row['m_Name']='TooltipPortraitFourteenPositionZones';row['inlineSheet']={'m_FileID':0,'m_PathID':STYLE}
style['m_Name']='TooltipPortraitFourteenPositionZones_Style'
zones={}
for r in rs.values():
 a=r.get('data',{});sd=rs.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if a.get('m_FullTypeName')!='SI.Bindable.SIButton' or not name.startswith('PositionZone_'):continue
 x,y,w,h=[value(style,r,key) for key in [131089,131104,131105,131087]]
 assert all(v is not None for v in [x,y,w,h])
 nx,ny,nw,nh=y,100-x-w,h,w
 st.edit(r,[st.p(131089,st.pct(f32(nx))),st.p(131104,st.pct(f32(ny))),st.p(131105,st.pct(f32(nw))),st.p(131087,st.pct(f32(nh)))])
 zones[name.removeprefix('PositionZone_')]=[nx,ny,nw,nh]
assert len(zones)==14
assert zones['GK'][0]==0 and abs(zones['GK'][1]-100*5/6)<.001 and zones['GK'][2]==100
assert abs(zones['ST'][1])<.001 and zones['ST'][2]==100
assert zones['DL'][0]<zones['DR'][0]
clone(G,row_source,ROW,row);clone(G,style_source,STYLE,style)

# Recover the lost external stylesheet attachment, which gives generated item roots size.
pitchobj=named(G,'TooltipVerticalPositionPitch');pitch=pitchobj.read_typetree();pr=refs(pitch)
pso=obs[G][pitch['inlineSheet']['m_PathID']];ps=pso.read_typetree();pst=Styles(ps)
pr[2014]['data']['m_Stylesheets']=[{'m_FileID':0,'m_PathID':STYLE}]
serial(pr,2018)['ItemTemplate']['m_AssetGUID']=ROWGUID
assert serial(pr,2018)['ItemUssClassName']=='fm27-position-item-root'
serial(pr,2014)['AspectRatio']=.5
pst.box(pr[2014],0,98,200,400)
image=serial(pr,1022)
args=image['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']
raw=bytes(args);old=b'de4347c150b35ea49bcdb90a30c85d09';assert raw.count(old)==1
image['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw.replace(old,PORTRAIT_GUID.encode()))
image['PlaceholderImagePath']='Assets/UIAssets/Textures/PitchFlatGreen.png'
pr[1022]['data']['m_Classes']=[]
pst.box(pr[1022],0,0,200,400)
serial(pr,1023)['Orientation']=0;serial(pr,1023)['Orientation_UxmlAttributeFlags']=1
serial(pr,1023)['FlipPositions']=0;serial(pr,1023)['FlipPositions_UxmlAttributeFlags']=1
assert all(pr[i]['data']['m_Parent']=={'rid':2014} for i in [1022,1023,2018])
assert serial(pr,2018)['VisualFuncBinding']['m_inputs']==refs(pitchobj.read_typetree())[2019]['data']['VisualFuncBinding']['m_inputs']
save(G,pitchobj,pitch);save(G,pso,ps)

# Shrink the complete right side by a further 50px and contract the overall width.
regions={'Fixed_PlayerHeader':(626,12,694,64),'Fixed_SmallAttributes':(626,88,694,380),
 'Fixed_CoachScoutReport':(626,480,272,128),'Fixed_PlayerMood':(910,480,136,128),
 'Fixed_PlayerPosition':(1058,480,262,128),'RightPanelBackground':(626,12,694,596)}
for name in ['PlayerReportPreviewTooltip','PlayerCellInMatch','MatchPlayerReport']:
 o=named(W,name);d=o.read_typetree();rr=refs(d);so=obs[W][d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 for r in rr.values():
  a=r.get('data',{})
  if a.get('m_RuleIndex',-1)<0:continue
  props=[st.p(key,st.px(1342)) for key in [131105,131097,131095] if value(s,r,key)==1392]
  if props:st.edit(r,props)
  sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if sd.get('name')=='FixedPlayerPreview1392x620':sd['name']='FixedPlayerPreview1342x620'
 for label,(x,y,w,h) in regions.items():
  n=node(rr,label);st.box(n,x,y,w,h);st.edit(n,[st.p(131095,st.px(w)),st.p(131094,st.px(h))])
 save(W,o,d);save(W,so,s)

# Register only the private portrait row, preserving the existing native/main-page row.
bundle=next(o for o in obs[G].values() if o.type.name=='AssetBundle');meta=bundle.read_typetree()
sourcekey=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':row_source.path_id})
span=[row['m_Script'],style['m_Script'],{'m_FileID':0,'m_PathID':ROW},{'m_FileID':0,'m_PathID':STYLE}]
meta['m_Container'].append((ROWGUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':ROW}}));meta['m_PreloadTable'].extend(copy.deepcopy(span))
for k,entry in meta['m_Container']:
 if entry['asset']!={'m_FileID':0,'m_PathID':pitchobj.path_id}:continue
 span0=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for p in span:
  if p not in span0:span0.append(copy.deepcopy(p))
 entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span0));meta['m_PreloadTable'].extend(span0)
meta['m_Container'].sort(key=lambda e:e[0]);save(G,bundle,meta)
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=oldcat.locations(sourcekey)[0];cat=cm.Catalog(oldcat.add_key_location(ROWGUID,loc,loc))
idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx]
locs=[p[0] for p in cat.array(ls,'I')]+cat.locations(ROWGUID);records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True))
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catout=bytes(cat.data);cat=cm.Catalog(catout)
assert cat.location(cat.location(cat.locations(PORTRAIT_GUID)[0])['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-textures_assets_all.bundle')

# Remove two invalid value types from our transparent-popup rule, reported in Player.log.
style_outputs={}
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/S]);os={o.path_id:o for o in e.objects};hs={i:sha(o.get_raw_data()) for i,o in os.items()}
 o=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');d=o.read_typetree();st=Styles(d)
 rules=[r for r in d['m_Rules'] if 'tf27-fc-preview-transparent' in str(r['m_ComplexSelectors'])];assert len(rules)==1
 for p in rules[0]['m_Properties']:
  if p['m_Id']==458753:p['m_Values']=[{'m_ValueType':1,'valueIndex':3}]
  if p['m_Id']==262146:p['m_Values']=[st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})]
 o.save_typetree(d);b=e.file.save(packer='lz4');check={a.path_id:a for a in UnityPy.load(b).objects}
 for i,a in check.items():
  if i==o.path_id:assert json.dumps(a.read_typetree(),sort_keys=True)==json.dumps(d,sort_keys=True)
  else:assert sha(a.get_raw_data())==hs[i]
 style_outputs[folder/S]=b

# Read back all modified objects, preserving main profile, shared row and FC card bytes.
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(obs[n])|set(expected[n])
 for i,o in check.items():
  if i in expected[n]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[n][i],sort_keys=True),(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
assert -940000000010020 not in expected[G] and row_source.path_id not in expected[G] and style_source.path_id not in expected[G]
assert -960000000003010 not in expected[W]
newkeys=dict(cat.keys());added=cat.locations(ROWGUID)
for key,locset in oldcat.keys():
 oldlocs=[p[0] for p in oldcat.array(locset,'I')];newlocs=[p[0] for p in cat.array(newkeys[key],'I')]
 assert newlocs==oldlocs+(added if key=='GlobalVisualTreeAssetPreload' else [])
 for p in oldlocs:assert oldcat.location(p)==cat.location(p)

out=R/('popup-portrait-content-fix-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for n in [W,G,S]:(backup/n).write_bytes(before[folder/n])
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';(backup/'catalog.bin').write_bytes(before[cp])
(out/'backup-game'/'catalog.hash').write_bytes(before[GAME.parent/'catalog.hash'])
install={folder/n:b for folder in [GAME,SKIN] for n,b in outputs.items()};install.update(style_outputs)
hashout=hashlib.md5(catout).hexdigest().encode('ascii');install.update({GAME.parent/'catalog.bin':catout,SKIN/'catalog.bin':catout,GAME.parent/'catalog.hash':hashout})
for p,b in before.items():assert p.read_bytes()==b
try:
 for p,b in install.items():p.write_bytes(b)
 for p,b in install.items():assert p.read_bytes()==b
except BaseException:
 for p in install:p.write_bytes(before[p])
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'size':[1342,620],'right_width':694,'pitch_size':[200,400],
 'pitch_background':'PitchFlatGreen (128x256 native portrait)','row_guid':ROWGUID,'zone_positions':zones,
 'content_fix':'attach private row stylesheet at the pitch fitter; generated item roots fill the pitch',
 'regions':regions,'main_page_and_shared_position_row_unchanged':True,'transparent_style_value_types_corrected':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True,indent=2))
