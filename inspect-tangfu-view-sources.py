from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
p=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root']);out=R/'tangfu-view-research';out.mkdir(exist_ok=True)
for key in ['tableviews','tablefactories']:
 e=UnityPy.load(str(p/f'ui-{key}_assets_all.bundle'));lines=[]
 for ob in e.objects:
  if ob.type.name!='MonoBehaviour':continue
  n=ob.peek_name();d=ob.read_typetree()
  if key=='tableviews' and (n in ['FirstTeamTableSelectionInfo','FirstTeamSquadAndYouthTeamSquadCollection'] or ('TacticTeamSelection' in n and 'InMatch' not in n)):
   (out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8');lines.append({'pid':ob.path_id,'name':n,'columns':[c['m_columnID'] for c in d.get('m_tableView',{}).get('m_tableConfig',[])]})
  if key=='tablefactories' and (n=='PlayerTableFactory' or ('Tactic' in n and 'm_rowData' in d)):
   (out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8');lines.append({'pid':ob.path_id,'name':n,'columns':[c for c in d['m_rowData'] if re.search('condition|sharpness|morale|happ|ability|age|wage|value',c['m_id'],re.I)]})
 (out/(key+'-summary.json')).write_text(json.dumps(lines,ensure_ascii=False,indent=2),'utf8')
print(str(out))
