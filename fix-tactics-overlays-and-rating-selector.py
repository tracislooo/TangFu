"""Raise the card art and live controls inside the existing tactics frame."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-overlays-down-rating-switch-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

parsed = ast.parse(base)
definitions = [node for node in parsed.body if getattr(node, 'name', '') in {'style_value', 'preserve_original_bindings'}]
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'tactics-card-geometry', 'exec'))

for filename, names in [('combine-tactics-condition-sharpness.py', {'decode','encode'}), ('apply-tactics-green-pitch-player-card.py', {'absolute_box'})]:
    parsed=ast.parse((R/filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in parsed.body if getattr(n,'name','') in names],type_ignores=[]),filename,'exec'))
index_path=R/'current-tactics-card-layout.json'
index=json.loads(index_path.read_text('utf8'))
TOP=131104
LEFT=131089
outputs={}
checks=[]
def shift(doc,node):
    value=style_value(doc,node,TOP)
    assert value['unit']==1
    doc.st(node,[(TOP,doc.px(value['value']+10))])
def add(doc,donor,node,parent,name):
    result=doc.add(donor,node,parent,name)
    if 'm_ParentId' in doc.a(result):doc.a(result)['m_ParentId']=doc.a(parent)['m_Id']
    return result
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
    env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={}
    original_hashes={pid:sha(o.get_raw_data()) for pid,o in objs[W].items()}
    donor=Doc(W,name='TacticsPositionCombined')
    switch=donor.named('PitchFitnessAbove7')
    for template in ['TacticsPositionCombined','TacticsPositionDetailed','TacticsDetailedCardDetailsDesktop','TacticsDetailedCardDetailsTouch']:
        doc=Doc(W,name=template);original=copy.deepcopy(doc.d)
        body=template in ('TacticsPositionCombined','TacticsPositionDetailed')
        combined=template=='TacticsPositionCombined'
        if body:
            for node in ((1029,1033,1032,1031) if combined else (1024,1028,1027,1026,1017)):shift(doc,node)
            for node,record in list(doc.r.items()):
                if 'm_Parent' in record.get('data',{}) and doc.data(node).get('name','').startswith('PitchFitnessPercent'):shift(doc,node)
        if template!='TacticsPositionDetailed':
            prefix='Combined' if combined else 'Detailed'
            for side in ['Left','Right']:shift(doc,doc.named(prefix+side+'FootednessPlayerVisible'))
            # Keep the badge two pixels beneath the newly lowered feet.
            shift(doc,1036 if combined else (1027 if template.endswith('Touch') else 1022))
            host=doc.named('DirectTacticsRatingBadges')
            for rating,ch in enumerate(list(doc.a(host)['m_Children'])):
                gate=ch['rid'];assert doc.data(gate)['name']==f'DirectTacticsRatingEquals{rating}'
                # Reuse the live percentage selector rather than a separately wired SIVisible function.
                selector=add(doc,donor,switch,host,f'TacticsRatingSelector{rating}')
                absolute_box(doc,selector,0,0,24,12)
                fn=doc.data(selector)['Binding']['m_visualFunction'];args=decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
                struct.pack_into('<i',args[0],len(args[0])-4,2)
                struct.pack_into('<i',args[1],len(args[1])-4,rating)
                old=b'position.Player.Condition';path=b'starrating.minvalue'
                assert args[2].endswith(bytes([len(old)])+old)
                args[2][-len(old)-1:]=bytes([len(path)])+path
                fn['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
                blank=add(doc,donor,1036,selector,'RatingNotMatched');absolute_box(doc,blank,0,0,24,12)
                # Replace the old visible control with a plain visual leaf, retaining its two children.
                leaf=add(doc,donor,1036,selector,f'TacticsRatingValue{rating}');absolute_box(doc,leaf,0,0,24,12)
                doc.st(leaf,[(458752,doc.val(4,style_value(doc,gate,458752)))])
                for child in list(doc.a(gate)['m_Children']):
                    node=child['rid'];doc.move(node,leaf)
                    if 'm_ParentId' in doc.a(node):doc.a(node)['m_ParentId']=doc.a(leaf)['m_Id']
                    if doc.data(node).get('name')=='DirectTacticsRatingNumber':
                        z=doc.data(node)
                        z['TextBinding']['m_direct']['Path']['m_path']=''
                        z['DebugDisplay']='';z['DebugDisplay_UxmlAttributeFlags']=0
                dead={gate,doc.a(gate)['m_SerializedData']['rid']}
                doc.a(host)['m_Children'].remove({'rid':gate})
                doc.d['references']['RefIds']=[x for x in doc.d['references']['RefIds'] if x['rid'] not in dead]
                for node in dead:del doc.r[node]
                assert doc.a(selector)['m_Children']==[{'rid':blank},{'rid':leaf}]
                assert doc.data(doc.a(leaf)['m_Children'][0]['rid'])['text']==f'{rating/2:g}'
            assert len(doc.a(host)['m_Children'])==11
        # Existing native events/bindings remain unchanged; only the custom badge is rebuilt.
        for node,record in refs(original).items():
            if node not in doc.r:continue
            old=record.get('data',{});actual=doc.r[node].get('data',{})
            for key,value in old.items():
                if key.endswith('Event') or key in ('Mappings','Parameters','ShortcutEvent'):
                    assert actual[key]==value,(template,node,key)
        doc.save();checks.append({'target':tag,'template':template,'overlays_down_px':10,'native_events_preserved':True})
    data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
    assert saved.keys()==original_hashes.keys()
    for pid,obj in saved.items():
        if pid in changes[W]:assert obj.read_typetree()==changes[W][pid]
        else:assert sha(obj.get_raw_data())==original_hashes[pid]
    outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
description='左右百分比/脚及右图标下移10px，星级保持在脚下。数字星级改用已显示体能的原生分支控件及原生小写评分路径，清除数字标签残留绑定。保留原缺失规则、框和整卡位置；运行效果待确认。'
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index.update({'patch':str(OUT),'installed':manifest['installed'],'runtime_verified':False,'side_overlay_offset_y':10,'rating_badge':[3,49,24,12],'rating_source':'starrating.minvalue','rating_visibility':'native percentage selector with exact equality','manifest':str(OUT/'manifest.json')})
index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf8')
