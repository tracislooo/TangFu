"""Render the approved club-location UI diagram without touching game files."""
from pathlib import Path
import base64, hashlib, html, io, json, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.codex-deps'))
import resvg_py
from PIL import Image, ImageChops

OUT=ROOT/'exports/Spurs-club-location-mockup-20261117'
OUT.mkdir(parents=True,exist_ok=True)
SCREEN=Path('C:/Users/traci/AppData/Local/Temp/codex-clipboard-6dca1a2d-e585-46bd-8966-4a60e700ff93.png')
PHOTO=Path('G:/Doc/Sports Interactive/Football Manager 27/graphics/Stadiums/stadium_backgrounds/images/28096287.jpg')
old=ROOT/'exports/UK-premier-league-locations-2026-27'
# Original source file was moved; recover its exact embedded bytes from the prior SVG.
tree=ET.parse(old/'map_UK-premier-league-2026-27.svg')
map_uri=tree.getroot().find('{http://www.w3.org/2000/svg}image').attrib['href']
map_bytes=base64.b64decode(map_uri.split(',',1)[1])
coordinate_data=json.loads((old/'club-coordinates.json').read_text(encoding='utf-8'))
assert hashlib.sha256(map_bytes).hexdigest()==coordinate_data['source_sha256']
club=next(r for r in coordinate_data['clubs'] if r['club']=='Tottenham Hotspur')
mapping=json.loads((ROOT/'club-stadium-comeback-20261115-233007/photo-mapping.json').read_text(encoding='utf-8'))
mapped=next(r for r in mapping if r['club_id']==728)
assert mapped['stadium_id']==28096287 and Path(mapped['image'])==PHOTO

X,Y,W,H=32,528,1080,656
s=W/1920
px,py=club['x']*s,club['y']*s
def uri(path,mime):return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
def text(x,y,value,size=17,color='#f3f7fa',weight='400'):
    return f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(value)}</text>'

parts=[f'<rect width="{W}" height="{H}" fill="#030609"/>',f'<image href="{map_uri}" x="0" y="0" width="{W}" height="{1080*s}"/>']
parts += [f'<circle cx="{px}" cy="{py}" r="13" fill="#21d6f2" fill-opacity=".12" stroke="#37dff6" stroke-opacity=".3"/>',f'<circle cx="{px}" cy="{py}" r="7" fill="#061c25" stroke="#31d8ee" stroke-width="2.5"/>',f'<circle cx="{px}" cy="{py}" r="2.5" fill="white"/>',f'<path d="M{px+12},{py} h22" stroke="#63e5f5" stroke-width="1.5"/>',text(px+40,py+6,'托特纳姆热刺',18,'#eafcff','600')]
parts += [text(598,30,'托特纳姆热刺体育场',22,weight='600'),f'<image href="{uri(PHOTO,"image/jpeg")}" x="598" y="49" width="458" height="257.625" preserveAspectRatio="xMinYMin meet"/>', '<path d="M598,329 H1056" stroke="#31424d"/>']
fields=[('名称','托特纳姆热刺体育场'),('城市','伦敦'),('球场容量','62,850 个座席'),('建立年份','2019'),('草皮','天然草皮'),('场地尺寸','105 米 × 68 米')]
for i,(key,value) in enumerate(fields):
    yy=360+i*43
    parts.extend([text(600,yy,key,17,'#9daebb'),text(747,yy,value,18,weight='500')])
panel=''.join(parts)
def svg(width,height,body):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{body}</svg>'
panel_svg=svg(W,H,panel)
page_svg=svg(2242,1292,f'<image href="{uri(SCREEN,"image/png")}" width="2242" height="1292"/><svg x="{X}" y="{Y}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">{panel}</svg>')
for name,data in [('spurs-location-panel',panel_svg),('spurs-club-page-mockup',page_svg)]:
    (OUT/(name+'.svg')).write_text(data,encoding='utf-8')
    (OUT/(name+'.png')).write_bytes(resvg_py.svg_to_bytes(svg_string=data,font_family='Microsoft YaHei'))

original=Image.open(SCREEN).convert('RGB')
result=Image.open(OUT/'spurs-club-page-mockup.png').convert('RGB')
diff=ImageChops.difference(original,result)
bounds=diff.getbbox()
assert bounds and bounds[0]>=X and bounds[1]>=Y and bounds[2]<=X+W and bounds[3]<=Y+H,bounds
report=dict(club_uid=728,stadium_uid=28096287,source_coordinate=[club['x'],club['y']],source_image_size=[1920,1080],panel_rect=[X,Y,W,H],scale=s,scaled_marker_center=[px,py],screenshot_marker_center=[X+px,Y+py],map_display_size=[W,1080*s],changed_pixel_bounds=bounds,outside_panel_pixels_identical=True,source_map_sha256=coordinate_data['source_sha256'],game_resources_modified=False,kind='static UI mockup; no runtime implementation')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
