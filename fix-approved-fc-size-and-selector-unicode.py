"""Restore literal Chinese titles and match the unscaled middle FC card size."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named'})]:
 tree=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';HOST=7857044477279960178;PAGE=-941100000001060;STYLE=-941100000001061
OUT=R/('approved-fc-middle-size-unicode-titles-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for name in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
titles={'OverviewLeftTestVariantTitle':'左边版大头像+隐藏','OverviewLeftPortraitHiddenVariantTitle':'左边版大头像+隐藏（旧版）','OverviewLeftFCVariantTitle':'左边版FC卡面+隐藏（旧版）','OverviewLeftFCHiddenApprovedTitle':'左边版FC卡面+隐藏'}
tx=[];checks=[]
for tag,root in roots:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
 host=obs[HOST].read_typetree();oldhost=copy.deepcopy(host);hr=refs(host)
 variables=next(x['data']for x in hr.values()if x.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
 for key,title in titles.items():
  variable=next(v for v in variables['ValueVariables']if v['m_name']==key)
  old=variable['m_scopeValue']['m_serializedData'];assert '\\u'in old
  variable['m_scopeValue']['m_serializedData']='String|'+title+'|'
 assert len(variables['ValueVariables'])==len(next(x['data']for x in refs(oldhost).values()if x.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')['ValueVariables'])
 page=obs[PAGE].read_typetree();pr=refs(page);sheet=obs[STYLE].read_typetree();oldsheet=copy.deepcopy(sheet);st=Styles(sheet)
 middle=obs[-930000000001001].read_typetree();mr=refs(middle);ms=obs[middle['inlineSheet']['m_PathID']].read_typetree()
 def dimension(s,rr,node,key):
  prop=next(p for p in s['m_Rules'][rr[node]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==key);h=prop['m_Values'][0];assert h['m_ValueType']==3
  d=s['dimensions'][h['valueIndex']];assert d['unit']==1;return d['value']
 middle_bg=named(middle,'ReportMiddleCA000Layer');new_bg=named(page,'ReportMiddleCA000Layer')
 width=dimension(ms,mr,middle_bg,131105);height=dimension(ms,mr,middle_bg,131087)
 assert width==height==286
 assert dimension(sheet,pr,new_bg,131105)==width and dimension(sheet,pr,new_bg,131087)==height
 portrait=named(page,'ReportPortraitStatusColumn');stage=named(page,'ReportPortraitLayerStage');changed=set()
 for node,values in [(portrait,[st.p(131105,st.px(width)),st.p(131097,st.px(width)),st.p(131095,st.px(width))]),
                     (stage,[st.p(327681,st.num(1),st.num(1)),st.p(131093,st.px(0))])]:
  rule=pr[node]['data']['m_RuleIndex'];assert [i for i,r in pr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
  props=sheet['m_Rules'][rule]['m_Properties'];keys={p['m_Id']for p in values}
  sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+values;changed.add(rule)
 for i,value in enumerate(oldsheet['m_Rules']):
  if i not in changed:assert sheet['m_Rules'][i]==value
 oldrefs=refs(oldhost);newrefs=refs(host)
 for i,record in oldrefs.items():
  if record==newrefs[i]:continue
  expected=copy.deepcopy(record)
  assert 'ValueVariables'in expected['data']
  for var in expected['data']['ValueVariables']:
   if var['m_name']in titles:var['m_scopeValue']['m_serializedData']='String|'+titles[var['m_name']]+'|'
  assert newrefs[i]==expected
 changes={HOST:host,STYLE:sheet}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated change',i)
 for i,value in changes.items():assert check[i].read_typetree()==value
 readvars=next(x['data']['ValueVariables']for x in refs(check[HOST].read_typetree()).values()if x.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
 for key,title in titles.items():
  text=next(v for v in readvars if v['m_name']==key)['m_scopeValue']['m_serializedData'];assert text=='String|'+title+'|'and '\\u'not in text
 source,backup=OUT/tag/W,OUT/('backup-'+tag)/W;source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,literal_unicode_titles=titles,unicode_codepoints_verified_after_serialization=True,
  middle_card_native_size=[width,height],new_card_uniform_scale=1,card_slot_width=width,
  only_changed_objects=list(changes),approved_portrait_and_all_ui_bindings_unchanged=True,
  selector_entries_cache_and_active_selection_unchanged=True,unrelated_objects_byte_identical=True))
 print('Verified '+tag+': actual Chinese titles and middle-size unscaled 286px FC card',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,change='Replace literal Unicode escape sequences with Chinese codepoints; remove FC downscale to match middle card size',fc_uniform_scale=1,fc_card_native_size=[286,286])
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
 (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'approved-fc-size-unicode-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
