from pathlib import Path
import sys,json
R=Path(__file__).parent
source=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('# 1. Prematch')[0]
source=source.replace('match-ui-avatars-layout-','match-native-subs-heart-fix-').replace('NAMES=[W,G,M,F]','NAMES=[W,M]')
exec(compile(source,'backup-current-match-ui-and-load-helpers','exec'))

removed=[]
for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall','SquadOverviewPlayerBlock-Compact']:
 d=Doc(W,name=name)
 icons=[i for i,x in d.r.items() if 'm_Parent' in x.get('data',{}) and d.data(i).get('name')=='Conditionicon' and x['data'].get('m_FullTypeName')=='SI.Bindable.SIImage']
 assert len(icons)==1,(name,icons)
 icon=icons[0];parent=d.a(icon)['m_Parent']['rid'];assert d.a(parent)['m_FullTypeName']=='SI.Bindable.BindableSwitchElement'
 assert d.a(parent)['m_Children'][0]['rid']==icon and len(d.a(parent)['m_Children'])==2
 blank=ve(d,parent,'NoLegacyConditionHeart',0,0);d.st(blank,[(262150,[d.px(0)]),(262151,[d.px(0)]),(458767,d.num(0))]);d.move(blank,parent,0)
 sid=d.a(icon)['m_SerializedData']['rid'];d.a(parent)['m_Children'].remove({'rid':icon})
 assert not d.a(icon)['m_Children'];d.r.pop(icon);d.r.pop(sid);d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in [icon,sid]]
 d.save();removed.append({'template':name,'removed_icon':icon,'empty_normal_branch':blank,'injury_branch':d.a(parent)['m_Children'][1]['rid']})

baseline_path=R/'match-ui-avatars-layout-20261023-141148'/'backup-game'/M
base_env=UnityPy.load(str(baseline_path));base_objs={o.path_id:o for o in base_env.objects}
base_doc=base_objs[4934403862489788947].read_typetree();base_refs=refs(base_doc);base_sheet=base_objs[base_doc['inlineSheet']['m_PathID']].read_typetree()
d=Doc(M,name='SquadOverview')
# Original pools/rules remain unchanged prefixes: original native rule indices are safe to restore.
for pool in set(poolmap.values()):assert d.s[pool][:len(base_sheet[pool])]==base_sheet[pool],pool
assert d.s['m_Rules'][:len(base_sheet['m_Rules'])]==base_sheet['m_Rules']

def erase_subtree(i):
 for c in list(d.a(i).get('m_Children',[])):erase_subtree(c['rid'])
 parent=d.a(i)['m_Parent']['rid']
 if parent in d.r and {'rid':i} in d.a(parent).get('m_Children',[]):d.a(parent)['m_Children'].remove({'rid':i})
 sr=d.a(i).get('m_SerializedData',{}).get('rid');ids=[i]+([sr] if sr is not None and sr!=-2 else [])
 for rid in ids:d.r.pop(rid,None)
 d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in ids]

host=d.named('MatchBottomTacticalToolbar');d.move(host,1009)
wrappers=[i for i,x in d.r.items() if 'm_Parent' in x.get('data',{}) and d.data(i).get('name','').startswith('MatchSubstitutesAnchor_')]
assert len(wrappers)==4
restored=[]
for sub in [1032,1035,1038,1041]:
 parent=base_refs[sub]['data']['m_Parent']['rid'];old_parent=d.a(sub)['m_Parent']['rid'];d.a(old_parent)['m_Children'].remove({'rid':sub})
 # Restore the complete original element and serialized list data, not a hand-selected width.
 old_data=sd(base_refs,sub);new_data=d.data(sub)
 assert all(new_data.get(k)==v or v is None and new_data.get(k) in [None,0,False] for k,v in old_data.items()),('native list bindings unexpectedly changed',sub)
 assert all(k in old_data or v in [None,0,False] for k,v in new_data.items()),('new native list data',sub)
 d.r[sub].clear();d.r[sub].update(copy.deepcopy(base_refs[sub]))
 d.a(parent)['m_Children']=copy.deepcopy(base_refs[parent]['data']['m_Children'])
 restored.append({'list':sub,'parent':parent,'fixed_cell_width':d.data(sub)['FixedElementSize']})
for wrapper in wrappers:erase_subtree(wrapper)

# Independent overlay: it cannot contribute width to any native player/substitute list.
d.a(host)['m_Classes']=['padding-horizontal-global-padding-extra-large']
d.st(host,[(131102,d.enum('absolute')),(131080,d.pct(100)),(131089,d.px(0)),(131103,d.px(0)),(131087,d.px(32)),(131096,d.px(32)),(131094,d.px(32)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0)),(131091,d.px(0)),(131092,d.px(0)),(131088,d.enum('flex-end'))])
d.save()

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for pid,h in hashes[n].items():
  if pid not in changes[n]:assert sha(check[pid].get_raw_data())==h,('unrelated object modified',n,pid)
 for pid,expected in changes[n].items():assert check[pid].read_typetree()==expected,('roundtrip mismatch',n,pid)
 for doc in [x for x in documents if x.n==n]:validate_ui(check[doc.obj.path_id].read_typetree(),check[doc.sid].read_typetree())
 (OUT/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'changes':{n:{str(pid):v.get('m_Name','') for pid,v in ps.items()} for n,ps in changes.items()},'removed_legacy_hearts':removed,'native_substitute_lists_restored':restored,'baseline':str(baseline_path),'toolbar_independent_of_substitute_layout':True,'toolbar_height':32,'unrelated_objects_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'removed_hearts':len(removed),'native_lists_restored':len(restored),'changed_objects':{n:len(ps) for n,ps in changes.items()}},ensure_ascii=False))
