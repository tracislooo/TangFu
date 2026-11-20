"""Verify every allowed flag/override and literal paint delta in the UI repair."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
s=json.loads((R/'current-light-readability-fix.json').read_text('utf8'));out=Path(s['record'])
m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
paint={65536,196610,458752,458753,262146,458758,458761,458762,458763};flags={'IgnoreEmbeddedDataStyling','DisableLinkStyling'}
allowed_flags=flags|{f+'_UxmlAttributeFlags' for f in flags}
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def objs(raw):return {o.path_id:o for o in UnityPy.load(raw).objects}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def selector_text(sel):return ' '.join(''.join({3:'.',4:':',6:'#'}.get(p['m_Type'],'')+p['m_Value'] for p in s['m_Parts']) for s in sel['m_Selectors'])
def leaf(doc,path,documents,aliases):
 for j,eid in enumerate(path):
  rr=refs(doc);found=[r for r in rr.values() if r.get('data',{}).get('m_Id')==eid]
  assert len(found)==1,('Invalid override path element',doc['m_Name'],path,eid)
  a=found[0]['data']
  if j==len(path)-1:assert a.get('m_FullTypeName')=='SI.Bindable.SIText';return
  alias=a.get('m_TemplateAlias');assert alias
  u=next(u for u in doc['m_Usings'] if u['alias']==alias);assert u['path'] in aliases
  doc=documents[aliases[u['path']]]

reports=[];documents_total=0;added_total=0;ink_total=0
for tag,folder in [('game',Path(tx['game'])),('skin',Path(tx['skin']))]:
 envs={};aliases={};documents={}
 for target,src in tx['sources'].items():
  if Path(target).parent!=folder or 'visualtree' not in target:continue
  oo=objs(Path(src).read_bytes());envs[Path(target).name]=oo
  meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
  for o in oo.values():
   if o.type.name=='MonoBehaviour':
    d=o.read_typetree()
    if 'inlineSheet' in d:documents[(Path(target).name,o.path_id)]=d
  for key,item in meta['m_Container']:
   pair=(Path(target).name,item['asset']['m_PathID'])
   if re.fullmatch('[0-9a-f]{32}',key) and pair in documents:aliases[key]=pair
 for target,src in tx['sources'].items():
  if Path(target).parent!=folder:continue
  raw=Path(src).read_bytes();before=Path(tx['before'][target]).read_bytes()
  assert sha(raw)==m['after_sha256'][target] and sha(before)==m['before_sha256'][target]
  now,old=objs(raw),objs(before);assert set(now)==set(old)
  changed={pid for pid in now if now[pid].get_raw_data()!=old[pid].get_raw_data()}
  assert changed=={int(x) for x in m['objects'][target]['changed_ids']}
  for pid in changed:
   a,b=now[pid].read_typetree(),old[pid].read_typetree()
   if 'm_Rules' in a:
    norm=copy.deepcopy(a)
    for i,prior in enumerate(b['m_Rules']):
     actual=a['m_Rules'][i];assert actual['m_ComplexSelectors']==prior['m_ComplexSelectors']
     assert len(actual['m_Properties'])==len(prior['m_Properties'])
     for j,p in enumerate(actual['m_Properties']):
      op=prior['m_Properties'][j]
      if p==op:continue
      assert p['m_Id']==458752 or (p['m_Id']==-1 and p['m_CustomName'].startswith(('--global-sink-surface-','--global-lift-surface-')))
      q=copy.deepcopy(p);q['m_Values']=op['m_Values'];assert q==op
      assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4
      norm['m_Rules'][i]['m_Properties'][j]=copy.deepcopy(op)
    for rule in a['m_Rules'][len(b['m_Rules']):]:
     if not rule['m_ComplexSelectors']:continue
     for p in rule['m_Properties']:
      assert p['m_Id'] in paint or (p['m_Id']==-1 and p['m_CustomName']=='--unity-image-tint-color')
      if p['m_Id']==458753:assert p['m_Values']==[{'m_ValueType':1,'valueIndex':6}]
      elif p['m_Id'] in paint or p['m_Id']==-1:
       assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4
    norm['m_Rules']=norm['m_Rules'][:len(b['m_Rules'])]
    for p in set(pool.values()):assert a[p][:len(b[p])]==b[p];norm[p]=norm[p][:len(b[p])]
    assert norm==b,'Non-paint stylesheet change'
    continue
   assert 'inlineSheet' in a
   rr,oldrr=refs(a),refs(b);nr=copy.deepcopy(a);nrefs=refs(nr);added=set(rr)-set(oldrr)
   assert set(oldrr)<=set(rr)
   for rid in added:
    sd=rr[rid]['data'];assert sd['IgnoreEmbeddedDataStyling']==sd['DisableLinkStyling']==1
    assert all(v==0 or k in allowed_flags for k,v in sd.items() if k.endswith('_UxmlAttributeFlags'))
   for rid,rec in oldrr.items():
    actual=rr[rid];nd=nrefs[rid].get('data',{});orig=rec.get('data',{})
    if 'm_Parent' in orig:
     if nd.get('m_RuleIndex')!=orig.get('m_RuleIndex'):
      sh=now[a['inlineSheet']['m_PathID']].read_typetree();osh=old[b['inlineSheet']['m_PathID']].read_typetree()
      ni,oi=nd['m_RuleIndex'],orig['m_RuleIndex'];ps=sh['m_Rules'][ni]['m_Properties'];op=osh['m_Rules'][oi]['m_Properties'] if oi>=0 else []
      assert [p for p in ps if p['m_Id'] not in paint]==[p for p in op if p['m_Id'] not in paint]
      for p in ps:
       if p in op:continue
       assert p['m_Id'] in paint
       assert p['m_Values']==[{'m_ValueType':1,'valueIndex':6}] if p['m_Id']==458753 else len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4
      nd['m_RuleIndex']=orig['m_RuleIndex']
     if nd.get('m_Classes')!=orig.get('m_Classes'):
      assert nd['m_Classes']==orig['m_Classes']+['tf-light-neutral-name'];nd['m_Classes']=copy.deepcopy(orig['m_Classes'])
     if 'm_SerializedDataOverride' in orig:
      entries=nd['m_SerializedDataOverride'];prior=orig['m_SerializedDataOverride'];assert entries[:len(prior)]==prior
      for e in entries[len(prior):]:
       alias=orig['m_TemplateAlias'];u=next(u for u in a['m_Usings'] if u['alias']==alias)
       leaf(documents[aliases[u['path']]],e['m_ElementIdsPath'],documents,aliases)
       assert e['m_SerializedData']['rid'] in added and e['m_ElementId']==e['m_ElementIdsPath'][-1]
       assert rr[e['m_SerializedData']['rid']]['data']['uxmlAssetId']==e['m_ElementId']
      nd['m_SerializedDataOverride']=copy.deepcopy(prior)
    for key in allowed_flags:
     if nd.get(key)!=orig.get(key):
      assert nd[key]==1
      if key in orig:nd[key]=orig[key]
      else:nd.pop(key)
      ink_total+=1
   nr['references']['RefIds']=[r for r in nr['references']['RefIds'] if r['rid'] not in added]
   assert nr==b,('Unexpected binding/layout/event edit',a['m_Name'])
   documents_total+=1;added_total+=len(added)
  reports.append({'target':target,'changed_objects':len(changed),'all_other_objects_identical':True})
  print(tag,Path(target).name,'verified',len(changed),flush=True)
result={'passed':True,'files':len(reports),'documents':documents_total,'name_override_records':added_total,
        'existing_format_flags_changed':ink_total,'layout_bindings_events_and_asset_ids_preserved':True,
        'no_new_inline_color_variables':True,'nested_override_paths_verified':True,'runtime_verified':False,'details':reports}
(out/'qa-readability.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in result.items() if k!='details'},ensure_ascii=False))
