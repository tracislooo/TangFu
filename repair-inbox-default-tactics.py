"""Incremental repair of the three requested UI settings from current resources."""
from pathlib import Path
import sys,json,copy,ast,hashlib,datetime,struct,uuid,importlib.util,winreg
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';V='ui-tableviews_assets_all.bundle';F='ui-tablefactories_assets_all.bundle'
OUT=R/('inbox-default-tactics-repair-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'templates').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
extract('add-card-six-ratings.py',{'validate_ui'});extract('build-match-ui-avatars-layout.py',{'refs','sd','find','Doc'})
before={};backups={};payloads={};protected={};reports=[];documents=[]
widths={'picked-position':44.,'picked-role':46.,'overview-position':44.,'ip-position':48.,'oop-position':48.,'ip-role':46.,'oop-role':46.,'tactic-ability':60.,'role-ability':60.,'positions':87.}
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for p in folder.glob('*.bundle'):
  if p.name not in [W,V,F]:protected[str(p)]=sha(p.read_bytes())
 for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash'] if tag=='game' else [SKIN/'catalog.bin',SKIN/'catalog.hash']:
  if p.exists():protected[str(p)]=sha(p.read_bytes())
 env={n:UnityPy.load(str(folder/n)) for n in [W,V,F]};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()};changes={n:{} for n in env}
 def put(n,o,d):
  if o.read_typetree()!=d:o.save_typetree(d);changes[n][o.path_id]=copy.deepcopy(d)
 modern=any(o.type.name=='MonoBehaviour' and o.peek_name()=='PortalMessageView' for o in objs[W].values())
 doc=Doc(W,name='PortalMessageView' if modern else 'PortalMessagesContentBlock');pic=1015 if modern else 1019;host=1005 if modern else 1008;original=copy.deepcopy(doc.d);doc.size(pic,192,192)
 # This sender instance alone expands; its header has natural height.
 wanted=copy.deepcopy(original);refs(wanted)[pic]['data']['m_RuleIndex']=doc.a(pic)['m_RuleIndex'];assert wanted==doc.d
 doc.st(host,[(131096,doc.px(192))]);doc.save()
 factory=find(F,'TacticTeamSelectionTableFactory');fd=factory.read_typetree();fc={c['m_id']:c for c in fd['m_rowData']};assert fc['condition']['m_defaultWidth']==90 and fc['tactics-fatigue-value']['m_defaultWidth']==40
 for k in ['condition','tactics-fatigue-value']:
  c=fc[k];assert c['m_uxmlRef']['m_AssetGUID'];assert c['m_valueBindings']
 # Prevent the position text column from absorbing health-column space.
 fc['positions'].update(m_defaultWidth=87.,m_minimumWidth=75.,m_allowWidthAutoResizing=0);put(F,factory,fd)
 changed_views=[]
 for o in objs[V].values():
  if o.type.name!='MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name():continue
  d=o.read_typetree();cs=d.get('m_tableView',{}).get('m_tableConfig',[])
  if not any(c['m_columnID']=='condition' for c in cs):continue
  old=copy.deepcopy(cs);cs[:]=[c for c in cs if c['m_columnID'] not in ['sharpness','tactics-fatigue-value']]
  c=next(c for c in cs if c['m_columnID']=='condition');c['m_columnMetadata'].update(m_widthOverride=90.,m_minWidthOverride=90.)
  fat=copy.deepcopy(c);fat['m_columnID']='tactics-fatigue-value';fat['m_columnMetadata'].update(m_widthOverride=40.,m_minWidthOverride=40.);fat['m_columnMetadata']['m_titleTranslationIdOverride']['GameID']=0;cs.insert(cs.index(c)+1,fat)
  for c in cs:
   if c['m_columnID'] in widths:
    w=widths[c['m_columnID']];c['m_columnMetadata'].update(m_widthOverride=w,m_minWidthOverride=75. if c['m_columnID']=='positions' else w)
  put(V,o,d)
  if cs!=old:changed_views.append(d['m_Name'])
  assert [c['m_columnID'] for c in cs].count('tactics-fatigue-value')==1
 # A is the native default (first item); retain B and every other menu entry.
 cd=find(V,'FirstTeamSquadAndYouthTeamSquadCollection').read_typetree();assert cd['m_tableViewSettings'][0]['PropertyValue']['m_PathID']==-991111000002000
 assert objs[V][-991111000002000].peek_name()=='tangfu A'
 # Existing cells and header GUIDs must resolve to actual objects in the catalog.
 spec=importlib.util.spec_from_file_location('catalog_repair',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';cat=cm.Catalog(cp.read_bytes())
 meta=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle');container=dict(meta['m_Container'])
 health_checks=[]
 for k in ['condition','tactics-fatigue-value']:
  for field in ['m_uxmlRef','m_headerUxmlRef']:
   guid=fc[k][field]['m_AssetGUID']
   if not guid:continue
   locs=cat.locations(guid);assert locs
   assert any(cat.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' for loc in locs)
   assert guid in container;pid=container[guid]['asset']['m_PathID'];assert pid in objs[W]
   tree=objs[W][pid].read_typetree();assert tree['inlineSheet']['m_PathID'] in objs[W]
   health_checks.append({'column':k,'field':field,'guid':guid,'pid':pid})
 for n in [W,V,F]:
  p=folder/n
  if not changes[n]:protected[str(p)]=sha(p.read_bytes());continue
  raw=env[n].file.save(packer='lz4');oo={o.path_id:o for o in UnityPy.load(raw).objects};assert oo.keys()==objs[n].keys()
  for pid,h in hashes[n].items():
   if pid not in changes[n]:assert sha(oo[pid].get_raw_data())==h,(tag,n,pid)
  for pid,d in changes[n].items():assert oo[pid].read_typetree()==d
  bp=OUT/('backup-'+tag)/n;bp.parent.mkdir(exist_ok=True);before[str(p)]=p.read_bytes();bp.write_bytes(before[str(p)]);backups[str(p)]=str(bp)
  dst=OUT/('output-'+tag)/n;dst.parent.mkdir(exist_ok=True);dst.write_bytes(raw);payloads[str(p)]=str(dst)
 reports.append({'target':tag,'portrait_old':48 if modern else 144,'portrait_new':192,'portrait_template':doc.d['m_Name'],'changed_views':changed_views,'changed_objects':{n:list(cs) for n,cs in changes.items()},'health_assets':health_checks,'other_objects_byte_identical':True})
regpath=r'Software\Sports Interactive\Football Manager 27';key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,regpath);registry=[]
prefixes=['FirstTeamSquadAndYouthTeamSquadCollection','TacticTeamSelectionTableViewCollectionOverview','TacticTeamSelectionTableViewCollectionPossession','TacticTeamSelectionTableViewCollectionBoth']
for i in range(winreg.QueryInfoKey(key)[1]):
 name,value,kind=winreg.EnumValue(key,i)
 if any(name.startswith(p+'IsCustom_') or name.startswith(p+'BuildIn_') for p in prefixes):
  assert kind==winreg.REG_DWORD;registry.append({'name':name,'before':value,'after':0,'type':kind})
assert len(registry)==8
manifest={'installed':False,'runtime_verified':False,'checks':reports,'registry_path':regpath,'registry':registry,'before_sha256':{p:sha(b) for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) for p,s in payloads.items()},'protected_sha256':protected}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'sources':payloads,'before':backups},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-primary-navigation-patch.py').read_text('utf8')
installer=installer.replace('import hashlib, json, os, subprocess, sys, uuid','import hashlib, json, os, subprocess, sys, uuid, winreg')
needle="if verify:\n"
setup="""rk=winreg.OpenKey(winreg.HKEY_CURRENT_USER,m['registry_path'],0,winreg.KEY_READ|winreg.KEY_SET_VALUE)
reg_current={r['name']:winreg.QueryValueEx(rk,r['name']) for r in m['registry']}
for r in m['registry']:
    v,t=reg_current[r['name']]
    assert t==r['type'] and v in [r['before'],r['after']],('Preference changed',r['name'])
    if verify:assert v==r['after'],('Preference mismatch',r['name'])
"""
installer=installer.replace(needle,setup+needle)
installer=installer.replace("except BaseException:\n", "    for r in m['registry']:\n        v=r['before'] if restore else r['after']\n        winreg.SetValueEx(rk,r['name'],0,r['type'],v)\n        assert winreg.QueryValueEx(rk,r['name'])==(v,r['type'])\nexcept BaseException:\n    for name,(value,kind) in reg_current.items():winreg.SetValueEx(rk,name,0,kind,value)\n")
(OUT/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
for p,b in before.items():assert Path(p).read_bytes()==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
(R/'current-inbox-default-tactics-repair.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'runtime_verified':False},indent=2),'utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'checks':reports,'registry':registry},ensure_ascii=False),flush=True)
