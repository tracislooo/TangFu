from pathlib import Path
import sys,ast,copy,json,struct,hashlib,datetime,importlib.util
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
oldwrite=TypeTreeHelper.write_value
helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
sha=lambda b:hashlib.sha256(b).hexdigest()
before={p/n:(p/n).read_bytes() for p in [GAME,SKIN] for n in [W,G]};outputs={};audits=[]
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name not in [W,G]}
for folder in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:
  p=folder/n
  if p.exists():protected[p]=sha(p.read_bytes())
for folder in [GAME,SKIN]:
 envs={n:UnityPy.load(before[folder/n]) for n in [W,G]};oo={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};expected={W:{},G:{}};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in oo.items()}
 def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
 def size(st,r,w,h):st.edit(r,[st.p(k,st.px(v)) for k,v in [(131105,w),(131097,w),(131095,w),(131087,h),(131096,h),(131094,h)]])
 # Reuse the current horizontal row, including its 14 native side-preference tooltips.
 o=oo[G][-960000000003040];prior=o.read_typetree();row=copy.deepcopy(oo[G][-940000000018000].read_typetree());style=copy.deepcopy(oo[G][row['inlineSheet']['m_PathID']].read_typetree());row['m_Name']=prior['m_Name'];row['inlineSheet']=prior['inlineSheet'];style['m_Name']='TooltipHorizontalPositionZones_Style';rr=refs(row);st=Styles(style)
 assert sum(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.Tooltip' for r in rr.values())==14
 for r in rr.values():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
  if r['rid'] in [1001,1002,1004] or name.startswith('PositionZoneMaskAbove'):st.box(r,0,0,400,200)
 for rule in style['m_Rules']:
  if 'fm27-position-item-root' in str(rule.get('m_ComplexSelectors')):
   keys={131105:400,131097:400,131095:400,131087:200,131096:200,131094:200};rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id'] not in keys]+[st.p(k,st.px(v)) for k,v in keys.items()]
 save(G,o,row);save(G,oo[G][row['inlineSheet']['m_PathID']],style)
 o=oo[G][-960000000003030];d=o.read_typetree();rr=refs(d);so=oo[G][d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 size(st,rr[1001],400,200);st.box(rr[2014],0,0,400,200);rr[rr[2014]['data']['m_SerializedData']['rid']]['data']['AspectRatio']=2.
 for rid in [1022,1023,2018]:st.box(rr[rid],0,0,400,200)
 shapes={'BlackPitchLine_Outline':(1,1,98,98),'BlackPitchLine_Halfway':(50,1,0,98),'BlackPitchLine_CentreCircle':(42.5,35,15,30),'BlackPitchLine_TopPenaltyArea':(1,28,16,44),'BlackPitchLine_BottomPenaltyArea':(83,28,16,44),'BlackPitchLine_TopGoalArea':(1,40,6,20),'BlackPitchLine_BottomGoalArea':(93,40,6,20)}
 for r in rr.values():
  name=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
  if name in shapes:
   x,y,w,h=shapes[name];st.edit(r,[st.p(k,st.pct(v)) for k,v in zip([131089,131104,131105,131087],[x,y,w,h])])
 save(G,o,d);save(G,so,s)
 # Merge current source-row preload references into the private row/pitch registrations.
 ab=next(o for o in oo[G].values() if o.type.name=='AssetBundle');meta=ab.read_typetree();src=next(v for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':-940000000018000});span=meta['m_PreloadTable'][src['preloadIndex']:src['preloadIndex']+src['preloadSize']]
 for k,v in meta['m_Container']:
  if v['asset']['m_PathID'] not in [-960000000003040,-960000000003030] or v['asset']['m_FileID']:continue
  entries=copy.deepcopy(meta['m_PreloadTable'][v['preloadIndex']:v['preloadIndex']+v['preloadSize']])
  for p in span:
   if p not in entries:entries.append(copy.deepcopy(p))
  v.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(entries));meta['m_PreloadTable'].extend(entries)
 save(G,ab,meta)
 for pid,body,canvas,viewport in [(-3760232355926433866,120002,120002,1010),(-498859349613660051,120002,120002,70007),(-1857952619964471988,100000,80013,120002)]:
  o=oo[W][pid];d=o.read_typetree();rr=refs(d);so=oo[W][d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  def named(name):
   found=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name];assert len(found)==1,name;return found[0]
  # Original card remains 400x596. Remove the middle column, shifting right content 200px left.
  for name,x,y,w,h in [('Fixed_FCPlayerCard',12,12,400,596),('Fixed_VerticalPositionPitch',12,620,400,200),('Fixed_PlayerHeader',426,12,694,64),('Fixed_SmallAttributes',426,88,694,380),('Fixed_CoachScoutReport',426,480,272,128),('Fixed_PlayerMood',710,480,136,128),('Fixed_PlayerPosition',858,480,262,128),('RightPanelBackground',12,12,1118,808),('PopupPanelOutline_Pitch',12,620,400,200),('PopupPanelOutline_Attributes',12,12,1118,808)]:st.box(named(name),x,y,w,h)
  size(st,rr[body],1142,832)
  if pid==-1857952619964471988:
   size(st,rr[80017],1142,832);size(st,rr[canvas],1142,888)
  size(st,rr[viewport],f32(1142*.85),f32((888 if pid==-1857952619964471988 else 832)*.85))
  save(W,o,d);save(W,so,s)
 for n,e in envs.items():
  b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo[n])
  for i,o in check.items():
   if i in expected[n]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[n][i],sort_keys=True),(n,i)
   else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
  outputs[folder/n]=b
 audits.append({'target':str(folder),'modified_objects':{n:list(expected[n]) for n in [W,G]},'native_position_tooltips':14})
# No textures or IDs created. All current image bundles, catalog files and other bundles stay byte-identical.
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('stacked-popup-horizontal-pitch-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 dst=out/('backup-'+tag);dst.mkdir()
 for n in [W,G]:(dst/n).write_bytes(before[folder/n])
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'design_size':[1142,832],'display_size':[970.7,707.2],'click_shell_display_size':[970.7,754.8],'card_size_preserved':[400,596],'pitch_design_size':[400,200],'pitch_display_size':[340,170],'whole_popup_background':True,'all_three_routes':True,'audits':audits,'main_pages_and_all_texture_bundles_unchanged':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
