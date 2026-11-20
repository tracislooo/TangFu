from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));p=Path(cfg['bundle_root'])/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
e=UnityPy.load(str(p))
for o in e.objects:
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if n not in ['ClubInfoReportBlock','ClubHistoryHonourCardRow','ClubHistoryHonours_4x4_Row','ClubOverview','ClubOverviewBlock','ClubOverviewEightPanelBody','ClubHistoryHonoursBlock']:continue
 d=o.read_typetree();(Path(__file__).parent/('target-'+n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
 print(n,o.path_id)
 rr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
 for i,r in rr.items():
  a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if re.search('honour|HistoryHonours',str(s),re.I):print(i,a.get('m_Parent'),a.get('m_FullTypeName'),a.get('m_TemplateAlias'),a.get('m_Properties'),s)

