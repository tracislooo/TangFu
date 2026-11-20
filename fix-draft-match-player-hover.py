from pathlib import Path

R = Path(__file__).parent
shared = (R/'refine-shuffle-position-and-hover.py').read_text('utf8')
exec(compile(shared.split('def apply_tile_layout():', 1)[0], '<shuffle bundle helpers>', 'exec'))

# Use the same fixed body as the draft cards and live-picks list.
_, baseline = objects(str(R/'shuffle-draft-current-hover-20261102-104742/game'/WN))
source = baseline[-3760232355926433866].read_typetree()
source_styles = baseline[source['inlineSheet']['m_PathID']].read_typetree()
assert not source_styles['assets']
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R/('draft-match-player-hover-'+stamp)
out.mkdir()
transactions, audits, protected = [], [], {}
approved_names = {'PlayerCellInMatch', 'InMatchTacticsFitnessPortraitName', 'TacticsWhitePlayerReportPreview', 'OutsideMatchSquare_PlayerReportPreviewTooltip'}

for tag, root in [('game',GAME),('skin',SKIN)]:
    target = root/WN
    before = target.read_bytes()
    env, obs = objects(before)
    hashes = {pid:sha(obj.get_raw_data()) for pid,obj in obs.items()}
    expected, entries = {}, []
    for obj in obs.values():
        if obj.type.name!='MonoBehaviour' or b'FantasyDraftScalableBindableGridLayoutElement' not in obj.get_raw_data():
            continue
        doc = obj.read_typetree()
        if 'm_VisualTree' not in doc or doc['m_Name'] not in approved_names:
            continue
        refs = {r['rid']:r for r in doc['references']['RefIds']}
        style_obj = obs[doc['inlineSheet']['m_PathID']]
        assert style_obj.path_id not in expected
        sheet = style_obj.read_typetree()
        legacy, = [i for i,r in refs.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.ScalableBindableGridLayoutElement' and serialized(i).get('name')=='FantasyDraftScalableBindableGridLayoutElement']
        node = refs[legacy]['data']
        parent = node['m_Parent']['rid']
        switch = copy.deepcopy(serialized(parent))
        arguments = switch['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']
        assert b'IsFantasyDraftGame' in bytes(arguments)
        assert len(children(parent))==2 and not children(legacy)
        regular, = [c['rid'] for c in children(parent) if c['rid']!=legacy]
        regular_ids = set(walk(regular))
        regular_before = {i:copy.deepcopy(refs[i]) for i in regular_ids}
        next_rid = max(refs)+100
        next_eid = 1959000000
        used_ids = {r['data']['m_Id'] for r in refs.values() if 'm_Id' in r.get('data',{})}
        assert not used_ids.intersection(range(next_eid,next_eid+1000))
        imported = import_tree(source,source_styles,1010,parent)
        children(parent)[children(parent).index({'rid':legacy})] = {'rid':imported[1010]}
        del refs[node['m_SerializedData']['rid']], refs[legacy]
        # Use separate aliases when the regular branch resolves a different child.
        aliases = {u['alias']:u for u in doc['m_Usings']}
        rename = {}
        for row in source['m_Usings']:
            using = copy.deepcopy(row)
            alias = using['alias']
            if alias in aliases and aliases[alias]!=using:
                using['alias'] = 'DraftMatch_'+alias
                rename[alias] = using['alias']
            assert using['alias'] not in aliases or aliases[using['alias']]==using
            aliases[using['alias']] = using
        for i in imported.values():
            value = refs[i].get('data',{})
            for key in ['m_TemplateAlias','templateId']:
                if value.get(key) in rename:
                    value[key] = rename[value[key]]
        doc['m_Usings'] = list(aliases.values())
        doc['references']['RefIds'] = list(refs.values())
        reachable = list(walk(doc['m_VisualTree']['rid']))
        assert len(set(reachable))==len(reachable)
        assert all(i in reachable for i,r in refs.items() if 'm_Parent' in r.get('data',{}))
        assert serialized(parent)==switch
        assert all(refs[i]==previous for i,previous in regular_before.items())
        obj.save_typetree(doc)
        style_obj.save_typetree(sheet)
        expected[obj.path_id],expected[style_obj.path_id] = doc,sheet
        entries.append({'path_id':str(obj.path_id),'template':doc['m_Name'],'draft_branch':imported[1010]})
    assert {x['template'] for x in entries}==approved_names

    catpath = (GAME.parent if tag=='game' else SKIN)/'catalog.bin'
    cat = catalog.Catalog(catpath.read_bytes())
    keys = dict(cat.keys())
    _, global_obs = objects(str(root/GN))
    resource_maps = {WN:(obs,container(obs)),GN:(global_obs,container(global_obs))}
    checked = {}

    def check(guid, kind, required_object=None):
        locs = [cat.location(item[0]) for item in cat.array(keys[guid],'I')]
        loc = next(x for x in locs if x['internal']==guid and x['type'][1]==kind)
        dependencies = [cat.location(i)['internal'].replace('\\','/').split('/')[-1] for i in loc['dependencies']]
        owner = dependencies[0]
        if owner not in resource_maps:
            _, resources = objects(str(root/owner))
            resource_maps[owner] = resources,container(resources)
        resources, records = resource_maps[owner]
        field = 'm_VisualTree' if kind.endswith('VisualTreeAsset') else 'm_nodes'
        ids = [v['asset']['m_PathID'] for key,v in records if key==guid and v['asset']['m_FileID']==0 and v['asset']['m_PathID'] in resources and field in resources[v['asset']['m_PathID']].read_typetree()]
        assert ids and (required_object is None or required_object in ids),(tag,guid,ids)
        if guid=='64033a72b9925c8dad3b08826077c328':
            assert BG in dependencies
        checked[guid] = {'bundle':owner,'type':kind,'objects':[str(i) for i in ids]}
        return resources[ids[0]].read_typetree()

    vta = 'UnityEngine.UIElements.VisualTreeAsset'
    for entry in entries:
        pid = int(entry['path_id'])
        guid, = {k for k,v in container(obs) if v['asset']['m_FileID']==0 and v['asset']['m_PathID']==pid}
        check(guid,vta,pid)
    for using in source['m_Usings']:
        check(using['path'],vta)
    card = check('64033a72b9925c8dad3b08826077c328',vta)
    rating_guids = set()
    for item in card['references']['RefIds']:
        data = item.get('data',{})
        if data.get('name','').startswith('Overview') and data.get('name','').endswith('Value'):
            guid = data.get('TextBinding',{}).get('m_visualFunction',{}).get('m_target',{}).get('m_guid')
            if guid:
                rating_guids.add(guid)
    assert len(rating_guids)==11
    for guid in rating_guids:
        check(guid,'SI.VisualScripting.VisualFunction')

    output = env.file.save(packer='lz4')
    _, saved = objects(output)
    assert set(saved)==set(obs)
    for pid,obj in saved.items():
        if pid in expected:
            assert obj.read_typetree()==expected[pid],pid
        else:
            assert sha(obj.get_raw_data())==hashes[pid],pid
    backup, candidate = out/('backup-'+tag)/WN,out/tag/WN
    backup.parent.mkdir()
    candidate.parent.mkdir()
    backup.write_bytes(before)
    candidate.write_bytes(output)
    transactions.append({'target':str(target),'backup':str(backup),'source':str(candidate),'before':sha(before),'after':sha(output)})
    for path in [catpath,root/FN,root/GN,root/BG]:
        protected[str(path)] = sha(path.read_bytes())
    audits.append({'target':tag,'entries':entries,'addressables':checked,'unchanged_objects':len(obs)-len(expected)})

manifest = {'installed':False,'runtime_verified':False,'protected_sha256':protected,'audits':audits}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(transactions,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher = (R/'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig')
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
print(out)
