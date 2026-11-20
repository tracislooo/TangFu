exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
for pid in [-930000000001001,-941100000001010]:
 d=o[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree()
 for rid in ([6228,1035] if pid==-930000000001001 else [1067,6278,1295]):
  a=rr[rid]['data'];ix=a.get('m_RuleIndex',-1);print(pid,rid,[(pr['m_Id'],[(v['m_ValueType'],s.get({2:'floats',3:'dimensions',4:'colors',7:'strings'}.get(v['m_ValueType'],''),[])[v['valueIndex']] if v['m_ValueType'] in [2,3,4,7] else v) for v in pr['m_Values']]) for pr in s['m_Rules'][ix]['m_Properties']] if ix>=0 else [])
import importlib.util
sp=importlib.util.spec_from_file_location('cat','catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm);c=cm.Catalog((p.parent.parent/'catalog.bin').read_bytes())
for x in c.locations('a3fc5b9c1c155a2cb6fa40c244b1f25d'):print('CAT',c.location(x))
print('BUNDLE',c.location(375106))
