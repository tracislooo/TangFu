from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,subprocess,sys
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(cfg['bundle_root']),Path(cfg['skin_packages'])
FN='ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
out=R/('shuffle-tile-columns-centered-manager-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[];audits=[];protected={}
targets=[('game',GAME)] if '--game-only' in sys.argv else [('game',GAME),('skin',SKIN)]
for tag,root in targets:
    for n in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle','ui-styles_assets_default.bundle']:
        protected[str(root/n)]=sha((root/n).read_bytes())
    for p in [(GAME.parent if tag=='game' else SKIN)/'catalog.bin',(GAME.parent if tag=='game' else SKIN)/'catalog.hash']:
        if p.exists():protected[str(p)]=sha(p.read_bytes())
    before=(root/FN).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
    tile=obs[1519666771143645661];doc=tile.read_typetree();original=copy.deepcopy(doc)
    refs={r['rid']:r for r in doc['references']['RefIds']}
    sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet);P=st.p
    def data(i):return refs.get(refs[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
    def named(name):
        matches=[r['rid'] for r in refs.values() if 'm_SerializedData' in r.get('data',{}) and data(r['rid']).get('name')==name]
        assert len(matches)==1,(name,matches)
        return matches[0]
    def edit(i,props,reset=False):st.edit(refs[i],props,reset=reset)
    def color(r,g,b,a=1):return st.h(4,{'r':r,'g':g,'b':b,'a':a})
    titles=values=separators=0
    for branchname in ['OverviewCardSixRatings','OverviewCardGoalkeeperRatings']:
        branch=named(branchname)
        row=refs[branch]['data']['m_Children'][0]['rid']
        cells=refs[row]['data']['m_Children'];assert len(cells)==6
        for index,c in enumerate(cells):
            cell=c['rid']
            # A left border on columns 2..6 yields exactly five internal dividers.
            edit(cell,[P(131077,st.px(1 if index else 0)),P(262146,color(.5,.5,.5,1))])
            if index:separators+=1
            for child in refs[cell]['data']['m_Children']:
                i=child['rid'];sd=data(i)
                if sd.get('name','').endswith('Title'):
                    edit(i,[P(65537,st.px(9))]);titles+=1
                elif sd.get('name','').endswith('Value'):
                    edit(i,[P(65537,st.px(12))]);values+=1
    assert (titles,values,separators)==(12,12,10)
    # The native selected/unselected switch remains authoritative, now centered over the full tile.
    status=refs[1030];oldparent=status['data']['m_Parent']['rid']
    refs[oldparent]['data']['m_Children'].remove({'rid':1030})
    status['data']['m_Parent']={'rid':1020}
    refs[1020]['data']['m_Children'].append({'rid':1030})
    edit(1020,[P(131102,st.en('relative'))])
    edit(1030,[P(131102,st.en('absolute')),P(131089,st.pct(50)),P(131104,st.pct(50)),P(131105,st.px(160)),P(131087,st.px(32)),P(327683,st.px(-80),st.px(-16)),P(458768,st.en('visible'))],True)
    data(1030).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    ribbon=named('ShuffleDraftManagerRedRibbon')
    edit(ribbon,[P(131105,st.pct(100)),P(131087,st.pct(100)),P(327680,st.h(3,{'unit':5,'value':45.0})),P(458768,st.en('visible'))],True)
    def descend(i):
        yield i
        for c in refs[i]['data'].get('m_Children',[]):yield from descend(c['rid'])
    manager_texts=0;border_nodes=0
    for i in descend(ribbon):
        v=refs[i]['data'];typ=v.get('m_FullTypeName','')
        if typ=='SI.Bindable.BindingExpect':
            edit(i,[P(131105,st.pct(100)),P(131087,st.pct(100))])
        if 'data_display-draft-player-selection-label' in v.get('m_Classes',[]):
            edit(i,[P(131105,st.pct(100)),P(131087,st.pct(100)),*[P(k,st.px(1)) for k in [131076,131077,131078,131079]],*[P(k,color(1,0,0)) for k in [458758,458761,458762,458763]],P(262146,color(1,0,0)),P(131073,st.en('center')),P(131088,st.en('center'))])
            border_nodes+=1
        if typ=='UnityEngine.UIElements.VisualElement' and data(i).get('name')=='Drafted':
            edit(i,[P(131105,st.pct(100)),P(131087,st.pct(100)),P(131073,st.en('center')),P(131088,st.en('center'))])
        if typ=='SI.Bindable.SIText':
            edit(i,[P(65537,st.px(16)),P(65536,color(1,0,0)),P(65546,st.en('middle-center')),P(131105,st.pct(100)),P(131087,st.pct(100))]);manager_texts+=1
    assert border_nodes==1 and manager_texts==3
    doc['references']['RefIds']=list(refs.values())
    originalrefs={r['rid']:r for r in original['references']['RefIds']}
    # All formula inputs, native events and switch conditions are untouched.
    for i,r in refs.items():
        a=originalrefs[i].get('data',{});b=r.get('data',{})
        for k,x in a.items():
            if k in ['TextBinding','Binding'] or 'Event' in k:assert b[k]==x,(tag,i,k)
    seen=set()
    def walk(i):
        assert i not in seen;seen.add(i)
        for c in refs[i]['data'].get('m_Children',[]):
            assert refs[c['rid']]['data']['m_Parent']['rid']==i
            walk(c['rid'])
    walk(doc['m_VisualTree']['rid'])
    assert all(r['rid'] in seen for r in refs.values() if 'm_Parent' in r.get('data',{}))
    tile.save_typetree(doc);sheetobj.save_typetree(sheet)
    output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
    assert set(saved)==set(obs)
    for i,o in saved.items():
        if i in [tile.path_id,sheetobj.path_id]:assert o.read_typetree()==(doc if i==tile.path_id else sheet)
        else:assert sha(o.get_raw_data())==hashes[i],(tag,i)
    backup,source=out/('backup-'+tag)/FN,out/tag/FN
    backup.parent.mkdir();source.parent.mkdir();backup.write_bytes(before);source.write_bytes(output)
    tx.append({'target':str(root/FN),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)})
    audits.append({'target':tag,'unchanged_objects':len(obs)-2,'rating_title_px':9,'rating_value_px':12,'dividers_per_branch':5,'manager_font_px':16,'manager_center':'full tile center','manager_size_px':[160,32],'manager_rotation':45,'manager_color':'#FF0000','manager_border_color':'#FF0000','formula_and_native_events_unchanged':True})
manifest={'installed':False,'runtime_verified':False,'change':'Smaller six-rating text and internal dividers; centered larger red manager label retaining clockwise 45-degree rotation with red border','protected_sha256':protected,'audits':audits}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher=(R/'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig')
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
(R/'current-shuffle-player-tile.json').write_text(json.dumps({'patch':str(out),'manifest':str(out/'manifest.json'),'installed':False,'status':'prepared','runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
print(out)
