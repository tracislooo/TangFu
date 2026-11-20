from pathlib import Path
import json
R=Path(__file__).resolve().parent
location=json.loads((R/'current-game-location.json').read_text('utf8'))
base=(R/'start-banner-video520-tfwx120.py').read_text('utf8')
boot=base.split("assert rr[1002]['data']['m_Children']==[{'rid':1004}]")[0].replace('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa',location['aa_root'])
boot=boot.replace("'video_size':[520,112],'TFWX_slot':[120,112]","'left_image':'TFWPS','right_image':'TFWX'")
exec(compile(boot,'current-path-bootstrap','exec'))
parsed=ast.parse(base)
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['val','px','en','num','style','styled']],type_ignores=[]),'style-helpers','exec'))
URL='https://www.kdocs.cn/etapps/workbench/w/2myl8aB8';WPID=-910000000000153
wp=next(t for t in registry['textures'] if t['name']=='TFWPS');assert int(wp['path_id'])==WPID and WPID not in banned
qr=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and data(i).get('name')=='StartScreenTFWX')
assert styled(qr,131105)==styled(1004,131105)=={'unit':2,'value':50.0}
assert rr[1004]['data']['m_Children']==[{'rid':1006},{'rid':1007}]
main=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MainMenu').read_typetree();mr={r['rid']:r for r in main['references']['RefIds']}
donor=next(r for r in mr.values() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingSetter')
ds=copy.deepcopy(mr[donor['data']['m_SerializedData']['rid']]);switch=rr[1004]['data'];srid=switch['m_SerializedData']['rid']
switch['m_FullTypeName']='SI.Bindable.BindingSetter';switch['m_Children']=[{'rid':1006}]
ds.update(rid=srid);ds['data'].update(uxmlAssetId=switch['m_Id'],name='TFWPSLinkScope',name_UxmlAttributeFlags=1,ValueVariables=[{'m_name':'tfwpsurl','m_scopeValue':{'m_serializedData':'String|'+URL+'|'}}],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables=[],ReferenceVariables_UxmlAttributeFlags=1,BindFunction=[],BindFunction_UxmlAttributeFlags=1)
rr[srid].clear();rr[srid].update(ds)
# Keep the native OpenURL action type, replacing only its binding path and lengths.
old_event=bytes(data(1006)['Events']['m_bytes']);assert old_event[:5]==b'\x01\x01\x01\x01\x01' and b'promo.PromoURL' in old_event
arg=b'\x01\x01'+bytes([len('tfwpsurl')])+b'tfwpsurl'
payload=old_event[9:14]+struct.pack('<I',len(arg))+arg
event=b'\x01\x01\x01\x01\x01'+struct.pack('<I',len(payload))+payload
assert payload[:5]==old_event[9:14] and struct.unpack_from('<I',event,5)[0]==len(event)-9
data(1006).update(Events={'m_bytes':list(event)},Events_UxmlAttributeFlags=1)
# Replace the video display with the same native VisualElement used for TFWX.
left=rr[1009]['data'];lrid=left['m_SerializedData']['rid'];copy_sd=copy.deepcopy(rr[rr[qr]['data']['m_SerializedData']['rid']])
copy_sd['rid']=lrid;copy_sd['data'].update(uxmlAssetId=left['m_Id'],name='StartScreenTFWPS',name_UxmlAttributeFlags=1)
left['m_FullTypeName']='UnityEngine.UIElements.VisualElement';left['m_Classes']=[]
rr[lrid].clear();rr[lrid].update(copy_sd)
ptr=copy.deepcopy(styled(qr,458753));ptr['m_PathID']=WPID
style(1009,[(458753,val(6,ptr)),(262153,en('scale-to-fit'))])
removed={1007,old_rr[1007]['data']['m_SerializedData']['rid']}
d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in removed]
assert RT not in json.dumps(d) and 'promo.PromoURL' not in json.dumps(d)
validate_ui(d,s);obj.save_typetree(d);a.objects[sid].save_typetree(s)
outbytes=e.file.save(packer='lz4');sa=UnityPy.load(outbytes).assets[0]
assert set(sa.objects)==set(hashes)
for i,h in hashes.items():
 if i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h
linked=UnityPy.load(outbytes,bgb);la=next(x for x in linked.assets if x.name==a.name)
resolved=PPtr(m_FileID=ptr['m_FileID'],m_PathID=WPID,assetsfile=la).deref();assert resolved.peek_name()=='TFWPS' and sha(resolved.get_raw_data())==wp['texture_sha256']
worlds={name:UnityPy.load(str(GAME/name)).assets[0] for name in [WORLD,GLOBAL]}
exec(compile(base[base.index("outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};audits=[]"):base.index("agents_text=before[agents].decode('utf8')")],'catalog-audit','exec'))
out=R/('start-banner-tfwps-link-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
rule='开始页横幅最新为左TFWPS、右TFWX各50%，高112px，等比完整显示；移除视频显示及原promo链接分支，左TFWPS复用原生OpenURL事件，绑定 '+URL+'；固定复用TFWPS -910000000000153和TFWX -910000000000150。'
outputs[agents]=(before[agents].decode('utf8')+'\n- 2026-11-05：'+rule+'\n').encode('utf8')
outputs[note]=(before[note].decode('utf8')+'\n\n## 12. 2026-11-05 最新：TFWPS替换左侧视频\n\n'+rule+'\n\n恢复时在新版MarketingBannerTile_8x2上移除旧视频RenderTexture显示和promo.PromoURL条件分支，左侧保留SIButton；使用局部BindingSetter的String常量tfwpsurl供原生OpenURL读取，图片VisualElement直接引用backgrounds中TFWPS。保留右TFWX、左右百分比约束及112px高度。不得恢复旧视频方案。\n\n脚本start-banner-tfwps-link.py；安装/回退记录'+out.name+'。序列化与引用校验通过，未打开链接或启动游戏，运行时待用户验证。\n').encode('utf8')
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
report={'installed':False,'runtime_verified':False,'left_image':'TFWPS','right_image':'TFWX','widths':['50%','50%'],'height':112,'url':URL,'video_display_removed':True,'native_url_event_type_preserved':True,'source_texture_pointer_verified':True,'unrelated_objects_unchanged':len(hashes)-2,'catalog_audits':audits,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for action in ['install','restore']:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(Path(__file__).resolve())+"' '--"+action+"' $PSScriptRoot\n",'utf-8-sig')
install(out)
