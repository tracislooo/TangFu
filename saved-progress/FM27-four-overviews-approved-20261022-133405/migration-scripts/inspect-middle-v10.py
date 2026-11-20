import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy

root = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
for name in ['ui-backgrounds_assets_common.bundle', 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
    print('\nBUNDLE', name)
    env = UnityPy.load(str(root / name))
    objects = {o.path_id: o for o in env.objects}
    for pid in [-910000000000001, -910000000000002, -910000000000003]:
        if pid in objects:
            o = objects[pid]
            d = o.read_typetree()
            print('TEXTURE', pid, d['m_Name'], d['m_Width'], d['m_Height'], d['m_TextureFormat'])
    if 'backgrounds' in name:
        continue
    header_id = 5775949770471550939 if 'gameworld' in name else -4194025542157271532
    style_id = -1940069326759809061 if 'gameworld' in name else 8045407476604796436
    h = objects[header_id].read_typetree()
    s = objects[style_id].read_typetree()
    print('EXTERNALS', [(i+1, e.path) for i,e in enumerate(objects[header_id].assets_file.externals)])
    print('ASSETS', s['assets'])
    print('USINGS', h['m_Usings'])
    refs = {r['rid']:r for r in h['references']['RefIds']}
    def dump(rid, indent=''):
        d = refs[rid].get('data',{})
        serial = refs.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        print(indent, rid, serial.get('name',''), d.get('m_FullTypeName',''), 'rule',d.get('m_RuleIndex'), 'classes',d.get('m_Classes'), 'style',s['m_Rules'][d['m_RuleIndex']] if d.get('m_RuleIndex',-1)>=0 else '')
        if 'Picture' in str(serial.get('name','')) or 'picture' in str(d.get('m_FullTypeName','')).lower():
            print('SERIAL', serial)
        for child in d.get('m_Children',[]):
            dump(child['rid'],indent+'  ')
    if 'gameworld' in name:
        for rid,r in refs.items():
            if r.get('data',{}).get('name')=='PlayerTopBackgroundTextureLayer':
                node = next(n for n in refs.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==rid)
                dump(node['rid'])
    else:
        mid = next(r for r in refs.values() if r.get('data',{}).get('name')=='ReportPortraitStatusColumn')
        node = next(n for n in refs.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==mid['rid'])
        dump(node['rid'])
        print('STYLE POOLS', {k:s[k] for k in ['floats','dimensions','strings']})
        template_pointer = next(x['asset'] for x in h['m_Usings'] if x['alias']=='PersonPicture')
        o = objects[template_pointer['m_PathID']]
        print('PERSON TEMPLATE',o.read_typetree())
