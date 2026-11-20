from pathlib import Path
import json
R=Path(__file__).resolve().parent
location=json.loads((R/'current-game-location.json').read_text('utf8'))
base=(R/'start-banner-video520-tfwx120.py').read_text('utf8')
boot=base.split("assert rr[1002]['data']['m_Children']==[{'rid':1004}]")[0]
boot=boot.replace("F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa",location['aa_root'])
boot=boot.replace("'video_size':[520,112],'TFWX_slot':[120,112]","'video_width':'50%','TFWX_width':'50%'")
exec(compile(boot,'current-path-bootstrap','exec'))
assert str(GAME).replace('\\','/')==location['bundle_root']
parsed=ast.parse(base)
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['val','px','en','num','style','styled']],type_ignores=[]),'style-helpers','exec'))
nr=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and data(i).get('name')=='StartScreenTFWX')
assert rr[1002]['data']['m_Children']==[{'rid':1004},{'rid':nr}]
def pct(v):return val(3,{'unit':2,'value':float(v)})
def width(i,v):style(i,[(131105,pct(v)),(131097,px(0)),(131095,pct(v)),(131084,num(0)),(131085,num(1))])
width(1002,100)
for i in [1004,nr]:width(i,50)
for i in [1006,1007,1009]:width(i,100)
for i in [1004,nr]:assert styled(i,131105)=={'unit':2,'value':50.0}
for i in [1004,1006,1007,1009,nr]:assert styled(i,131087)=={'unit':1,'value':112.0}
for rid,old in old_rr.items():
 actual=copy.deepcopy(rr[rid])
 if 'm_RuleIndex' in old.get('data',{}):actual['data']['m_RuleIndex']=old['data']['m_RuleIndex']
 assert actual==old
assert s['assets']==old_s['assets']
validate_ui(d,s);obj.save_typetree(d);a.objects[sid].save_typetree(s)
outbytes=e.file.save(packer='lz4');sa=UnityPy.load(outbytes).assets[0]
assert set(sa.objects)==set(hashes)
for i,h in hashes.items():
 if i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h
worlds={name:UnityPy.load(str(GAME/name)).assets[0] for name in [WORLD,GLOBAL]}
exec(compile(base[base.index("outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};audits=[]"):base.index("agents_text=before[agents].decode('utf8')")],'catalog-audit','exec'))
out=R/('start-banner-equal-halves-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
new_rule='- 开始页横幅最终为视频与TFWX左右各50%，父容器宽100%，高度112px；内部视频控件宽100%，移除旧390/240px固定宽约束。保留TFWX固定ID、等比完整显示、视频播放及点击绑定。'
outputs[agents]=(before[agents].decode('utf8')+'\n'+new_rule+'\n').encode('utf8')
outputs[note]=(before[note].decode('utf8')+'\n\n## 11. 2026-11-01 最终横幅：左右各50%\n\n本节覆盖第10节390／240px固定宽度。当前游戏目录以current-game-location.json为准，禁止写旧Project Taco目录。\n\n视频与TFWX两块各占当前横幅50%，外层container宽100%，内层按钮及视频图像宽100%；旧width/min-width/max-width固定像素约束已替换为百分比宽度、min-width 0和匹配的百分比max-width。高度112px、scale-to-fit、原节点/事件/纹理引用保留。随父容器等宽分配，非固定315px。\n\n实施脚本start-banner-equal-halves.py；记录目录：'+out.name+'。未启动游戏做运行时验证。\n').encode('utf8')
items=[]
for p,b in outputs.items():
 assert 'Project Taco' not in str(p)
 tag='workspace' if p.parent==R else ('game' if p.parent in [AA,GAME] else 'skin');src=Path(tag)/p.name;bak=Path('backup-'+tag)/p.name
 for rel,content in [(src,b),(bak,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(content)
 items.append({'target':str(p),'source':str(src),'backup':str(bak),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
for p,b in before.items():assert p.read_bytes()==b
for p,b in before.items():
 if p not in outputs:protected[p]=sha(b)
report={'installed':False,'runtime_verified':False,'video_width':'50%','tfwx_width':'50%','height':112,'bindings_children_and_texture_references_unchanged':True,'unrelated_objects_unchanged':len(hashes)-2,'catalog_audits':audits,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for action in ['install','restore']:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(Path(__file__).resolve())+"' '--"+action+"' $PSScriptRoot\n",'utf-8-sig')
install(out)
print(json.dumps({'output':str(out),'video':'50%','TFWX':'50%','height':112},ensure_ascii=False))
