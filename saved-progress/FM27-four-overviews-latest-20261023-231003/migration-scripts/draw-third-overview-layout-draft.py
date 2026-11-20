from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math

out=Path.cwd()/'third-overview-layout-draft'
out.mkdir(exist_ok=True)
im=Image.new('RGB',(1620,1080),'#0a101c');d=ImageDraw.Draw(im)
fontpath='C:/Windows/Fonts/msyh.ttc'
def text(x,y,s,size=18,color='#e8eef8',anchor=None):
    d.text((x,y),s,font=ImageFont.truetype(fontpath,size),fill=color,anchor=anchor)
def line(points,color='#43546b',width=1):d.line(points,fill=color,width=width)
def box(rect,fill='#111f31',outline='#40556f',radius=8):d.rounded_rectangle(rect,radius,fill=fill,outline=outline,width=1)
def center(rect,s,size=18,color='#e8eef8'):
    x1,y1,x2,y2=rect;text((x1+x2)/2,(y1+y2)/2,s,size,color,'mm')
def pitch(rect,vertical=False):
    x1,y1,x2,y2=rect;box(rect,'#0d4b3a','#a8bcb8',0)
    midx=(x1+x2)/2;midy=(y1+y2)/2
    if vertical:
        line([(x1,midy),(x2,midy)],'#8bb5a4');d.ellipse((midx-15,midy-15,midx+15,midy+15),outline='#8bb5a4')
        d.rectangle((x1+18,y1,x2-18,y1+36),outline='#8bb5a4');d.rectangle((x1+18,y2-36,x2-18,y2),outline='#8bb5a4')
        points=[(.5,.90),(.2,.73),(.5,.73),(.8,.73),(.2,.48),(.5,.48),(.8,.48),(.2,.25),(.5,.25),(.8,.25),(.5,.09)]
    else:points=[]
    for j,(px,py) in enumerate(points):
        x=x1+(x2-x1)*px;y=y1+(y2-y1)*py;r=5
        d.ellipse((x-r,y-r,x+r,y+r),fill='#d7dc23' if j in [4,5] else '#1f302c',outline='#c1dacb' if j==4 else None)

text(28,16,'第三版 · 左边版FC卡面+隐藏',27)
text(1592,26,'布局草图｜非游戏截图',17,'#9caec6','ra')
text(28,59,'三栏等宽；比例按扣除间距后的可用空间计算。当前第一版、第二版及底部卡片保持原样。',17,'#9caec6')
xs=[28,554,1080];w=512;top=119;bottom=929;h=810;gap=8
for x,name in zip(xs,['左栏  1/3','中栏  1/3','右栏  1/3']):
    center((x,88,x+w,115),name,19,'#b8ceeb')
    box((x,top,x+w,bottom))

# Left: whole-column background, top half card and lower half identity plus bans.
x=xs[0];cut=top+(h-gap)//2
for y in range(top+1,bottom):
    t=(y-top)/h;line([(x+1,y),(x+w-1,y)],('#123552' if t<.5 else '#102b47'))
for k in range(10):line([(x+2,top+35+k*77),(x+w-2,top+95+k*77)],'#16415f')
text(x+14,top+12,'上半 50% · FC卡面',18,'#a8c4e2')
cx=x+w/2;cy=top+62
card=[(cx-96,cy+18),(cx-73,cy),(cx-48,cy+8),(cx-22,cy),(cx+22,cy),(cx+48,cy+8),(cx+73,cy),(cx+96,cy+18),(cx+96,cy+267),(cx,cy+292),(cx-96,cy+267)]
d.polygon(card,fill='#081c2a',outline='#6bd2dd');d.line(card+[card[0]],fill='#a7dbe2',width=3)
d.ellipse((cx-39,cy+40,cx+39,cy+119),fill='#7d8a9b');d.rounded_rectangle((cx-62,cy+122,cx+62,cy+195),10,fill='#546c8b')
text(cx-82,cy+41,'140',18,'#e9dc54');text(cx-82,cy+72,'156',18);text(cx-82,cy+107,'D (R)',14);text(cx-82,cy+140,'186cm',13)
box((cx+30,cy+11,cx+87,cy+33),'#3eac79','#3eac79',3);center((cx+30,cy+11,cx+87,cy+33),'状态',12)
center((cx-84,cy+209,cx+84,cy+232),'速度  盘带  防守',16)
center((cx-84,cy+237,cx+84,cy+261),'六项属性 · 左右脚',14,'#a9c9cf')
line([(x+8,cut),(x+w-8,cut)],'#83a7c8',2)
lowtop=cut+gap;lowh=bottom-lowtop;identityend=lowtop+int((lowh-gap)*.7)
text(x+14,lowtop+9,'下半 50% · 姓名资料 70% / 禁赛 30%',16,'#a8c4e2')
text(x+15,lowtop+43,'球员姓名',30)
text(x+15,lowtop+88,'位置 · 年龄 · 出生日期',15,'#becbdb')
text(x+15,lowtop+116,'身价          工资          定位',16)
labels=[('身高 · 经纪人 · 个性',151),('声望 · 媒体评价 · 生涯总结',181),('里程碑 · 媒体意见',211),('国家队信息        俱乐部信息',241)]
for lab,dy in labels:
    if lowtop+dy+20<identityend+12:
        line([(x+14,lowtop+dy-5),(x+w-14,lowtop+dy-5)],'#42637d');text(x+16,lowtop+dy,lab,15,'#d2dce8')
line([(x+10,identityend),(x+w-10,identityend)],'#83a7c8')
text(x+16,identityend+10,'禁赛 · 保留原生比赛与累计进度',16)
for j,lab in enumerate(['联赛     1/5  ━━━━━','杯赛     0/2  ━━━━━']):text(x+22,identityend+43+j*26,lab,15,'#bac9db')

# Center: attributes 60%, lower pitch/phase/comparison split three ways.
x=xs[1];cut=top+int((h-gap)*.6)
text(x+14,top+12,'上部 60% · 三列属性（随栏宽缩放）',18,'#a8c4e2')
groups=[['传球','传中','盯人','技术','盘带','抢断','射门','停球','头球','远射','罚点球','角球','界外球','任意球'],['才华','防守站位','工作投入','集中','决断','领导力','侵略性','视野','团队合作','无球跑动','意志力','勇敢','预判','镇定'],['爆发力','弹跳','灵活','耐力','平衡','强壮','速度','体质']]
cw=(w-32)/3
for c,items in enumerate(groups):
    xx=x+12+c*(cw+4)
    for r,lab in enumerate(items):
        yy=top+51+r*27
        if yy+24>cut-9:break
        d.rectangle((xx,yy,xx+cw-5,yy+25),fill='#173528' if r%3==0 else '#1c2939' if r%2 else '#101a27')
        text(xx+5,yy+4,lab,14);box((xx+cw-37,yy+3,xx+cw-11,yy+23),'#716c15','#716c15',3);center((xx+cw-37,yy+3,xx+cw-11,yy+23),str(10+(r+c)%8),12)
    if c==2:
        yy=top+51+8*27+14;line([(xx,yy),(xx+cw-7,yy)],'#48617b');text(xx+3,yy+12,'能力评分',14);text(xx+3,yy+42,'习惯列表',14,'#c6d2e3')
line([(x+8,cut),(x+w-8,cut)],'#83a7c8',2)
lower=cut+gap;text(x+14,lower+9,'下部 40% · 三列等宽',17,'#a8c4e2')
parts=(w-32)/3
for c in range(1,3):line([(x+8+c*(parts+4)-3,lower+42),(x+8+c*(parts+4)-3,bottom-10)],'#415672')
px=x+13;py=lower+47;ph=min(235,bottom-py-30);pw=ph*.7
pitch((px+(parts-pw)/2,py,px+(parts+pw)/2,py+ph),True)
center((px,py+ph+4,px+parts,bottom-3),'位置名称',13,'#b7c9df')
xx=x+13+parts+5
center((xx,lower+46,xx+parts,lower+76),'持球 / 无球',15)
for j in range(5):
    yy=lower+91+j*35;text(xx+2,yy,'●' if j==0 else '○',16,'#c2a6f1');text(xx+25,yy,'★★★',14,'#edcb6b');text(xx+25,yy+18,'角色选项',12)
xx=x+13+2*(parts+5);center((xx,lower+46,xx+parts,lower+76),'比较',15)
for j in range(5):
    yy=lower+92+j*37;text(xx+4,yy,f'球员 {j+1}',14);text(xx+67,yy,'★★★',13,'#edcb6b')

# Right: current hidden/pros/tactics group, below radar and report/fitness/statistics.
x=xs[2];cut=top+int((h-gap)*.6)
text(x+14,top+12,'上部 60% · 保留第一版完整组合',18,'#a8c4e2')
text(x+17,top+52,'● 能力 140       ● 潜力 156      声望 6900',17)
text(x+17,top+89,'隐藏',13,'#a0a0a0');d.rounded_rectangle((x+68,top+93,x+w-19,top+100),3,fill='#35475c');d.rounded_rectangle((x+68,top+93,x+w-95,top+100),3,fill='#04c1a7')
line([(x+14,top+118),(x+w-14,top+118)],'#48617b')
hidden=[['适应性','雄心','忠诚','抗压','职业'],['体育道德','情绪控制','多面性','肮脏动作'],['稳定','大赛发挥','争论','受伤倾向']]
for c,items in enumerate(hidden):
    xx=x+15+c*163
    for j,lab in enumerate(items):
        yy=top+130+j*27;text(xx,yy,lab,14);box((xx+113,yy,xx+143,yy+22),'#6c6816','#6c6816',3);center((xx+113,yy,xx+143,yy+22),str(11+(c+j)%7),13)
yy=top+278;line([(x+14,yy),(x+w-14,yy)],'#48617b')
line([(x+w/2,yy+11),(x+w/2,cut-12)],'#3e536d')
text(x+18,yy+17,'优点',17,'#85d97b');text(x+20,yy+53,'●  ◆  ●  ◆  ●  ◆',20,'#85d97b')
text(x+18,yy+96,'缺点',17,'#ef7d87');text(x+20,yy+131,'◆  ●  ●',20,'#ef7d87')
text(x+w/2+15,yy+19,'战术执行力',17)
text(x+w/2+15,yy+59,'原生内容，无背景和标题',13,'#aebfd3')
for j,lab in enumerate(['战术理解力   ●','球员认同       ●','球员能力       ●']):text(x+w/2+15,yy+91+j*28,lab,14,'#d0dbe8')
line([(x+8,cut),(x+w-8,cut)],'#83a7c8',2)
lower=cut+gap;text(x+14,lower+9,'下部 40% · 左右各 50%',17,'#a8c4e2')
line([(x+w/2,lower+39),(x+w/2,bottom-10)],'#435873')
cx=x+w/4;cy=lower+166;rad=79;pts=[]
for i in range(8):
    a=-math.pi/2+i*math.pi/4;pts.append((cx+rad*math.cos(a),cy+rad*math.sin(a)))
for scale in [.33,.66,1]:d.polygon([(cx+(a-cx)*scale,cy+(b-cy)*scale) for a,b in pts],outline='#51647e')
data=[(cx+(a-cx)*(.68+(i%3)*.1),cy+(b-cy)*(.68+(i%3)*.1)) for i,(a,b) in enumerate(pts)];d.polygon(data,fill='#64728b',outline='#d0d6e9')
center((x+8,lower+49,x+w/2-8,lower+81),'八卦图 / 雷达图',16)
for i,(a,b) in enumerate(pts):d.ellipse((data[i][0]-3,data[i][1]-3,data[i][0]+3,data[i][1]+3),fill='#e4e8f0')
xx=x+w/2+10;rw=w/2-22
center((xx,lower+44,xx+rw,lower+73),'球探报告',14)
for j in range(3):
    cx2=xx+rw*(j+.5)/3;cy2=lower+98;d.ellipse((cx2-13,cy2-13,cx2+13,cy2+13),outline='#c8d929',width=4);text(cx2,cy2+20,['体能','比赛状态','疲劳'][j],10,'#a9bfd0','mm')
statlabels=[['获胜/场次','当场最佳','进球'],['预期进球/90','射正/90','创造机会'],['预期助攻/90','关键传球','传球成功/90'],['关键抢断','抢断成功','关键头球/90']]
for row,items in enumerate(statlabels):
    yy=lower+139+row*39
    for col,lab in enumerate(items):
        cx2=xx+rw*(col+.5)/3;text(cx2,yy,lab,9,'#aabbd0','mm');text(cx2,yy+16,['3','6.8','12'][col],13,['#eed668','#64baff','#6be192'][col],'mm')
    line([(xx,yy+29),(xx+rw,yy+29)],'#43546b')

text(28,949,'底部原有独立卡片保持现状（不计入上方三栏比例）',17,'#a8bdd7')
widths=[2,2,2,8,2,4];labels=['模块1','模块2','模块3','赛季统计','训练 / 资格','战术执行力'];left=28;unit=(1564-5*8)/20
for width,label in zip(widths,labels):
    right=left+unit*width;box((left,981,right,1036),'#152237');center((left,981,right,1036),label,16);left=right+8
text(28,1050,'背景：仅第三版左栏铺原有 background；第一版与第二版不变。',14,'#8198b3')
im.save(out/'third-overview-layout.png')
print(str(out/'third-overview-layout.png'))
