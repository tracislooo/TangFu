"""Check the latest roster, draft, tactics and match changes in a staged build."""
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / '.codex-deps'))
import UnityPy

out = Path(sys.argv[1])
manifest = json.loads((out / 'manifest.json').read_text('utf-8'))
records = manifest['stage_assets']
staged_names = {row['name'] for row in records}
required = {
    'SquadOverviewTableBlock', 'PlayerReportPreviewTooltip',
    'TacticsPositionCombined', 'TacticsPositionDetailed',
    'TacticalEffectivenessGauge', 'TacticalEffectivenessPercentageGauge',
    'MatchExperienceHumanGridComposition-Large',
    'shuffle-tiles-primary draft-graded-base',
}
assert required <= staged_names, required - staged_names

spec = importlib.util.spec_from_file_location('catalog', Path('catalog-binary-v35.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
catalog = module.Catalog((out / 'catalog.bin').read_bytes())
keys = dict(catalog.keys())
roster_guid = '0b79ae3b71e45568a4c2ea9bf1d1ecf3'
roster_location, = [offset for offset, in catalog.array(keys[roster_guid], 'I')]
preload = {
    offset for offset, in catalog.array(keys['GameWorldVisualTreeAssetPreload'], 'I')
}
assert roster_location in preload
assert not any(isinstance(key, str) and 'tfreferencebookmark' in key.lower() for key in keys)

host = next(row for row in records if row['name'] == 'SquadOverviewTableBlock')
world = UnityPy.load(str(out / host['bundle']))
objects = {obj.path_id: obj for obj in world.objects}
assert not any('tfreferencebookmark' in (obj.peek_name() or '').lower()
               for obj in world.objects if obj.type.name == 'MonoBehaviour')
tree = objects[host['id']].read_typetree()
nodes = [row['data'] for row in tree['references']['RefIds'] if 'data' in row]
scroller, = [node for node in nodes if node.get('name') == 'TFClubSquadRoster']
assert scroller['RowTemplate']['m_AssetGUID'] == roster_guid
assert scroller['Binding']['m_direct']['Path']['m_path'] == 'team.Players'
assert scroller['ScrollViewMode'] == 1

report = {'staged_latest_assets': sorted(required), 'roster_guid': roster_guid,
          'roster_preload_verified': True, 'roster_horizontal_scroll': True}
(out / 'scope-1-16-verification.json').write_text(json.dumps(report, indent=2), 'utf-8')
print(json.dumps(report))
