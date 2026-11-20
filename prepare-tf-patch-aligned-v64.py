"""Deterministic, user-approved perspective correction of the existing PNG."""
from pathlib import Path
import sys, json, datetime, shutil, hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent/'.codex-deps'))
import cv2, numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else R/('tactics-tf-pitch-card-background-v64-'+stamp);OUT.mkdir(exist_ok=True)
src=R/'TF-patch图片新增-V62-20261028/源PNG/TF patch.png'
raw=src.read_bytes();bgr=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
# Far/near goal-line intersections with the two touchlines. The lower grass
# apron is excluded. Coordinates are retained for future reproducible migration.
corners=np.float32([[835.75,158],[1236,158],[1642.75,643],[410.25,643]])
width,height=1024,1584
dst=np.float32([[0,0],[width-1,0],[width-1,height-1],[0,height-1]])
matrix=cv2.getPerspectiveTransform(corners,dst)
working=bgr.copy()
# Fill the photographed near goal from grass on the same scanlines first;
# a large Telea hole would otherwise produce a visible triangular smear.
for row in range(567,652):
    left=np.median(working[row,max(0,946-14):946-3],axis=0)
    right=np.median(working[row,1128:1140],axis=0)
    mix=np.linspace(0,1,180)[:,None]
    working[row,946:1126]=np.rint(left*(1-mix)+right*mix).astype(np.uint8)
warped=cv2.warpPerspective(working,matrix,(width,height),flags=cv2.INTER_CUBIC)
hsv=cv2.cvtColor(warped,cv2.COLOR_BGR2HSV)
white=((hsv[:,:,1]<165)&(hsv[:,:,2]>130)).astype(np.uint8)*255
white=cv2.dilate(white,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(25,25)))
# The near goal is a vertical photographed object, not part of the grass plane.
# Remove its projecting mesh with the same source-to-field transform.
goal_src=np.float32([[[946,567],[1125,567],[1125,651],[946,651]]])
goal_dst=cv2.perspectiveTransform(goal_src,matrix).round().astype(np.int32)
clean=cv2.inpaint(warped,white,7,cv2.INPAINT_TELEA)
Image.fromarray(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB)).convert('RGBA').save(OUT/'TF patch aligned.png')
Image.fromarray(cv2.cvtColor(warped,cv2.COLOR_BGR2RGB)).save(OUT/'草坪透视校正-清线前.png')
Image.fromarray(white).save(OUT/'原图白线及近端球门清理掩码.png')
annotated=bgr.copy()
for i,(x,y) in enumerate(corners):
    cv2.circle(annotated,(round(float(x)),round(float(y))),8,(0,0,255),-1)
    cv2.putText(annotated,['TL','TR','BR','BL'][i],(round(float(x))+10,round(float(y))-10),cv2.FONT_HERSHEY_SIMPLEX,.8,(0,0,255),2)
cv2.polylines(annotated,[corners.round().astype(np.int32)],True,(0,0,255),2)
Image.fromarray(cv2.cvtColor(annotated,cv2.COLOR_BGR2RGB)).save(OUT/'源图场地四角标定.png')
shutil.copy2(src,OUT/'TF patch original.png')
shutil.copy2(R/'patchplayerbg图片新增-V63-20261028/源PNG/patchplayerbg.png',OUT/'patchplayerbg original.png')
reprojected=cv2.perspectiveTransform(corners[None,:,:],matrix)[0]
error=float(np.max(np.linalg.norm(reprojected-dst,axis=1)));assert error<.001
record={'source':str(src),'source_sha256':hashlib.sha256(raw).hexdigest(),'source_size':[bgr.shape[1],bgr.shape[0]],'source_corners_TL_TR_BR_BL':corners.tolist(),'target_size':[width,height],'target_corners':dst.tolist(),'homography':matrix.tolist(),'inverse_homography':np.linalg.inv(matrix).tolist(),'corner_error_pixels':error,'line_mask_fraction':float(np.mean(white>0)),'policy':'grass priority; photo white markings and near goal cleared, game native markings authoritative','texture_name':'TF patch aligned','path_id':'-910000000000148'}
(OUT/'alignment.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
print(str(OUT))
