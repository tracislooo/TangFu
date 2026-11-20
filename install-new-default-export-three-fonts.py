from pathlib import Path
import json
R=Path.cwd()
location=json.loads((R/'current-game-location.json').read_text(encoding='utf-8-sig'))
assert location['game_root']=='F:/Steam/steamapps/common/Football Manager 27'
base=(R/'replace-game-fonts-rounded.py').read_text(encoding='utf-8-sig')
base=base.replace('K:/桌面/27skin/fonts/FM圆体.ttf','F:/tangfu file/proximanova-regular.otf')
base=base.replace("'font-rounded-replacement-'","'font-new-default-install-'")
base=base.replace("assert sum(len(b['fonts']) for b in report['bundles'])==5;", "assert {n for b in report['bundles'] for n in b['fonts']}==targets; assert sum(len(b['fonts']) for b in report['bundles'])==5;")
base=base.replace('try:\n for p,old,new in pending:', 'assert all(p.read_bytes()==old for p,old,new in pending), "Game changed during packaging"\ntry:\n for p,old,new in pending:')
exec(compile(base,'<install new default font>','exec'),{'__name__':'__main__'})
print('DEFAULT INSTALLED; EXPORTING THREE VARIANTS',flush=True)
exec(compile((R/'export-three-font-bundle-variants.py').read_text(encoding='utf-8-sig'),'<export three alternatives>','exec'),{'__name__':'__main__'})
