"""Replace the secondary navigation's entity gradient with 60%-transparent black."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys

R=Path(__file__).resolve().parent
location=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(location['bundle_root']); SKIN=Path(location['skin_packages'])
assert GAME==Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 tree=ast.parse((R/name).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),name+':definitions-only','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
protected={}
for f in [GAME,SKIN]:
 for name in ['ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-visualfunctions_assets_all.bundle']:
  p=f/name
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:
 protected[R/n]=sha((R/n).read_bytes())
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved}|{-910000000000001,-910000000000002}
spec=importlib.util.spec_from_file_location('secondary_catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in en.objects}
 hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 candidates=[o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='SecondaryNavigationBar']
 assert len(candidates)==1
 obj=candidates[0];doc=obj.read_typetree();old_doc=copy.deepcopy(doc)
 rr={r['rid']:r for r in doc['references']['RefIds']}
 serial=lambda i:rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 roots=rr[doc['m_VisualTree']['rid']]['data']['m_Children'];assert len(roots)==1
 root=roots[0]['rid']
 gradients=[i for i in rr if serial(i).get('name')=='EntityGradient']
 assert len(gradients)==1;gradient=gradients[0]
 assert rr[gradient]['data']['m_Parent']['rid']==root
 foreground=[c['rid'] for c in rr[root]['data']['m_Children'] if c['rid']!=gradient]
 assert len(foreground)==1 and rr[foreground[0]]['data']['m_FullTypeName']=='SI.UI.SISafeAreaElement'
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();old_sheet=copy.deepcopy(sheet);st=Styles(sheet)
 alpha=struct.unpack('<f',struct.pack('<f',0.4))[0]
 st.edit(rr[root],[st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':alpha})),st.p(458753,st.en('none'))])
 st.edit(rr[gradient],[st.p(131081,st.en('none'))])
 # Preserve all bindings, foreground controls, layout properties, IDs, and original style rules.
 original_refs={r['rid']:r for r in old_doc['references']['RefIds']}
 for i,r in rr.items():
  expected=copy.deepcopy(original_refs[i])
  if i in [root,gradient]:expected['data']['m_RuleIndex']=r['data']['m_RuleIndex']
  assert r==expected,('Unrelated navigation record changed',i)
 assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
 for key,v in old_sheet.items():
  if isinstance(v,list):assert sheet[key][:len(v)]==v
  else:assert sheet[key]==v
 for i in [root,gradient]:
  assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] for h in p['m_Values'])
 validate_ui(doc,sheet)
 obj.save_typetree(doc);oo[sid].save_typetree(sheet)
 raw=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(check)==set(oo)
 for i,o in check.items():
  if i in [obj.path_id,sid]:assert o.read_typetree()=={obj.path_id:doc,sid:sheet}[i]
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated bundle object changed',tag,i)
 validate_ui(check[obj.path_id].read_typetree(),check[sid].read_typetree())
 meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 keys=[k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':obj.path_id}]
 assert len(keys)==1;guid=keys[0]
 catalog_path=(GAME.parent if tag=='game' else SKIN)/'catalog.bin';cat=cm.Catalog(catalog_path.read_bytes())
 locs=[l for l in cat.locations(guid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset']
 assert locs
 for loc in locs:
  info=cat.location(loc);assert info['internal']==guid and info['dependencies']
  assert cat.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
 # No object, container, preload, imported template or catalog registration is added.
 assert banned.isdisjoint(set(check)-set(oo))
 outputs[folder/W]=raw
 reports.append({'target':str(folder/W),'template':'SecondaryNavigationBar','path_id':str(obj.path_id),'guid':guid,
  'inline_sheet':str(sid),'black_background_rgba':[0,0,0,0.4],'transparency_percent':60,'opacity_percent':40,
  'hidden_decorative_layer':'EntityGradient','foreground_and_bindings_unchanged':True,
  'new_inline_variables':False,'changed_bundle_objects':2,'other_objects_unchanged':len(oo)-2,
  'typed_catalog_owner_verified':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('secondary-tabbar-black-transparent60-'+stamp);out.mkdir();tx=[]
for p,data in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(data);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(data)})
manifest={'installed':False,'runtime_verified':False,'changes':reports,'no_image_changes':True,
 'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'targets':len(outputs),'transparency_percent':60,'alpha':0.4},ensure_ascii=False))
