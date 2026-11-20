"""Refine the current banner without recreating its image or native bindings."""
from pathlib import Path
R=Path(__file__).resolve().parent
base=(R/'start-banner-video520-tfwx120.py').read_text('utf8')
boot=base.split("assert rr[1002]['data']['m_Children']==[{'rid':1004}]")[0]
boot=boot.replace("'video_size':[520,112]","'video_size':[390,112]").replace("'TFWX_slot':[120,112]","'TFWX_slot':[240,112]")
exec(compile(boot,'current-bundles-and-validators','exec'))
parsed=ast.parse(base)
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['val','px','en','num','style','size','styled']],type_ignores=[]),'existing-style-helpers','exec'))
nr=next(rid for rid,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and data(rid).get('name')=='StartScreenTFWX')
assert rr[1002]['data']['m_Children']==[{'rid':1004},{'rid':nr}]
assert all(styled(i,131105)=={'unit':1,'value':520.0} for i in [1004,1006,1007,1009])
assert styled(nr,131105)=={'unit':1,'value':120.0}
assert all(styled(i,131087)=={'unit':1,'value':112.0} for i in [1004,1006,1007,1009,nr])
ptr=styled(nr,458753);assert ptr['m_PathID']==PID and styled(nr,262153)=='scale-to-fit'
for i in [1004,1006,1007,1009,nr]:
 width=240 if i==nr else 390
 style(i,[(131105,px(width)),(131097,px(width)),(131095,px(width))])
for rid,old in old_rr.items():
 actual=copy.deepcopy(rr[rid])
 if 'm_RuleIndex' in old.get('data',{}):actual['data']['m_RuleIndex']=old['data']['m_RuleIndex']
 assert actual==old,('Unexpected node/binding change',rid)
assert s['m_Rules'][:len(old_s['m_Rules'])]==old_s['m_Rules']
assert s['assets']==old_s['assets'] and s['strings']==old_s['strings']
for i in [1004,1006,1007,1009,nr]:
 width=240 if i==nr else 390
 assert all(styled(i,k)=={'unit':1,'value':float(width)} for k in [131105,131097,131095])
 assert styled(i,131087)=={'unit':1,'value':112.0}
 before_rule=old_s['m_Rules'][old_rr[i]['data']['m_RuleIndex']]['m_Properties']
 after_rule=s['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']
 assert [p for p in before_rule if p['m_Id'] not in [131105,131097,131095]]==[p for p in after_rule if p['m_Id'] not in [131105,131097,131095]]
validate_ui(d,s);obj.save_typetree(d);a.objects[sid].save_typetree(s)
outbytes=e.file.save(packer='lz4');sa=UnityPy.load(outbytes).assets[0]
assert set(sa.objects)==set(hashes)
for i,h in hashes.items():
 if i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h,('Unrelated object changed',i)
validate_ui(sa.objects[obj.path_id].read_typetree(),sa.objects[sid].read_typetree());retired_absent(sa)
linked=UnityPy.load(outbytes,bgb);la=next(x for x in linked.assets if x.name==a.name)
resolved=PPtr(m_FileID=ptr['m_FileID'],m_PathID=PID,assetsfile=la).deref()
assert resolved.peek_name()=='TFWX' and sha(resolved.get_raw_data())==tf['texture_sha256']
worlds={name:UnityPy.load(str(GAME/name)).assets[0] for name in [WORLD,GLOBAL]}
auditcode=base[base.index("outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};audits=[]"):base.index("agents_text=before[agents].decode('utf8')")]
exec(compile(auditcode,'current-addressables-audit','exec'))
old_line='原生视频显示宽度由640减至520px，高112px；右侧120×112px区域等比完整显示TFWX'
new_line='原生视频显示宽度由640减至390px，高112px；右侧240×112px区域等比完整显示TFWX'
text=before[agents].decode('utf8');assert old_line in text
outputs[agents]=text.replace(old_line,new_line).encode('utf8')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('start-banner-video390-tfwx240-'+stamp)
addition='''

## 9. 2026-10-29 横幅宽度再调整：视频390px，TFWX区域240px

本节覆盖第8节的最终宽度：视频520→390px（再减少130px），右侧TFWX区域120→240px（增加120px）。高度仍112px，保持原左对齐；两块合计630px，比上版少10px，未添加间距。

TFWX继续scale-to-fit；当前已安装V71新版1200×600横图，实际显示224×112px，240px区域内左右各8px留空。未拉伸或裁剪图片，未改变高度。调整前发现游戏和皮肤均已安装V71成品，但清单仍为V70；核对成品和保护资源后已补齐V71安装记录与恢复清单。

原视频播放、RenderTexture、语言选择、点击事件、分支节点顺序，以及背景和其他页面均保留。只修改横幅模板内5个节点的宽度／最小宽度／最大宽度，保留既有TFWX引用，不创建新元素、纹理或资源ID。
'''
addition+='\n实施脚本：`resize-start-banner-video390-tfwx240.py`；本次记录：`'+out.name+'`。\n'
outputs[note]=(before[note].decode('utf8')+addition).encode('utf8')
out.mkdir();(out/'templates').mkdir()
for name,tree in [('MarketingBannerTile_8x2.json',d),('MarketingBannerTile_8x2-style.json',s)]:
 (out/'templates'/name).write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8')
items=[]
for p,b in outputs.items():
 tag='workspace' if p.parent==R else ('game' if p.parent in [AA,GAME] else 'skin')
 source=Path(tag)/p.name;backup=Path('backup-'+tag)/p.name
 for rel,content in [(source,b),(backup,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(content)
 items.append({'target':str(p),'source':source.as_posix(),'backup':backup.as_posix(),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p not in outputs:protected[p]=sha(b)
verify={'passed':True,'serialization_roundtrip':True,'video_display_size':[390,112],'tfwx_slot_size':[240,112],'total_content_width':630,'video_width_change':-130,'tfwx_slot_width_change':120,'all_bindings_serialized_data_and_child_order_unchanged':True,'only_five_nodes_width_constraints_changed':True,'all_texture_pointers_preserved':True,'current_custom_textures_verified':len(registry['textures']),'unrelated_intro_objects_unchanged':len(hashes)-2,'runtime_verified':False}
report={'installed':False,'runtime_verified':False,'template':d['m_Name'],'template_path_id':str(obj.path_id),'style_path_id':str(sid),'video_width_before':520,'video_width_after':390,'video_height':112,'tfwx_slot_before':[120,112],'tfwx_slot':[240,112],'texture_pointer':ptr,'verification':verify,'catalog_audits':audits,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(out/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install','--install'),('restore','--restore')]:
 script="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(Path(__file__).resolve())+"' '"+flag+"' $PSScriptRoot\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n"
 (out/(action+'.ps1')).write_text(script,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'verification':verify,'custom_resources_checked':[len(x['custom_resources_checked']) for x in audits]},ensure_ascii=False),flush=True)
install(out)
