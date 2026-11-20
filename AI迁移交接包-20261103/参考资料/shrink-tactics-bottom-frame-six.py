from pathlib import Path
source=Path('add-tactics-fitness-backdrop-thinner-rim.py').read_text('utf8')
source=source.replace('tactics-fitness-backdrop-thinner-rim-','tactics-bottom-frame-minus6-').replace('hours=-6','hours=-7')
start=source.index("  gate=d.named('PitchFitnessPlayerVisible')")
end=source.index(' data=env[G].file.save',start)
source=source[:start]+'''  border=next(i for i,a in d.r.items() if 'm_Parent' in a.get('data',{}) and d.data(i).get('name','').endswith('CardNativePositionBackground'))
  props=d.s['m_Rules'][d.a(border)['m_RuleIndex']]['m_Properties']
  def dim(k):
   h=next(p for p in props if p['m_Id']==k)['m_Values'][0]
   return d.s['dimensions'][h['valueIndex']]['value']
  x,y,w,h=[dim(k) for k in [131089,131104,131105,131087]]
  assert w>=12 and h>=12
  d.size(border,w-6,h-6)
  d.st(border,[(131089,d.px(x+3)),(131104,d.px(y+3))])
  for i,a in r0.items():
   b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
   if i==border:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   assert a==b,('unrelated node changed',name,i)
  d.save();checks.append({'target':str(folder/G),'template':name,'before':[x,y,w,h],'after':[x+3,y+3,w-6,h-6],'center_preserved':True,'only_bottom_color_frame_changed':True})
'''+source[end:]
# Replace the old descriptive text with this patch's requirements.
start=source.index("tail=tail.replace(")
end=source.index("exec(compile(tail",start)
source=source[:start]+'''a=tail.index("(OUT/'修改说明.md').write_text(");b=tail.index('\\nprint(',a)
tail=tail[:a]+"(OUT/'修改说明.md').write_text('Combined和Detailed最底层位置色框按当前尺寸宽高各减6px，x/y各增加3px保持中心。只改底框样式，头像、姓名、体能底色、进度条、星级及所有绑定和交互不变。游戏/皮肤分别在现有非侧栏资源上迁移；回读和无关对象一致性校验通过，游戏内视觉待确认。','utf8')"+tail[b:]
'''+source[end:]
exec(compile(source,'shrink-existing-frame','exec'))
