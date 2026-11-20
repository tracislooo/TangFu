"""Six native values over one six-axis radar, with acyclic nested binding scopes."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for filename, names in [('build-fc-player-hover-layout.py', {'write', 'Styles'}),
                        ('add-card-six-ratings.py', {'validate_ui'}),
                        ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named', 'rid_links', 'owned_refs'}),
                        ('add-left-test-overview.py', {'prune'}),
                        ('split-season-radar-two-charts.py', {'add_node', 'graph'})]:
    mod = ast.parse((R / filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names],
                            type_ignores=[]), filename, 'exec'))
spec = importlib.util.spec_from_file_location('radar', R / 'season-radar-builders.py')
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)
TypeTreeHelper.write_value = write
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
indexpath = R / 'current-player-overview-test-variant.json'
previous = json.loads(indexpath.read_text('utf8'))
m = json.loads(Path(previous['manifest']).read_text('utf8'))
assert previous['installed'] and m.get('charts_per_branch') == 2
OUT = R / ('season-six-values-one-radar-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
protected = {str(p): sha(p.read_bytes()) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p.name != W}
for p in [GAME.parent/'catalog.bin', GAME.parent/'catalog.hash', SKIN/'catalog.bin', SKIN/'catalog.hash']:
    protected[str(p)] = sha(p.read_bytes())
GROUPS = [
    dict(panel='SeasonStatsOutfielderPanel', prefix='SeasonStat', radar_indices=[3, 4, 6, 8, 10, 11],
         radar_fields=['ExpectedGoalsPer90', 'ShotsOnTargetPer90', 'ExpectedAssistsPer90', 'PassCompletedPer90', 'TacklesCompletedPer90', 'KeyHeadersPer90'],
         values=[('GamesWonAndPlayed','获胜/场次'), ('PlayerOfTheMatchAwards','当场最佳'), ('Goals','进球'),
                 ('ChancesCreated','创造机会'), ('KeyPasses','关键传球'), ('KeyTackles','关键抢断')]),
    dict(panel='SeasonStatsGoalkeeperPanel', prefix='GoalkeeperStat', radar_indices=[3, 4, 5, 6, 7, 8],
         radar_fields=['ExpectedGoalsPreventedPer90', 'TotalSavesPer90', 'ConcededPer90', 'PossessionWonPer90', 'PossessionLostPer90', 'PassCompletedPer90'],
         values=[('GamesWonAndPlayed','获胜/场次'), ('PlayerOfTheMatchAwards','当场最佳'), ('Clearances','解围'),
                 ('PenaltiesFaced','点球失球/面对'), ('MinutesPerGoalConceded','失球间隔(分)'), ('GoalMistakes','致命失误')]),
]
tx, audits = [], []
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    path = folder / W
    before = path.read_bytes()
    env = UnityPy.load(before)
    obs = {o.path_id:o for o in env.objects}
    oldhash = {pid:sha(o.get_raw_data()) for pid,o in obs.items()}
    source = obs[-950000000000168].read_typetree()
    doc = copy.deepcopy(source)
    sheet = obs[source['inlineSheet']['m_PathID']].read_typetree()
    st = Styles(sheet)
    oldprivate = obs[m['stats']].read_typetree()
    main = obs[m['page']].read_typetree()
    mr = refs(main)
    plain = (copy.deepcopy(mr[1291]),copy.deepcopy(mr[mr[1291]['data']['m_SerializedData']['rid']]))
    setter_proto = (copy.deepcopy(mr[1167]),copy.deepcopy(mr[mr[1167]['data']['m_SerializedData']['rid']]))
    sw = named(doc,'SeasonStatsIsGoalkeeperSwitch')
    rr = refs(doc)
    switch_proto = (copy.deepcopy(rr[sw]),copy.deepcopy(rr[rr[sw]['data']['m_SerializedData']['rid']]))
    def fill(width, height=None, grow=1, direction='column'):
        p=[st.p(131105,width),st.p(131097,st.px(0)),st.p(131096,st.px(0)),
           st.p(131084,st.num(grow)),st.p(131085,st.num(1)),st.p(131073,st.en('stretch')),
           st.p(131083,st.en(direction))]
        if grow:p.append(st.p(131082,st.px(0)))
        if height is not None:p.append(st.p(131087,height))
        return p
    for group in GROUPS:
        panel = named(doc,group['panel'])
        rr=refs(doc)
        oldchildren=list(rr[panel]['data']['m_Children'])
        table=add_node(doc,plain,panel,'SeasonSixValuesTable')
        rr=refs(doc)
        st.edit(rr[table],fill(st.pct(100),st.px(56),0)+[st.p(131085,st.num(0)),st.p(131090,st.px(4))],reset=True)
        rows=[add_node(doc,plain,table,'SeasonSixValuesRow'+str(i+1))for i in range(2)]
        rr=refs(doc)
        for row in rows:
            st.edit(rr[row],fill(st.pct(100),st.px(28),0,'row')+[st.p(131085,st.num(0))],reset=True)
        for j,(field,title) in enumerate(group['values']):
            cell=named(doc,group['prefix']+'Cell_'+field)
            rr=refs(doc)
            oldparent=rr[cell]['data']['m_Parent']['rid']
            rr[oldparent]['data']['m_Children'].remove({'rid':cell})
            rr[cell]['data']['m_Parent']={'rid':rows[j//3]}
            rr[rows[j//3]]['data']['m_Children'].append({'rid':cell})
            st.edit(rr[cell],fill(st.px(0),st.px(28),1)+[st.p(131085,st.num(1))],reset=True)
            title_node=named(doc,group['prefix']+'Title_'+field)
            ts=data(rr,title_node)
            ts.update(text=title,DebugDisplay=title,text_UxmlAttributeFlags=1)
            st.edit(rr[title_node],[st.p(65537,st.px(8)),st.p(131087,st.px(15)),st.p(131096,st.px(15)),st.p(131094,st.px(15))])
            for i in owned_refs(rr,cell):
                if rr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText' and i!=title_node:
                    st.edit(rr[i],[st.p(65537,st.px(10)),st.p(131087,st.px(13)),st.p(131096,st.px(13)),st.p(131094,st.px(13))])
        for child in oldchildren:
            prune(doc,child['rid'])
        rr=refs(doc)
        st.edit(rr[panel],fill(st.pct(100),st.pct(100)),reset=True)
        oldr=refs(oldprivate)
        oldsetter=oldr[named(oldprivate,group['panel'])]['data']['m_Children'][0]['rid']
        oldsd=data(oldr,oldsetter)
        outer=add_node(doc,setter_proto,panel,'SeasonRadarNumericValues')
        rr=refs(doc)
        outer_sd=data(rr,outer)
        outer_sd.update(ValueVariables=[copy.deepcopy(v)for v in oldsd['ValueVariables']if not v['m_scopeValue']['m_serializedData'].startswith('{')],
                        ReferenceVariables=[],BindFunction=[copy.deepcopy(oldsd['BindFunction'][i])for i in group['radar_indices']])
        prefixes=['seasonRadar'+str(i)for i in group['radar_indices']]
        for prefix in prefixes:
            outer_sd['ReferenceVariables'].extend(copy.deepcopy(v)for v in oldsd['ReferenceVariables']if v['m_name']in[prefix+s for s in ['Raw','Plot','Max','Valid']])
        for key in ['ValueVariables','ReferenceVariables','BindFunction']:outer_sd[key+'_UxmlAttributeFlags']=1
        inner=add_node(doc,setter_proto,outer,'SeasonRadarPointReferences')
        rr=refs(doc)
        inner_sd=data(rr,inner)
        inner_sd.update(ValueVariables=[copy.deepcopy(v)for v in oldsd['ValueVariables']if v['m_name']in[p+'Point'for p in prefixes]],
                        ReferenceVariables=[dict(m_type={'id':0},m_initToNull=1,m_name='radarSixPoints')],
                        BindFunction=[rb.function(oldsd['BindFunction'][12]['m_target']['m_guid'],
                            rb.path_list_arg([p+'Point'for p in prefixes]),rb.path_arg('radarSixPoints'))])
        for key in ['ValueVariables','ReferenceVariables','BindFunction']:inner_sd[key+'_UxmlAttributeFlags']=1
        gate=add_node(doc,switch_proto,inner,'SeasonSelectedRadarReady')
        rr=refs(doc)
        gs=data(rr,gate)
        gs['Binding']=dict(m_kind=2,m_direct={'Path':{'m_path':''},'Nullable':0},
                           m_visualFunction=rb.function('a4dffe7b331c90949b43d2d4e3155117',rb.path_arg('radarSixPoints')))
        gs['Binding_UxmlAttributeFlags']=1
        waiting=add_node(doc,plain,gate,'SeasonSelectedRadarWaiting')
        # Both branches intentionally use the same chart prototype; binding paths
        # and label data are supplied by each branch's own nested scope.
        candidate=next(i for i,r in oldr.items()if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMSpiderChart')
        chart_proto=(copy.deepcopy(oldr[candidate]),copy.deepcopy(oldr[oldr[candidate]['data']['m_SerializedData']['rid']]))
        chart=add_node(doc,chart_proto,gate,'SeasonSelectedSixAxisRadar')
        rr=refs(doc)
        rr[chart]['data']['m_Classes'] = ['fmspiderchartlarge']
        cd=data(rr,chart)
        cd.update(SpiderChartVertices=6,SpiderChartVertices_UxmlAttributeFlags=1,
                  SpiderChartRadiusPercentage=28.,LabelDistanceFromChart=10.)
        cd['BindDataFunction']=rb.function(cd['BindDataFunction']['m_target']['m_guid'],rb.path_arg('radarSixPoints'),
                                         rb.bool_arg(False),rb.bool_arg(False),rb.path_arg('radarZero'))
        for node in [outer,inner,gate,waiting,chart]:st.edit(rr[node],fill(st.pct(100)),reset=True)
    doc.update(m_Name='LeftTestSeasonSixValuesAndSixAxisRadar',inlineSheet={'m_FileID':0,'m_PathID':m['style']},
               m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(b'season-six-values-one-radar-v1')))[0])
    sheet['m_Name']=doc['m_Name']+'Style'
    graph(doc)
    validate_ui(doc,sheet)
    assert data(refs(doc),sw)==data(refs(source),sw)
    label=obs[m['label']].read_typetree()
    ls=obs[m['label_style']].read_typetree()
    lst,lr=Styles(ls),refs(label)
    labelroot=named(label,'SeasonRadarAxisLabel')
    lst.edit(lr[labelroot],[lst.p(131105,lst.px(72)),lst.p(131087,lst.px(24))])
    for i,r in lr.items():
        if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':
            lst.edit(r,[lst.p(65537,lst.px(9)),lst.p(131087,lst.px(12))])
    changed={m['stats']:doc,m['style']:sheet,m['label_style']:ls}
    for pid,d in changed.items():obs[pid].save_typetree(d)
    output=env.file.save(packer='lz4')
    check={o.path_id:o for o in UnityPy.load(output).objects}
    assert set(check)==set(obs)
    for pid,h in oldhash.items():
        if pid not in changed:assert sha(check[pid].get_raw_data())==h,('unrelated object',tag,pid)
        else:assert check[pid].read_typetree()==changed[pid],('roundtrip',tag,pid)
    src,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    src.parent.mkdir();backup.parent.mkdir()
    src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(path),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
    audits.append(dict(target=tag,native_six_value_bindings_preserved=True,scopes_separated=True,
                       tables=[3,3],charts_per_branch=1,axes_per_chart=6))
    print('Verified '+tag+': six native values, one selected six-axis radar, separate calculation/reference scopes.',flush=True)
for row in tx:assert sha(Path(row['target']).read_bytes())==row['before']
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],
         protected_sha256=protected,groups=GROUPS,charts_per_branch=1,axes_per_chart=6,native_value_rows=[3,3],
         separate_numeric_and_dynamic_reference_scopes=True,audits=audits)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8').replace('.codex-fitness-','.codex-season-six-'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
idx=dict(previous,manifest=str(OUT/'manifest.json'),script=str(Path(__file__).resolve()),installed=False,
         installed_verified=False,runtime_verified=False,previous_manifest=previous['manifest'],
         layout='six native values in two rows above one selected six-axis radar',
         runtime_failure_fixed='separate numeric calculation scope from derived point-reference scope')
idx.pop('verification',None)
indexpath.write_text(json.dumps(idx,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(prepared=True,output=str(OUT),files=len(tx)),ensure_ascii=False))
