exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
for bn in [p,p.parent/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 en=UnityPy.load(str(bn));ob={x.path_id:x for x in en.objects};ab=next(x for x in ob.values() if x.type.name=='AssetBundle').read_typetree()
 for key,v in ab['m_Container']:
  if key not in ['a3fc5b9c1c155a2cb6fa40c244b1f25d','57e6899e45c151e9bd45c64591495855']:continue
  pid=v['asset']['m_PathID'];d=ob[pid].read_typetree();print('FOUND',bn.name,key,pid,d['m_Name']);rr={r['rid']:r for r in d['references']['RefIds']};s=ob[d['inlineSheet']['m_PathID']].read_typetree()
  for i,r in rr.items():
   a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});nm=sd.get('name','')
   if 'UxmlSerializedData' in r.get('type',{}).get('class',''):continue
   ix=a.get('m_RuleIndex',-1);print(i,nm,a.get('m_FullTypeName'),a.get('m_Children'),[(pr['m_Id'],pr['m_Values']) for pr in s['m_Rules'][ix]['m_Properties']] if ix>=0 else [])
for pid in [-930000000001001,-941100000001010]:
 d=o[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree()
 for i in ([6228,1035] if pid==-930000000001001 else [1067,6238,6268,6270]):
  a=rr[i]['data'];ix=a.get('m_RuleIndex',-1);print('STYLE',pid,i,rr[a['m_SerializedData']['rid']]['data'].get('name'), s['m_Rules'][ix] if ix>=0 else {})
