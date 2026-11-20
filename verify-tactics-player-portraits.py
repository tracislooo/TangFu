from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
root=Path.cwd();out=sorted(root.glob('tactics-overview-player-portraits-*'))[-1];report=json.loads((out/'manifest.json').read_text('utf8'))
assert report['installed']
game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');skin=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');name='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
b=(game/name).read_bytes();assert b==(skin/name).read_bytes()==(out/name).read_bytes()
o={x.path_id:x for x in UnityPy.load(b).objects}
for pid,a in zip([-8273082868742719783,3127595210179668386],report['templates']):
 d=o[pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree();shirt=r[a['shirt']]['data'];props=s['m_Rules'][shirt['m_RuleIndex']]['m_Properties'];p=next(p for p in props if p['m_Id']==458767);assert s['floats'][p['m_Values'][0]['valueIndex']]==0
 assert not any(p['m_Id']==458766 for p in props)
 m=r[r[a['mapper']]['data']['m_SerializedData']['rid']]['data'];assert m['Mappings'][0]['to']['m_path']=='position.Player'
 assert r[a['portrait']]['data']['m_TemplateAlias']=='PersonPicture'
 assert r[a['portrait']]['data']['m_Parent']=={'rid':a['mapper']}
 assert r[a['mapper']]['data']['m_Parent']==shirt['m_Parent']
 print(a['template'],'opacity=0, native PersonPicture binding=position.Player, separate visible portrait: PASS')
report['installed_verified']=True;report['opacity_property_id']=458767;(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('Game and skin packages identical; output:',out)
