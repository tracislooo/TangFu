"""Reapply only the latest user-approved sidebar delta to current common resources."""
from pathlib import Path
import ast,copy,hashlib,json,shutil
R=Path(__file__).resolve().parent
INDEX=json.loads((R/'current-sidebar-version.json').read_text('utf8'))
approved=Path(INDEX['approved_version'])
conversion=Path(INDEX['latest_non_sidebar_conversion'])
stage=R/'sidebar-latest-approved-migration-source-20261103'
stage.mkdir(exist_ok=True)
tx=json.loads((conversion/'transaction.json').read_text('utf8'))
records=[]
for row in tx:
 name=Path(row['target']).name
 side=approved/'aa'/('StandaloneWindows64' if name.endswith('.bundle') else '')/name
 base=Path(row['source'])
 assert hashlib.sha256(side.read_bytes()).hexdigest()==row['before']
 assert hashlib.sha256(base.read_bytes()).hexdigest()==row['after']
 for src,folder in [(side,'packages'),(base,'non-sidebar-baseline')]:
  dest=stage/folder/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
 records.append(dict(target=row['target'],before=row['after'],after=row['before']))
(stage/'transaction.json').write_text(json.dumps(records,indent=2),'utf8')
source=(R/'rebase-approved-sidebar-current.py').read_text('utf8')
source=source.replace("ARCHIVE = R / 'saved-progress/FM27-sidebar-approved-20261101'","ARCHIVE = R / 'sidebar-latest-approved-migration-source-20261103'")
source=source.replace("count = len(base['m_Rules'])\n    assert approved['m_Rules'][:count] == base['m_Rules']\n    assert len(approved['m_Rules']) - count == 8", "count = 5642\n    assert len(approved['m_Rules']) == len(base['m_Rules']) + 8\n    assert 'tf-reference-sidebar' in str(approved['m_Rules'][count]['m_ComplexSelectors'])")
source=source.replace("for rule in approved['m_Rules'][count:]:", "for rule in approved['m_Rules'][count:count+8]:")
source=source.replace("'sidebar_left_top_width': [0, 0, 100]", "'sidebar_left_top_width': [0, 85, 100]")
source=source.replace("'bookmark_default_preset_installed': False", "'bookmark_default_preset_installed': False, 'fixed_navigation_count': 15, 'bookmark_view_height_px': 400, 'sidebar_background_hex': '#263445', 'bookmark_editor_position': 'above native bookmark list'")
exec(compile(source,str(R/'rebase-approved-sidebar-current.py'),'exec'),dict(__file__=str(R/'rebase-approved-sidebar-current.py'),__name__='__main__'))
