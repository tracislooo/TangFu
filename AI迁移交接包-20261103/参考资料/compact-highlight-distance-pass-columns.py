from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','compact-highlight-distance-pass-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tableviews_assets_all.bundle\"]')")
exec(compile(prefix,'backup-load','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];V='ui-tableviews_assets_all.bundle'+suffix;main=Doc(G,name='MatchViewer_12x4')
 factory=find(F,'HighlightEightFieldsFactory').read_typetree();guids={}
 for index,ident in enumerate(['run','pass%']):
  guid=next(c for c in factory['m_rowData'] if c['m_id']==ident)['m_uxmlRef']['m_AssetGUID'];hits=[]
  for bn in [W,G]:
   meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
   hits.extend((bn,v['asset']['m_PathID']) for k,v in meta['m_Container'] if k==guid and objs[bn][v['asset']['m_PathID']].type.name=='MonoBehaviour' and 'inlineSheet' in objs[bn][v['asset']['m_PathID']].read_typetree())
  assert len(hits)==1,hits
  bn,pid=hits[0];cell,newguid=clone_doc(Doc(bn,pid=pid),'HighlightCompact'+('Distance' if index==0 else 'PassPercentage')+'Cell',-981030000040000-index*10)
  for i,r in cell.r.items():
   x=r.get('data',{})
   if 'm_Parent' in x and x.get('m_FullTypeName')=='SI.Bindable.SIText':cell.st(i,[(65537,cell.px(9)),(131099,cell.px(1)),(131100,cell.px(1))])
  cell.save();guids[ident]=newguid
 widths={'run':64.,'pass%':64.,'goals':26.,'assists':26.,'keyPasses':26.,'keyTackles':26.}
 for ob in objs[F].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsFactory':continue
  t=ob.read_typetree()
  for c in t['m_rowData']:
   if c['m_id'] in widths:c.update(m_defaultWidth=widths[c['m_id']],m_minimumWidth=widths[c['m_id']],m_allowWidthAutoResizing=0,m_autoSizeCellPadding=0.)
   if c['m_id'] in guids:c['m_uxmlRef']['m_AssetGUID']=guids[c['m_id']]
  ob.save_typetree(t);changes[F][ob.path_id]=t
 for ob in objs[V].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsView':continue
  t=ob.read_typetree()
  for c in t['m_tableView']['m_tableConfig']:
   if c['m_columnID'] in widths:c['m_columnMetadata'].update(m_widthOverride=widths[c['m_columnID']],m_minWidthOverride=widths[c['m_columnID']])
  ob.save_typetree(t);changes[V][ob.path_id]=t
 register=(R/'separate-match-fitness-and-toolbar-colors.py').read_text('utf8').split(' new=[a for a in asset_clones')[1].split(' audits.append')[0]
 exec(__import__('textwrap').dedent(' new=[a for a in asset_clones'+register))
 audits.append({'variant':tag,'metric_font':9,'metric_widths':64,'four_following_widths':26,'cell_side_padding':1})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))

