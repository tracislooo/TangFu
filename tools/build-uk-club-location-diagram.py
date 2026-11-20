"""Build a deterministic SVG coordinate diagram; never modifies game resources."""
from pathlib import Path
import base64, csv, hashlib, html, json, math, re, urllib.request
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('K:/下载文件/map_UK.png')
OUT = ROOT / 'exports/UK-premier-league-locations-2026-27'
OUT.mkdir(parents=True, exist_ok=True)
url = 'https://fchd.info/maps/GAZ.htm'
raw = urllib.request.urlopen(url, timeout=40).read().decode('utf-8', errors='replace')
(OUT/'source-gazetteer.html').write_text(raw, encoding='utf-8')
names = [
 ('Arsenal','阿森纳'),('Aston Villa','阿斯顿维拉'),('AFC Bournemouth','伯恩茅斯'),
 ('Brentford','布伦特福德'),('Brighton & Hove Albion','布莱顿'),('Chelsea','切尔西'),
 ('Coventry City','考文垂'),('Crystal Palace','水晶宫'),('Everton','埃弗顿'),
 ('Fulham','富勒姆'),('Hull City','赫尔城'),('Ipswich Town','伊普斯维奇'),
 ('Leeds United','利兹联'),('Liverpool','利物浦'),('Manchester City','曼城'),
 ('Manchester United','曼联'),('Newcastle United','纽卡斯尔联'),
 ('Nottingham Forest','诺丁汉森林'),('Sunderland','桑德兰'),('Tottenham Hotspur','托特纳姆热刺')]
geo = {}
for match in re.finditer(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|\Z)', raw, re.S|re.I):
    name = html.unescape(re.sub('<[^>]+>', '', match[1])).strip()
    ll = re.search(r'>(-?\d+\.\d+),\s*(-?\d+\.\d+)</a>',match[2],re.I)
    if ll: geo[name]=(float(ll[1]),float(ll[2]))
def merc(lat): return math.log(math.tan(math.pi/4+math.radians(lat)/2))
# Manually identified coastal landmarks on the supplied unreferenced artwork.
# Independent x/y scales: no claim that the artwork is exactly Web Mercator.
anchors = [
 dict(name='Lands End', lat=50.066, lon=-5.715, x=475, y=971),
 dict(name='Lowestoft Ness',lat=52.482,lon=1.762,x=819,y=791),
 dict(name='Duncansby Head',lat=58.644,lon=-3.025,x=597,y=286),
 dict(name='Dover',lat=51.126,lon=1.321,x=801,y=892)]
cx=np.linalg.lstsq(np.array([[1,a['lon']] for a in anchors]),np.array([a['x'] for a in anchors]),rcond=None)[0]
cy=np.linalg.lstsq(np.array([[1,merc(a['lat'])] for a in anchors]),np.array([a['y'] for a in anchors]),rcond=None)[0]
rows=[]
for i,(en,zh) in enumerate(names,1):
    lat,lon=geo[en]
    x=float(cx[0]+cx[1]*lon); y=float(cy[0]+cy[1]*merc(lat))
    rows.append(dict(number=i,club=en,club_zh=zh,latitude=lat,longitude=lon,x=round(x,2),y=round(y,2),pixel_x=round(x),pixel_y=round(y),x_percent=round(x/1920*100,5),y_percent=round(y/1080*100,5)))
assert len(rows)==20 and all(0<=r['x']<1920 and 0<=r['y']<1080 for r in rows)
meta=dict(season='2026/27',image_width=1920,image_height=1080,origin='top-left',x_direction='right',y_direction='down',marker_anchor='center',precision='Approximate coastal-landmark calibration of unreferenced artwork; subpixel values are computational, not geographic accuracy.',source_image=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),club_list_source='https://www.premierleague.com/en/news/4675097/all-380-fixtures-for-season-2026-27',coordinate_source=url,anchors=anchors,transform=dict(x=list(cx),y_mercator=list(cy)),clubs=rows)
(OUT/'club-coordinates.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'club-coordinates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
bg='data:image/png;base64,'+base64.b64encode(SOURCE.read_bytes()).decode()
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#9ce9ff"/></marker></defs><image href="{bg}" width="1920" height="1080"/>', '<g font-family="Microsoft YaHei,Segoe UI,sans-serif">']
def text(x,y,s,size=16,color='#e9f7ff',**attrs):
    a=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {a}>{html.escape(s)}</text>')
parts.append('<path d="M1,1 H1880 M1,1 V1035" fill="none" stroke="#9ce9ff" stroke-width="2" marker-end="url(#arrow)"/>')
text(14,28,'(0, 0)',18);text(1840,30,'X →',20);text(15,1045,'Y ↓',20)
for x in range(200,1900,200):
    parts.append(f'<path d="M{x},1 v9" stroke="#9ce9ff"/>');text(x-16,29,str(x),13)
for y in range(200,1050,200):
    parts.append(f'<path d="M1,{y} h9" stroke="#9ce9ff"/>');text(14,y+5,str(y),13)
text(1060,92,'英超俱乐部位置 · 2026/27',32)
text(1060,124,'1920 × 1080  /  左上角原点  /  主场位置',17,'#9ce9ff')
for idx,r in enumerate(rows):
    col=idx//10; n=idx%10;tx=1060+col*418;ty=174+n*34
    text(tx,ty,f'{r["number"]:02}  {r["club_zh"]}',17)
    text(tx+233,ty,f'({r["x"]:.2f}, {r["y"]:.2f})',15,'#9ce9ff')
# Label all non-London clubs around the main map; point centers are never shifted.
london={1,4,6,8,10,20}
west={9,14,15,16,2,7,3}
for side,chosen in [('west',[r for r in rows if r['number'] in west]),('east',[r for r in rows if r['number'] not in west|london])]:
    chosen.sort(key=lambda r:r['y'])
    ys=[]
    for r in chosen: ys.append(max(r['y'],ys[-1]+31 if ys else 0))
    for r,ly in zip(chosen,ys):
        lx=410 if side=='west' else 870
        end=lx+6 if side=='west' else lx-6
        parts.append(f'<path d="M{r["x"]},{r["y"]} L{end},{ly}" stroke="#99eaff" opacity=".65" fill="none"/>')
        text(lx,ly+5,f'{r["number"]:02} {r["club_zh"]}',16,text_anchor='end' if side=='west' else 'start',paint_order='stroke',stroke='#07121e',stroke_width=4)
for r in rows:
    parts.append(f'<circle cx="{r["x"]}" cy="{r["y"]}" r="3" fill="#c4f8ff" stroke="#008fbd" stroke-width="1"><title>{html.escape(r["club_zh"])} ({r["x"]}, {r["y"]})</title></circle>')
# Separate enlarged London schematic preserves the exact projected positions.
parts.append('<rect x="1060" y="545" width="810" height="350" rx="12" fill="#081523" fill-opacity=".94" stroke="#31586c"/>')
text(1080,577,'伦敦六队放大 · 标注点不作避让移动',19)
def local(r):return (1430+(r['x']-731)*14,735+(r['y']-867)*14)
labelpos={1:(1580,670),20:(1580,620),8:(1580,835),4:(1110,700),10:(1110,810),6:(1110,755)}
for r in rows:
    if r['number'] not in london:continue
    px,py=local(r);lx,ly=labelpos[r['number']]
    ex=lx+155 if lx<1400 else lx-8
    parts.append(f'<path d="M{px},{py} L{ex},{ly-5}" stroke="#63c8e9" fill="none"/><circle cx="{px}" cy="{py}" r="5" fill="#b8f4ff"/>')
    text(lx,ly,f'{r["number"]:02} {r["club_zh"]}',17)
text(1060,940,'坐标指圆点中心；同城球队可能仅相隔数像素。',17)
text(1060,971,'底图无地理配准信息，位置经海岸地标校准，属于示意定位。',16,'#a7baca')
text(1060,1000,'缩放时：X′ = X × 新宽 / 1920；Y′ = Y × 新高 / 1080。',16,'#a7baca')
parts.append('</g></svg>')
svg=''.join(parts)
(OUT/'map_UK-premier-league-2026-27.svg').write_text(svg,encoding='utf-8')
import sys
sys.path.insert(0,str(ROOT/'.codex-deps'))
import resvg_py
(OUT/'map_UK-premier-league-2026-27.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,font_family='Microsoft YaHei'))
(OUT/'README.md').write_text('''# 英超位置示意图 2026/27

原图1920×1080，左上角为(0,0)，X向右，Y向下；坐标是标记圆心。
SVG内嵌原始底图，保留原始尺寸，可独立打开；CSV/JSON为后续皮肤映射数据。
原图没有投影/边界元数据，以四个海岸地标拟合经度线性、纬度墨卡托变换，属于近似定位。小数位只是计算结果，不代表测绘精度；没有已知误差界限。
伦敦放大框只是帮助辨认，表中坐标始终对应1920×1080原图。
图片整体等比缩放时，坐标随之缩放；若使用contain/cover，还须计算留白偏移或裁切偏移。
球队名单依据英超官方2026/27赛程；主场坐标依据FCHD球场名录。
https://www.premierleague.com/en/news/4675097/all-380-fixtures-for-season-2026-27
https://fchd.info/maps/GAZ.htm
未修改或安装任何游戏资源。
''',encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
print(str(OUT))
