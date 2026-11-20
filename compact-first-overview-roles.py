exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','first-overview-compact-roles-'))
outputs={}
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};pid=-940000000005000
 doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 table=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedTable' and rr[r['data']['m_SerializedData']['rid']]['data'].get('SelectedItemsBinding',{}).get('m_path')=='rolemask')
 s=rr[rr[table]['data']['m_SerializedData']['rid']]['data'];b=bytes(s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert b.count(b'cc14c4f1722a75c4c9267bf074000f3f')==1
 s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(b.replace(b'cc14c4f1722a75c4c9267bf074000f3f',b'd1c0acd9f2ee5add8b898cdee2d64a96'));s['FactoryAsset']['m_AssetGUID']='d59f71d13eb15573b949818cf0c7113b'
 rr[table]['data']['m_Classes'].append('fm27-compact-role-table234');ptr={'m_FileID':0,'m_PathID':sid}
 if ptr not in rr[table]['data']['m_Stylesheets']:rr[table]['data']['m_Stylesheets'].append(ptr)
 idx=rule([prop(65537,px(10))]);sheet['m_Rules'][idx]['m_ComplexSelectors']=[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':'fm27-compact-role-table234','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'SIText','m_Type':1}],'m_PreviousRelationship':2}],'ruleIndex':idx}]
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 assert check[pid].read_typetree()==doc and check[sid].read_typetree()==sheet
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 outputs[folder/G]=out;(OUT/('game.bundle' if folder==GAME else 'skin.bundle')).write_bytes(out)
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Game is running; prepared only'
for path,b in outputs.items():path.write_bytes(b);assert path.read_bytes()==b
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'runtime_verified':False,'version':1,'role_font_px':10,'reuse_compact_view':'d1c0acd9f2ee5add8b898cdee2d64a96','star_column_min_px':75,'only_changed_path_ids':[str(pid),str(sid)]},indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for path in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if path.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(path)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
print(json.dumps({'installed':True,'output':str(OUT)}))
