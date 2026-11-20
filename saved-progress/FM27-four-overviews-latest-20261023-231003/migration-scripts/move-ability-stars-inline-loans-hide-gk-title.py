from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<current asset loader>','exec'))
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';TABLE=-930000000001003
extra_before={folder/GN:(folder/GN).read_bytes() for folder in [GAME,SKIN]};assert extra_before[GAME/GN]==extra_before[SKIN/GN]
ge=UnityPy.load(extra_before[GAME/GN]);go={o.path_id:o for o in ge.objects};gh={i:sha(o.get_raw_data()) for i,o in go.items()}
# Hide all Goalkeeping headings in the overview-private attribute table, with no residual height.
gdoc=go[TABLE].read_typetree();gr={r['rid']:r for r in gdoc['references']['RefIds']};gsid=gdoc['inlineSheet']['m_PathID'];gsheet=go[gsid].read_typetree()
# Style helpers capture the active sheet, so return to the full overview sheet after this edit.
full_sheet=sheet;sheet=gsheet;hidden=[]
for i,r in gr.items():
 if r.get('data',{}).get('DebugDisplay','').casefold()=='goalkeeping':
  node=next(n for n in gr.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==i)
  override(node['data'],[prop(131081,en('none')),prop(131087,px(0)),prop(131096,px(0)),prop(131094,px(0)),prop(262150,px(0)),prop(262151,px(0)),prop(131093,px(0)),prop(131090,px(0))]);hidden.append(node['rid'])
assert len(hidden)==3
validate_ui(gdoc,gsheet);go[TABLE].save_typetree(gdoc);go[gsid].save_typetree(gsheet)
sheet=full_sheet
# Inline per-page native templates so moving/hiding branches does not alter shared templates.
SCOUT=-547355884850947872;TEAM=-7609784215942621793
srcdocs={pid:objects[pid].read_typetree() for pid in [SCOUT,TEAM]};srcsheets={pid:objects[d['inlineSheet']['m_PathID']].read_typetree() for pid,d in srcdocs.items()}
next_eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
imports=[]
def refs_in(v):
 if isinstance(v,dict):
  if set(v)=={'rid'}:yield v['rid']
  else:
   for a in v.values():yield from refs_in(a)
 elif isinstance(v,list):
  for a in v:yield from refs_in(a)
def import_native(pid,parent,prefix,empty_branch=None):
 global next_eid
 sd=copy.deepcopy(srcdocs[pid]);sr={r['rid']:r for r in sd['references']['RefIds']};ss=srcsheets[pid]
 if empty_branch is not None:sr[empty_branch]['data']['m_Children']=[]
 live=set();stack=[sd['m_VisualTree']['rid']]
 while stack:
  i=stack.pop()
  if i in live:continue
  assert i in sr;live.add(i);stack.extend(refs_in(sr[i].get('data',{})))
 ids=[r['rid'] for r in sd['references']['RefIds'] if r['rid'] in live and r['rid'] not in [-2,1000]]
 start=max(rr)+1;mapping={i:start+k for k,i in enumerate(ids)};mapping[1000]=parent
 idmap={}
 for i in ids:
  if 'm_Id' in sr[i].get('data',{}):idmap[sr[i]['data']['m_Id']]=next_eid;next_eid+=1
 aliases={u['alias']:prefix+u['alias'] for u in sd['m_Usings']}
 for u in sd['m_Usings']:
  nu=copy.deepcopy(u);nu['alias']=aliases[u['alias']];assert not any(e['alias']==nu['alias'] for e in doc['m_Usings']);doc['m_Usings'].append(nu)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid'] in mapping:v['rid']=mapping[v['rid']]
   else:
    for k,a in list(v.items()):
     if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(a,int) and a in idmap:v[k]=idmap[a]
     elif k in ['m_TemplateAlias','templateId'] and a in aliases:v[k]=aliases[a]
     else:remap(a)
    if v.get('name')=='template' and v.get('value') in aliases:v['value']=aliases[v['value']]
  elif isinstance(v,list):
   for a in v:remap(a)
 for i in ids:
  r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
  ix=r['data'].get('m_RuleIndex',-1)
  if ix>=0:
   newrule=copy.deepcopy(ss['m_Rules'][ix])
   for p in newrule['m_Properties']:
    for h in p['m_Values']:
     if h['m_ValueType']==1:continue
     pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]))
     h['valueIndex']=len(sheet[pool])-1
   r['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(newrule)
  rr[r['rid']]=r;doc['references']['RefIds'].append(r)
 roots=[mapping[c['rid']] for c in sr[1000]['data']['m_Children']]
 rr[parent]['data']['m_Children'].extend([{'rid':i} for i in roots])
 imports.append({'source':pid,'prefix':prefix,'records':len(ids),'empty_branch':empty_branch,'mapping':mapping})
 return mapping
# Convert an existing TemplateAsset instance into a local container; no native instance overrides exist.
def local_container(i,name):
 old=rr[i];a=old['data'];assert not a['m_AttributeOverrides'] and not a['m_SlotUsages']
 ns=copy.deepcopy(rr[1297]['data']);ns.update(m_Id=a['m_Id'],m_Parent=a['m_Parent'],m_Children=[],m_Classes=a['m_Classes'],m_RuleIndex=a['m_RuleIndex'],m_SerializedData=a['m_SerializedData'])
 rr[i]['type']=copy.deepcopy(rr[1297]['type']);rr[i]['data']=ns
 sdi=a['m_SerializedData']['rid'];sd=copy.deepcopy(rr[rr[1297]['data']['m_SerializedData']['rid']]);sd['rid']=sdi
 sd['data'].update(uxmlAssetId=a['m_Id'],name=name,name_UxmlAttributeFlags=1)
 rr[sdi]=sd
 for index,r in enumerate(doc['references']['RefIds']):
  if r['rid']==sdi:doc['references']['RefIds'][index]=sd;break
# Left: same report gates and bindings, with an empty scout-report branch.
base=copy.deepcopy(rr[1295]);bsd=copy.deepcopy(rr[base['data']['m_SerializedData']['rid']]);nid=max(rr)+1;did=nid+1
base['rid']=nid;bsd['rid']=did;base['data'].update(m_Id=next_eid,m_Parent={'rid':1297},m_Children=[],m_SerializedData={'rid':did},m_Classes=[],m_RuleIndex=-1)
bsd['data'].update(uxmlAssetId=next_eid,name='ReportIdentityAbilityStars',name_UxmlAttributeFlags=1);next_eid+=1
rr[nid]=base;rr[did]=bsd;doc['references']['RefIds'].extend([base,bsd])
idx=rr[1297]['data']['m_Children'].index({'rid':1295});rr[1297]['data']['m_Children'].insert(idx,{'rid':nid})
left=import_native(SCOUT,nid,'IdentityAbility_',empty_branch=1008)
# Right: preserve the original scouting report while removing the star branch's children entirely.
local_container(1203,'ReportRightScoutContent');right=import_native(SCOUT,1203,'RightScout_',empty_branch=1009)
# Club information gets an isolated native copy with explicit horizontal loan columns.
local_container(1193,'ReportInlineClubInformation');club=import_native(TEAM,1193,'IdentityClub_')
def edit(i,p):override(rr[i]['data'],p)
def pct(n):return val(3,{'unit':2,'value':float(n)})
zerogap=[prop(262150,px(0)),prop(262151,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131101,px(0)),prop(131098,px(0))]
edit(nid,zerogap+[prop(131087,auto()),prop(131096,px(0)),prop(131094,px(32)),prop(131084,num(0)),prop(131085,num(0)),prop(131105,pct(100)),prop(131097,px(0))])
for i in [1001,1002,1004,1006]:edit(left[i],zerogap+[prop(131087,auto()),prop(131096,px(0)),prop(131094,px(32)),prop(131084,num(0)),prop(131085,num(0)),prop(131105,pct(100))])
edit(left[1008],zerogap+[prop(131087,px(0)),prop(131096,px(0)),prop(131094,px(0))])
for i in [1009,1013]:edit(left[i],zerogap+[prop(131083,en('row')),prop(131073,en('center')),prop(131087,px(32)),prop(131096,px(32)),prop(131094,px(32)),prop(131084,num(0)),prop(131085,num(0)),prop(131105,pct(100)),prop(131097,px(0))])
for i in [1018,1019]:edit(left[i],zerogap+[prop(131083,en('column')),prop(131087,px(32)),prop(131096,px(0)),prop(131084,num(0)),prop(131085,num(1)),prop(131097,px(0)),prop(131092,px(16 if i==1018 else 0))])
for i in [1025,1029]:edit(left[i],zerogap+[prop(65537,px(11)),prop(131087,px(12)),prop(131096,px(0)),prop(131085,num(0))])
for i in [1026,1030]:edit(left[i],zerogap+[prop(131087,px(20)),prop(131096,px(0)),prop(131085,num(0))])
edit(right[1009],zerogap+[prop(131087,px(0)),prop(131096,px(0)),prop(131094,px(0))])
edit(club[1007],zerogap+[prop(131083,en('row')),prop(131073,en('center')),prop(131105,pct(100)),prop(131097,px(0)),prop(131085,num(1))])
for i in [1012,1013]:
 rr[club[i]]['data']['m_Classes']=[c for c in rr[club[i]]['data']['m_Classes'] if 'margin' not in c]
 edit(club[i],zerogap+[prop(131083,en('row')),prop(131073,en('center')),prop(131074,en('stretch')),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131092,px(10 if i==1012 else 0))])
for i in [1021,1026]:edit(club[i],[prop(131097,px(0)),prop(131085,num(1))])
# Both branches retain native conditions; their layouts no longer depend on the global team/scout templates.
assert rr[left[1008]]['data']['m_Children']==[]
assert rr[right[1009]]['data']['m_Children']==[]
assert rr[1297]['data']['m_Children'].index({'rid':nid})+1==rr[1297]['data']['m_Children'].index({'rid':1295})
assert property_value(rr[club[1007]],131083)=='row'
assert rr[1297]['data']['m_Parent']==old_refs[1297]['data']['m_Parent']
# Imported serialized data are native copies (only identity IDs and template aliases are remapped).
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
world_output=env.file.save(packer='lz4');global_output=ge.file.save(packer='lz4')
ws={o.path_id:o for o in UnityPy.load(world_output).objects};gs={o.path_id:o for o in UnityPy.load(global_output).objects}
assert set(ws)==set(objects) and set(gs)==set(go)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert ws[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(ws[i].get_raw_data())==h,('Unrelated world asset changed',i)
for i,h in gh.items():
 if i in [TABLE,gsid]:assert gs[i].read_typetree()=={TABLE:gdoc,gsid:gsheet}[i]
 else:assert sha(gs[i].get_raw_data())==h,('Unrelated global asset changed',i)
validate_ui(ws[FULL].read_typetree(),ws[sid].read_typetree());validate_ui(gs[TABLE].read_typetree(),gs[gsid].read_typetree())
all_before={**before,**extra_before}
for p,data in all_before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('gk-no-title-left-stars-horizontal-loans-'+stamp);out.mkdir();outputs={WN:world_output,GN:global_output}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for name in outputs:(backup/name).write_bytes(all_before[folder/name])
for name,data in outputs.items():(out/name).write_bytes(data)
report={'installed':False,'runtime_verified':False,'goalkeeping_titles_hidden':hidden,'ability_stars_before_country_club':True,'star_holder':nid,'star_native_gates_and_context_preserved':True,'right_scout_report_preserved_without_stars':True,'loan_club_layout':'horizontal row, two flexible columns','native_shared_templates_preserved':True,'inline_imports':imports,'changed_assets':{WN:[FULL,sid],GN:[TABLE,gsid]},'before_sha256':{str(p):sha(data) for p,data in all_before.items()},'after_sha256':{name:sha(data) for name,data in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  for name,data in outputs.items():(folder/name).write_bytes(data);assert (folder/name).read_bytes()==data
 for p,h in protected.items():
  if p not in extra_before:assert sha(p.read_bytes())==h
except Exception:
 for p,data in all_before.items():p.write_bytes(data)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'goalkeeping_headings_hidden':len(hidden),'star_holder':nid,'inline_imports':[(x['prefix'],x['records']) for x in imports],'after_sha256':report['after_sha256']},ensure_ascii=False,indent=2))
