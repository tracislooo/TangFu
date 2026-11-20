"""Export the requested bookmark preset as source JSON only; never write game files."""
from pathlib import Path
import copy
import hashlib
import json
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy

location = json.loads((ROOT / 'current-game-location.json').read_text('utf8'))
source = Path(location['bundle_root']) / 'ui-globalnavigation_assets_all.bundle'
original = source.read_bytes()
env = UnityPy.load(original)
trees = {o.peek_name(): o.read_typetree() for o in env.objects if o.type.name == 'MonoBehaviour'}

# Native club-manager routes. Preserve each entry's arguments, localization and gates.
specs = [
    ('消息', 'PortalSubtabs', ['Messages']),
    ('一线队', 'SquadSubtabs', ['First Team']),
    ('动态', 'SquadSubtabs', ['Dynamics']),
    ('战术', 'TacticsSubtabs', ['Overview']),
    ('数据中心', 'TacticsSubtabs', ['Data Hub']),
    ('职员', 'ClubSubtabs', ['Staff']),
    ('训练', 'TrainingSubtabs', ['Overview']),
    ('医疗中心', 'TrainingSubtabs', ['Medical Centre']),
    ('赛程安排', 'PortalSubtabs', ['Calendar', 'Fixture Schedule (Tab)']),
    ('比赛', 'PortalSubtabs', ['Competitions']),
    ('球探', 'RecruitmentSubtabs', ['Scouting ']),
    ('俱乐部', 'ClubSubtabs', ['Overview']),
    ('财政', 'ClubSubtabs', ['Finances']),
    ('青年', 'SquadSubtabs', ['Youth Setup']),
]
entries = []
for order, (label, tree_name, path) in enumerate(specs, 1):
    tree = trees[tree_name]
    refs = {r['rid']: r for r in tree['references']['RefIds']}
    choices = tree['m_submenus']
    for index, part in enumerate(path):
        item = next(x for x in choices if x['name'] == part)
        if index < len(path) - 1:
            choices = [refs[x['rid']]['data'] for x in item['ChildList']]
    value = copy.deepcopy(item['PropertyValue'])
    assert value['m_panelIDRef']['m_AssetGUID']
    entries.append({'order': order, 'label_zh': label, 'default_selected': True,
                    'native_navigation_asset': tree_name, 'native_entry_path': path,
                    'native_property_value': value})

assert len(entries) == 14
assert len({x['native_property_value']['m_panelIDRef']['m_AssetGUID'] for x in entries}) == 14
preset = {
    'schema': 'tf27-sidebar-bookmark-preset-source-v1',
    'date': '2026-11-01', 'scope': 'approved-sidebar-only',
    'default_count': 14, 'width_px': 100, 'direction': 'vertical',
    'status': 'source_preset_only_not_integrated_or_installed',
    'game_reads_this_json_directly': False,
    'existing_saved_bookmarks_modified': False,
    'matches_label_means': 'Competitions overview, matching the existing 比赛 navigation entry',
    'source_sha256': hashlib.sha256(original).hexdigest(),
    'entries': entries,
}
(OUT / 'default-bookmarks.json').write_text(json.dumps(preset, ensure_ascii=False, indent=2) + '\n', 'utf8')
assert source.read_bytes() == original
print(json.dumps({'output': str(OUT / 'default-bookmarks.json'), 'count': len(entries),
                  'game_source_unchanged': True, 'bundles_written': 0}, ensure_ascii=False))
