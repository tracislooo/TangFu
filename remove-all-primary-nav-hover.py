"""Freeze primary navigation hover paint at its normal values, including Continue."""
from pathlib import Path
import copy,datetime,json,re,struct,sys
R=Path(__file__).resolve().parent
# Reuse the current-resource, catalog and image audit only, never an old installer.
audit=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0]
exec(compile(audit,'<current-resource-audit>','exec'))
original_args=sys.argv[:]
engine_src=(R/'verify-lake-blue-controls.py').read_text('utf8').split('checks=0;button_count=0')[0]
engine_src=engine_src.replace("p=out/tag/name if (out/tag/name).exists() else folder/name","p=folder/name")
compiler_src=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in compiler_src.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
payloads={};reports={}
KEYS=[458752,65536,196610,458767,262146,458758,458761,458762,458763,'--start-colour','--end-colour']
def compound(n):
 text=n['type']
 if re.fullmatch(r'[A-Za-z_][\w-]*',n['name']):text+='#'+n['name']
 text+=''.join('.'+c for c in sorted(n['classes']) if re.fullmatch(r'[A-Za-z_][\w-]*',c))
 return text
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 sys.argv=['verify-lake-blue-controls.py',str(R/'lake-blue-controls-20261028-001232')]+(['--skin'] if tag=='skin' else [])
 ns={'__file__':str(R/'verify-lake-blue-controls.py')}
 exec(compile(engine_src,'<live-navigation-cascade>','exec'),ns)
 ns['expand'](ns['W'],ns['named'](ns['W'],'PrimaryNavigationBar'))
 nodes=ns['nodes'];ancestry=ns['ancestry'];original_applied=ns['applied'];cache={}
 def fast(n,state):
  key=(id(n),tuple(sorted(state)))
  if key not in cache:cache[key]=original_applied(n,state)
  return cache[key]
 ns['applied']=fast
 p=folder/S;en=UnityPy.load(before[p]);oo={o.path_id:o for o in en.objects}
 hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
 sh=ob.read_typetree();old=copy.deepcopy(sh);rules={};differences=0
 for selected in [False,True]:
  # Exercise both native active/inactive menu classes, including runtime switches.
  changed=[]
  if selected:
   for n in nodes:
    cls=n['classes']
    if 'navigation-tab-portal-default-active-false' in cls:
     changed.append(n);cls.remove('navigation-tab-portal-default-active-false');cls.add('navigation-tab-portal-default-active-true')
  cache.clear()
  for n in nodes:
   a=fast(n,{'enabled'});b=fast(n,{'enabled','hover'})
   for key in KEYS:
    normal=ns['prop'](n,key,{'enabled'});hover=ns['prop'](n,key,{'enabled','hover'})
    if normal==hover:continue
    if normal is None:
     normal=1. if key==458767 else {'r':0.,'g':0.,'b':0.,'a':0.} if key==458752 else None
    if normal is None:continue
    chain=ancestry(n)
    owner=next((a for a in chain[1:] if a['type'] in ['SIButton','SIDropdown']),None)
    target=compound(n)
    # Control state classes keep selected and unselected normal paint distinct.
    path=('#MainNav.fm27-fixed-primary-nav:hover '+(compound(owner)+' ' if owner else '')+target+':enabled')
    values=rules.setdefault(path,{})
    assert key not in values or values[key]==normal,(path,key)
    values[key]=normal;differences+=1
  for n in changed:n['classes'].remove('navigation-tab-portal-default-active-true');n['classes'].add('navigation-tab-portal-default-active-false')
 for text,properties in rules.items():
  idx=len(sh['m_Rules']);props=[]
  for key,val in properties.items():
   typ=4 if isinstance(val,dict) else 2;pool='colors' if typ==4 else 'floats'
   sh[pool].append(copy.deepcopy(val))
   props.append({'m_Id':-1 if isinstance(key,str) else key,'m_CustomName':key if isinstance(key,str) else '', 'm_Line':-1,'m_Values':[{'m_ValueType':typ,'valueIndex':len(sh[pool])-1}]})
  sel=selector(text,idx)
  # Scope contains an actual MainNav ID and the control's existing class/name;
  # higher than any native per-control hover rule, without touching shared roles.
  sh['m_Rules'].append({'m_ComplexSelectors':[sel],'m_Properties':props,'line':-1})
 # Verify every override wins and freezes the observed property at normal paint.
 added=sh['m_Rules'][len(old['m_Rules']):]
 checks=0
 for selected in [False,True]:
  changed=[]
  if selected:
   for n in nodes:
    if 'navigation-tab-portal-default-active-false' in n['classes']:
     changed.append(n);n['classes'].remove('navigation-tab-portal-default-active-false');n['classes'].add('navigation-tab-portal-default-active-true')
  cache.clear()
  for n in nodes:
   baseline=fast(n,{'enabled'});hover=fast(n,{'enabled','hover'}).copy()
   for r in added:
    sel=r['m_ComplexSelectors'][0]
    if not ns['matches'](n,sel,{'enabled','hover'}):continue
    for prop in r['m_Properties']:
     key=prop['m_CustomName'] or prop['m_Id'];weight=(sel['m_Specificity'],1000000)
     if weight>=hover.get(key,((-1,-1),None))[0]:hover[key]=(weight,sh['colors' if prop['m_Values'][0]['m_ValueType']==4 else 'floats'][prop['m_Values'][0]['valueIndex']])
   for key in KEYS:
    base=ns['prop'](n,key,{'enabled'});value=hover.get(key)
    actual=value[1] if value else ns['prop'](n,key,{'enabled','hover'})
    if base is None and actual in [1.,{'r':0.,'g':0.,'b':0.,'a':0.}]:continue
    assert base==actual,('Hover still differs',n['name'],key,base,actual)
    checks+=1
  for n in changed:n['classes'].remove('navigation-tab-portal-default-active-true');n['classes'].add('navigation-tab-portal-default-active-false')
 for k,v in old.items():
  if isinstance(v,list):assert sh[k][:len(v)]==v,k
  else:assert sh[k]==v,k
 ob.save_typetree(sh);raw=en.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(oo)
 for pid,o in saved.items():
  if pid==ob.path_id:assert o.read_typetree()==sh
  else:assert sha(o.get_raw_data())==hashes[pid],pid
 payloads[str(p)]=raw;reports[str(p)]={'added_hover_only_rules':len(added),'normal_hover_comparisons':checks,'selected_and_unselected_verified':True,'navigation_nodes':len(nodes),'runtime_verified':False}
sys.argv=original_args
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-remove-all-hover-'+stamp);out.mkdir();sources={};backups={}
for p,b in payloads.items():
 tag='game' if Path(p).parent==GAME else 'skin';(out/tag).mkdir();(out/('backup-'+tag)).mkdir()
 target=out/tag/S;target.write_bytes(b);backup=out/('backup-'+tag)/S;backup.write_bytes(before[Path(p)])
 sources[p]=str(target);backups[p]=str(backup)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{p:sha(b) for p,b in payloads.items()},'protected_sha256':protected,'hover_verification':reports,'catalog_audits':audits,'active_textures_verified':len(registry['textures'])}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[S],'sources':sources,'before':backups},ensure_ascii=False,indent=2),'utf8')
(out/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'说明.md').write_text('取消最上方主导航全部悬停视觉反馈，包括文字透明度、图标/标签高亮、背景变化和湖蓝继续按钮悬停变色。常态配色保持原样；点击/按下、菜单、提示和禁用状态保留。只在 MainNav 范围内追加 hover 专用规则，冻结为当前常态值；不改模板事件、图片和其他页面的悬停效果。已完成选中/未选中导航的离线样式对比，实际显示待启动游戏确认。','utf8')
print(json.dumps({'prepared':True,'output':str(out),'checks':reports},ensure_ascii=False),flush=True)
