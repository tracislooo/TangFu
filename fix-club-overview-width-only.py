"""Remove the accidental width cap while retaining the requested height limit."""
from pathlib import Path
R=Path(__file__).resolve().parent
L='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','club-overview-width-fix-').replace('NAMES=[W,G,M,F]','NAMES=[L]').replace('hours=-4','hours=-6')
exec(compile(boot,'current-club-width-resources','exec'))
base=UnityPy.load((R/'club-overview-native-site-20261029-105920/backup-game'/L).read_bytes())
originals={o.path_id:o for o in base.objects};audit=[]
for size in ['Large','Standard','Small']:
 ob=find(L,'ClubComposition-'+size);old=ob.read_typetree();tree=copy.deepcopy(old)
 slot=next(x for x in tree['m_gridComponents'] if x['m_elementID']=='ClubScreenOverviewBlock')
 native=next(x for x in originals[ob.path_id].read_typetree()['m_gridComponents'] if x['m_elementID']==slot['m_elementID'])
 prev=slot['m_maxSize']['x'];slot['m_maxSize']['x']=native['m_maxSize']['x']
 assert slot['m_maxSize']['y']==slot['m_location']['height']
 tree['m_compositionVersion']+=1
 expected=copy.deepcopy(old);expected['m_compositionVersion']=tree['m_compositionVersion']
 next(x for x in expected['m_gridComponents'] if x['m_elementID']==slot['m_elementID'])['m_maxSize']['x']=native['m_maxSize']['x']
 assert tree==expected
 ob.save_typetree(tree);changes[L][ob.path_id]=tree
 audit.append({'name':tree['m_Name'],'max_width_before':prev,'max_width_after':slot['m_maxSize']['x'],'height_limit_unchanged':slot['m_maxSize']['y'],'all_other_layout_fields_preserved':True})
b=env[L].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
assert set(check)==set(objs[L])
for i,h in hashes[L].items():
 if i not in changes[L]:assert sha(check[i].get_raw_data())==h,i
for i,d in changes[L].items():assert check[i].read_typetree()==d
(OUT/L).write_bytes(b)
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 p=folder/L;tx.append({'target':str(p),'source':str(OUT/L),'backup':str(OUT/('backup-'+tag)/L),'before':sha(before[p]),'after':sha(b)})
for p,data in before.items():
 assert p.read_bytes()==data
 if p.name!=L:protected[p]=sha(data)
for p,h in protected.items():assert sha(p.read_bytes())==h
manifest={'installed':False,'runtime_verified':False,'request':'Restore native Club overview horizontal expansion; keep original heights and current site content.','layouts':audit,'only_max_width_and_composition_version_changed':True,'unrelated_objects_byte_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 script="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n"
 (OUT/(action+'.ps1')).write_text(script,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(OUT),'layouts':audit},ensure_ascii=False),flush=True)
import subprocess
assert subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(OUT)]).returncode==0
