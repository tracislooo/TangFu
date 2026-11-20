from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={p:(p/N).read_bytes() for p in [GAME,SKIN]}
assert before[GAME]==before[SKIN]
env=UnityPy.load(before[GAME]);obs={o.path_id:o for o in env.objects}
hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in obs.items()}
oldwrite=TypeTreeHelper.write_value
helpers=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
obj=obs[-960000000003010];doc=obj.read_typetree();rs={r['rid']:r for r in doc['references']['RefIds']}
so=obs[doc['inlineSheet']['m_PathID']];sheet=so.read_typetree();st=Styles(sheet)
def named(name):
    items=[r for r in rs.values() if rs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name]
    assert len(items)==1,name
    return items[0]
for name,y in [('TooltipCardPosition',237),('TooltipCardHeight',301)]:
    st.box(named(name),28,y,92,30)
    st.edit(named(name),[st.p(65537,st.px(16)),st.p(65546,st.en('middle-center')),st.p(65543,st.en('bold'))])
for name,x in [('TooltipCard_NationFlag_Small',53),('TooltipCard_TeamIcon32px',51)]:
    st.edit(named(name),[st.p(131089,st.px(x))])

bg=copy.deepcopy(rs[1299]);sd=copy.deepcopy(rs[rs[1299]['data']['m_SerializedData']['rid']])
bg['rid'],sd['rid']=52000,52001
assert 52000 not in rs and 52001 not in rs
bg['data'].update(m_Id=1970000002,m_Parent={'rid':1299},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_SerializedData={'rid':52001})
sd['data'].update(uxmlAssetId=1970000002,name='TooltipCardLeftInfoBackdrop',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
st.box(bg,24,88,100,246)
alpha=struct.unpack('<f',struct.pack('<f',128/255))[0]
st.edit(bg,[st.p(458752,st.h(4,{'r':0.0,'g':0.0,'b':0.0,'a':alpha})),st.p(262147,st.px(8))])
rs[52000],rs[52001]=bg,sd
children=rs[1299]['data']['m_Children']
index=next(i for i,c in enumerate(children) if c['rid']==1301)+1
children.insert(index,{'rid':52000})
doc['references']['RefIds']=list(rs.values())
for r in rs.values():
    a=r.get('data',{})
    for c in a.get('m_Children',[]):assert rs[c['rid']]['data']['m_Parent']['rid']==r['rid']
    i=a.get('m_SerializedData',{}).get('rid',-2)
    if i!=-2:assert rs[i]['data']['uxmlAssetId']==a['m_Id']
obj.save_typetree(doc);so.save_typetree(sheet)
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(obs)
for i,o in check.items():
    if i in [obj.path_id,so.path_id]:
        assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(doc if i==obj.path_id else sheet,sort_keys=True)
    else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i],i
out=R/('hover-card-info-column-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[p])
(out/N).write_bytes(output)
for p,b in before.items():assert (p/N).read_bytes()==b
try:
    for p in [GAME,SKIN]:(p/N).write_bytes(output)
    for p in [GAME,SKIN]:assert (p/N).read_bytes()==output
except BaseException:
    for p,b in before.items():(p/N).write_bytes(b)
    raise
report={'installed':True,'runtime_verified':False,'output':str(out),'position_and_height_font_before':12,'position_and_height_font_after':16,
        'column_center_x':74,'four_row_centers_y':[124,188,252,316],'backdrop':{'x':24,'y':88,'width':100,'height':246,'black_opacity':128/255},
        'only_changed_assets':['TooltipFCPlayerCard','TooltipFCPlayerCard_Style'],'other_assets_unchanged':len(obs)-2}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
