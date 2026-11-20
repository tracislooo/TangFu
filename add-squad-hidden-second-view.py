"""Expose the native squad hidden view as the second selector entry, without new UI assets."""
from pathlib import Path
import sys,json,copy,hashlib,datetime,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
assert GAME.parts[-5:-3] != ('Project Taco','fm_Data') and 'Football Manager 27' in str(GAME)
V='ui-tableviews_assets_all.bundle';F='ui-tablefactories_assets_all.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('squad-hidden-second-view-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
attributes=['adaptability','ambition','consistency','controversy','dirtiness','important-matches','injury-proneness','loyalty','pressure','professionalism','sportsmanship','temperament','versatility']
numbers=['hidden-current-ability','hidden-potential-ability','hidden-current-reputation','hidden-home-reputation','hidden-world-reputation']+['hidden-'+x for x in attributes]
before={};protected={};payloads={};edits=[];catalog_audit=[]
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 p=folder/V;raw=p.read_bytes();before[str(p)]=raw;backup=OUT/('backup-'+tag);backup.mkdir();(backup/V).write_bytes(raw)
 for other in folder.glob('*.bundle'):
  if other.name!=V:protected[str(other)]=sha(other.read_bytes())
 for name in ['catalog.bin','catalog.hash']:
  cp=GAME.parent/name if folder==GAME else folder/name
  if cp.exists():protected[str(cp)]=sha(cp.read_bytes())
 e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 named={o.peek_name():o for o in oo.values() if o.type.name=='MonoBehaviour'}
 hidden=named['FirstTeamTableHidden'];general=named['FirstTeamTableGeneralInfo'];collection=named['FirstTeamSquadAndYouthTeamSquadCollection']
 hd=hidden.read_typetree();gd=general.read_typetree();cd=collection.read_typetree();oldhd=copy.deepcopy(hd);oldcd=copy.deepcopy(cd)
 # Keep the existing desktop/compact player-name alternatives and picked/status columns.
 prefix=[]
 for col in gd['m_tableView']['m_tableConfig']:
  prefix.append(copy.deepcopy(col))
  if col['m_columnID']=='position':break
 assert [c['m_columnID'] for c in prefix]==['position-dropdown','inf-team','portrait-name','portrait-shortname','position']
 oldcols={c['m_columnID']:c for c in hd['m_tableView']['m_tableConfig']}
 donor=next(iter(oldcols.values()))
 cols=prefix[:]
 for ident in numbers:
  col=copy.deepcopy(oldcols.get(ident,donor));col['m_columnID']=ident
  meta=col['m_columnMetadata'];width=80. if 'reputation' in ident else 64.
  meta.update(m_widthOverride=width,m_minWidthOverride=width,m_applicableBreakpoints=-1,m_optionalConfigConditions=[],m_optionalConditions=[])
  cols.append(col)
 view=hd['m_tableView'];view['m_viewName']={'GameID':32477};view['m_requirements']=[];view['m_optionalConditions']=[];view['m_optionalConfigConditions']=[];view['m_tableConfig']=cols
 rows=cd['m_tableViewSettings'];existing=[x for x in rows if x['PropertyValue']=={'m_FileID':0,'m_PathID':hidden.path_id}]
 assert len(existing)==1,('Native hidden selector entry ambiguous',len(existing))
 entry=copy.deepcopy(existing[0]);entry.update(name='Hidden',debug_name='Hidden',Disable=0,AddSpacerBefore=0,DisplayValue={'GameID':32477},Requirement={'m_FileID':0,'m_PathID':0})
 keep=[x for x in rows if x is not existing[0]];cd['m_tableViewSettings']=keep[:1]+[entry]+keep[1:]
 assert [x for x in cd['m_tableViewSettings'] if x is not entry]==[x for x in oldcd['m_tableViewSettings'] if x['PropertyValue']!={'m_FileID':0,'m_PathID':hidden.path_id}]
 assert cd['m_tableViewSettings'][0]==oldcd['m_tableViewSettings'][0]
 assert hd['m_tableView']['m_tableConfig'][:len(prefix)]==prefix
 # All displayed values use native factory columns, including numeric ability/reputation.
 fe=UnityPy.load(str(folder/F));factory=next(o.read_typetree() for o in fe.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerTableFactory')
 factorycols={c['m_id']:c for c in factory['m_rowData']}
 assert all(c['m_columnID'] in factorycols for c in cols)
 for ident in numbers:assert factorycols[ident]['m_sortBinding']['m_path'].startswith('binding.')
 expected={hidden.path_id:hd,collection.path_id:cd}
 for pid,d in expected.items():oo[pid].save_typetree(d)
 output=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(oo)
 for pid,h in hashes.items():
  if pid not in expected:assert sha(check[pid].get_raw_data())==h,('Unrelated object modified',tag,pid)
 for pid,d in expected.items():assert check[pid].read_typetree()==d
 meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 assert all(any(v['asset']=={'m_FileID':0,'m_PathID':pid} for _,v in meta['m_Container']) for pid in expected)
 catpath=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';cat=cm.Catalog(catpath.read_bytes());keys=dict(cat.keys())
 # Validate every native cell template/function referenced by the selected columns.
 loaded={};seen=set()
 def audit_guid(g):
  if not g or g in seen:return
  seen.add(g);assert g in keys,('Missing GUID',g)
  locations=[cat.location(v[0]) for v in cat.array(keys[g],'I')]
  typed=[q for q in locations if q['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','SI.VisualScripting.VisualFunction']]
  if not typed:return
  for q in typed:
   assert q['dependencies'];bn=cat.location(q['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
   if bn not in loaded:
    path=folder/bn
    if folder==SKIN and not path.exists():path=GAME/bn
    assert path.exists(),('Owning bundle absent',tag,g,bn)
    env=UnityPy.load(str(path));os={o.path_id:o for o in env.objects};mt=next((o.read_typetree() for o in os.values() if o.type.name=='AssetBundle'),None);assert mt is not None,('Bundle has no metadata',tag,g,bn,len(os));idx={}
    for key,item in mt['m_Container']:
     ob=os.get(item['asset']['m_PathID']) if item['asset']['m_FileID']==0 else None
     if ob and ob.type.name=='MonoBehaviour':
      d=ob.read_typetree()
      if 'inlineSheet' in d or 'm_nodes' in d:idx[key]=(ob,d)
    loaded[bn]=(os,idx)
   os,idx=loaded[bn];assert g in idx,('GUID absent from owning bundle',g,bn)
   ob,d=idx[g];kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else 'SI.VisualScripting.VisualFunction';assert q['type'][1]==kind
   catalog_audit.append({'folder':tag,'guid':g,'name':d['m_Name'],'bundle':bn,'type':kind})
   def refs(v):
    if isinstance(v,dict):
     for k,x in v.items():
      if k in ['path','m_guid','m_AssetGUID'] and isinstance(x,str) and len(x)==32 and all(c in '0123456789abcdef' for c in x):audit_guid(x)
      else:refs(x)
    elif isinstance(v,(list,tuple)):
     for x in v:refs(x)
   refs(d)
 for col in cols:audit_guid(factorycols[col['m_columnID']]['m_uxmlRef']['m_AssetGUID'])
 target=OUT/tag;target.mkdir();source=target/V;source.write_bytes(output);payloads[str(p)]=str(source)
 edits.append({'folder':tag,'view_pid':hidden.path_id,'collection_pid':collection.path_id,'selector_index':1,'title':'隐藏','columns':[c['m_columnID'] for c in cols],'native_hidden_column_bindings':{c:factorycols[c]['m_valueBindings'] for c in numbers},'original_first_view_and_other_entries_preserved':True})
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
for p,b in before.items():assert Path(p).read_bytes()==b
m={'installed':False,'runtime_verified':False,'request':'Squad selector second entry Hidden; preserve picked/status/player/position, show ability/potential/reputations and 13 hidden attributes.','edits':edits,'catalog_templates_functions_verified':len(catalog_audit),'catalog_unchanged':True,'no_new_objects':True,'unrelated_objects_byte_identical':True,'before_sha256':{p:sha(b) for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) for p,s in payloads.items()},'protected_sha256':protected}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'catalog-audits.json').write_text(json.dumps(catalog_audit,ensure_ascii=False,indent=2),'utf8')
tx={'game':str(GAME),'skin':str(SKIN),'sources':payloads,'before':{p:str(OUT/('backup-game' if Path(p).parent==GAME else 'backup-skin')/V) for p in before}}
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('阵容/青年队原生表格选择器第二项显示“隐藏”。保留已选、现状、球员、位置及原球员名称响应式分支；后续依次为当前能力、潜力、当前声望、本土声望、世界声望、适应性、野心、稳定性、争议性、肮脏程度、大赛表现、受伤倾向、忠诚、抗压能力、职业素养、体育精神、脾气、多面性。复用全部原生字段、数值单元格及既有隐藏视图，不新建头像、模板或纹理。只改两份tableviews包内Hidden视图和列表集合两对象，原第一项及其他视图保持。文件检查通过，实际游戏显示与数值待用户确认。游戏更新后按新版相同逻辑增量重做，禁止旧整包覆盖。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'native_hidden_numeric_columns':len(numbers),'changed_objects_per_bundle':2,'catalog_resources_checked':len(catalog_audit)},ensure_ascii=False),flush=True)
