from pathlib import Path
p=Path('migrate-last-skin-to-updated-game.py');s=p.read_text('utf8')
s=s.replace("OUT=R/('updated-game-last-skin-migration-'+stamp)","OUT=R/('restore-approved-four-overviews-'+stamp)")
s=s.replace("SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')","SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')\nSNAPSHOT=Path((R/'LATEST-FM27-PROGRESS.txt').read_text('utf8').splitlines()[0]);APPROVED=SNAPSHOT/'skin-tf27-01'/'packages'")
s=s.replace("oldenv={n:UnityPy.load(b) for n,b in skinbefore.items() if n.endswith('.bundle')}","oldenv={n:UnityPy.load(str(APPROVED/n)) for n in NAMES+[B]}")
s=s.replace("oldcat=cm.Catalog(skinbefore['catalog.bin'])","oldcat=cm.Catalog((APPROVED/'catalog.bin').read_bytes())")
s=s.replace("# These layout records control the saved two-version overview and its 8+2 row layout.","# Preserve the four approved variants and bottom layout.")
s=s.replace("if item.get('name')=='person' and not any(v.get('name')=='person' for v in newgrid[k]):newgrid[k].append(copy.deepcopy(item))","if (item.get('name')=='person' or item.get('name','').endswith('VariantTitle')) and not any(v.get('name')==item.get('name') for v in newgrid[k]):newgrid[k].append(copy.deepcopy(item))")
s=s.replace("{'PlayerOverviewFull','PlayerOverviewSimple'}","{'PlayerOverviewFull','PlayerOverviewSimple','PlayerOverviewLeftFC','PlayerOverviewLeftPortrait'}")
needle="assert binding_adds>0\nno[newpage[0]][newpage[1]].save_typetree(np)"
replacement="""assert binding_adds>0
# Restore all four native selector title constants without replacing the updated page.
oldrefs={r['rid']:r for r in op['references']['RefIds']};newrefs={r['rid']:r for r in np['references']['RefIds']}
oldvars=next(r['data'] for r in oldrefs.values() if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
newvars=next(r['data'] for r in newrefs.values() if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
for v in oldvars['ValueVariables']:
 if v['m_name'].endswith('VariantTitle') and not any(x['m_name']==v['m_name'] for x in newvars['ValueVariables']):newvars['ValueVariables'].append(copy.deepcopy(v))
for r in newrefs.values():
 if r.get('data',{}).get('m_Id')==newvars['uxmlAssetId'] and r.get('type',{}).get('class')=='UxmlObjectAsset':
  for p in r['data']['m_Properties']:
   if p['name']=='value-vars':p['value']=','.join('{'+v['m_name']+'}{'+v['m_scopeValue']['m_serializedData']+'}' for v in newvars['ValueVariables'])
no[newpage[0]][newpage[1]].save_typetree(np)"""
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("'installed':False,'runtime_verified':False,","'installed':False,'runtime_verified':False,'approved_snapshot':str(SNAPSHOT),'restored_versions':4,",1)
Path('restore-approved-four-overviews.py').write_text(s,'utf8')
