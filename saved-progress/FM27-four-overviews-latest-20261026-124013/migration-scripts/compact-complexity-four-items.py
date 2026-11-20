from pathlib import Path
import struct,uuid,importlib.util
source=Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig');exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-','complexity-four-compact-rows-no-scroll-'),'boot','exec'))
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
PID,SID=-970000000007000,-970000000007001;GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/CompactComplexityFactorRow/v1').hex;MODULE=1593217430813700770;TILE=-1280300632260697255
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
 before[p]=p.read_bytes();protected.pop(p,None);(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name).write_bytes(before[p])
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def named(r,n):return next(i for i,a in r.items() if a.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(r,i)['data'].get('name')==n)
doc=objs[TILE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);old_sid=doc['inlineSheet']['m_PathID'];sheet=objs[old_sid].read_typetree();doc['m_Name']='CompactComplexityFactorRow';doc['inlineSheet']['m_PathID']=SID;sheet['m_Name']='CompactComplexityFactorRow_Style';st=Styles(sheet);P=st.p
for i in [1001]:st.edit(rr[i],[P(131087,st.px(32)),P(131096,st.px(32)),P(131094,st.px(32)),P(131084,st.num(0)),P(131085,st.num(0)),P(262150,st.px(0)),P(262151,st.px(2))])
st.edit(rr[1003],[P(131098,st.px(0)),P(131090,st.px(0))])
st.edit(rr[1005],[P(131087,st.px(18)),P(131096,st.px(18)),P(131094,st.px(18)),P(131097,st.px(0))])
st.edit(rr[1010],[P(65537,st.px(11)),P(65552,st.en('nowrap')),P(131097,st.px(0)),P(131085,st.num(1))])
st.edit(rr[1022],[P(65537,st.px(9)),P(65552,st.en('nowrap')),P(196609,st.en('ellipsis')),P(131087,st.px(14)),P(131096,st.px(14)),P(131094,st.px(14)),P(131097,st.px(0))])
for i in [1009,1019]:st.edit(rr[i],[P(131105,st.px(16)),P(131087,st.px(16)),P(131096,st.px(16)),P(131085,st.num(0))])
for i,a in old.items():
 if 'UxmlSerializedData' in a.get('type',{}).get('class',''):assert rr[i]==a
validate_ui(doc,sheet)
def clone(source,pid,data):
 assert pid not in objs;o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;objs[pid]=o;o.save_typetree(data)
clone(objs[TILE],PID,doc);clone(objs[old_sid],SID,sheet)
module=objs[MODULE].read_typetree();mr=refs(module);msid=module['inlineSheet']['m_PathID'];msh=objs[msid].read_typetree();mst=Styles(msh);P=mst.p
right=named(mr,'ComplexityFactorsScroll');sdid=mr[right]['data']['m_SerializedData']['rid'];proto=copy.deepcopy(serial(mr,named(mr,'EffectivenessAndComplexityRow')));proto['rid']=sdid;proto['data'].update(uxmlAssetId=mr[right]['data']['m_Id'],name='ComplexityFactorsNoScroll',name_UxmlAttributeFlags=1);mr[sdid].clear();mr[sdid].update(proto);mr[right]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement';mst.edit(mr[right],[P(131087,mst.px(152)),P(131096,mst.px(152)),P(131094,mst.px(152)),P(131085,mst.num(0))])
for i,a in mr.items():
 v=a.get('data',{});s=mr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if s.get('name')=='EmbeddedComplexityHeading':mst.edit(a,[P(131087,mst.px(20)),P(131096,mst.px(20)),P(131094,mst.px(20)),P(131090,mst.px(4)),P(131093,mst.px(0)),P(131084,mst.num(0)),P(131085,mst.num(0))])
 if v.get('m_FullTypeName')=='SI.Bindable.StreamedObjectList':
  assert s['Binding']['m_direct']['Path']['m_path']=='keyfactor.KeyFactors';s['RowTemplate']['m_AssetGUID']=GUID
  for k,val in {'FixedElementSize':32.0,'DynamicElements':0,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':2}.items():s[k]=val;s[k+'_UxmlAttributeFlags']=1
  mst.edit(a,[P(131087,mst.px(128)),P(131096,mst.px(128)),P(131094,mst.px(128)),P(131084,mst.num(0)),P(131085,mst.num(0))])
validate_ui(module,msh);objs[MODULE].save_typetree(module);objs[msid].save_typetree(msh)
metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();native=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==TILE);span=copy.deepcopy(meta['m_PreloadTable'][native['preloadIndex']:native['preloadIndex']+native['preloadSize']]);span=[p for p in span if not(p['m_FileID']==0 and p['m_PathID'] in [TILE,old_sid])];span += [{'m_FileID':0,'m_PathID':PID},{'m_FileID':0,'m_PathID':SID}];meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));meta['m_PreloadTable'].extend(span);entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==MODULE);sp=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);sp.extend(p for p in span if p not in sp);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(sp));meta['m_PreloadTable'].extend(sp);meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta)
# Reuse the established catalog/roundtrip/backup installer, adding the changed module stylesheet.
tail=(R/'remove-embedded-tactical-tile-background-title.py').read_text('utf8').split('spec=importlib.util.spec_from_file_location')[1]
tail='spec=importlib.util.spec_from_file_location'+tail
tail=tail.replace("oldcat.locations('414d4dc7ae21fca47a2684eb783dd244')","oldcat.locations('ead96a6509d51424a84c778512854495')")
tail=tail.replace('changed={PID:doc,SID:sheet,MODULE:module,metaobj.path_id:meta}','changed={PID:doc,SID:sheet,MODULE:module,msid:msh,metaobj.path_id:meta}')
tail=tail.replace("'card_shell_background_removed':True,'title_and_header_space_removed':True", "'right_scroll_container_removed':True,'factor_row_height':32,'four_rows_height':128,'heading_height_with_gap':24,'total_height':152")
tail=tail.replace("'background_removed':True,'title_removed':True", "'four_rows_fit':True,'right_scroll_removed':True")
exec(compile(tail,'catalog-and-install','exec'))
