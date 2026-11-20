"""Change only the installed shortcut's native initial selection to Next match."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'serialization-helper','exec'))
TypeTreeHelper.write_value=write
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
assert before[GAME/W]==before[SKIN/W]
protected={}
for f in [GAME,SKIN]:
 for n in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualfunctions_assets_all.bundle']:
  p=f/n
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
e=UnityPy.load(before[GAME/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
nav=oo[8206725239586998471];doc=nav.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
def named(name):
 return next(r for r in rr.values() if r.get('data',{}).get('name')==name)
node=named('HeaderHolidayDate')
# The named record is the TemplateContainer serialized data; locate its actual template overrides.
element=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==node['rid'])
override=next(r for r in element['data']['m_SerializedDataOverride'] if 'BindChoicesFunction' in rr[r['m_SerializedData']['rid']]['data'])
target=rr[override['m_SerializedData']['rid']]['data']
native=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='HolidayReturnDateTypeChooseRadioButtonOption')
nr={r['rid']:r for r in native['references']['RefIds']};function=copy.deepcopy(nr[1014]['data']['BindChoicesFunction'])
assert function['m_target']['m_guid']=='50902af85e1d1534cabaecf7660bda36'
raw=bytes(function['m_inputs']['m_variable']['m_argumentBytes']);assert raw[0]==3
p=1;args=[]
for _ in range(raw[0]):
 n=struct.unpack_from('<I',raw,p)[0];p+=4;args.append(raw[p:p+n]);p+=n
assert p==len(raw) and struct.unpack('<i',args[-1][-4:])[0]==0
args[-1]=args[-1][:-4]+struct.pack('<i',2)
function['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
target['BindChoicesFunction']=function
assert target['TriggerSelectionEventOnInit']==0
assert target['BindChoicesFunction_UxmlAttributeFlags']==1
changed=[override['m_SerializedData']['rid']]
for r in old['references']['RefIds']:
 if r['rid'] not in changed:assert rr[r['rid']]==r,('Other navigation record changed',r['rid'])
nav.save_typetree(doc);data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
assert set(check)==set(oo)
for i,o in check.items():
 if i==nav.path_id:assert o.read_typetree()==doc
 else:assert sha(o.get_raw_data())==hashes[i],('Unrelated asset changed',i)
# Native initialization function already exists and is registered; no new catalog entries needed.
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for f in [GAME.parent,SKIN]:
 c=cm.Catalog((f/'catalog.bin').read_bytes());locs=c.locations(function['m_target']['m_guid'])
 assert any(c.location(l)['type'][1]=='SI.VisualScripting.VisualFunction' and c.location(c.location(l)['dependencies'][0])['internal'].endswith('ui-visualfunctions_assets_all.bundle') for l in locs)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('header-holiday-default-next-match-'+stamp);out.mkdir();tx=[]
for tag,f in [('game',GAME),('skin',SKIN)]:
 src=out/tag/W;bak=out/('backup-'+tag)/W;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(data);bak.write_bytes(before[f/W])
 tx.append({'target':str(f/W),'source':str(src),'backup':str(bak),'before':sha(before[f/W]),'after':sha(data)})
manifest={'installed':False,'runtime_verified':False,'default_option':'Next match','native_zero_based_index':2,
 'native_option_order_verified_in_previous_live_session':['Next week','Next month','Next match','Choose...'],
 'changed_serialized_records':changed,'initializer':'BindSIDropdown-InitSelectionIndex','no_initial_confirmation_event':True,
 'crash_fix_and_all_styles_preserved':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for n,flag in [('install',''),('restore',' --restore')]:
 (out/(n+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'default':'Next match','index':2,'changed_navigation_records':len(changed),'other_assets_unchanged':True},ensure_ascii=False))
