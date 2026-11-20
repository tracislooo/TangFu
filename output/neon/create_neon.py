from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path
import math

OUT=Path(__file__).parent
base=Image.open(r'K:\桌面\27skin\FcCard\新建文件夹\CA140.png').convert('RGBA')
W,H=base.size
# Paths follow the existing frame and the bent luminous ribbons in the artwork.
paths=[
[(375,49),(348,74),(326,77),(303,69),(286,51),(255,57),(191,81),(122,115),(53,143),(48,281),(48,457),(48,647),(51,805),(66,847),(98,866),(190,882),(285,903),(375,926),(463,903),(569,882),(661,859),(692,837),(704,791),(705,611),(706,432),(705,273),(702,145),(642,122),(558,87),(482,58),(453,52),(433,73),(413,78),(391,67),(375,49)],
[(298,77),(320,126),(344,186),(373,247),(422,269),(499,302),(584,343),(690,393)],
[(411,438),(380,392),(346,347),(318,315),(307,315),(302,338),(310,392),(334,476),(367,586),(409,703),(456,817)],
[(691,515),(629,487),(564,456),(510,435),(480,432),(454,446),(438,471),(438,500),(451,540),(490,617),(545,710),(595,798)],
[(686,553),(635,527),(577,498),(537,475),(521,476),(510,491),(513,521),(539,574),(583,641),(635,707)],
[(215,173),(231,203),(250,244),(268,293),(271,335),(257,359),(240,383),(233,421),(247,477),(270,536),(300,602),(327,661)],
[(73,862),(138,909),(210,918),(295,920),(375,937),(463,918),(565,908),(673,858)],
]

def sample(points):
    a=np.array(points,float); result=[]
    for p,q in zip(a[:-1],a[1:]):
        n=max(2,int(np.linalg.norm(q-p)/2))
        result.extend(p+(q-p)*np.arange(n)[:,None]/n)
    return np.array(result)
trails=[sample(p) for p in paths]
colors=[(47,238,255),(102,255,239),(42,205,255),(124,213,255),(190,255,118),(255,224,122),(127,163,255)]
alpha_clip=np.array(base.getchannel('A'),float)/255
frames=[]; previews=[]
N=48
for f in range(N):
    t=f/N
    sharp=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(sharp)
    for j,pts in enumerate(trails):
        n=len(pts)
        # Traveling light packets, with soft tails and a short bright head.
        phase=(t*(1 if j%2==0 else -1)+j*.173)%1
        for k in range(n-1):
            u=k/n
            delta=(phase-u)%1
            amp=max(math.exp(-delta*delta/(2*.043**2)),.70*math.exp(-(((phase+.5-u)%1)**2)/(2*.035**2)))
            if amp<.025: continue
            c=colors[j]
            d.line([tuple(pts[k]),tuple(pts[k+1])],fill=(*c,int(amp*240)),width=3)
            if amp>.68:
                d.line([tuple(pts[k]),tuple(pts[k+1])],fill=(218,255,255,int(amp*235)),width=1)
        # Small breathing glints precisely on the frame/ribbon path.
        if j in (0,2,3):
            p=pts[int(phase*(n-1))]; x,y=p
            a=int(180*(.6+.4*math.sin(2*math.pi*(t*2+j))**2))
            d.line((x-6,y,x+6,y),fill=(197,255,255,a),width=1)
            d.line((x,y-6,x,y+6),fill=(197,255,255,a),width=1)
    glow=sharp.filter(ImageFilter.GaussianBlur(7))
    glow2=sharp.filter(ImageFilter.GaussianBlur(2.4))
    frame=Image.alpha_composite(Image.alpha_composite(glow,glow2),sharp)
    a=np.array(frame); a[:,:,3]=(a[:,:,3]*alpha_clip).astype('uint8')
    frame=Image.fromarray(a)
    frames.append(frame)
    previews.append(Image.alpha_composite(base,frame).convert('RGB'))

# APNG preserves soft transparency; GIF uses ordered alpha dithering.
frames[0].save(OUT/'CA140_neon_overlay.png',save_all=True,append_images=frames[1:],duration=80,loop=0,disposal=0,blend=0)
bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
threshold=np.tile((bayer+.5)*16,(math.ceil(H/4),math.ceil(W/4)))[:H,:W]
gif_frames=[]
for fr in frames:
    a=np.array(fr)
    p=fr.convert('RGB').quantize(colors=255,method=Image.Quantize.FASTOCTREE)
    idx=np.array(p); idx[a[:,:,3]<=threshold]=255
    out=Image.fromarray(idx,'P'); pal=p.getpalette()[:765]+[0,0,0]
    out.putpalette(pal); out.info['transparency']=255
    gif_frames.append(out)
gif_frames[0].save(OUT/'CA140_neon_overlay.gif',save_all=True,append_images=gif_frames[1:],duration=80,loop=0,transparency=255,disposal=2,optimize=False)
previews[0].save(OUT/'CA140_neon_preview.gif',save_all=True,append_images=previews[1:],duration=80,loop=0,optimize=False)
previews[10].save(OUT/'preview_still.png')
for name in ['CA140_neon_overlay.gif','CA140_neon_overlay.png','CA140_neon_preview.gif']:
    im=Image.open(OUT/name)
    print(name, im.size, im.n_frames, (OUT/name).stat().st_size)
