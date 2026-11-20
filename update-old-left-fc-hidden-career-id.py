"""Update only the old left FC hidden overview using current installed donor modules."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-940000000010000;DONOR=-941100000001020
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('old-left-fc-hidden-career-id-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for name in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
def remove(doc,root):
 rr=refs(doc);owned=owned_refs(rr,root);parent=rr[root]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':root});doc['references']['RefIds']=[r for r in doc['references']['RefIds']if r['rid']not in owned];return owned

def graft(doc,sheet,source,ss,root,parent,slot=None):
 rr,dr=refs(doc),refs(source);owned=owned_refs(dr,root);start=max(rr)+1;rm={i:start+j for j,i in enumerate(sorted(owned))};startid=max(r.get('data',{}).get('m_Id',0)for r in rr.values())+1
 im={dr[i]['data']['m_Id']:startid+j for j,i in enumerate(sorted(i for i in owned if 'm_Id'in dr[i]['data']))};assert max(im.values())<2147483647
 rules={}
 def remap(v):
  if isinstance(v,list):
   for x in v:remap(x)
  elif isinstance(v,dict):
   if set(v)=={'rid'}:v['rid']=rm.get(v['rid'],v['rid'])
   else:
    for k,x in list(v.items()):
     if k in ['m_Id','m_ParentId','uxmlAssetId','m_ElementId']and isinstance(x,int):v[k]=im.get(x,x)
     elif k=='m_ElementIdsPath':v[k]=[im.get(a,a)for a in x]
     else:remap(x)
 for i in sorted(owned):
  r=copy.deepcopy(dr[i]);r['rid']=rm[i];remap(r['data']);a=r['data']
  if i==root:a['m_Parent']={'rid':parent}
  idx=a.get('m_RuleIndex',-1)
  if idx>=0:
   if idx not in rules:
    rule=copy.deepcopy(ss['m_Rules'][idx]);assert not rule['m_ComplexSelectors']
    for p in rule['m_Properties']:
     for h in p['m_Values']:
      pool=poolmap.get(h['m_ValueType'])
      if pool:sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    rules[idx]=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
   a['m_RuleIndex']=rules[idx]
  alias=a.get('m_TemplateAlias')
  if alias:
   u=next(u for u in source['m_Usings']if u['alias']==alias);old=next((x for x in doc['m_Usings']if x['alias']==alias),None)
   if old:assert old==u,(alias,old,u)
   else:doc['m_Usings'].append(copy.deepcopy(u))
  doc['references']['RefIds'].append(r)
 kids=refs(doc)[parent]['data']['m_Children'];kids.insert(len(kids)if slot is None else slot,{'rid':rm[root]})
 return rm
for tag,root in roots:
 print('Preparing '+tag,flush=True);before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 doc=obs[PAGE].read_typetree();old=copy.deepcopy(doc);sheet=obs[doc['inlineSheet']['m_PathID']].read_typetree();source=obs[DONOR].read_typetree();ss=obs[source['inlineSheet']['m_PathID']].read_typetree()
 # Remove management badges from the imported module; keep its native star-rating context.
 remove(source,1351);remove(source,6304)
 removed=remove(doc,1011);rm=graft(doc,sheet,source,ss,1011,1703)
 # Replace the entire old fitness/season-stat panel with the current native career table.
 removed|=remove(doc,1173);career=graft(doc,sheet,source,ss,8274,6322)
 rr=refs(doc);st=Styles(sheet)
 def edit(i,props):st.edit(rr[i],props)
 auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
 # Preserve the old upper region height; let both module columns fill that region.
 edit(rm[1011],[st.p(131105,st.pct(100)),st.p(131087,st.pct(100)),st.p(131082,st.px(0)),st.p(131084,st.num(1))])
 edit(rm[6298],[st.p(131087,st.pct(100)),st.p(131096,st.px(0)),st.p(131094,st.pct(100)),st.p(131093,st.px(0)),st.p(131085,st.num(1))])
 # Free layout height below the horizontal divider for the career table.
 edit(career[8274],[st.p(131087,st.px(0)),st.p(131082,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131096,st.px(0))])
 edit(6334,[st.p(131093,st.px(4)),st.p(131090,st.px(4))])
 # Clone the current vertical separator and insert it between identity and attributes.
 prototype=(rr[6330],rr[rr[6330]['data']['m_SerializedData']['rid']]);sep=add_node(doc,prototype,1002,'OldLeftFCIdentityAttributesDivider');rr=refs(doc)
 rr[1002]['data']['m_Children'].remove({'rid':sep});rr[1002]['data']['m_Children'].insert(1,{'rid':sep})
 props=copy.deepcopy(sheet['m_Rules'][rr[6330]['data']['m_RuleIndex']]['m_Properties']);st.edit(rr[sep],props,reset=True)
 # Move the existing preference-controlled ID instance above the complete name row.
 oldid=copy.deepcopy(data(rr,1221));rr[1205]['data']['m_Children'].remove({'rid':1221});rr[1188]['data']['m_Children'].insert(0,{'rid':1221});rr[1221]['data']['m_Parent']={'rid':1188}
 edit(1221,[st.p(131102,st.en('relative')),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131074,st.en('center'))]);assert data(rr,1221)==oldid
 graph(doc);validate_ui(doc,sheet)
 # Prove the full FC card and all retained serialized bindings remain unchanged.
 original=refs(old)
 assert all(rr[i]==r for i,r in original.items()if i in owned_refs(original,1299))
 for i,r in original.items():
  if i not in removed and 'm_SerializedData'not in r.get('data',{}):assert rr[i]==r,('Retained binding changed',i)
 # Extend the target preload span and Addressables dependencies with the current donor closure.
 ab=next(o for o in obs.values()if o.type.name=='AssetBundle');meta=ab.read_typetree()
 def entry_for(pid):return next((k,e)for k,e in meta['m_Container']if e['asset']=={'m_FileID':0,'m_PathID':pid})
 target_key,te=entry_for(PAGE);donor_key,de=entry_for(DONOR)
 span=copy.deepcopy(meta['m_PreloadTable'][te['preloadIndex']:te['preloadIndex']+te['preloadSize']])
 for ptr in copy.deepcopy(meta['m_PreloadTable'][de['preloadIndex']:de['preloadIndex']+de['preloadSize']]):
  if ptr['m_FileID']==0:ptr['m_PathID']={DONOR:PAGE,source['inlineSheet']['m_PathID']:doc['inlineSheet']['m_PathID']}.get(ptr['m_PathID'],ptr['m_PathID'])
  if ptr not in span:span.append(ptr)
 reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
 assert not any(p['m_PathID']in reserved for p in span)
 te.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 catpath=(root.parent if tag=='game'else root)/'catalog.bin';hashpath=catpath.with_name('catalog.hash');cb=catpath.read_bytes();hb=hashpath.read_bytes();cat=cm.Catalog(cb)
 tl=next(i for i in cat.locations(target_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'));dl=next(i for i in cat.locations(donor_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 deps=list(dict.fromkeys(cat.location(tl)['dependencies']+cat.location(dl)['dependencies']));assert cat.location(deps[0])['internal'].endswith(W)
 if deps!=cat.location(tl)['dependencies']:
  raw=b''.join(struct.pack('<I',i)for i in deps);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,tl+12,offset,zlib.crc32(raw));cat=cm.Catalog(bytes(cat.data))
 assert cat.location(tl)['dependencies']==deps and tl in cat.locations('GameWorldVisualTreeAssetPreload')
 # Every newly referenced template must already have a VTA directory registration.
 oldaliases={u['alias']for u in old['m_Usings']}
 for u in doc['m_Usings']:
  if u['alias']not in oldaliases:assert any(cat.location(i)['type'][1].endswith('VisualTreeAsset')for i in cat.locations(u['path'])),u
 changes={PAGE:doc,doc['inlineSheet']['m_PathID']:sheet,ab.path_id:meta}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in baseline.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',tag,i)
 for i,d in changes.items():assert check[i].read_typetree()==d
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 if bytes(cat.data)!=cb:
  for target,bef,aft in [(catpath,cb,bytes(cat.data)),(hashpath,hb,hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii'))]:
   protected.pop(str(target));src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name;src.write_bytes(aft);backup.write_bytes(bef);tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(bef),after=sha(aft)))
 checks.append(dict(target=tag,page=PAGE,hidden_attributes_and_pros_cons_imported=True,career_statistics_context_preserved=True,horizontal_separator=6334,vertical_separator=sep,id_above_name=True,id_preference_unchanged=True,fc_card_byte_identical=True,unrelated_objects_byte_identical=True));print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,change='Old left FC hidden: two-column hidden/pros-cons, native career statistics, identity divider and preference-controlled ID above name',protected_sha256=protected,checks=checks)
for name,value in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'old-left-fc-hidden-career-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)


