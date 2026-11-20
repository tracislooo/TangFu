"""Keep four added navigation shortcuts visually unchanged on pointer hover."""
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
 source=ast.parse((R/filename).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),filename+':definitions-only','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]};protected={}
for f in [GAME,SKIN]:
 for n in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle','ui-globalnavigation_assets_all.bundle']:
  p=f/n
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in en.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 obj=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar');doc=obj.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();old_sheet=copy.deepcopy(sheet);st=Styles(sheet)
 def serial(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
 def named(n):return next(i for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(i).get('name')==n)
 se=UnityPy.load(str(folder/'ui-styles_assets_default.bundle'))
 styles=next(o.read_typetree() for o in se.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
 opacity=[]
 for r in styles['m_Rules']:
  if any(len(s['m_Selectors'])==2 and [p['m_Value'] for q in s['m_Selectors'] for p in q['m_Parts']]==['navigation-tab-portal-default-active-false','portal-text'] for s in r.get('m_ComplexSelectors',[])):
   opacity.extend(styles['floats'][h['valueIndex']] for p in r['m_Properties'] if p['m_Id']==458767 for h in p['m_Values'] if h['m_ValueType']==2)
 assert opacity and len(set(opacity))==1
 normal_opacity=opacity[0];assert normal_opacity==0.75
 changed=[]
 for name in ['Messages','Competitions','Youth','Staff']:
  button=named('PrimaryNav'+name+'Button');label=named('PrimaryNav'+name+'Label')
  st.edit(rr[button],[st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),st.p(458753,st.en('none')),
                      st.p(458767,st.num(1)),st.p(262148,st.px(0))])
  st.edit(rr[label],[st.p(458767,st.num(normal_opacity)),st.p(65536,st.h(4,{'r':0.,'g':0.,'b':0.,'a':1.}))])
  changed.extend([button,label])
 for i,r in {r['rid']:r for r in old['references']['RefIds']}.items():
  expected=copy.deepcopy(r)
  if i in changed:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
  assert rr[i]==expected,('Binding, event or unrelated record changed',i)
 assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
 for i in changed:
  assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] for h in p['m_Values'])
 validate_ui(doc,sheet);obj.save_typetree(doc);oo[sid].save_typetree(sheet)
 raw=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in [obj.path_id,sid]:assert o.read_typetree()=={obj.path_id:doc,sid:sheet}[i]
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated bundle asset changed',i)
 validate_ui(check[obj.path_id].read_typetree(),check[sid].read_typetree())
 outputs[folder/W]=raw
 reports.append({'target':str(folder/W),'buttons':['Messages','Competitions','Youth','Staff'],'button_background':'transparent',
 'label_color':'black','label_opacity_pinned_to_native_normal_state':normal_opacity,'changed_records':changed,
 'events_translations_layout_and_other_tabs_unchanged':True,'new_inline_variables':False})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-shortcuts-no-hover-'+stamp);out.mkdir();tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(b);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(b)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for n,flag in [('install',''),('restore',' --restore')]:
 (out/(n+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'native_normal_opacity':0.75,'hover_effect_removed_for_four_shortcuts':True},ensure_ascii=False))
