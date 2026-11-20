from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
e=UnityPy.load(str(p));o={x.path_id:x for x in e.objects}
for x in o.values():
 if x.type.name!='MonoBehaviour':continue
 n=x.peek_name() or ''
 if ('Overview' in n and any(t in n for t in ['Left','Portrait','FC','SeasonTwelve'])):
  print(x.path_id,n)
  d=x.read_typetree()
  if 'references' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree()
  print('USINGS',[(u['alias'],u['asset']['m_PathID']) for u in d.get('m_Usings',[])])
  for i,r in rr.items():
   a=r.get('data',{})
   if a.get('m_FullTypeName')!='SI.Bindable.SIText':continue
   sd=rr[a['m_SerializedData']['rid']]['data'];ix=a.get('m_RuleIndex',-1);ps=s['m_Rules'][ix]['m_Properties'] if ix>=0 else []
   font=[s['dimensions'][v['valueIndex']]['value'] for p in ps if p['m_Id']==65537 for v in p['m_Values'] if v['m_ValueType']==3]
   print(i,sd.get('name'),font,a.get('m_Classes'))
