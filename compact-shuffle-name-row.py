from pathlib import Path

R = Path(__file__).parent
shared = (R / 'refine-shuffle-position-and-hover.py').read_text('utf8')
exec(compile(shared.split('def apply_tile_layout():', 1)[0], '<shuffle bundle helpers>', 'exec'))

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R / ('shuffle-name-row-clear-compact-' + stamp)
out.mkdir()
transactions = []
for tag, root in [('game', GAME), ('skin', SKIN)]:
    target = root / FN
    before = target.read_bytes()
    env, obs = objects(before)
    hashes = {pid:sha(obj.get_raw_data()) for pid,obj in obs.items()}
    tile = obs[1519666771143645661]
    doc = tile.read_typetree()
    refs = {ref['rid']:ref for ref in doc['references']['RefIds']}
    style_obj = obs[doc['inlineSheet']['m_PathID']]
    sheet = style_obj.read_typetree()
    st = Styles(sheet)
    P = st.p

    assert named('Name')==1052 and named('Club')==1057 and named('Nation')==1059
    edit(1029,[P(131087,st.px(18))])
    edit(1052,[P(65537,st.px(11))])
    for i in [1057,1059]:
        edit(i,[P(327681,st.num(.85),st.num(.85))])

    # Only the selected ribbon gets a full-size rectangle. The common state
    # anchor has no area to paint over the unselected player's name.
    assert refs[1030]['data']['m_Parent']=={'rid':1020}
    clear = st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})
    edit(1030,[P(131102,st.en('absolute')),P(131089,st.pct(50)),P(131104,st.pct(50)),P(131105,st.px(0)),P(131087,st.px(0)),P(458768,st.en('visible')),P(458752,clear)],True)
    ribbon = named('ShuffleDraftManagerRedRibbon')
    edit(ribbon,[P(131102,st.en('absolute')),P(131089,st.px(-80)),P(131104,st.px(-16)),P(131105,st.px(160)),P(131087,st.px(32))])
    # Keep optional native grade content above the name within its own bounds.
    edit(1041,[P(131102,st.en('absolute')),P(131089,st.px(-28)),P(131104,st.px(-22)),P(131105,st.px(56)),P(131087,st.px(18)),P(458752,clear),P(131088,st.en('center'))])

    doc['references']['RefIds'] = list(refs.values())
    tile.save_typetree(doc)
    style_obj.save_typetree(sheet)
    output = env.file.save(packer='lz4')
    _, saved = objects(output)
    assert set(saved)==set(obs)
    assert saved[tile.path_id].read_typetree()==doc
    assert saved[style_obj.path_id].read_typetree()==sheet
    for pid, obj in saved.items():
        if pid not in (tile.path_id, style_obj.path_id):
            assert sha(obj.get_raw_data())==hashes[pid], pid
    backup, source = out/('backup-'+tag)/FN, out/tag/FN
    backup.parent.mkdir()
    source.parent.mkdir()
    backup.write_bytes(before)
    source.write_bytes(output)
    transactions.append({'target':str(target),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)})

manifest = {'installed':False,'runtime_verified':False,'name_font_px':11,'name_row_px':18,'club_and_nation_scale':.85,'manager_anchor_px':[0,0],'selected_ribbon_px':[160,32],'protected_sha256':{}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(transactions,indent=2),'utf8')
for name, arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher = (R/'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig')
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
print(out)
