import json
from pathlib import Path
for pid in [-940000000010000,-941100000001020]:
 d=json.loads(Path('inspect-old-fc-'+str(pid)+'.json').read_text('utf8'));rr={r['rid']:r for r in d['references']['RefIds']}
 print('PAGE',pid)
 for i,r in rr.items():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});n=sd.get('name','');al=a.get('m_TemplateAlias','')
  if n in ['RightHiddenAttributesPanel','OverviewProsConsTacticsEqualRow','ThirdOverviewRightColumn','Frame','ThirdOverviewLeftBoundedNoScroll','ThirdOverviewMiddleColumn'] or any(k in n for k in ['Career','ProsCons','TestHidden','Name','Database','ReportOriginal','ScoutHeader']) or 'DatabaseObject' in al:
   print(i,'parent',a.get('m_Parent'),n,al,'kids',a.get('m_Children'),'rule',a.get('m_RuleIndex'));print(' SD',str(sd)[:600] if ('DatabaseObject' in al or 'Name' in n) else '')
