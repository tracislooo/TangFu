"""Rebuild from the exact pre-avatar backup; retain only shape edits on existing portraits."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
BASE=R/'outside-match-square-portraits-20261029-110433'
NEWS=R/'news-inbox-original-portraits-20261029-111117'
sha0=lambda b:hashlib.sha256(b).hexdigest()
old=json.loads((BASE/'manifest.json').read_text('utf8'));news=json.loads((NEWS/'manifest.json').read_text('utf8'))
expected=dict(old['after_sha256']);expected.update(news['after_sha256'])
for p,h in expected.items():assert sha0(Path(p).read_bytes())==h,('Resource changed after avatar edits; refuse broad rollback',p)
src=(R/'build-outside-match-square-portraits.py').read_text('utf8')
src=src.replace("'outside-match-square-portraits-'","'existing-portraits-only-'")
marker="exec(compile(boot,'bundle-codecs','exec'))"
rebase='''
# Backups and transaction preconditions describe the currently installed state.
# The editing base is the checked snapshot immediately before adding list avatars.
baseline={n:(BASE/'backup-game'/n).read_bytes() for n in NAMES}
for n,b in baseline.items():
 assert sha(b)==old['before_sha256'][str(GAME/n)]
 env[n]=UnityPy.load(b);objs[n]={o.path_id:o for o in env[n].objects}
 hashes[n]={i:sha(o.get_raw_data()) for i,o in objs[n].items()}
'''
src=src.replace(marker,marker+rebase)
src=src.replace("exec(compile(plan,'match-dependency-closure','exec'))","plan=plan.replace(\"targets={'PlayerNameCell','PlayerNameCell14px','PlayerNameCell14pxBold','PlayerNameCell16px','PlayerNameCell16pxBold','PlayerCell'}\",\"targets=set()\")\nexec(compile(plan,'match-dependency-closure','exec'))")
src=src.replace("catalog=before[GAME.parent/'catalog.bin'];originalcat=cm.Catalog(catalog)","catalog=(BASE/'backup-game/catalog.bin').read_bytes();originalcat=cm.Catalog(catalog)")
# Four explicit longhand radii override the native 50% circle rules.
src=src.replace("[262144,262145,262146,262147]","[458759,458760,458764,458765]")
# Retain the portrait's native scale and dimensions. This task changes clipping only.
start=src.index('  # Cancel the inherited 75% portrait scale')
end=src.index(' if key in namebases:',start)
src=src[:start]+src[end:]
# Reset circular avatar ancestors such as the inbox sender icon selector.
start=src.index('  if \'Circle\' in original[\'m_Name\']:')
end=src.index(' if key==thumbbase:',start)
src=src[:start]+'''  parent=a['m_Parent']['rid']
  while parent in d.r and parent!=1000:
   pa=d.a(parent);pi=pa.get('m_RuleIndex',-1)
   ps=d.s['m_Rules'][pi]['m_Properties'] if pi>=0 else []
   rounded=any(p['m_Id'] in [458759,458760,458764,458765] and any(v['m_ValueType']==3 and d.s['dimensions'][v['valueIndex']]['value']>0 for v in p['m_Values']) for p in ps)
   if rounded and pa.get('m_Classes') is not None:unround(d,parent);localshape.append(parent)
   parent=pa.get('m_Parent',{}).get('rid')
'''+src[end:]
src=src.replace("def unround(d,i):\n d.st(i,", "def unround(d,i):\n d.a(i)['m_Classes']=[c for c in d.a(i).get('m_Classes',[]) if c!='person-picture-circle-frame']\n d.st(i,")
src=src.replace("'portrait_size':24","'portrait_size':None,'added_list_avatars':False,'rebuilt_from_pre_avatar_backup':True")
src=src.replace("比赛外球员列表姓名前新增24×24头像；图片等比完整显示，保留原图透明轮廓。比赛外头像实例取消圆形裁切。", "撤回为列表新增头像的改动；仅保留原本已有的头像并取消圆形裁切。头像数量、原尺寸和数据绑定沿用新增头像前的版本。")
exec(compile(src,'rebuild-existing-portraits-only','exec'))
assert not nameaudit
# The clone process must not add elements, pictures or data bindings to any source.
for c in cloneaudit:
 if c['kind']!='template':continue
 source=docs[c['bundle'],c['source_pid']];result=changes[c['bundle']][c['pid']]
 sr=refs(source);rr=refs(result);assert set(sr)==set(rr)
 for i,a in sr.items():
  if 'm_Children' in a.get('data',{}):assert a['data']['m_Children']==rr[i]['data']['m_Children']
m=json.loads((OUT/'manifest.json').read_text('utf8'));m['no_new_avatar_elements_verified']=True
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
