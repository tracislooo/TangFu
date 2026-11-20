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
    matches=[r for r in rs.values() if rs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name]
    assert len(matches)==1,name
    return matches[0]
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
centers=[144+(296-144)*i/3 for i in range(4)]
changes=[]
for name,center,height in zip(['TooltipCard_NationFlag_Small','TooltipCard_TeamIcon32px','TooltipCardPosition','TooltipCardHeight'],centers,[28,46,30,30]):
    top=f32(center-height/2)
    st.edit(named(name),[st.p(131104,st.px(top))])
    changes.append({'name':name,'top':top,'center':center})
background=named('TooltipCardLeftInfoBackdrop')
removed={background['rid'],background['data']['m_SerializedData']['rid']}
parent=rs[background['data']['m_Parent']['rid']]['data']
parent['m_Children']=[c for c in parent['m_Children'] if c['rid']!=background['rid']]
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
assert changes[0]['top']==130 and changes[-1]['top']==281
assert all(abs((centers[i+1]-centers[i])-(152/3))<1e-9 for i in range(3))
obj.save_typetree(doc);so.save_typetree(sheet)
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(obs)
for i,o in check.items():
    if i in [obj.path_id,so.path_id]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(doc if i==obj.path_id else sheet,sort_keys=True)
    else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i],i
out=R/('hover-card-info-spacing-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[p])
(out/N).write_bytes(output)
for p,b in before.items():assert (p/N).read_bytes()==b
try:
    for p in [GAME,SKIN]:(p/N).write_bytes(output)
    for p in [GAME,SKIN]:assert (p/N).read_bytes()==output
except BaseException:
    for p,b in before.items():(p/N).write_bytes(b)
    raise
report={'installed':True,'runtime_verified':False,'output':str(out),'changes':changes,'center_spacing':152/3,'black_backdrop_removed':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
