from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
helper = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n, ast.FunctionDef) and n.name == 'write' or isinstance(n, ast.ClassDef) and n.name == 'Styles'], type_ignores=[]), '<helpers>', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(cfg['bundle_root']), Path(cfg['skin_packages'])
FN = 'ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R / ('shuffle-player-tile-fc-ratings-' + stamp)
out.mkdir()
sp = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(sp); sp.loader.exec_module(cm)
tx, audits, protected = [], [], {}

for tag, root in [('game', GAME), ('skin', SKIN)]:
    before = (root / FN).read_bytes()
    env = UnityPy.load(before); obs = {o.path_id:o for o in env.objects}
    hashes = {i:sha(o.get_raw_data()) for i,o in obs.items()}
    tile = obs[1519666771143645661]; doc = tile.read_typetree()
    sheetobj = obs[doc['inlineSheet']['m_PathID']]; sheet = sheetobj.read_typetree(); st = Styles(sheet)
    refs = {r['rid']:r for r in doc['references']['RefIds']}
    sourceenv = UnityPy.load(str(root / WN)); sourceobs = {o.path_id:o for o in sourceenv.objects}
    card = sourceobs[-960000000003010].read_typetree()
    cardsheet = sourceobs[card['inlineSheet']['m_PathID']].read_typetree()
    sourcerefs = {r['rid']:r for r in card['references']['RefIds']}
    original_events = {i:copy.deepcopy(refs[i]) for i in [1084,1086,1088,1067,1092]}
    next_rid, next_eid = 300000, 1955000000

    def managed(v):
        if isinstance(v, dict):
            if set(v) == {'rid'}:
                if v['rid'] != -2: yield v['rid']
            else:
                for k,x in v.items():
                    if k != 'm_Parent': yield from managed(x)
        elif isinstance(v,list):
            for x in v: yield from managed(x)

    def import_tree(sd, ss, rootrid, parent):
        global next_rid, next_eid
        sr = {r['rid']:r for r in sd['references']['RefIds']}
        keep, todo = set(), [rootrid]
        while todo:
            i = todo.pop()
            if i in keep: continue
            keep.add(i); todo.extend(managed(sr[i].get('data',{})))
        ridmap = {i:next_rid+j for j,i in enumerate(sorted(keep))}; next_rid += len(keep)
        elements = [sr[i]['data']['m_Id'] for i in sorted(keep) if 'm_Id' in sr[i].get('data',{})]
        emap = {i:next_eid+j for j,i in enumerate(elements)}; next_eid += len(elements)
        def remap(v):
            if isinstance(v,dict):
                if set(v)=={'rid'}: return {'rid':ridmap.get(v['rid'],v['rid'])}
                return {k:emap.get(x,x) if k in ['m_Id','uxmlAssetId','m_ParentId','m_ElementId'] and isinstance(x,int) else remap(x) for k,x in v.items()}
            if isinstance(v,list): return [remap(x) for x in v]
            return v
        rules = {}
        def rule(j):
            if j not in rules:
                r = copy.deepcopy(ss['m_Rules'][j]); r['m_ComplexSelectors']=[]
                for p in r['m_Properties']:
                    for h in p['m_Values']:
                        if h['m_ValueType'] in poolmap:
                            pool=poolmap[h['m_ValueType']]; x=copy.deepcopy(ss[pool][h['valueIndex']]); h['valueIndex']=len(sheet[pool]); sheet[pool].append(x)
                rules[j]=len(sheet['m_Rules']); sheet['m_Rules'].append(r)
            return rules[j]
        for i in sorted(keep):
            r=remap(copy.deepcopy(sr[i])); r['rid']=ridmap[i]; v=r.get('data',{})
            if i==rootrid: v['m_Parent']={'rid':parent}
            if v.get('m_RuleIndex',-1)>=0: v['m_RuleIndex']=rule(v['m_RuleIndex'])
            refs[r['rid']]=r
        return ridmap

    def edit(i, props, reset=False): st.edit(refs[i],props,reset=reset)
    P=st.p
    def detach(i):
        par=refs[i]['data']['m_Parent']['rid']
        refs[par]['data']['m_Children']=[c for c in refs[par]['data']['m_Children'] if c['rid']!=i]
    def move(i,parent):
        detach(i);refs[i]['data']['m_Parent']={'rid':parent};refs[parent]['data']['m_Children'].append({'rid':i})
    # Keep the native picture centered and retain all native selection/favourite events.
    for i in [1057,1059]: move(i,1022)
    edit(1022,[P(131074,st.en('stretch')),P(131105,st.pct(100)),P(131085,st.num(0)),P(131102,st.en('relative'))])
    edit(1025,[P(131102,st.en('absolute')),P(131089,st.pct(12.5)),P(131104,st.pct(14))])
    edit(1027,[P(131102,st.en('absolute')),P(131103,st.pct(12.5)),P(131104,st.pct(14))])
    for i, edge in [(1057,131089),(1059,131103)]:
        refs[i]['data']['m_Classes']=['align-items-center','justify-content-center']
        edit(i,[P(131102,st.en('absolute')),P(edge,st.pct(2)),P(131080,st.px(1)),P(131105,st.pct(32)),P(131087,st.px(22)),P(131084,st.num(0)),P(131085,st.num(0))],True)
    # A private copy of the working FC subtree carries the exact IsGoalkeeper switch and score bindings.
    ratingmap=import_tree(card,cardsheet,1819,1023)
    rating=ratingmap[1819]
    refs[1023]['data']['m_Children'].append({'rid':rating})
    edit(1023,[P(131102,st.en('relative'))])
    edit(rating,[P(131102,st.en('absolute')),P(131089,st.pct(0)),P(131080,st.px(1)),P(131105,st.pct(100)),P(131087,st.pct(45)),P(131084,st.num(0)),P(131085,st.num(0))],True)
    branch_titles=[]; score_guids=set()
    for b in [1777,1821]:
        branch=ratingmap[b];edit(branch,[P(131105,st.pct(100)),P(131087,st.pct(100))],True)
        row=refs[branch]['data']['m_Children'][0]['rid']
        edit(row,[P(131083,st.en('row')),P(131105,st.pct(100)),P(131087,st.pct(100))],True)
        titles=[]
        for c in refs[row]['data']['m_Children']:
            cell=c['rid'];edit(cell,[P(131083,st.en('column')),P(131105,st.pct(struct.unpack('<f',struct.pack('<f',100/6))[0])),P(131087,st.pct(100)),P(131073,st.en('center')),P(131085,st.num(0))],True)
            for index,ch in enumerate(refs[cell]['data']['m_Children']):
                i=ch['rid'];edit(i,[P(131105,st.pct(100)),P(131087,st.pct(42 if index==0 else 58)),P(65537,st.px(10 if index==0 else 13)),P(65546,st.en('middle-center'))])
                sd=refs[refs[i]['data']['m_SerializedData']['rid']]['data']
                if index==0: titles.append(sd['text'])
                else: score_guids.add(sd['TextBinding']['m_visualFunction']['m_target']['m_guid'])
        branch_titles.append(titles)
    assert branch_titles==[['速度','射门','传球','盘带','防守','身体'],['扑救','站位','出球','反应','神经','速度']]
    assert len(score_guids)==11
    # Move the original selection-status switch out of the ratings area.
    move(1030,1022)
    refs[1030]['data']['m_Classes']=[]
    edit(1030,[P(131102,st.en('absolute')),P(131103,st.px(0)),P(131104,st.px(29)),P(131105,st.px(94)),P(131087,st.px(22)),P(458768,st.en('visible'))],True)
    # Embed the label privately so red text applies only to these shuffle tiles.
    label=obs[5653413884780862693].read_typetree(); labelsheet=obs[label['inlineSheet']['m_PathID']].read_typetree()
    oldlabelid=refs[1042]['data']['m_Id']; oldparent=refs[1042]['data']['m_Parent']
    oldsd=refs[1042]['data']['m_SerializedData']['rid']
    wrapper=copy.deepcopy(refs[1041]); wrapper['rid']=1042
    wrapper['data'].update(m_Id=oldlabelid,m_Parent=oldparent,m_Children=[],m_Classes=[],m_RuleIndex=-1,m_SerializedData={'rid':oldsd})
    refs[1042]=wrapper
    sd=copy.deepcopy(refs[refs[1041]['data']['m_SerializedData']['rid']]);sd['rid']=oldsd;sd['data'].update(uxmlAssetId=oldlabelid,name='ShuffleDraftManagerRedRibbon',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);refs[oldsd]=sd
    labelrefs={r['rid']:r for r in label['references']['RefIds']}
    labelroot=labelrefs[label['m_VisualTree']['rid']]['data']['m_Children'][0]['rid']
    labelmap=import_tree(label,labelsheet,labelroot,1042)
    refs[1042]['data']['m_Children']=[{'rid':labelmap[labelroot]}]
    edit(1042,[P(131105,st.pct(100)),P(131087,st.pct(100)),P(327680,st.h(3,{'unit':5,'value':45.0})),P(458768,st.en('visible'))],True)
    red=st.h(4,{'r':1.0,'g':0.0,'b':0.0,'a':1.0})
    for i in labelmap.values():
        v=refs[i].get('data',{})
        if v.get('m_FullTypeName')=='SI.Bindable.SIText':
            edit(i,[P(65536,red),P(65537,st.px(11)),P(65546,st.en('middle-center'))])
    # All native action objects and all copied calculation bindings remain byte-for-byte equivalent.
    for i,old in original_events.items(): assert refs[i]==old
    for old,new in ratingmap.items():
        a=sourcerefs[old].get('data',{});b=refs[new].get('data',{})
        for k in ['TextBinding','Binding']:
            if k in a: assert a[k]==b[k]
    doc['references']['RefIds']=list(refs.values())
    seen=set()
    def walk(i):
        assert i not in seen;seen.add(i);v=refs[i]['data']
        sd=v.get('m_SerializedData',{}).get('rid',-2)
        if sd!=-2: assert refs[sd]['data']['uxmlAssetId']==v['m_Id']
        for c in v.get('m_Children',[]):
            assert refs[c['rid']]['data']['m_Parent']['rid']==i
            walk(c['rid'])
    walk(doc['m_VisualTree']['rid'])
    assert all(r['rid'] in seen for r in refs.values() if 'm_Parent' in r.get('data',{}))
    tile.save_typetree(doc);sheetobj.save_typetree(sheet)
    output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
    assert set(saved)==set(obs)
    for i,o in saved.items():
        if i in [tile.path_id,sheetobj.path_id]:assert o.read_typetree()==(doc if i==tile.path_id else sheet)
        else:assert sha(o.get_raw_data())==hashes[i],i
    catpath=(GAME.parent if tag=='game' else SKIN)/'catalog.bin';cat=cm.Catalog(catpath.read_bytes());keymap=dict(cat.keys())
    ge=UnityPy.load(str(root/GN));go={o.path_id:o for o in ge.objects};meta=next(o.read_typetree() for o in go.values() if o.type.name=='AssetBundle')
    functionobjects={k:go[v['asset']['m_PathID']] for k,v in meta['m_Container'] if v['asset']['m_FileID']==0 and v['asset']['m_PathID'] in go and go[v['asset']['m_PathID']].type.name=='MonoBehaviour' and 'm_nodes' in go[v['asset']['m_PathID']].read_typetree()}
    for guid in score_guids:
        assert guid in functionobjects and guid in keymap
        locs=[cat.location(x[0]) for x in cat.array(keymap[guid],'I')]
        assert any(l['type'][1]=='SI.VisualScripting.VisualFunction' and l['internal']==guid and cat.location(l['dependencies'][0])['internal'].endswith(GN) for l in locs)
    for n in [WN,GN,'ui-styles_assets_default.bundle','ui-backgrounds_assets_common.bundle','ui-tileslayouts_assets_all.bundle']:
        protected[str(root/n)]=sha((root/n).read_bytes())
    for n in ['catalog.bin','catalog.hash']:
        p=catpath.parent/n
        if p.exists():protected[str(p)]=sha(p.read_bytes())
    backup,source=out/('backup-'+tag)/FN,out/tag/FN
    backup.parent.mkdir();source.parent.mkdir();backup.write_bytes(before);source.write_bytes(output)
    tx.append({'target':str(root/FN),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)})
    audits.append({'target':tag,'changed_assets':[str(tile.path_id),str(sheetobj.path_id)],'unchanged_objects':len(obs)-2,'ratings':branch_titles,'rating_functions_verified':len(score_guids),'bindings_and_native_actions_unchanged':True,'manager_label_rotation':45,'manager_label_color':'#FF0000'})

manifest={'installed':False,'runtime_verified':False,'change':'Club below favourite; nation below pick; six existing FC ratings below name/position; original manager status in red clockwise-45-degree upper-right ribbon','audits':audits,'protected_sha256':protected}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
print('Prepared:',out,flush=True)
subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(out)],check=True)
(R/'current-shuffle-player-tile.json').write_text(json.dumps({'patch':str(out),'manifest':str(out/'manifest.json'),'installed':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
