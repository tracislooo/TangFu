from pathlib import Path
import ast,copy,json
s=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','first-transfer2x1-favoured-personnel-split-')
exec(compile(s,'backup-and-helpers','exec'))
PAGE,STYLE=-930000000001001,-930000000001000
doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
serial=lambda r,i:r[r[i]['data']['m_SerializedData']['rid']]
row=named('FirstOverviewTransferPlayerMapping');left=named('FirstOverviewNativeTransferStatusFallback');switch=named('FirstOverviewProsConsOrTransferSwitch')
meta=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle')
def key(pid):return next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
transferkey=key(-6532285783748324082);favouredkey=key(-6585881198965646880)
for u in doc['m_Usings']:
 if u['alias']=='FirstOverviewNativeTransferStatus':u.update(path=transferkey,asset={'m_FileID':0,'m_PathID':0})
right=add_pair(old[left],serial(old,left),row,'FirstOverviewFavouredPersonnelFallback')
alias='FirstOverviewNativeFavouredPersonnel';rr[right]['data'].update(m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);sd(right).update(templateId=alias,templateId_UxmlAttributeFlags=1);doc['m_Usings'].append({'alias':alias,'path':favouredkey,'asset':{'m_FileID':0,'m_PathID':0}})
# A one-pixel line and equal four-pixel margins are excluded from both equal halves.
line=add_pair(old[6298],serial(old,6298),row,'FirstOverviewTransferFavouredVerticalDivider')
f=__import__('struct').unpack('<f',__import__('struct').pack('<f',.32))[0]
override(rr[line]['data'],[prop(131105,px(1)),prop(131097,px(1)),prop(131095,px(1)),prop(131082,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131091,px(4)),prop(131092,px(4)),prop(131093,px(0)),prop(131090,px(0)),prop(458752,val(4,{'r':1.0,'g':1.0,'b':1.0,'a':f}))])
rr[row]['data']['m_Children']=[{'rid':left},{'rid':line},{'rid':right}]
override(rr[row]['data'],[prop(131083,en('row')),prop(131073,en('stretch')),prop(131088,en('flex-start'))])
for i in [left,right]:
 override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131091,px(0)),prop(131092,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131073,en('stretch'))])
assert serial(rr,switch)==serial(old,switch),'fallback condition changed'
assert rr[switch]['data']['m_Children']==old[switch]['data']['m_Children']
assert rr[6306]==old[6306] and rr[6308]==old[6308],'pros and cons changed'
validate_ui(doc,sheet);objs[W][PAGE].save_typetree(doc);objs[W][STYLE].save_typetree(sheet)
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in [PAGE,STYLE]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
assert check[PAGE].read_typetree()==doc and check[STYLE].read_typetree()==sheet
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'first_only':True,'fallback_condition_unchanged':True,'fallback_height_preserved':260,'fallback_columns':[50,50],'left_native':'PlayerTransferStatusTile_2x1','left_guid':transferkey,'right_native':'FavouredPersonnelTile_4x2','right_guid':favouredkey,'vertical_divider_px':1,'pros_cons_and_other_versions_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'fallback_condition_unchanged':True,'split':'50/50','left':'Transfer Status 2x1','right':'Favoured Personnel'}))
