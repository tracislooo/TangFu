exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','fix-second-role-content-visible-'))
SOURCE=R/'restore-role-list-vertical-scroll234-20261101-042425';outputs={};audits=[];pid=-940000000008000;chain=[1075,1068,1063,1055,1042,1028,1012,2010]
for folder in [GAME,SKIN]:
 tag='backup-game' if folder==GAME else 'backup-skin';bo={o.path_id:o for o in UnityPy.load(str(SOURCE/tag/G)).objects};base=bo[pid].read_typetree();br=refs(base);bs=bo[base['inlineSheet']['m_PathID']].read_typetree()
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 for i in chain:
  ix=br[i]['data'].get('m_RuleIndex',-1)
  props=copy.deepcopy(bs['m_Rules'][ix]['m_Properties']) if ix>=0 else []
  for p0 in props:
   for q in p0['m_Values']:
    typ=q['m_ValueType']
    if typ in poolmap:
     pool=poolmap[typ];assert typ!=6;sheet[pool].append(copy.deepcopy(bs[pool][q['valueIndex']]));q['valueIndex']=len(sheet[pool])-1
  rr[i]['data']['m_RuleIndex']=rule(props)
 sdid=rr[1075]['data']['m_SerializedData']['rid'];s=rr[sdid]['data'];fields={'ScrollViewMode':0,'VerticalScrollerVisibility':1,'HorizontalScrollerVisibility':2,'MouseWheelScrollSize':24.0}
 for k,v in fields.items():s[k]=v;s[k+'_UxmlAttributeFlags']=1
 for i,r in old.items():
  if i not in chain and i!=sdid:assert rr[i]==r
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 cr=refs(check[pid].read_typetree());cs=check[sid].read_typetree()
 for i in chain:
  actual=cs['m_Rules'][cr[i]['data']['m_RuleIndex']]['m_Properties'];baseline=bs['m_Rules'][br[i]['data']['m_RuleIndex']]['m_Properties']
  def semantic(props,ss):
   return [(p['m_Id'],[(q['m_ValueType'],ss[poolmap[q['m_ValueType']]][q['valueIndex']] if q['m_ValueType'] in poolmap else q['valueIndex']) for q in p['m_Values']]) for p in props]
  assert semantic(actual,cs)==semantic(baseline,bs)
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out);audits.append({'target':str(folder),'only_version':2,'restore_original_role_ancestor_styles':chain,'vertical_scrolling_retained':True,'pitch_and_other_versions_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)}))
