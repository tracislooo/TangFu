"""Read-only regression checks for the nickname and inbox/tactics fixes."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
D='ui-styles_assets_default.bundle'
V='ui-tableviews_assets_all.bundle'
F='ui-tablefactories_assets_all.bundle'

def verify(root,fallback=None):
    def path(n):
        p=root/n
        return p if p.exists() else fallback/n
    oo={n:{o.path_id:o for o in UnityPy.load(str(path(n))).objects} for n in [W,D,V,F]}
    doc=oo[W][5775949770471550939].read_typetree()
    rr={r['rid']:r.get('data',{}) for r in doc['references']['RefIds']}
    buttons=[d for d in rr.values() if d.get('name')=='PlayerTouchbarNickname']
    assert len(buttons)==1,'Missing nickname button'
    button=buttons[0]
    assert button['ActionId']==1295398490 and button['RecordsBinding']['m_path']=='Person'
    assert button['ShowOnlyFirstButton']==1
    sheet=next(o.read_typetree() for o in oo[D].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
    assert any(any(p['m_Value']=='player-touchbar-nickname-button' for c in r['m_ComplexSelectors'] for s in c['m_Selectors'] for p in s['m_Parts']) for r in sheet['m_Rules']),'Missing nickname scoped style'
    doc=oo[W][1236674676499774051].read_typetree();rr={r['rid']:r['data'] for r in doc['references']['RefIds'] if 'data' in r}
    sheet=oo[W][doc['inlineSheet']['m_PathID']].read_typetree()
    props={p['m_Id']:p for p in sheet['m_Rules'][rr[1015]['m_RuleIndex']]['m_Properties']}
    for k in [131105,131087,131095,131094,131097,131096]:assert sheet['dimensions'][props[k]['m_Values'][0]['valueIndex']]=={'unit':1,'value':192.},'Inbox portrait size regressed'
    views=[]
    for o in oo[V].values():
        if o.type.name!='MonoBehaviour':continue
        n=o.peek_name()
        if n=='FirstTeamSquadAndYouthTeamSquadCollection':assert o.read_typetree()['m_tableViewSettings'][0]['PropertyValue']['m_PathID']==-991111000002000
        if not n.startswith('TacticTeamSelection') or 'InMatch' in n:continue
        d=o.read_typetree();cols={c['m_columnID']:c for c in d.get('m_tableView',{}).get('m_tableConfig',[])}
        if 'condition' not in cols:continue
        assert 'sharpness' not in cols and 'tactics-fatigue-value' in cols
        for k,width in [('condition',90),('tactics-fatigue-value',40)]:
            md=cols[k]['m_columnMetadata'];assert md['m_widthOverride']==width and md['m_minWidthOverride']==width,(n,k)
        views.append(n)
    assert len(views)==6,views
    fac=oo[F][-7014073910555419620].read_typetree();cols={c['m_id']:c for c in fac['m_rowData']}
    assert cols['positions']['m_allowWidthAutoResizing']==0
    assert cols['condition']['m_defaultWidth']==90 and cols['tactics-fatigue-value']['m_defaultWidth']==40
    return dict(nickname_button=True,nickname_action=1295398490,nickname_scoped_style=True,inbox_portrait_px=192,tangfu_A_default=True,tactics_views=views,health_column_width=90,fatigue_column_width=40)

if __name__=='__main__':
    root=Path(json.loads((R/'current-game-location.json').read_text())['bundle_root']) if len(sys.argv)==1 else Path(sys.argv[1])
    print(json.dumps(verify(root),ensure_ascii=True))
