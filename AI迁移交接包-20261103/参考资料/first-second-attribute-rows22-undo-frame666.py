exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','first-second-attribute-rows22-undo-frame666-'))
import uuid,importlib.util
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
ROW=-940000000021000;RS=ROW-1;TABLE=ROW-2;TS=ROW-3;RK=uuid.uuid5(uuid.NAMESPACE_URL,'FM27FirstSecondAttributeRow22').hex;TK=uuid.uuid5(uuid.NAMESPACE_URL,'FM27FirstSecondAttributeTable22').hex
for pid in [ROW,RS,TABLE,TS]:assert str(pid) not in (R/'reserved-texture-ids.json').read_text('utf8')
outputs={};audits=[];pages=[-930000000001001,-930000000001003,-940000000010000,-940000000012000]
for folder in [GAME,SKIN]:
 es={bn:UnityPy.load(before[folder/bn]) for bn in [W,G]};os={bn:{o.path_id:o for o in es[bn].objects} for bn in [W,G]};hh={bn:{i:sha(o.get_raw_data()) for i,o in os[bn].items()} for bn in [W,G]};changed={W:set(),G:set()};go=os[G]
 assert not any(i in go for i in [ROW,RS,TABLE,TS])
 rd=go[-930000000001001].read_typetree();rssrc=rd['inlineSheet']['m_PathID'];sheet=go[rssrc].read_typetree();rd['m_Name']='OverviewFirstSecondAttributeRow22';rd['inlineSheet']['m_PathID']=RS;sheet['m_Name']='OverviewFirstSecondAttributeRow22Style';rr=refs(rd)
 for i in [1001,1008,1009,1014]:override(rr[i]['data'],[prop(131087,px(22)),prop(131096,px(22)),prop(131094,px(22))])
 validate_ui(rd,sheet);rowstyle=sheet
 td=go[-930000000001003].read_typetree();tssrc=td['inlineSheet']['m_PathID'];sheet=go[tssrc].read_typetree();td['m_Name']='OverviewFirstSecondAttributeTable22';td['inlineSheet']['m_PathID']=TS;rr=refs(td);listcount=0
 for i,r in rr.items():
  v=r.get('data',{})
  if 'm_FullTypeName' not in v:continue
  s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if s.get('RowTemplate',{}).get('m_AssetGUID')!='aa5993dcecf4529d9fa280f078b11b0c':continue
  assert s['FixedElementSize']==24.;s['FixedElementSize']=22.;s['FixedElementSize_UxmlAttributeFlags']=1;s['RowTemplate']['m_AssetGUID']=RK;listcount+=1
  props=sheet['m_Rules'][v['m_RuleIndex']]['m_Properties'];ed=[]
  for p in props:
   if p['m_Id'] in [131087,131096,131094]:
    q=p['m_Values'][0]
    if q['m_ValueType']==3:
     d=sheet['dimensions'][q['valueIndex']]
     if d['unit']==1 and d['value']>0:ed.append(prop(p['m_Id'],px(round(d['value']/24*22,4))))
  if ed:override(v,ed)
 assert listcount>=6;validate_ui(td,sheet);tablestyle=sheet
 for srcid,pid,d in [(rssrc,RS,rowstyle),(-930000000001001,ROW,rd),(tssrc,TS,tablestyle),(-930000000001003,TABLE,td)]:
  o=copy.copy(go[srcid]);o.path_id=pid;o.assets_file.objects[pid]=o;go[pid]=o;o.save_typetree(d);changed[G].add(pid)
 ab=next(o for o in go.values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
 for sourcekey,key,sourcepid,pid,sourceStyle,styleid in [('aa5993dcecf4529d9fa280f078b11b0c',RK,-930000000001001,ROW,rssrc,RS),('3bc158458fec50bf9230826edbc62cd1',TK,-930000000001003,TABLE,tssrc,TS)]:
  entry=next(v for k,v in meta['m_Container'] if k==sourcekey and v['asset']['m_PathID']==sourcepid);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  for p in span:
   if p['m_FileID']==0 and p['m_PathID'] in [sourcepid,sourceStyle]:p['m_PathID']={sourcepid:pid,sourceStyle:styleid}[p['m_PathID']]
  if pid==TABLE:
   for p in [{'m_FileID':0,'m_PathID':ROW},{'m_FileID':0,'m_PathID':RS}]:
    if p not in span:span.append(p)
  meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable'].extend(span)
 meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta);changed[G].add(ab.path_id)
 for pid in pages:
  doc=os[W][pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=os[W][sid].read_typetree();p0=next(p for p in sheet['m_Rules'][rr[1001]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131096);assert sheet['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==666;override(rr[1001]['data'],[prop(131096,px(674))])
  if pid in pages[:2]:
   u=next(u for u in doc['m_Usings'] if u['alias']=='AttributesTableTemplate');assert u['path']=='3bc158458fec50bf9230826edbc62cd1';u.update(path=TK,asset={'m_FileID':0,'m_PathID':0})
  validate_ui(doc,sheet);os[W][pid].save_typetree(doc);os[W][sid].save_typetree(sheet);changed[W].update([pid,sid])
 for bn in [W,G]:
  out=es[bn].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
  for i,h in hh[bn].items():
   if i not in changed[bn]:assert sha(check[i].get_raw_data())==h,(folder,bn,i)
  outputs[folder/bn]=out;dest=OUT/('prepared-game' if folder==GAME else 'prepared-skin');dest.mkdir(exist_ok=True);(dest/bn).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[p])
 c=cm.Catalog(before[catfolder/'catalog.bin'])
 for sourcekey,key in [('aa5993dcecf4529d9fa280f078b11b0c',RK),('3bc158458fec50bf9230826edbc62cd1',TK)]:
  loc=next(x for x in c.locations(sourcekey) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(key,loc,loc));nl=c.locations(key)[0];assert c.location(c.location(nl)['dependencies'][0])['internal'].endswith(G)
 outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'target':str(folder),'compact_lists':listcount,'first_second_row_height':22,'third_fourth_row_height':24,'all_root_min_restored':674})
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'changes':audits,'private_row':str(ROW),'private_table':str(TABLE),'row_guid':RK,'table_guid':TK};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'row_height':22}))
