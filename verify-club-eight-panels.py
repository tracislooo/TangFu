from pathlib import Path
import sys,json,importlib.util,struct
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'));cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
audits=[]
for target in m['audits']:
 tag=target['target'];folder=Path(cfg['bundle_root'] if tag=='game' else cfg['skin_packages']);cat=cm.Catalog((out/tag/'catalog.bin').read_bytes());loaded={};index={};overrides=0;functions=set()
 def loadbundle(name):
  if name in loaded:return
  p=out/tag/name
  if not p.exists():p=folder/name
  if not p.exists():p=Path(cfg['bundle_root'])/name
  af=UnityPy.load(p.read_bytes()).assets[0];loaded[name]=af
  meta=next(o.read_typetree() for o in af.objects.values() if o.type.name=='AssetBundle')
  for key,e in meta['m_Container']:
   o=af.objects.get(e['asset']['m_PathID']) if e['asset']['m_FileID']==0 else None
   if o and o.type.name=='MonoBehaviour':
    d=o.read_typetree()
    if 'inlineSheet' in d:index[key]=d
 def get(guid):
  if guid not in index:
   loc=next(cat.location(l) for l in cat.locations(guid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
   n=cat.location(loc['dependencies'][0])['internal'].replace('\\','/').split('/')[-1];loadbundle(n)
  assert guid in index,guid
  return index[guid]
 def resolve(d,path):
  if not path:return False
  elements={r['data']['m_Id']:r['data'] for r in d['references']['RefIds'] if 'm_Id' in r.get('data',{})};node=elements.get(path[0])
  if node is None:return False
  if len(path)==1:return True
  alias=node.get('m_TemplateAlias');u=next((u for u in d['m_Usings'] if u['alias']==alias),None)
  return bool(u and resolve(get(u['path']),path[1:]))
 def inspect(v):
  if isinstance(v,dict):
   if v.get('m_guid'):functions.add(v['m_guid'])
   for x in v.values():inspect(x)
  elif isinstance(v,list):
   for x in v:inspect(x)
 for clone in target['private_templates']:
  d=get(clone['guid']);inspect(d)
  aliases={u['alias']:u['path'] for u in d['m_Usings']}
  for r in d['references']['RefIds']:
   nd=r.get('data',{});alias=nd.get('m_TemplateAlias')
   if not alias:continue
   source=get(aliases[alias])
   for override in nd.get('m_SerializedDataOverride',[]):
    path=override['m_ElementIdsPath'];assert resolve(source,path),(tag,d['m_Name'],alias,path);overrides+=1
 for guid in functions:assert any(cat.location(l)['type'][1]=='SI.VisualScripting.VisualFunction' for l in cat.locations(guid)),guid
 stad=next(get(c['guid']) for c in target['private_templates'] if get(c['guid'])['m_Name']=='ClubOverviewStadiumStack')
 rr={r['rid']:r for r in stad['references']['RefIds']};node=next(r for r in rr.values() if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto');args=bytes(node['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert args[0]==3
 chunks=[];p=1
 for _ in range(args[0]):
  ln=struct.unpack_from('<I',args,p)[0];p+=4;chunks.append(args[p:p+ln]);p+=ln
 assert p==len(args) and chunks[1][-4:]==struct.pack('<i',21) and chunks[2].endswith(b'club.MainTeam.Stadium.UniqueId')
 for chunk in chunks:assert chunk[0]>0 and chunk[1:chunk[0]+1].decode('ascii')
 body=next(get(c['guid']) for c in target['private_templates'] if get(c['guid'])['m_Name']=='ClubOverviewEightPanelBody')
 assert not any(r.get('data',{}).get('name') in ['BottomTiles','BottomBarExpandCollapseSwitch_focusser'] for r in body['references']['RefIds'])
 audits.append({'target':tag,'template_override_paths_resolved':overrides,'visual_functions_registered':len(functions),'stadium_native_binding_arguments_valid':True,'old_bottom_tiles_removed':True})
result={'passed':True,'runtime_verified':False,'audits':audits}
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
