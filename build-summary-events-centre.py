from pathlib import Path
R=Path(__file__).parent
source=(R/'separate-summary-horizontal-formations.py').read_text('utf8')
source=source.replace('summary-horizontal-formations-','summary-events-centre-').replace("REPORT_PREFIXES=('HalfTimeTeamReport','FullTimeTeamReport','PastMatchTeamReport')","REPORT_PREFIXES=('HalfTimeTeamReport','FullTimeTeamReport')")
start=source.index(' for index,side in enumerate(')
end=source.index(' report_assets=[];layouts=[]',start)
body=''' source=Doc(G,name='MatchViewer_12x4')
 name='SummaryMatchEventsCentre';pid=-981111000040000
 d=copy.deepcopy(source.d);s=copy.deepcopy(source.s);d['inlineSheet']={'m_FileID':0,'m_PathID':pid-1}
 ob,d=clone_asset(G,source.obj,pid,name,d)
 _,s=clone_asset(G,objs[G][source.sid],pid-1,name+'_Style',s)
 doc=Doc(G,pid=pid,tree=d,style=s)
 event_source=Doc(G,name='HighlightMatchEvents70Percent')
 eventguid=asset_guid(G,event_source.obj.path_id)
 remapper=next(i for i,r in doc.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
 context=doc.add(doc,remapper,2147,'SummaryMatchEventsContext')
 doc.data(context).update(Mappings=[{'m_serialisedType':0,'from':'fixture','to':{'m_path':'fixturetouse'},'type':{'id':1718188148}},{'m_serialisedType':0,'from':'isonmainscreen','to':{'m_path':'const.False'},'type':{'id':0}}],Mappings_UxmlAttributeFlags=1)
 doc.a(context)['m_RuleIndex']=doc.a(1022)['m_RuleIndex']
 alias='SummaryHighlightMatchEvents';doc.d['m_Usings'].append({'alias':alias,'path':eventguid,'asset':{'m_FileID':0,'m_PathID':0}})
 instance=next(i for i,r in doc.r.items() if r.get('data',{}).get('m_TemplateAlias'))
 event=doc.add(doc,instance,context,'SummaryHighlightMatchEvents')
 doc.a(event)['m_TemplateAlias']=alias;doc.data(event)['templateId']=alias
 for k in ['m_AttributeOverrides','m_SerializedDataOverride','m_SlotUsages']:doc.a(event)[k]=[]
 doc.a(event)['m_Classes']=[]
 doc.fill(event);doc.st(1022,[(131081,doc.enum('none'))]);doc.move(context,2147,1)
 for i,r in refs(source.d).items():
  if 'm_Parent' not in r.get('data',{}):assert doc.r[i]==r
 doc.save()
 guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/summary-events/'+name).hex
 oldguid=asset_guid(G,source.obj.path_id);guidmap[oldguid]=guid
 private.append({'bundle':G,'pid':pid,'style':pid-1,'guid':guid,'source_guid':oldguid,'name':name,'kind':'VisualTreeAsset'})
 desc=objs[T][2268119280419395392];dt=tree(T,desc.path_id)
 descpid=-981111000040020;descname='SummaryMatchEventsCentreDescription'
 for c in dt[CK]:
  c['Description']['m_PathID']=descpid
  if c['AssetRef']['m_AssetGUID']==oldguid:c['AssetRef']['m_AssetGUID']=guid
 _,dt=clone_asset(T,desc,descpid,descname,dt)
 descguid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/summary-events/'+descname).hex
 private.append({'bundle':T,'pid':descpid,'guid':descguid,'source_guid':asset_guid(T,desc.path_id),'name':descname,'kind':'GridElementDescription'})
 pidmap[desc.path_id]=descpid
 panel_audits.append({'centre':'Highlight second-row fourth MatchEvents module','event_template':event_source.d['m_Name'],'event_guid':eventguid,'fixture_binding':'fixturetouse','maps_and_summary_formations_unchanged':True})
'''
source=source[:start]+body+source[end:]
source=source.replace('len(layouts)==6','len(layouts)==4').replace('len(report_assets)==11','len(report_assets)==8')
source=source.replace("summary_layouts_each_variant':6","summary_layouts_each_variant':4")
source=source.replace("current-summary-formations.json","current-summary-events-centre.json").replace("'summary_orientation':1","'centre':'HighlightMatchEvents70Percent'")
source=source.replace("'source_script':str(Path(__file__))","'source_script':str(R/'build-summary-events-centre.py')")
mark=source.index("(OUT/'修改说明.md').write_text(")
end=source.index('\nstate=',mark)
source=source[:mark]+"(OUT/'修改说明.md').write_text('中场和赛后总结中央黑白球场替换为比赛Highlight第二排第四个的赛事模块HighlightMatchEvents70Percent，显示进球助攻等事件。专用中央模板与描述保留MatchViewer逻辑ID和全部原绑定，fixture映射fixturetouse；仅总结四份布局与四份集合替换引用。两侧分析图、统计图和横向阵型保持，赛中Highlight不改。游戏与独立皮肤分别增量生成，备份与restore.ps1带哈希保护。实际游戏显示待确认。','utf8')"+source[end:]
exec(compile(source,str(R/'build-summary-events-centre.py'),'exec'))
