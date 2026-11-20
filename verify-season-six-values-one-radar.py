"""Verify requested fields, native table bindings and an acyclic radar scope tree."""
from pathlib import Path
import ast
import hashlib
import json
import struct
import sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
mod=ast.parse((R/'add-two-portrait-hidden-overviews.py').read_text('utf8'))
names={'refs','data','named','owned_refs','rid_links'}
exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),'helpers','exec'))
indexpath=R/'current-player-overview-test-variant.json'
idx=json.loads(indexpath.read_text('utf8'))
OUT=Path(idx['manifest']).parent
m=json.loads((OUT/'manifest.json').read_text('utf8'))
tx=json.loads((OUT/'transaction.json').read_text('utf8'))
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
installed='--installed'in sys.argv
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return{o.path_id:o for o in UnityPy.load(str(p)).objects}
def args(fn):
    b=bytes(fn['m_inputs']['m_variable']['m_argumentBytes']);pos=1;out=[]
    for _ in range(b[0]):
        n=struct.unpack_from('<I',b,pos)[0];out.append(b[pos+4:pos+4+n]);pos+=4+n
    assert pos==len(b)
    return out
results=[]
for tag,live in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
    old=load(OUT/('backup-'+tag)/W)
    new=load((live if installed else OUT/tag)/W)
    assert set(new)==set(old)
    allowed={m['stats'],m['style'],m['label_style']}
    for pid,o in old.items():
        if pid not in allowed:assert o.get_raw_data()==new[pid].get_raw_data(),('unrelated object',tag,pid)
    doc=new[m['stats']].read_typetree()
    native=new[-950000000000168].read_typetree()
    rr,nr=refs(doc),refs(native)
    switch=named(doc,'SeasonStatsIsGoalkeeperSwitch')
    assert data(rr,switch)==data(nr,switch)
    for group in m['groups']:
        panel=named(doc,group['panel'])
        table,outer=[c['rid']for c in rr[panel]['data']['m_Children']]
        rows=rr[table]['data']['m_Children']
        assert len(rows)==2
        values=[]
        for row in rows:
            cells=rr[row['rid']]['data']['m_Children'];assert len(cells)==3
            for cell in cells:
                name=data(rr,cell['rid'])['name'];values.append(name)
                original=named(native,name)
                for rid in owned_refs(nr,original):
                    r=nr[rid]
                    if r.get('type',{}).get('class','').endswith('/UxmlSerializedData'):
                        d=r.get('data',{})
                        if d.get('name','').startswith(group['prefix']+'Title_'):continue
                        assert rr[rid]==r,('native numeric/fallback binding changed',name,rid)
        assert values==[group['prefix']+'Cell_'+field for field,_ in group['values']]
        outerdata=data(rr,outer)
        assert len(outerdata['BindFunction'])==6
        assert all(not v['m_scopeValue']['m_serializedData'].startswith('{')for v in outerdata['ValueVariables'])
        outerfields={v['m_name']for v in outerdata['ReferenceVariables']}
        outerconstants={v['m_name']for v in outerdata['ValueVariables']}
        assert len(outerfields)==24
        for fn,field in zip(outerdata['BindFunction'],group['radar_fields']):
            assert args(fn)[0].endswith(('SeasonStats.'+field).encode())
        inner,=[c['rid']for c in rr[outer]['data']['m_Children']]
        innerdata=data(rr,inner)
        assert len(innerdata['ValueVariables'])==6 and len(innerdata['BindFunction'])==1
        innerfields={v['m_name']for v in innerdata['ReferenceVariables']}
        assert innerfields=={'radarSixPoints'}
        for value in innerdata['ValueVariables']:
            ref=json.loads(value['m_scopeValue']['m_serializedData'])
            dependencies={x['BindingPath']for x in ref['m_data']}
            assert dependencies<=outerfields|outerconstants
            assert not dependencies&innerfields, 'Derived values must not depend on outputs of their own initializer'
        listargs=args(innerdata['BindFunction'][0]);assert listargs[0][1+listargs[0][0]]==6
        gate,=[c['rid']for c in rr[inner]['data']['m_Children']]
        gating=data(rr,gate)['Binding']['m_visualFunction']
        assert gating['m_target']['m_guid']=='a4dffe7b331c90949b43d2d4e3155117'
        assert args(gating)[0].endswith(b'radarSixPoints')
        empty,chart=[c['rid']for c in rr[gate]['data']['m_Children']]
        assert rr[empty]['data']['m_Children']==[]
        cd=data(rr,chart)
        assert cd['SpiderChartVertices']==6
        assert args(cd['BindDataFunction'])[0].endswith(b'radarSixPoints')
        assert cd['LabelsTemplate']['m_AssetGUID']==m['label_guid']
    # Native season/league setup outside the two content panels is untouched.
    excluded=set()
    for group in m['groups']:excluded|=owned_refs(nr,named(native,group['panel']))
    for rid,ref in nr.items():
        if rid not in excluded:assert rr[rid]==ref,('season context changed',rid)
    results.append(dict(target=tag,table_rows=[3,3],chart_count_per_branch=1,radar_axes=6,
                        selected_fields_exact=True,native_values_and_season_context_preserved=True,
                        derived_scope_has_no_self_dependency=True,chart_creation_guarded=True,
                        all_other_objects_byte_identical=True))
for row in tx:
    assert sha(Path(row['backup']).read_bytes())==row['before']
    assert sha(Path(row['target']if installed else row['source']).read_bytes())==row['after']
for path,h in m['protected_sha256'].items():assert sha(Path(path).read_bytes())==h
report=dict(passed=True,installed=installed,runtime_verified=False,files=len(tx),results=results)
p=OUT/('verification-installed.json'if installed else'verification-prepared.json')
p.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
if installed:
    idx.update(installed=True,installed_verified=True,verification=str(p))
    indexpath.write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=False))
