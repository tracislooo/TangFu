from pathlib import Path
import json,csv,shutil,hashlib,html

OUT=Path(__file__).resolve().parent
SRC=Path('G:/Doc/deepseek-harness/default-workspace/tt/china_map_handover')
ROOT=OUT.parent.parent
d=json.loads((SRC/'china_coordinates.json').read_text('utf8'))
db=json.loads((ROOT/'analysis/comeback-stadium-20261115/clubs-client.json').read_text('utf8'))
aliases={'Beijing Guoan':406,'Chongqing Tonglianglong':2000208932,'Guangdong GZ-Power':2000328121,'Henan':131162,'Qingdao West Coast':34039025,'Meizhou Hakka':23199255}
rows=[]
for i,c in enumerate(d['clubs']):
    c=dict(c)
    matches=[a for a in db if any(c['club'].casefold()==n.casefold() for n in a['names'])]
    uid=aliases.get(c['club'])
    if uid is None and len(matches)==1:uid=matches[0]['id']
    if c['club']=='Ningbo':uid=None
    c.update(index=i+1,uid=uid,x_percent=round(c['x']/1920*100,6),y_percent=round(c['y']/1080*100,6),uid_status='matched_local_database' if uid else 'needs_review_renamed_club')
    if uid:c['database_names']=next(a['names'] for a in db if a['id']==uid)
    else:c['uid_candidates']=[{'uid':a['id'],'names':a['names']} for a in db if a['id'] in [23366052,23009373,2000525586]]
    rows.append(c)
assert len(rows)==32 and sum(c['league_zh']=='中超' for c in rows)==16
assert all(0<=c['x']<1920 and 0<=c['y']<1080 for c in rows)
assert len({c['uid'] for c in rows if c['uid']})==sum(bool(c['uid']) for c in rows)
for name in ['map_China_ninedash.png','china_locations.png']:
    shutil.copyfile(SRC/name,OUT/name)
    assert hashlib.sha256((SRC/name).read_bytes()).digest()==hashlib.sha256((OUT/name).read_bytes()).digest()
data={'season':2026,'image':'map_China_ninedash.png','width':1920,'height':1080,'origin':'top-left','x_direction':'right','y_direction':'down','position':'stadium; approximate poster coordinates','marker':'cyan ring with white center; one selected club; no label or leader line','official_roster_source':'https://www.cfl-china.cn/zh/content/announcements/bRVz.html','coordinate_source':'provided handover china_coordinates.json; retained without recalculation','runtime_verified':False,'clubs':rows}
(OUT/'club-coordinates.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
fields=['index','league_zh','club_zh','club','uid','uid_status','city_zh','stadium','x','y','x_percent','y_percent','lat','lon','needs_review']
with (OUT/'club-coordinates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>中国两级联赛位置预览</title><style>body{margin:0;background:#0b1018;color:#eee;font:16px "Microsoft YaHei",sans-serif}header{padding:18px 24px}select{font:inherit;background:#263445;color:white;padding:7px;border:1px solid #62778b}p{color:#aab8c7;font-size:13px}.map{position:relative;width:100%}.map img{display:block;width:100%;height:auto}.marker{position:absolute;width:18px;height:18px;border:2px solid #39ddff;border-radius:50%;transform:translate(-50%,-50%);box-sizing:border-box;box-shadow:0 0 10px #39ddff}.marker:after{content:"";position:absolute;width:4px;height:4px;left:50%;top:50%;transform:translate(-50%,-50%);background:white;border-radius:50%}</style><header><select id="club"></select><p id="info"></p><p>原图1920×1080，原点左上角。地图内仅显示所选球队圆圈，不显示队名和引线；位置为海报近似定位。</p></header><div class="map"><img src="map_China_ninedash.png"><div class="marker" id="marker"></div></div><script>const clubs=DATA;const select=document.getElementById('club');for(const c of clubs){let o=document.createElement('option');o.value=c.index;o.textContent=c.league_zh+' · '+c.club_zh;select.append(o)}function update(){const c=clubs.find(c=>c.index==select.value);const m=document.getElementById('marker');m.style.left=c.x_percent+'%';m.style.top=c.y_percent+'%';document.getElementById('info').textContent='UID '+(c.uid??'待核对')+' ｜ '+c.stadium+' ｜ 原图圆心 ('+c.x+', '+c.y+')'+(c.needs_review?' ｜ 多主场或坐标待复核':'')}select.onchange=update;update();</script></html>'''
(OUT/'single-club-preview.html').write_text(page.replace('DATA',json.dumps(rows,ensure_ascii=False)),'utf8')
readme='''# 中国中超、中甲位置整理（2026）

32队：中超16队、中甲16队。名单核对中足联2026年2月2日准入公告：
https://www.cfl-china.cn/zh/content/announcements/bRVz.html

- `china_locations.png`：交接目录已有总览核对图，原样复制；其编号和名称仅用于核对。
- `map_China_ninedash.png`：用户指定底图，原样复制。
- `single-club-preview.html`：选择球队后仅显示一个青色圆圈和白色中心点，无队名或引线。双击可在浏览器预览。本次没有打开程序或浏览器。
- `club-coordinates.csv/json`：原图坐标及本地数据库UID匹配。左上角(0,0)，X向右、Y向下，位置指圆心。缩放宽度W时，圆心为(x*W/1920,y*W/1920)。

坐标沿用交接表，未重新测绘；底图为风格化海报，属于近似定位。长春亚泰、定南赣联、广西恒宸、无锡吴钩保留原表的needs_review标记。

31队UID已对应本地数据库；宁波涉及原上海嘉定汇龙更名迁址及同名俱乐部，UID留空并列出候选，未猜测。已匹配UID表示名称身份对应，未验证当前存档参赛名单或游戏运行时切换。

本次仅整理资料和预览，未安装或修改游戏。交接文档中的赛季冠军、赛果、主场场次数等未作为本次结论。
'''
(OUT/'README.md').write_text(readme,'utf8')
(OUT/'verification.json').write_text(json.dumps({'clubs':len(rows),'csl':sum(c['league_zh']=='中超' for c in rows),'league_one':sum(c['league_zh']=='中甲' for c in rows),'uid_matched':sum(bool(c['uid']) for c in rows),'unresolved':[c['club_zh'] for c in rows if not c['uid']],'all_points_within_canvas':True,'base_and_overview_copies_byte_identical':True,'game_modified':False},ensure_ascii=False,indent=2),'utf8')
print((OUT/'verification.json').read_text('utf8'))
