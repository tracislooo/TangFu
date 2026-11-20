from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={p:(p/G).read_bytes() for p in [GAME,SKIN]};assert before[GAME]==before[SKIN]
e=UnityPy.load(before[GAME]);obs={o.path_id:o for o in e.objects};hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in obs.items()}
oldwrite=TypeTreeHelper.write_value
h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
f32=lambda v:struct.unpack('<f',struct.pack('<f',float(v)))[0]
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def serial(rs,i):return rs[rs[i]['data']['m_SerializedData']['rid']]['data']
def value(s,n,k):
 p=next(p for p in s['m_Rules'][n['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)
 h=p['m_Values'][0];return s['dimensions'][h['valueIndex']]['value']
pitchobj=obs[-960000000003030];pd=pitchobj.read_typetree();pr=refs(pd);pso=obs[pd['inlineSheet']['m_PathID']];ps=pso.read_typetree();pst=Styles(ps)
serial(pr,2014)['AspectRatio']=f32(200/327)
pst.box(pr[2014],0,134.5,200,327)
for i in [1022,1023,2018]:pst.box(pr[i],0,0,200,327)
assert all(pr[i]['data']['m_Parent']=={'rid':2014} for i in [1022,1023,2018])

rowobj=obs[-960000000003040];rd=rowobj.read_typetree();rr=refs(rd);rso=obs[rd['inlineSheet']['m_PathID']];rs=rso.read_typetree();rst=Styles(rs)
canvas_nodes=[];cells=[]
for r in rr.values():
 a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
 if r['rid'] in [1001,1002,1004] or name.startswith('PositionZoneMaskAbove'):
  rst.box(r,0,0,200,327);canvas_nodes.append(r['rid'])
 if a.get('m_FullTypeName')=='SI.Bindable.SIButton' and name.startswith('PositionZone_'):
  x,y,w,h=[value(rs,r,k) for k in [131089,131104,131105,131087]]
  cells.append((name,x,y,w,h))
assert len(cells)==14 and len(canvas_nodes)==16
# Generated item wrappers must also be explicit; percent heights can resolve against 100px wrappers.
css=next(r for r in rs['m_Rules'] if 'fm27-position-item-root' in str(r['m_ComplexSelectors']))
for prop in css['m_Properties']:
 if prop['m_Id']==131105:prop['m_Values']=[rst.px(200)]
 if prop['m_Id']==131087:prop['m_Values']=[rst.px(327)]
css['m_Properties'] += [rst.p(131096,rst.px(327)),rst.p(131094,rst.px(327)),rst.p(131097,rst.px(200)),rst.p(131095,rst.px(200))]
for col in range(3):
 for band in range(6):
  x,y=(col+.5)*100/3,(band+.5)*100/6
  hits=[name for name,xx,yy,ww,hh in cells if xx-.001<=x<xx+ww-.001 and yy-.001<=y<yy+hh-.001]
  assert len(hits)==1,(col,band,hits)
for name,x,y,w,h in cells:
 assert x>=-.001 and y>=-.001 and x+w<=100.001 and y+h<=100.001

pitchobj.save_typetree(pd);pso.save_typetree(ps);rowobj.save_typetree(rd);rso.save_typetree(rs)
expected={pitchobj.path_id:pd,pso.path_id:ps,rowobj.path_id:rd,rso.path_id:rs}
b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
 else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i],i
out=R/('popup-pitch-200x327-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[p])
(out/G).write_bytes(b)
for p,old in before.items():assert (p/G).read_bytes()==old
try:
 for p in [GAME,SKIN]:(p/G).write_bytes(b)
 for p in [GAME,SKIN]:assert (p/G).read_bytes()==b
except BaseException:
 for p,old in before.items():(p/G).write_bytes(old)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'pitch_size':[200,327],'pitch_top_in_module':134.5,
 'explicit_canvas_nodes':len(canvas_nodes),'zone_cells':len(cells),'all_18_pitch_grid_cells_covered_once':True,
 'generated_wrapper_height':327,'all_popup_routes_share_this_pitch':True,'other_resources_unchanged':len(obs)-4}
(out/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report))
