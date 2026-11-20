exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
for pid,ids in [(-7609784215942621793,[1007,1012,1013])]:
 d=go[pid].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};s=go[d['inlineSheet']['m_PathID']].read_typetree()
 for i in ids:
  a=sr[i]['data'];ix=a['m_RuleIndex'];print(i,a['m_Classes'],{p['m_Id']:[('kw',h['valueIndex']) if h['m_ValueType']==1 else s[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in s['m_Rules'][ix]['m_Properties']} if ix>=0 else {})
# Resolve the overview-specific attribute table by its registered GUID.
for bn,e in [('W',env),('G',ge)]:
 for k,v in e.container.items():
  if k=='3bc158458fec50bf9230826edbc62cd1':
   oo={o.path_id:o for o in e.objects};d=oo[v.path_id].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};print('TABLE',bn,v.path_id,d['m_Name'])
   for i,r in sr.items():
    if 'goalkeep' in r.get('data',{}).get('DebugDisplay','').lower():print('GK SD',i,'NODE',[n['rid'] for n in sr.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==i])
