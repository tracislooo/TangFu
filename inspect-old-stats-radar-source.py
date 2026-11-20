from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
state=json.loads(Path('current-old-left-fc-hidden-overview.json').read_text('utf8'));out=Path(state['manifest']).parent;e=UnityPy.load(str(out/'backup-game/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));o={x.path_id:x for x in e.objects};d=o[-950000000000162].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree()
for i in [6298,6228,1035,1026,1043]:
 a=rr[i]['data'];print(i,a);sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print('SD',str(sd)[-1700:]);idx=a.get('m_RuleIndex',-1);print('STYLE',[(p['m_Id'],[(h['m_ValueType'],s[{2:'floats',3:'dimensions',4:'colors',7:'strings'}.get(h['m_ValueType'],'strings')][h['valueIndex']]if h['m_ValueType']in [2,3,4,7]else h['valueIndex'])for h in p['m_Values']])for p in s['m_Rules'][idx]['m_Properties']]if idx>=0 else [])
print('ALIASES',[u for u in d['m_Usings']if u['alias']=='PlayerReportBansBlock'])
