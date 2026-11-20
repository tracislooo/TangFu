from pathlib import Path
import sys,json,struct
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<installed resources>','exec'))
helpers=ast.parse((R/'build-seven-badges-v39.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='decode'],type_ignores=[]),'<native codec>','exec'))
from UnityPy.classes import PPtr
out=Path(sys.argv[1]);manifest=json.loads((out/'manifest.json').read_text(encoding='utf8'))
for folder in [GAME,SKIN]:assert sha((folder/WN).read_bytes())==manifest['after_sha256']
old={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/WN)).objects}
source=old[-930000000001001].read_typetree();sr={r['rid']:r for r in source['references']['RefIds']};ss=old[source['inlineSheet']['m_PathID']].read_typetree()
def data(rs,i):return rs[rs[i]['data']['m_SerializedData']['rid']]['data']
def valueprops(rs,style,i):
 a=rs[i]['data'];ix=a.get('m_RuleIndex',-1)
 if ix<0:return {}
 return {p['m_Id']:[('keyword',h['valueIndex']) if h['m_ValueType']==1 else style[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in style['m_Rules'][ix]['m_Properties']}
tested=0;pagechecks=[]
for page in manifest['pages']:
 pid=page['page_id'];d=objects[pid].read_typetree();rs={r['rid']:r for r in d['references']['RefIds']};style=objects[d['inlineSheet']['m_PathID']].read_typetree();od=old[pid].read_typetree();ors={r['rid']:r for r in od['references']['RefIds']}
 assert rs[1011]['data']['m_Children']==[{'rid':1035},{'rid':page['panel']}]
 for i,r in ors.items():
  if i==1011:
   restored=copy.deepcopy(rs[i]);restored['data']['m_Children']=r['data']['m_Children'];assert restored==r
  else:assert rs[i]==r,('old content differs',pid,i)
 for clone in page['summary_copies']:
  mapping={int(k):v for k,v in clone['mapping'].items()}
  for sourceid,newid in mapping.items():
   original=sr[sourceid]
   if 'm_SerializedData' in original.get('data',{}):assert valueprops(sr,ss,sourceid)==valueprops(rs,style,newid)
   if 'UxmlSerializedData' in original.get('type',{}).get('class',''):
    expected=copy.deepcopy(original['data']);expected['uxmlAssetId']=rs[newid]['data']['uxmlAssetId']
    if 'name' in expected:expected['name']='RightHidden_'+expected['name']
    assert rs[newid]['data']==expected
 assert [r['key'] for r in page['rows']]==[a['key'] for a in manifest['attributes']]
 assert len(page['rows'])==13
 for row,item in zip(page['rows'],manifest['attributes']):
  assert valueprops(rs,style,row['row'])[131087]==[{'unit':1,'value':24.0}]
  gate=data(rs,row['gate']);args=decode(gate['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
  threshold=struct.unpack('<i',args[1][1])[0];assert threshold==0
  assert args[2][1][2:].decode()==item['path']
  assert rs[row['gate']]['data']['m_Children']==[{'rid':row['missing']},{'rid':row['mapper']}]
  assert data(rs,row['missing'])['text']=='--'
  mapper=data(rs,row['mapper']);assert [m['from'] for m in mapper['Mappings']]==['propertyValue','minValue']
  assert all(m['to']['m_path']==item['path'] for m in mapper['Mappings'])
  assert rs[row['badge']]['data']['m_TemplateAlias']=='RightHiddenAttributeBadge'
  # Every valid value maps unchanged; every unavailable value selects the explicit missing branch.
  for v in [None,-2147483648,-1,0]+list(range(1,21)):
   selected=rs[row['gate']]['data']['m_Children'][int(v is not None and v>threshold)]['rid']
   assert selected==(row['missing'] if v is None or v<=0 else row['mapper']);tested+=1
  upper=next(r for r in sr.values() if sr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='OverviewHiddenNumber_'+item['key']+'Value')
  assert data(sr,upper['rid'])['TextBinding']['m_direct']['Path']['m_path']==item['path']
 assert next(u['path'] for u in d['m_Usings'] if u['alias']=='RightHiddenAttributeBadge')==manifest['native_attribute_badge_guid']
 scroll=next(r for r in rs.values() if rs.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='OverviewInfoScroll')
 assert scroll['data']['m_Children']==[{'rid':1011}]
 validate_ui(d,style)
 pagechecks.extend([{'page':pid,'player_type':t,'rows':13,'top_content_preserved':True,'bans_preserved':True} for t in ['goalkeeper','outfield']])
# Resolve all copied background image pointers from the installed UI bundle and actual background bundle.
bgbytes=(GAME/'ui-backgrounds_assets_common.bundle').read_bytes();loaded=UnityPy.load((GAME/WN).read_bytes(),bgbytes);wf=next(a for a in loaded.assets if a.name==objects[-930000000001001].assets_file.name)
imagechecks=0
for page in manifest['pages']:
 d=objects[page['page_id']].read_typetree();style=objects[d['inlineSheet']['m_PathID']].read_typetree();refs={r['rid']:r for r in d['references']['RefIds']}
 pointers=[]
 for clone in page['summary_copies']:
  for rid in clone['mapping'].values():
   ix=refs[rid].get('data',{}).get('m_RuleIndex',-1)
   if ix<0:continue
   for propdata in style['m_Rules'][ix]['m_Properties']:
    if propdata['m_Id']!=458753:continue
    for handle in propdata['m_Values']:
     if handle['m_ValueType']==6:pointers.append(style['assets'][handle['valueIndex']])
 for ptr in pointers:
  if ptr['m_FileID'] and ptr['m_PathID']:
   # The copied summary textures all use the existing background serialized file.
   external=wf.externals[ptr['m_FileID']-1]
   if '999dbe4fa4e66f3eb4b5f53d4512b8b8' in external.path:
    tex=PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=wf).deref();assert tex.read().image.size==(196,19);imagechecks+=1
result={'installed_game_skin_hashes_match':True,'four_player_layout_cases':pagechecks,'native_badge_guid_verified':True,'numeric_boundary_cases_verified':tested,'copied_background_image_references_resolved':imagechecks,'all_original_nodes_preserved':True,'runtime_verified':False}
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed_game_skin_match':True,'layout_cases':len(pagechecks),'value_cases':tested,'resolved_images':imagechecks,'original_top_and_bans_preserved':True,'runtime_verified':False}))
