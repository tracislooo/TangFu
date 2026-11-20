from pathlib import Path
R=Path(__file__).resolve().parent
L='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','club-overview-original-heights-').replace('NAMES=[W,G,M,F]','NAMES=[W,L]').replace('hours=-4','hours=-6')
exec(compile(boot,'current-club-height-resources','exec'))
baseline=UnityPy.load((R/'club-overview-native-site-20261029-105920/backup-game'/L).read_bytes())
oldobjs={o.path_id:o for o in baseline.objects};audit=[]
for size in ['Large','Standard','Small']:
 ob=find(L,'ClubComposition-'+size);current=ob.read_typetree();original=oldobjs[ob.path_id].read_typetree()
 assert original['m_Name']==current['m_Name']
 tree=copy.deepcopy(original);tree['m_compositionVersion']=current['m_compositionVersion']+1
 overview=next(x for x in tree['m_gridComponents'] if x['m_elementID']=='ClubScreenOverviewBlock')
 # Lock the overview's native grid extent, preventing content-driven expansion.
 overview['m_maxSize']={'x':overview['m_location']['width'],'y':overview['m_location']['height']}
 overview['m_expandToContent']=0
 ob.save_typetree(tree);changes[L][ob.path_id]=tree
 for a,b in zip(original['m_gridComponents'],tree['m_gridComponents']):assert a['m_location']==b['m_location']
 audit.append({'name':tree['m_Name'],'original_positions_and_heights_restored':True,'overview_location':overview['m_location'],'overview_max_size':overview['m_maxSize']})
host=Doc(W,name='ClubScreenOverviewBlock');oldhost=copy.deepcopy(host.d)
host.st(1001,[(131087,host.pct(100)),(131094,host.pct(100)),(131096,host.px(0)),(131085,host.num(1)),(458768,host.enum('hidden'))])
body=next(i for i,x in host.r.items() if x.get('data',{}).get('m_TemplateAlias')=='ClubSiteBlock')
host.st(body,[(131087,host.px(0)),(131096,host.px(0)),(131094,host.pct(100)),(131084,host.num(1)),(131085,host.num(1)),(458768,host.enum('hidden'))]);host.save()
for i,r in refs(oldhost).items():
 x=copy.deepcopy(host.r[i])
 if 'm_RuleIndex' in r.get('data',{}):x['data']['m_RuleIndex']=r['data']['m_RuleIndex']
 assert x==r
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h,(n,i)
 for i,d in changes[n].items():assert check[i].read_typetree()==d
 (OUT/n).write_bytes(b)
validate_ui(host.d,host.s)
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in outputs:
  p=folder/n;tx.append({'target':str(p),'source':str(OUT/n),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(outputs[n])})
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name not in outputs:protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
manifest={'installed':False,'runtime_verified':False,'request':'Restore Club action row and overview to original heights; retain native site contents; constrain overview to its original slot.','layouts':audit,'top_native_template_and_content_size_restored':True,'overview_bindings_and_templates_preserved':True,'unrelated_objects_byte_identical':True,'catalog_unchanged':True,'textures_unchanged':True,'protected_sha256':{str(p):h for p,h in protected.items()},'changes':{n:{str(i):d.get('m_Name') for i,d in v.items()} for n,v in changes.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 script="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n"
 (OUT/(action+'.ps1')).write_text(script,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(OUT),'layouts':audit},ensure_ascii=False),flush=True)
import subprocess
result=subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(OUT)])
assert result.returncode==0
