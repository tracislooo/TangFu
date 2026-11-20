"""Keep native main tabs and extra shortcuts contiguous after locale changes."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
location=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(location['bundle_root']);SKIN=Path(location['skin_packages'])
assert GAME==Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 tree=ast.parse((R/filename).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),filename+':definitions-only','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]};protected={}
for folder in [GAME,SKIN]:
 for name in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-globalnavigation_assets_all.bundle','ui-panelids_assets_all.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle']:
  p=folder/name
  if p.exists():protected[p]=sha(p.read_bytes())
for folder in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[folder/n]=sha((folder/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 menu=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar');doc=menu.read_typetree();old=copy.deepcopy(doc)
 rr={r['rid']:r for r in doc['references']['RefIds']}
 def serial(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
 def named(n):return next(i for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(i).get('name')==n)
 group=named('ManagingClubButtons');wrapper=named('ClubAndMessagesRow')
 assert rr[group]['data']['m_Parent']['rid']==wrapper
 order=[serial(c['rid']).get('name') for c in rr[wrapper]['data']['m_Children']]
 assert order==['ManagingClubButtons','PrimaryNavMessagesButton','PrimaryNavCompetitionsButton','PrimaryNavYouthButton','PrimaryNavStaffButton']
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();old_sheet=copy.deepcopy(sheet);st=Styles(sheet);auto={'m_ValueType':1,'valueIndex':3}
 # Pin flex sizing in inline numeric/keyword styles so locale-specific USS cannot reintroduce expansion.
 st.edit(rr[group],[st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131082,auto),st.p(131105,auto),
                    st.p(131088,st.en('flex-start')),st.p(131083,st.en('row')),st.p(131086,st.en('nowrap'))])
 st.edit(rr[wrapper],[st.p(131084,st.num(1)),st.p(131088,st.en('flex-start')),st.p(131083,st.en('row')),
                      st.p(131086,st.en('nowrap')),st.p(131082,auto)])
 def properties(i):return {p['m_Id']:p['m_Values'] for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']}
 p=properties(group);assert sheet['floats'][p[131084][0]['valueIndex']]==0
 assert sheet['floats'][p[131085][0]['valueIndex']]==0 and p[131105]==[auto]
 assert sheet['strings'][properties(wrapper)[131088][0]['valueIndex']]=='flex-start'
 for i,r in {r['rid']:r for r in old['references']['RefIds']}.items():
  expected=copy.deepcopy(r)
  if i in [group,wrapper]:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
  assert rr[i]==expected,('Unrelated record changed',i)
 assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
 for i in [group,wrapper]:
  assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] for h in p['m_Values'])
 validate_ui(doc,sheet);menu.save_typetree(doc);oo[sid].save_typetree(sheet)
 raw=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(oo)
 for i,o in saved.items():
  if i in [menu.path_id,sid]:assert o.read_typetree()=={menu.path_id:doc,sid:sheet}[i]
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated asset changed',tag,i)
 validate_ui(saved[menu.path_id].read_typetree(),saved[sid].read_typetree())
 outputs[folder/W]=raw
 reports.append({'target':str(folder/W),'original_group_flex_grow':0,'original_group_width':'auto','row_justify_content':'flex-start',
  'row_uses_remaining_space_after_staff':True,'order':order,'all_button_events_and_translation_bindings_unchanged':True,
  'no_language_specific_widths_or_positions':True,'changed_bundle_objects':[menu.path_id,sid],'runtime_verified':False})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-shortcuts-language-layout-fix-'+stamp);out.mkdir();tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(b);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(b)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for n,flag in [('install',''),('restore',' --restore')]:
 (out/(n+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'locale_independent_intrinsic_sizing':True,'runtime_verified':False},ensure_ascii=False))
