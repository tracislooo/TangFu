from pathlib import Path

R = Path(__file__).parent
shared = (R / 'refine-shuffle-position-and-hover.py').read_text('utf8')
exec(compile(shared.split('def apply_tile_layout():', 1)[0], '<shuffle bundle helpers>', 'exec'))

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R / ('shuffle-position-pitch-aligned-' + stamp)
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
    left = named('ShufflePositionHalf')
    pitch, = [child['rid'] for child in children(left)]
    panel, = [child['rid'] for child in children(pitch) if refs[child['rid']]['data']['m_FullTypeName']=='FM.UI.FMTacticsPanel']
    background, = [child['rid'] for child in children(pitch) if 'tactics-accent-pitch' in refs[child['rid']]['data']['m_Classes']]
    assert serialized(panel)['TacticPositionsBinding']['m_path']=='player.positionaptitudelist'
    assert serialized(panel)['Orientation']==1
    edit(pitch,[P(131105,st.px(78)),P(131087,st.px(46))])
    edit(background,[P(131102,st.en('absolute')),P(131089,st.px(0)),P(131104,st.px(0)),P(131105,st.pct(100)),P(131087,st.pct(100))])
    edit(panel,[P(131102,st.en('absolute')),P(131089,st.px(0)),P(131104,st.px(0)),P(131105,st.pct(100)),P(131087,st.pct(100))])
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

manifest = {'installed':False,'runtime_verified':False,'pitch_width':78,'pitch_height':46,'marker_and_background_bounds':'identical','protected_sha256':{}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(transactions,indent=2),'utf8')
for name, arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher = (R/'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig')
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
print(out)
