from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,subprocess,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
oldwrite=TypeTreeHelper.write_value
for filename,fn,cl in [('build-fc-player-hover-layout.py',{'write'},{'Styles'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'},set()),('unify-lake-blue-controls.py',{'append_rule','color'},set())]:
 tree=ast.parse((R/filename).read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in fn or isinstance(n,ast.ClassDef) and n.name in cl],type_ignores=[]),filename,'exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);S='ui-styles_assets_default.bundle';C='ui-styles_assets_common.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';BG='ui-backgrounds_assets_common.bundle';names=[S,C,M];sha=lambda b:hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
out=R/('lake-controls-progress-repair-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir()
before={};payloads={};protected={};audits=[];expected_by={}
for folder in [GAME,SKIN]:
 for name in names:before[folder/name]=(folder/name).read_bytes()
 catdir=folder.parent if folder==GAME else folder
 for name in ['catalog.bin','catalog.hash']:before[catdir/name]=(catdir/name).read_bytes()
 for p in folder.glob('*.bundle'):
  if p.name not in names:protected[str(p)]=sha(p.read_bytes())
for name in ['AGENTS.md','current-custom-textures.json','reserved-texture-ids.json','current-ui-surface-theme.json']:
 p=R/name
 if p.exists():protected[str(p)]=sha(p.read_bytes())
active=['.buttons-segmented-button-row-active-regular-placement-'+x for x in ['leading','middle','trailing']]+['.buttons-segmented-button-row-regular-selected','.segmented-button-group .unity-radio-button-group__child-active','.segmented-button-group-purple .unity-radio-button-group__child-active','.segmented-button-labels .unity-radio-button-group__child-active','.radio_group_button_purple .unity-radio-button-group__child-active','.tabgroup.SegmentedButtonRow .tabgroup__tab--active','.buttongroup.SegmentedButtonRow .buttongroup__button--active']
for folder in [GAME,SKIN]:
 tag='game' if folder==GAME else 'skin';rows=[]
 for bn in names:
  e=UnityPy.load(before[folder/bn]);oo={o.path_id:o for o in e.objects};expected={};original={i:o.get_raw_data() for i,o in oo.items()}
  if bn in [S,C]:
   for ob in oo.values():
    if ob.type.name!='MonoBehaviour':continue
    sh=ob.read_typetree()
    if 'm_Rules' not in sh:continue
    prior=copy.deepcopy(sh);edits=[]
    for r in sh['m_Rules']:
     for p in r['m_Properties']:
      k=p.get('m_CustomName')
      if k in ['--buttons-toggle-active-primary-surface','--buttons-toggle-active-primary-hover','--data-progress-indicator-foreground']:
       v=color('35C6E8' if k=='--data-progress-indicator-foreground' else '119DD5' if k.endswith('hover') else '078BC4')
       if len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4 and sh['colors'][p['m_Values'][0]['valueIndex']]==v:continue
       p['m_Values']=[Styles(sh).h(4,v)];edits.append(k)
    if sh['m_Name']=='AlwaysAppliedStyleSheet':
     # Replace only this patch's previous selector rules, making repeated use safe.
     specs=[([a,a+':hover'],[(458752,color('078BC4'))]) for a in active]
     specs += [(['#LoadGameProgress .progress-bar-value','#SaveGameProgress .progress-bar-value'],[(458752,color('35C6E8'))])]
     specs += [(['#playpause.tf27-lake-match-control','#playpause.tf27-lake-match-control:hover','#playpause.tf27-lake-match-control:active'],[(458752,color('078BC4'))])]
     for selectors,props in specs:
      idx=len(sh['m_Rules']);new=[selector(x,idx) for x in selectors]
      existing=next((r for r in reversed(sh['m_Rules']) if [{k:v for k,v in x.items() if k!='ruleIndex'} for x in r['m_ComplexSelectors']]==[{k:v for k,v in x.items() if k!='ruleIndex'} for x in new]),None)
      if existing:
       for k,v in props:
        p=next((p for p in existing['m_Properties'] if p['m_Id']==k),None)
        if p is None:existing['m_Properties'].append(Styles(sh).p(k,Styles(sh).h(4,v)))
        elif len(p['m_Values'])!=1 or p['m_Values'][0]['m_ValueType']!=4 or sh['colors'][p['m_Values'][0]['valueIndex']]!=v:p['m_Values']=[Styles(sh).h(4,v)]
      else:append_rule(sh,selectors,props)
     edits.append('selected controls / loading progress / playpause scoped rules')
    if sh!=prior:ob.save_typetree(sh);expected[ob.path_id]=sh;rows.append({'bundle':bn,'sheet':sh['m_Name'],'edits':edits})
  else:
   ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='DefaultMatchUI');d=ob.read_typetree();prior=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']};nodes=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='playpause'];assert len(nodes)==1;node=nodes[0];so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree()
   if 'tf27-lake-match-control' not in node['data']['m_Classes']:node['data']['m_Classes'].append('tf27-lake-match-control')
   Styles(sh).edit(node,[Styles(sh).p(458752,Styles(sh).h(4,color('078BC4')))])
   assert d['references']['RefIds'][0]==prior['references']['RefIds'][0]
   for r in d['references']['RefIds']:
    old=next(x for x in prior['references']['RefIds'] if x['rid']==r['rid'])
    if r['rid']!=node['rid']:assert r==old
   for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
   rows.append({'bundle':bn,'template':d['m_Name'],'node':'playpause','background':'#078BC4','events_bindings_other_nodes_unchanged':True})
  if not expected:
   protected[str(folder/bn)]=sha(before[folder/bn]);continue
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};assert set(check)==set(oo)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid],(tag,bn,pid)
   else:assert o.get_raw_data()==original[pid],(tag,bn,pid)
  payloads[folder/bn]=data;expected_by[str(folder/bn)]={'changed_objects':list(expected),'unrelated_objects_verified':len(oo)-len(expected)}
 # Change existing bundle options only; key arrays, dependency graph and provider IDs are retained.
 catdir=folder.parent if folder==GAME else folder;cp=catdir/'catalog.bin';c=cm.Catalog(before[cp]);locations={i:c.location(i) for _,ls in c.keys() for i, in c.array(ls,'I')};catalog_rows=[]
 for bn in names:
  if folder/bn not in payloads:continue
  data=payloads[folder/bn];rd=EndianBinaryReader(data);bu=object.__new__(BundleFile);bu.signature=rd.read_string_to_null();bu.version=rd.read_u_int();bu.version_player=rd.read_string_to_null();bu.version_engine=rd.read_string_to_null();_,block=bu.read_fs(rd);crc=zlib.crc32(block.bytes);count=0
  for i,v in locations.items():
   if v['type'][1].endswith('IAssetBundleResource') and v['internal'].replace('\\','/').endswith('/'+bn) and v['raw'][5]!=4294967295:
    typ,pt=c.unpack(v['raw'][5],'2I');raw=list(c.unpack(pt,'5I'));raw[2:4]=[crc,len(data)];extra=c.append(struct.pack('<2I',typ,c.append(struct.pack('<5I',*raw))));record=list(v['raw']);record[5]=extra;struct.pack_into('<7I',c.data,i,*record);count+=1
  assert count or tag=='skin',(tag,bn);catalog_rows.append({'bundle':bn,'crc':crc,'size':len(data),'locations':count})
 cc=cm.Catalog(bytes(c.data));assert len(c.data)>=len(before[cp])
 for i,v in locations.items():
  now=cc.location(i);a=list(v['raw']);b=list(now['raw']);a[5]=b[5]=0;assert a==b
 priorcat=cm.Catalog(before[cp]);assert priorcat.key_records==cc.key_records
 for oldk,pt in priorcat.keys():
  assert priorcat.array(pt,'I')==cc.array(pt,'I')
 payloads[cp]=bytes(c.data);payloads[catdir/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'variant':tag,'edits':rows,'catalog_crc_and_size':catalog_rows,'catalog_keys_dependencies_and_providers_preserved':True})
# Read-only image retirement audit; this patch never writes image bundles.
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(t['path_id']) for t in reserved}
for folder in [GAME,SKIN]:
 be=UnityPy.load(str(folder/BG));oo={o.path_id:o for o in be.objects};ab=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');assert banned.isdisjoint(oo);assert all(x['m_PathID'] not in banned for x in ab['m_PreloadTable']);assert all(v['asset']['m_PathID'] not in banned for k,v in ab['m_Container'])
for p,b in before.items():assert p.read_bytes()==b,p
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'aa':str(GAME.parent),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent in [GAME,GAME.parent] else 'skin';dst=out/tag/p.name;bak=out/('backup-'+tag)/p.name;dst.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'audits':audits,'object_audits':expected_by,'palette':{'selection_playpause':'#078BC4','hover':'#119DD5','loading_progress':'#35C6E8'}}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-native-background-overrides.py').read_text('utf8').replace("['game','skin','workspace']","['game','skin','workspace','aa']");(out/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'files':len(payloads),'audits':audits},ensure_ascii=False))

