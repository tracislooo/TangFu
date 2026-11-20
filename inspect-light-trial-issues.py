"""Read-only tracing of the roster's remaining neutral paint overrides."""
from pathlib import Path
import json, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
base=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
names={'PlayerNameButton','OutsideMatchSquare_PlayerNameButton','OutsideMatchSquare_PlayerNameCell',
       'TFClubSquadOverviewRosterPlayer','SquadOverviewSidebar','tile-figma-base-template',
       'tile-figma-background-template','tile-figma-carousel-additional-title-template',
       'TacticsTile_4x4','TrainingTile_4x4','SquadDynamicsTile_4x4','PlayerNameCell',
       'tile-figma-dual-title-template','text-cell-medium','text-cell-small'}
result=[]
for bn in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',
           'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
    obs={o.path_id:o for o in UnityPy.load(str(base/bn)).objects}
    for ob in obs.values():
        if ob.type.name!='MonoBehaviour' or ob.peek_name() not in names:continue
        d=ob.read_typetree()
        if 'inlineSheet' not in d:continue
        sh=obs[d['inlineSheet']['m_PathID']].read_typetree()
        rr={r['rid']:r for r in d['references']['RefIds']}
        nodes=[]
        for rid,rec in rr.items():
            a=rec.get('data',{})
            if 'm_FullTypeName' not in a:continue
            sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
            i=a.get('m_RuleIndex',-1)
            ps=[]
            for p in sh['m_Rules'][i]['m_Properties'] if i>=0 else []:
                if p['m_Id'] not in [65536,458752,196610,458753]:continue
                vals=[]
                for h in p['m_Values']:
                    pool={2:'floats',4:'colors',8:'strings',7:'strings',6:'assets'}.get(h['m_ValueType'])
                    vals.append(sh[pool][h['valueIndex']] if pool else h)
                ps.append((p['m_Id'],vals))
            n={'rid':rid,'type':a['m_FullTypeName'],'name':sd.get('name'),
               'classes':a.get('m_Classes'), 'template':sd.get('templateId'),'paint':ps,'data':sd,
               'overrides':{k:v for k,v in a.items() if 'Override' in k}}
            nodes.append(n)
        result.append({'bundle':bn,'id':ob.path_id,'name':d['m_Name'],'nodes':nodes,'usings':d['m_Usings']})
        print(d['m_Name'],ob.path_id)
        for n in nodes:
            if n['paint'] or 'StyleSetter' in n['type'] or n['template'] or n['type'].endswith('SIText'):
                print(n['rid'],n['type'].split('.')[-1],n['name'],n['template'],n['classes'],n['paint'])
                if n['overrides']:print(json.dumps(n['overrides'],ensure_ascii=False)[:1900])
(R/'light-ui-inspection'/'remaining-issues.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
