from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
S='ui-styles_assets_default.bundle'
before={p/n:(p/n).read_bytes() for p in [GAME,SKIN] for n in [W,S] if (p/n).exists()}
for n in [W,S]:
    if SKIN/n in before:assert before[GAME/n]==before[SKIN/n],n
env={n:UnityPy.load(before[GAME/n]) for n in [W,S]}
obs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
hashes={n:{i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in os.items()} for n,os in obs.items()}
expected={W:{},S:{}}
oldwrite=TypeTreeHelper.write_value
helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def named(n,name):
    matches=[o for o in obs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name]
    assert len(matches)==1,(name,len(matches))
    return matches[0]
def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
def color(style,r,g,b,a):
    return style.h(4,{k:struct.unpack('<f',struct.pack('<f',v/255))[0] for k,v in zip(['r','g','b','a'],[r,g,b,a])})
card=named(W,'TooltipFCPlayerCard');d=card.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
so=obs[W][d['inlineSheet']['m_PathID']];sheet=so.read_typetree();st=Styles(sheet)
def node(name):
    matches=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name]
    assert len(matches)==1,name
    return matches[0]
st.edit(node('OverviewCardGoalkeeperSwitch'),[st.p(131104,st.px(390))])
st.edit(node('TooltipCardPlayerName'),[st.p(65537,st.px(23)),st.p(131104,st.px(342))])
st.edit(node('PersonPictureFrame'),[st.p(327681,st.num(.95),st.num(.95)),st.p(131104,st.px(100))])
# Four entries share a 64px centre-to-centre pitch down the left of the portrait.
for name,x,y in [('TooltipCard_NationFlag_Small',49,110),('TooltipCard_TeamIcon32px',50,165)]:
    st.edit(node(name),[st.p(131089,st.px(x)),st.p(131104,st.px(y)),st.p(327681,st.num(1.43),st.num(1.43))])
position=node('TooltipCardPosition')
st.box(position,40,237,88,30)
st.edit(position,[st.p(65537,st.px(12)),st.p(65546,st.en('middle-left')),st.p(65552,st.en('normal'))])

# Preserve the game's localized, unit-aware height formatter from the player-page card.
full=obs[W][-930000000001001].read_typetree();fr={r['rid']:r for r in full['references']['RefIds']}
height_sd=next(r for r in fr.values() if r.get('data',{}).get('name')=='CardHeightValue')
height_node=next(r for r in fr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==height_sd['rid'])
hn,hs=copy.deepcopy(height_node),copy.deepcopy(height_sd)
hn['rid'],hs['rid']=51000,51001
hn['data'].update(m_Id=1970000000,m_Parent={'rid':1299},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_SerializedData={'rid':51001})
hs['data'].update(uxmlAssetId=1970000000,name='TooltipCardHeight',name_UxmlAttributeFlags=1)
rr[51000],rr[51001]=hn,hs;rr[1299]['data']['m_Children'].append({'rid':51000})
st.box(hn,40,301,88,30)
st.edit(hn,[st.p(65537,st.px(12)),st.p(65546,st.en('middle-left'))])
for n in [rr[1001],rr[1299]]:st.edit(n,[st.p(458752,color(st,0,0,0,0))])
d['references']['RefIds']=list(rr.values())
save(W,card,d);save(W,so,sheet)

# Apply transparency to this player popup alone; all other tooltips retain their styles.
preview=named(W,'PlayerReportPreviewTooltip');pd=preview.read_typetree();pr={r['rid']:r for r in pd['references']['RefIds']}
psobj=obs[W][pd['inlineSheet']['m_PathID']];ps=psobj.read_typetree();pst=Styles(ps)
tooltip=next(r for r in pr.values() if r['type']['class']=='Tooltip/UxmlSerializedData')
tooltip['data']['TooltipClassOverride']='tf27-fc-preview-transparent'
tooltip['data']['TooltipClassOverride_UxmlAttributeFlags']=1
pst.edit(pr[1010],[pst.p(458752,color(pst,0,0,0,0))])
fc=next(r for r in pr.values() if r.get('data',{}).get('m_TemplateAlias')=='FCPlayerCard')
pst.edit(fc,[pst.p(458752,color(pst,0,0,0,0))])

# A background behind the right-hand region only. Insert before the templates.
background=copy.deepcopy(pr[1002]);bg_sd=copy.deepcopy(pr[pr[1002]['data']['m_SerializedData']['rid']])
background['rid'],bg_sd['rid']=61000,61001
background['data'].update(m_Id=1970000001,m_Parent={'rid':1010},m_Children=[],m_RuleIndex=-1,
                          m_Classes=[],m_SerializedData={'rid':61001})
bg_sd['data'].update(uxmlAssetId=1970000001,name='RightPanelBackground',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
pst.box(background,424,12,844,616)
pst.edit(background,[pst.p(458752,color(pst,18,25,34,245)),pst.p(262147,pst.px(8))])
pr[61000],pr[61001]=background,bg_sd
pr[1010]['data']['m_Children'].insert(0,{'rid':61000})
pd['references']['RefIds']=list(pr.values())
save(W,preview,pd);save(W,psobj,ps)

styleobj=named(S,'AlwaysAppliedStyleSheet');globalstyle=styleobj.read_typetree();gst=Styles(globalstyle)
selector='tf27-fc-preview-transparent'
assert selector not in str(globalstyle['m_Rules'])
index=len(globalstyle['m_Rules'])
globalstyle['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':selector,'m_Type':3}],'m_PreviousRelationship':0}],'ruleIndex':index}],
    'm_Properties':[gst.p(458752,color(gst,0,0,0,0)),gst.p(458753,{'m_ValueType':1,'valueIndex':0}),
                    gst.p(262146,gst.px(0)),gst.p(262147,gst.px(0)),gst.p(262148,gst.px(0)),gst.p(262151,gst.px(0))],'line':-1})
save(S,styleobj,globalstyle)

for doc,s in [(d,sheet),(pd,ps)]:
    refs={r['rid']:r for r in doc['references']['RefIds']}
    assert len(refs)==len(doc['references']['RefIds'])
    for r in refs.values():
        a=r.get('data',{})
        for child in a.get('m_Children',[]):assert refs[child['rid']]['data']['m_Parent']['rid']==r['rid']
        sid=a.get('m_SerializedData',{}).get('rid',-2)
        if sid!=-2:assert refs[sid]['data']['uxmlAssetId']==a['m_Id']
        if a.get('m_RuleIndex',-1)>=0:assert a['m_RuleIndex']<len(s['m_Rules'])
assert hs['data']['TextBinding']==height_sd['data']['TextBinding']
assert 390+55<478
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects}
    assert set(check)==set(obs[n])
    for i,o in check.items():
        if i in expected[n]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[n][i],sort_keys=True),(n,i)
        else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[n][i],(n,i)
assert -930000000001001 not in expected[W]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('hover-fc-card-spacing-'+stamp);out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:
    backup=out/('backup-'+tag);backup.mkdir()
    for n in [W,S]:
        if p/n in before:(backup/n).write_bytes(before[p/n])
for n,b in outputs.items():(out/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
try:
    for p in [GAME,SKIN]:
        for n,b in outputs.items():(p/n).write_bytes(b)
    for p in [GAME,SKIN]:
        for n,b in outputs.items():assert (p/n).read_bytes()==b
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    for p in [GAME,SKIN]:
        for n in [W,S]:
            if p/n not in before and (p/n).exists():(p/n).unlink()
    raise
report={'installed':True,'runtime_verified':False,'output':str(out),'name_font':23,'name_top':342,
        'ratings_top_before':415,'ratings_top_after':390,'portrait_scale':.95,'portrait_top_before':105,'portrait_top_after':100,
        'flag_and_crest_scale_before':1.3,'flag_and_crest_scale_after':1.43,'left_column_center_pitch':64,
        'height_uses_native_localized_formatter':True,'left_popup_background':'transparent','right_popup_background':'dark',
        'popup_dimensions_unchanged':[1280,640],'main_player_page_unchanged':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
