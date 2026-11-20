from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'write','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));game=Path(loc['bundle_root']);skin=Path(loc['skin_packages'])
name='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';target=game/name;before=target.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
env=UnityPy.load(before);a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()};obj=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchUITacticalOptions');d=obj.read_typetree();original=copy.deepcopy(d)
source=UnityPy.load(str(skin/name));s=next(o.read_typetree() for o in source.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchUITacticalOptions')
refs=lambda x:{n['rid']:n for n in x['references']['RefIds']};rr=refs(d);sr=refs(s);audit=[]
for rid in [1018,1048]:
 dst=rr[rr[rid]['data']['m_SerializedData']['rid']]['data'];src=sr[sr[rid]['data']['m_SerializedData']['rid']]['data'];assert dst['ContentTemplate']==src['ContentTemplate']
 assert src['Anchor']==1 and src['HorizontalAlignment']==0
 for k in ['Anchor','HorizontalAlignment','Anchor_UxmlAttributeFlags','HorizontalAlignment_UxmlAttributeFlags']:
  audit.append(dict(node=rid,field=k,before=dst[k],after=src[k]));dst[k]=src[k]
assert d==s,'Additional differences require separate review'
assert original!=d
obj.save_typetree(d);payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
for i,o in check.objects.items():
 if i==obj.path_id:assert o.read_typetree()==d
 else:assert o.get_raw_data()==raw[i],i
out=R/('sidebar-popup-anchor-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();(out/'packages').mkdir();(out/'backup-game').mkdir();p=out/'packages'/name;p.write_bytes(payload);bak=out/'backup-game'/name;bak.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(game.glob('*.bundle'))+[game.parent/'catalog.bin',game.parent/'catalog.hash']+list(skin.glob('*')) if p.is_file() and p!=target}
tx=[dict(target=str(target),source=str(p),backup=str(bak),before=sha(before),after=sha(payload))]
(out/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps(dict(installed=False,runtime_verified=False,scope='sidebar game only; restore native popup anchor for top-right tweaks/shouts',checks=audit,all_other_objects_byte_identical=True,protected_sha256=protected),ensure_ascii=False,indent=2),'utf8')
shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for label,flag in [('install',''),('restore-popup',' --restore')]:
 (out/(label+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
assert target.read_bytes()==before
print(str(out),flush=True)
