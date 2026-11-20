"""Set only sidebar background to deep grey blue; remove its black inner tint."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<writer>','exec'));TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
outputs={};before={};color={k:f32(v/255) for k,v in zip(['r','g','b'],[38,52,69])};color['a']=1.
for name in [W,D]:
 path=GAME/name;before[path]=path.read_bytes();env=UnityPy.load(before[path]);a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()}
 if name==W:
  doc=next(o.read_typetree() for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='TFReferenceBookmarkSidebar');rr={r['rid']:r for r in doc['references']['RefIds']};obj=a.objects[doc['inlineSheet']['m_PathID']];d=obj.read_typetree();rule=d['m_Rules'][rr[1001]['data']['m_RuleIndex']];value={'r':0.,'g':0.,'b':0.,'a':0.}
 else:
  obj=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');d=obj.read_typetree();rules=[r for r in d['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','TFReferenceSidebar'] for sel in r['m_ComplexSelectors'])];assert len(rules)==1;rule=rules[0];value=color
 prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752);d['colors'].append(value);prop['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}];obj.save_typetree(d);payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
 for i,o in check.objects.items():
  if i==obj.path_id:assert o.read_typetree()==d
  else:assert o.get_raw_data()==raw[i]
 outputs[path]=payload
out=R/('sidebar-dark-grey-blue-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx=[]
for p,data in outputs.items():
 src=out/'packages'/p.name;bak=out/'backup-game'/p.name;src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(data);bak.write_bytes(before[p]);assert p.read_bytes()==before[p];tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(data)})
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p not in outputs}
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'sidebar_background':'#263445','inner_black_tint_removed':True,'other_objects_byte_identical':True,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
(out/'restore-color.ps1').write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot --restore\n",'utf-8-sig');print(str(out),flush=True)
