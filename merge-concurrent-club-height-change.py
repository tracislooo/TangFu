from pathlib import Path
import sys,json,hashlib,copy,ast,struct
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'))
TypeTreeHelper.write_value=write
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
club=max(R.glob('club-overview-original-heights-*/transaction.json'),key=lambda p:p.stat().st_mtime)
ctx=json.loads(club.read_text('utf8'));allowed={x['target']:x['after'] for x in ctx}
texture_update=R/'TFWX图片更新-V73-20261029'
texture_record=json.loads((texture_update/'图片及引用校验记录.json').read_text('utf8'))
assert texture_record['installed']
for x in texture_record['install_files']:allowed[x['target']]=x['after_sha256']
allowed[str(R/'current-custom-textures.json')]=sha((texture_update/'更新后的有效图片恢复来源.json').read_bytes())
preserved=[]
for target,source in tx['sources'].items():
 p=Path(target);live=p.read_bytes()
 if sha(live)==m['before_sha256'][target]:continue
 assert sha(live)==allowed.get(target),('Unrecognized concurrent change',target)
 old=Path(tx['before'][target]).read_bytes();dst=Path(source)
 oe=UnityPy.load(old);ce=UnityPy.load(live);de=UnityPy.load(dst.read_bytes())
 oo={o.path_id:o for o in oe.objects};co={o.path_id:o for o in ce.objects};do={o.path_id:o for o in de.objects}
 assert set(co)==set(oo)
 handled=set();expected_trees={}
 for i,c in co.items():
  if c.type.name!='MonoBehaviour' or c.get_raw_data()==oo[i].get_raw_data():continue
  cd=c.read_typetree()
  if 'inlineSheet' not in cd:continue
  od=oo[i].read_typetree();dd=do[i].read_typetree();sid=cd['inlineSheet']['m_PathID']
  cs=co[sid].read_typetree();ds=do[sid].read_typetree()
  rr=lambda t:{r['rid']:r for r in t['references']['RefIds']}
  cr,orr,dr=rr(cd),rr(od),rr(dd)
  offsets={key:len(ds[key]) for key in ['floats','dimensions','colors','strings','assets']}
  for key,offset in offsets.items():ds[key].extend(copy.deepcopy(cs[key]))
  ri=len(ds['m_Rules']);rules=copy.deepcopy(cs['m_Rules']);pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
  for rule in rules:
   for prop in rule['m_Properties']:
    for v in prop['m_Values']:
     if v['m_ValueType'] in pool:v['valueIndex']+=offsets[pool[v['m_ValueType']]]
  ds['m_Rules'].extend(rules)
  for rid,r in cr.items():
   before=orr[rid];normalized=copy.deepcopy(r)
   if 'm_RuleIndex' in r.get('data',{}):
    normalized['data']['m_RuleIndex']=before['data']['m_RuleIndex']
    if r['data']['m_RuleIndex']!=before['data']['m_RuleIndex']:dr[rid]['data']['m_RuleIndex']=ri+r['data']['m_RuleIndex']
   assert normalized==before,('External edit exceeded style scope',rid)
  do[i].save_typetree(dd);do[sid].save_typetree(ds);handled.update([i,sid])
  expected_trees[i]=copy.deepcopy(dd);expected_trees[sid]=copy.deepcopy(ds)
  preserved.extend([{'target':target,'pid':i,'name':cd['m_Name'],'semantic_style_merge':True},{'target':target,'pid':sid,'name':cs['m_Name'],'semantic_style_merge':True}])
 for i,c in co.items():
  oldraw=oo[i].get_raw_data();current=c.get_raw_data()
  if sha(current)==sha(oldraw) or i in handled:continue
  assert i in do and (sha(do[i].get_raw_data())==sha(oldraw) or do[i].read_typetree()==oo[i].read_typetree()),('Concurrent object conflict',c.peek_name(),i)
  do[i].set_raw_data(current);preserved.append({'target':target,'pid':i,'name':c.peek_name()})
 result=de.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(result).objects}
 for row in preserved:
  if row['target']==target:
   if row.get('semantic_style_merge'):
    a,b=check[row['pid']].read_typetree(),expected_trees[row['pid']]
    assert a==b,('Readback differs',row['name'],[(rid,rr(a).get(rid),rr(b).get(rid)) for rid in rr(a) if rr(a).get(rid)!=rr(b).get(rid)] if 'references' in a else [(k,a.get(k),b.get(k)) for k in a if a.get(k)!=b.get(k)])
   else:assert check[row['pid']].get_raw_data()==co[row['pid']].get_raw_data()
 dst.write_bytes(result)
 # Both game and skin share a payload, but each has its own checked installation backup.
 folder=out/('backup-install-skin' if p.parent==Path(tx['skin']) else 'backup-install-game');folder.mkdir(exist_ok=True)
 bp=folder/p.name;bp.write_bytes(live);tx['before'][target]=str(bp);m['before_sha256'][target]=sha(live)
for p,h in list(m['protected_sha256'].items()):
 current=sha(Path(p).read_bytes())
 if current!=h:
  assert allowed.get(p)==current,('Unrecognized protected change',p)
  m['protected_sha256'][p]=current
for p,source in tx['sources'].items():m['after_sha256'][p]=sha(Path(source).read_bytes())
m['concurrent_club_height_changes_preserved']=preserved
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'merged_objects':preserved},ensure_ascii=False))
