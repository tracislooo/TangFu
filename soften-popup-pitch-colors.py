from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BG='ui-backgrounds_assets_common.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
before={p/G:(p/G).read_bytes() for p in [GAME,SKIN]}
assert before[GAME/G]==before[SKIN/G],'Game and skin Global bundles differ; inspect separately.'
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in [folder/W,folder/BG,folder/'ui-textures_assets_all.bundle',folder/'catalog.bin' if folder==SKIN else GAME.parent/'catalog.bin'] if p.exists()}
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
reserved_ids={int(x['path_id']) for x in reserved};reserved_names={x['name'].lower() for x in reserved}
e=UnityPy.load(before[GAME/G]);obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
assert reserved_ids.isdisjoint(obs)
oldwrite=TypeTreeHelper.write_value
h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<style-helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
expected={}
pitchobj=obs[-960000000003030];pitch=pitchobj.read_typetree();pr=refs(pitch)
pso=obs[pitch['inlineSheet']['m_PathID']];ps=pso.read_typetree();pst=Styles(ps)
rowobj=obs[-960000000003040];row=rowobj.read_typetree();rr=refs(row)
rso=obs[row['inlineSheet']['m_PathID']];rs=rso.read_typetree();rst=Styles(rs)
oldpitch=copy.deepcopy(pitch);oldrow=copy.deepcopy(row)
fills=[]
for r in rr.values():
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if not sd.get('name','').startswith('PositionZoneColourFill_'):continue
 rule=rs['m_Rules'][a['m_RuleIndex']]
 p=next(p for p in rule['m_Properties'] if p['m_Id']==458767)
 assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==2
 assert abs(rs['floats'][p['m_Values'][0]['valueIndex']]-.38)<.00001
 rst.edit(r,[rst.p(458767,rst.num(.266))]);fills.append(r['rid'])
assert len(fills)==14
# A solid slate under the native pitch image changes the field hue without new textures.
# Only the image fades; the aptitude layer, numbers and selection borders stay untouched.
backdrop={'r':f32(32/255),'g':f32(48/255),'b':f32(75/255),'a':1.0}
pst.edit(pr[2014],[pst.p(458752,pst.h(4,backdrop))])
pst.edit(pr[1022],[pst.p(458767,pst.num(.30))])
pitchcheck=copy.deepcopy(pitch)
for rid in [2014,1022]:refs(pitchcheck)[rid]['data']['m_RuleIndex']=refs(oldpitch)[rid]['data']['m_RuleIndex']
assert pitchcheck==oldpitch,'Style edits must not alter pitch bindings or nodes.'
for rid,r in refs(oldrow).items():
 changed=copy.deepcopy(rr[rid])
 if rid in fills:changed['data']['m_RuleIndex']=r['data']['m_RuleIndex']
 assert changed==r,('Unexpected row change',rid)
for obj,d in [(pitchobj,pitch),(pso,ps),(rowobj,row),(rso,rs)]:
 if d!=obj.read_typetree():obj.save_typetree(d);expected[obj.path_id]=copy.deepcopy(d)
assert set(expected)=={-960000000003030,-960000000003031,-960000000003040,-960000000003041}
outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects}
assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
 else:assert sha(o.get_raw_data())==hashes[i],i
# Catalog audit covers actual custom VTA and VisualFunction entries, both installations.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
audits=[]
for folder in [GAME,SKIN]:
 catpath=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';cat=cm.Catalog(catpath.read_bytes());count=0
 for bn,en in [(G,e),(W,UnityPy.load(str(folder/W)))]:
  oo={o.path_id:o for o in en.objects};meta=next(o.read_typetree() for o in en.objects if o.type.name=='AssetBundle')
  for guid,entry in meta['m_Container']:
   if len(guid)!=32 or any(c not in '0123456789abcdef' for c in guid) or entry['asset']['m_FileID']!=0:continue
   obj=oo.get(entry['asset']['m_PathID'])
   if obj is None or obj.type.name!='MonoBehaviour' or not (-1000000000000000<obj.path_id<-900000000000000):continue
   d=obj.read_typetree();kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in d else None
   if kind is None:continue
   for loc in cat.locations(guid):
    location=cat.location(loc);assert location['type'][1]==kind,(guid,location)
    assert location['internal']==guid and location['dependencies'],guid
    owner=cat.location(location['dependencies'][0])['internal'].replace('\\','/');assert owner.endswith('/'+bn),(guid,owner)
    if guid=='64033a72b9925c8dad3b08826077c328':
     assert any(cat.location(x)['internal'].replace('\\','/').endswith('/'+BG) for x in location['dependencies']),guid
   count+=1
 audits.append({'catalog':str(catpath),'actual_custom_vta_and_functions_checked':count})
# The retired images and all active custom images remain untouched and correctly registered.
be=UnityPy.load(str(GAME/BG));bo={o.path_id:o for o in be.objects};bm=next(o.read_typetree() for o in be.objects if o.type.name=='AssetBundle')
assert reserved_ids.isdisjoint(bo)
assert all(o.peek_name().lower() not in reserved_names for o in be.objects if o.type.name=='Texture2D')
assert all(k.lower() not in reserved_names and v['asset']['m_PathID'] not in reserved_ids for k,v in bm['m_Container'])
assert all(p['m_PathID'] not in reserved_ids for p in bm['m_PreloadTable'])
active=json.loads((R/'current-custom-textures.json').read_text('utf8'))['textures'];assert len(active)==173
assert all(int(t['path_id']) in bo and bo[int(t['path_id'])].peek_name()==t['name'] for t in active)
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('popup-pitch-colors-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/G])
(out/G).write_bytes(outbytes)
docpath=R/'球员弹窗最终版本说明.md';snpath=R/'球员弹窗最终版本资源快照.json'
for p in [docpath,snpath]:(out/p.name).write_bytes(p.read_bytes())
snapshot=json.loads(snpath.read_text('utf8'))
for a in snapshot['assets']:
 if a['bundle']!=G:continue
 obj=check[a['path_id_reference_only']];d=obj.read_typetree();a['tree']=d
 a['inline_style']=check[d['inlineSheet']['m_PathID']].read_typetree()
snapshot.update(recorded_date='2026-10-27',revision='200x327 portrait pitch; aptitude fill opacity 26.6%; slate pitch backdrop #20304B with native lines at 30%; 694px right panel; 1342x620 popup',runtime_verified=False)
snapshot['bundles'][G]=sha(outbytes)
snapshot['pitch_colors']={'zone_fill_opacity':.266,'field_backdrop_hex':'#20304B','native_pitch_image_opacity':.30,'approximate_flat_field_hex':'#1A3646','numbers_borders_click_bindings_unchanged':True}
note='''

## 2026-10-27 弹窗球场底色调整

- 弹窗专用 `TooltipPortraitFourteenPositionZones` 的14个 `PositionZoneColourFill_*` 节点：仅将底色层 opacity（458767）从0.38改为0.266，相对降低30%。不要修改整个位置按钮或父节点的opacity，以免影响数字和边框。
- `TooltipVerticalPositionPitch` 的球场框（2014）使用深蓝灰背景 `#20304B`；其原生 `PitchFlatGreen` 图片（1022）opacity为0.30，叠加后场地平坦区域约 `#1A3646`，保留原场地线条。框外区域仍透明，不改共享纹理。
- 球场保持200×327px、垂直居中；数字、熟练度颜色绑定、普通边框、选中边框和点击事件均保持原样。三类弹窗共用同一模块，球员主页面不受本次修改影响。
- 实现脚本：`soften-popup-pitch-colors.py`。同步游戏和皮肤Global包，核对现存自定义VTA／VisualFunction目录类型、实际对象、所属包首项依赖及卡面背景跨包依赖；不修改catalog、背景图片包或禁用图片清单。
- 文件读回校验通过；本次配色的游戏内效果待重启确认。
'''
for p,b in before.items():assert p.read_bytes()==b
for p,hsh in protected.items():assert sha(p.read_bytes())==hsh,p
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
 snpath.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),'utf8')
 docpath.write_text(docpath.read_text('utf8')+note,'utf8')
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 for p in [docpath,snpath]:p.write_bytes((out/p.name).read_bytes())
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'zone_fill_opacity':.266,'zone_fill_count':len(fills),'background':'deep blue grey, approximate field #1A3646','pitch_size_unchanged':[200,327],'numbers_borders_click_bindings_unchanged':True,'unrelated_objects_unchanged':len(obs)-len(expected),'catalog_audits':audits,'catalogs_and_texture_bundles_unchanged':True,'retired_70_absent':True,'active_173_verified':True,'bundle_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
