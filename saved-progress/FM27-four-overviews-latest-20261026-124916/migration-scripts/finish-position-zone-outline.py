from pathlib import Path
import sys,json,hashlib,subprocess
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=R/'overview-position-rectangle-zones-20261026-123653';m=json.loads((O/'manifest.json').read_text('utf8'))
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');skin=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');sha=lambda b:hashlib.sha256(b).hexdigest()
b=(game/G).read_bytes();assert sha(b)==m['after_sha256'] and (skin/G).read_bytes()==b
e=UnityPy.load(b);obs={o.path_id:o for o in e.objects};o=obs[-940000000018001];d=o.read_typetree();selector=d['m_Rules'][-1]['m_ComplexSelectors'][0]['m_Selectors'];assert selector[1]['m_PreviousRelationship'] in [1,2];selector[1]['m_PreviousRelationship']=2
row=obs[-940000000018000].read_typetree();rr={r['rid']:r for r in row['references']['RefIds']};base=None;borderkeys={131076,131077,131078,131079,458758,458761,458762,458763}
for r in rr.values():
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if a.get('m_FullTypeName')=='SI.Bindable.SIButton' and sd.get('name','').startswith('PositionZone_'):
  rule=d['m_Rules'][a['m_RuleIndex']];base=base or [p for p in rule['m_Properties'] if p['m_Id'] in borderkeys];rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id'] not in borderkeys]
assert base and len(base)==8
idx=len(d['m_Rules']);d['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':10,'m_Selectors':[{'m_Parts':[{'m_Value':'fm27-position-block','m_Type':3}],'m_PreviousRelationship':0}],'ruleIndex':idx}],'m_Properties':base,'line':-1});o.save_typetree(d)
out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert check[-940000000018001].read_typetree()==d
for pid,o in obs.items():
 if pid!=-940000000018001:assert o.get_raw_data()==check[pid].get_raw_data()
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Exit game before installing'
for p in [O/G,game/G,skin/G]:p.write_bytes(out);assert p.read_bytes()==out
m['after_sha256']=sha(out);m['selected_border_css_relationship']='descendant';(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print('Selected border validated; global bundle synchronized.')
