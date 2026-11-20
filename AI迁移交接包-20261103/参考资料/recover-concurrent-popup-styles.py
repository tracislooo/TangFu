import sys,json,ast,hashlib
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
rec=R/'popup-season-stats-larger-20261102-222149';snap=json.loads((rec/'球员弹窗最终版本资源快照.json').read_text('utf8'));loc=json.loads((R/'current-game-location.json').read_text('utf8'));bn='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';ids=[-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]
refs=lambda d:{r["rid"]:r for r in d["references"]["RefIds"]}
for tag,folder in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 p=folder/bn;raw=p.read_bytes();e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};old={o.path_id:o for o in UnityPy.load(str(rec/('backup-'+tag+'.bundle'))).objects};changes=[]
 for pid in ids:
  d=oo[pid].read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();root=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='PopupFourRowsSeasonStats');todo=[root['rid']];count=0
  while todo:
   r=rr[todo.pop()];a=r['data'];todo.extend(c['rid'] for c in a.get('m_Children',[]));ix=a.get('m_RuleIndex',-1)
   if a.get('m_FullTypeName')!='SI.Bindable.SIText' or ix<0:continue
   rule=s['m_Rules'][ix];font=next((p for p in rule['m_Properties'] if p['m_Id']==65537),None)
   if not font:continue
   h=font['m_Values'][0];assert h['m_ValueType']==3;old=s['dimensions'][h['valueIndex']]['value'];assert old in [9,12],old
   new=12 if old==9 else 18
   s['dimensions'].append({'unit':1,'value':float(new)});font['m_Values']=[{'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}]
   # Keep the larger title and value inside each 50px row.
   for key,value in [(131087,20 if old==9 else 26),(131096,20 if old==9 else 26)]:
    prop=next((p for p in rule['m_Properties'] if p['m_Id']==key),None)
    if prop is not None:
     s['dimensions'].append({'unit':1,'value':float(value)});prop['m_Values']=[{'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}]
   count+=1
  assert count>=24,count;so.save_typetree(s);changes.append(so.path_id)
 if changes:
  b=e.file.save(packer='lz4');assert p.read_bytes()==raw
  (rec/('recovery-before-'+tag+'.bundle')).write_bytes(raw);p.write_bytes(b)
 print(tag,'recovered styles',changes)
