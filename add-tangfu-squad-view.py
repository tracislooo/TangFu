from pathlib import Path
import sys,json,copy,hashlib,datetime,ast,struct,importlib.util,uuid
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
assert 'Football Manager 27' in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';F='ui-tablefactories_assets_all.bundle';V='ui-tableviews_assets_all.bundle'
OUT=R/('tangfu-squad-view-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'templates').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
extract('add-card-six-ratings.py',{'validate_ui'});extract('build-match-ui-avatars-layout.py',{'refs','sd','find','Doc'})
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def locations(self,key):
 if not hasattr(self,'index'):self.index=dict(self.keys())
 return [x[0] for x in self.array(self.index[key],'I')]
cm.Catalog.locations=locations
PID,SID=-991111000001000,-991111000001001
GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/TangFu/squad/happiness-icon/v1').hex
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];assert {PID,SID}.isdisjoint(int(t['path_id']) for t in reserved)
before={};payloads={};backups={};protected={};reports=[];custom_views=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in [W,F,'catalog.bin','catalog.hash']:
  p=GAME.parent/n if folder==GAME and n.startswith('catalog.') else folder/n
  if not p.exists() and n=='catalog.hash':continue
  before[str(p)]=p.read_bytes();bp=OUT/('backup-'+tag)/n;bp.parent.mkdir(exist_ok=True);bp.write_bytes(before[str(p)]);backups[str(p)]=str(bp)
 for p in folder.glob('*.bundle'):
  if p.name not in [W,F]:protected[str(p)]=sha(p.read_bytes())
 env={n:UnityPy.load(before[str(folder/n)]) for n in [W,F]};objs={n:{o.path_id:o for o in env[n].objects} for n in env};hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()};changes={n:{} for n in env};documents=[]
 ve=UnityPy.load(str(folder/V));views={o.peek_name():o.read_typetree() for o in ve.objects if o.type.name=='MonoBehaviour'}
 original=views['FirstTeamTableSelectionInfo']['m_tableView'];newview=copy.deepcopy(original);newview['m_viewName']={'GameID':0}
 factory=find(F,'PlayerTableFactory');fd=factory.read_typetree();oldfd=copy.deepcopy(fd);cols={c['m_id']:c for c in fd['m_rowData']}
 tactic=find(F,'TacticTeamSelectionTableFactory').read_typetree();tc={c['m_id']:c for c in tactic['m_rowData']}
 # Private icon-only copy: keep the native happiness state and image binding.
 source=Doc(W,name='PlayerPlayingTimeHappinessCell');assert PID not in objs[W] and SID not in objs[W]
 tree=copy.deepcopy(source.d);sheet=copy.deepcopy(source.s);tree['m_Name']='TangFuSquadHappinessIcon';tree['inlineSheet']['m_PathID']=SID;sheet['m_Name']='TangFuSquadHappinessIconStyle'
 for ob,pid,data in [(source.obj,PID,tree),(objs[W][source.sid],SID,sheet)]:
  clone=copy.copy(ob);clone.path_id=pid;clone.data=None;clone._read_until=None;clone.assets_file.objects[pid]=clone;objs[W][pid]=clone;clone.save_typetree(data)
 d=Doc(W,pid=PID,tree=tree,style=sheet)
 d.st(1001,[(131105,d.px(28)),(131097,d.px(28)),(131095,d.px(28)),(131101,d.px(0)),(131100,d.px(0)),(131098,d.px(0)),(131099,d.px(0))])
 d.st(1002,[(131105,d.pct(100)),(131073,d.enum('center')),(131074,d.enum('center')),(131090,d.px(0)),(131093,d.px(0))])
 d.a(1004)['m_Classes']=[c for c in d.a(1004)['m_Classes'] if not c.startswith('margin-')]
 d.st(1004,[(131090,d.px(0)),(131093,d.px(0))]);d.st(1005,[(131081,d.enum('none'))]);d.save()
 # Only these new factory column IDs use the tactical displays or narrow happiness.
 newcols=[]
 condition=copy.deepcopy(tc['condition']);condition['m_id']='tangfu-fitness-sharpness'
 condition['m_valueBindings'][0]['to']['m_path']='binding';condition['m_sortBinding']['m_path']='binding.Condition';condition['m_sortBindingPlugin']=cols['condition-icon']['m_sortBindingPlugin'];newcols.append(condition)
 morale=copy.deepcopy(tc['morale-icon-only']);morale['m_id']='tangfu-morale';morale['m_sortBinding']['m_path']='binding.Morale';morale['m_sortBindingPlugin']=cols['morale-icon-only']['m_sortBindingPlugin']
 morale['m_valueBindings']=[{'m_serialisedType':0,'from':'binding','to':{'m_path':'binding.Morale'},'type':{'id':0}}];newcols.append(morale)
 happy=copy.deepcopy(cols['playing-time-happiness']);happy.update(m_id='tangfu-happiness-icon',m_defaultWidth=28.,m_minimumWidth=28.,m_allowWidthAutoResizing=0);happy['m_translationID']={'GameID':12800};happy['m_uxmlRef']['m_AssetGUID']=GUID;newcols.append(happy)
 assert not any(c['m_id'].startswith('tangfu-') for c in fd['m_rowData'])
 fd['m_rowData'].extend(newcols);factory.save_typetree(fd);changes[F][factory.path_id]=fd
 originalcols={c['m_columnID']:c for c in original['m_tableConfig']};prototype=original['m_tableConfig'][0]
 def config(ident,width=None):
  c=copy.deepcopy(originalcols.get(ident,prototype));c['m_columnID']=ident
  if width is not None:c['m_columnMetadata'].update(m_widthOverride=float(width),m_minWidthOverride=float(width),m_applicableBreakpoints=-1,m_optionalConditions=[],m_optionalConfigConditions=[])
  return c
 prefix=[]
 for c in original['m_tableConfig']:
  prefix.append(copy.deepcopy(c))
  if c['m_columnID']=='position':break
 financial=['age','current-ability-stars','potential-ability-stars','transfer-value','wage']
 removed={'injury-time-missed','stats-minutes','tactical-effectiveness-gauge','condition-icon','match-sharpness','morale-icon-only','playing-time-happiness'}|set(financial)|{c['m_columnID'] for c in prefix}
 result=prefix+[config(x,cols[x]['m_defaultWidth']) for x in financial]+[config('tangfu-fitness-sharpness',90),config('tangfu-morale',36)]+[copy.deepcopy(c) for c in original['m_tableConfig'] if c['m_columnID'] not in removed]+[config('tangfu-happiness-icon',28)]
 newview['m_tableConfig']=result
 assert result[-1]['m_columnID']=='tangfu-happiness-icon';assert all(x not in [c['m_columnID'] for c in result] for x in ['injury-time-missed','stats-minutes','tactical-effectiveness-gauge'])
 assert [c['m_columnID'] for c in result[len(prefix):len(prefix)+5]]==financial
 # Native custom table views use their JSON filename as the literal menu name.
 def native_json(v):
  if isinstance(v,dict):return {k:(bool(x) if k in ['m_required','m_sortingDisabled','m_overwriteFooterSettings','m_inverseCheck'] else native_json(x)) for k,x in v.items()}
  if isinstance(v,list):return [native_json(x) for x in v]
  return v
 custom_views.append(native_json(newview))
 metaobj=next(o for o in objs[W].values() if o.type.name=='AssetBundle');mt=metaobj.read_typetree()
 origin=next(v for g,v in mt['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':source.obj.path_id});oldguid=next(g for g,v in mt['m_Container'] if v is origin)
 span=copy.deepcopy(mt['m_PreloadTable'][origin['preloadIndex']:origin['preloadIndex']+origin['preloadSize']])
 for ref in span:
  if ref=={'m_FileID':0,'m_PathID':source.obj.path_id}:ref['m_PathID']=PID
  elif ref=={'m_FileID':0,'m_PathID':source.sid}:ref['m_PathID']=SID
 for pid in [PID,SID]:
  if {'m_FileID':0,'m_PathID':pid} not in span:span.append({'m_FileID':0,'m_PathID':pid})
 mt['m_Container'].append((GUID,{'preloadIndex':len(mt['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));mt['m_PreloadTable'].extend(span);mt['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(mt);changes[W][metaobj.path_id]=mt
 cp=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';oldcat=cm.Catalog(before[str(cp)]);loc=next(l for l in oldcat.locations(oldguid) if oldcat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
 cat=cm.Catalog(oldcat.add_key_location(GUID,loc,loc));keys=cat.keys();idx=next(i for i,(k,_) in enumerate(keys) if k=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[idx];oldlocs=[x[0] for x in cat.array(ls,'I')];records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',x) for x in oldlocs+cat.locations(GUID)),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
 # Validate actual templates/functions and ownership for every final table column.
 catalog_check=cm.Catalog(catalog);catkeys=dict(catalog_check.keys());loaded={};seen=set();audit=[]
 audit_source=(R/'add-squad-hidden-second-view.py').read_text('utf8');body=audit_source[audit_source.index(' def audit_guid(g):'):audit_source.index(' for col in cols:audit_guid')]
 cat=catalog_check;keys=catkeys;catalog_audit=audit
 exec(compile(body[1:].replace('\n ','\n'),'native-cell-audit','exec'))
 # Read the prepared world file for new private cells; original native dependencies
 # are checked before adding the private GUID below.
 allcols={c['m_id']:c for c in fd['m_rowData']}
 for c in result:
  fcol=allcols[c['m_columnID']]
  if fcol['m_uxmlRef']['m_AssetGUID']!=GUID:audit_guid(fcol['m_uxmlRef']['m_AssetGUID'])
  if fcol['m_headerUxmlRef']['m_AssetGUID']:audit_guid(fcol['m_headerUxmlRef']['m_AssetGUID'])
 q=catalog_check.location(catalog_check.locations(GUID)[0]);assert q['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and catalog_check.location(q['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
 for n in [W,F]:
  b=env[n].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
  for pid,h in hashes[n].items():
   if pid not in changes[n]:assert sha(check[pid].get_raw_data())==h,(tag,n,pid)
  for pid,data in changes[n].items():assert check[pid].read_typetree()==data
  destination=OUT/tag/n;destination.parent.mkdir(exist_ok=True);destination.write_bytes(b);payloads[str(folder/n)]=str(destination)
 for name,b in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  p=GAME.parent/name if folder==GAME else folder/name
  if str(p) not in before:continue
  destination=OUT/tag/name;destination.write_bytes(b);payloads[str(p)]=str(destination)
 reports.append({'folder':tag,'columns':[c['m_columnID'] for c in result],'retained_original_view':True,'happiness_width':28,'native_resources_verified':len(audit),'private_happiness_guid':GUID})
assert custom_views[0]==custom_views[1], 'Game and skin view definitions differ; keep the game custom view explicitly.'
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/FirstTeamSquadAndYouthTeamSquadCollection/TangFu.json')
data=json.dumps(custom_views[0],ensure_ascii=False,separators=(',',':')).encode('utf8');source=OUT/'TangFu.json';source.write_bytes(data);payloads[str(cache)]=str(source)
if cache.exists():
 before[str(cache)]=cache.read_bytes();bp=OUT/'backup-user-TangFu.json';bp.write_bytes(before[str(cache)]);backups[str(cache)]=str(bp)
else:before[str(cache)]=None;backups[str(cache)]=None
for p,b in before.items():assert (Path(p).read_bytes() if Path(p).exists() else None)==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
m={'installed':False,'runtime_verified':False,'reports':reports,'custom_view_file':str(cache),'before_sha256':{p:sha(b) if b is not None else None for p,b in before.items()},'after_sha256':{p:sha(Path(s).read_bytes()) for p,s in payloads.items()},'protected_sha256':protected,'original_selection_and_hidden_views_unchanged':True,'no_added_portraits':True}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps({'sources':payloads,'before':backups},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-tangfu-squad-view.py').read_bytes())
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('TangFu 是“选择信息”的独立原生自定义表格视图，以用户目录 FirstTeamSquadAndYouthTeamSquadCollection/TangFu.json 的文件名显示。位置之后放年龄、能力星级、潜力星级、转会身价、工资；体能与比赛状态复用战术表当前双环及标题，士气复用当前数字显示；去掉缺席时间、上场时间和战术效果。原上场时间满意度绑定保留，私有单元格仅显示笑脸，移至最后，宽28px。其他原统计列保留；原选择信息及隐藏视图不改，不新增头像。仅PlayerTableFactory新增三份私有列定义，增加一份私有满意度模板和必要目录/预加载；对游戏与独立皮肤分别增量打包。文件及资源检查通过，未启动游戏，实际显示与交互待用户确认。restore.ps1有哈希保护。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'custom_view':str(cache),'reports':reports},ensure_ascii=False),flush=True)
